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

## 总结

文章预告:

TUI的实现, 对`vibe coding`的看法

---

**版权声明**：本文为原创文章，转载请注明出处。

