---
title: IO的深入学习
date: '2026-02-17 09:58:55'
updated: '2026-02-17 09:58:55'
categories:
- C/C++
- 技术
tags:
- IO
---

# IO的深入学习

## 概述

在很久之前写C语言作业时遇到一个问题, 从stdin获取用户输入时会获取到两次用户输入, 以下是一个小demo

```c
#include <stdio.h>

void print_menu()
{
    printf("1.abc\n2.bcd\n3.ccc\n>>>");
}

void process(char cho)
{
    switch (cho)
    {
    case '1':
        printf("abc\n");
        break;
    case '2':
        printf("bcd\n");
        break;
    case '3':
        printf("ccc\n");
        break;
    default:
        printf("err\n");
        break;
    }
}

int main()
{
    while (1)
    {
        print_menu();
        char choic = getchar();
        printf("\n");
        process(choic);
    }
}
```

<!-- more -->

执行后我们会发现似乎结果并没有像预期的那样, **当时**询问AI, 会告诉我们这是缓冲区的问题, 加个fflush就能解决(然而实际不行, 这里是**当时的AI**, 现在不一样了)

```bash
1.abc
2.bcd
3.ccc
>>>1

abc               ← 处理 '1'
1.abc
2.bcd
3.ccc
>>>                ← 自动读取了 '\n'，所以菜单后没有等待直接换行
err                ← 处理 '\n'
1.abc
2.bcd
3.ccc
>>>                ← 现在缓冲区空了，等待新输入
```

我们把输入字符的ASCII码打印后可知这莫名的两次输入实际上是我们的回车符也被算作是一次输入了, 最终解决也很简单, 只要在下次读取前清空缓冲区即可. 

(全文完)

就怪了, 当然不能这么水, 既然都谈到缓冲区了, 那就好好的学学缓冲区这个东西

## 正文

<!-- 在这里开始写正文内容 -->

### fflush

从cpp reference上可以得知基础的一些信息:

> # fflush
> C File input/output 
> Defined in header <stdio.h>
> `int fflush( FILE* stream );`
> For output streams (and for update streams on which the last operation was output), writes any unwritten data from the stream's buffer to the associated output device.
> 
> For input streams (and for update streams on which the last operation was input), the behavior is undefined.
> 
> If stream is a null pointer, all open output streams are flushed, including the ones manipulated within library packages or otherwise not directly accessible to the program.
> 
> ## Parameters
> `stream`	-	the file stream to write out
> ## Return value
> Returns zero on success. Otherwise EOF is returned and the error indicator of the file stream is set.

很明显, 这个函数确实会刷新缓冲区, 但是对于输入流, 刷新缓冲区是未定义行为

### 缓冲区

#### 系统调用

其实在讲缓冲区之前可以先讲讲sys call, 也就是系统调用, 它的含义推荐去看CSAPP, 这里做简单讲解

我们都知道在电脑上运行的软件是有权限控制的, 不存在一个程序能直接占用电脑的所有硬件资源, 这些接近系统底层硬件都是由操作系统统筹的, 程序只要和操作系统打声招呼就能委托操作系统去进行IO操作, 而IO操作势必会有操作系统的介入, 从用户态陷入内核态, 内核把数据准备好并复制到用户缓冲区(从内核缓冲区到用户缓冲区), 这个过程就是系统调用, 它有个致命的问题就是, 操作系统和用户软件肯定不是同一个软件, 所以在切换时会产生上下文切换, 把用户程序寄存器保存, 读取内核的寄存器, 返回用户态时也要进行相应的逆过程.

#### 速度

众所周知, 整个电脑有着非常多的存储器件, 从快到慢有: 寄存器, 多级缓存, RAM, SSD(固态硬盘), HDD(机械硬盘), 这些器件CPU的访问速度几乎都是百倍增长的, 如果每次只是小量的往外存写入东西, 那速度简直就是灾难.

#### 打包

既然每次写入少量数据到外存会存在性能问题, 那就把大批数据打包, 等到数据量达到一定程度后统一写入外存, 这样就能减少很多IO次数, 减少系统调用(其实多级缓存的出现也差不多是为了优化从内存读取/写入, 依据局部性原理), 累积的东西就是存在缓冲区

#### 数据流

回顾上面的例子, 从用户输入内容按下回车到程序接收到程序读取, 我们的数据是这样流动的(其实还有屏幕的事, 不过后面讲UI再说):

[外设(比如键盘)]-产生硬件中断->[键盘驱动]--一系列过程-->[TTY输入缓冲区（内核空间）]-复制到用户缓冲区->[用户空间], 最后由`getchar`读取缓冲区的字符

回到我们的这个例子, 程序执行`getchar`后会先去用户缓冲区去拿, 发现用户缓冲区什么也没有, 则触发系统调用, 系统去检查内核缓冲区是否有未拷贝的数据, 如果都没有则会先把程序挂起, 然后操作系统就去调度别的程序了, 直到外设硬件产生中断, 数据抵达内核缓冲区, 系统复制`1<回车>`到用户缓冲区, 唤醒程序(加入就绪队列), `getchar`拿到`1`, 第二次调用, `getchar`发现用户缓冲区还有内容, 就把缓冲区的内容读取, 这才造成了额外的输入.

### Linux的Page Cache

在Linux系统中，**页缓存（Page Cache）**可以加快对非易失性存储上文件的访问速度。原理是这样的：当Linux第一次对硬盘这类存储介质进行读写操作时，会同时把数据拷贝一份存到**内存的闲置区域**，这块区域就起到缓存的作用。如果之后需要再次读取这些数据，就能直接从内存里的缓存快速调取。[1]

## 总结

文章预告:

TUI的实现, 对`vibe coding`的看法

---

引用

[1] [Page Cache](https://www.thomas-krenn.com/en/wiki/Linux_Page_Cache_Basics)

**版权声明**：本文为原创文章，转载请注明出处。

