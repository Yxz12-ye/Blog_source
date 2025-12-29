---
title: 从汇编层面学习C++右值引用
date: '2025-12-27 20:29:09'
updated: '2025-12-29 15:42:00'
categories:
- 技术
tags:
- C++
---

# 从汇编层面学习C++右值引用

## 概述

> 前言: 看这个最好需要有一定内存布局和汇编的基础
>
> 然后文章写到一半发现我也被搞糊涂了, 又去好好学习了一下`C++`😭
>
> 最后还是借助了AI辅助编写

众所周知, 右值是临时的值是不能取地址的值, 有时候我们只想临时使用右值而又不想拷贝或移动, 那就可以使用C++的右值特性, 那右值具体是如何实现的呢?

这里我准备了一个测试代码

<!-- more -->

```c++
#include <iostream>
#include <string>
#include <vector>

struct MyStruct
{
	int ID;
	std::string str;
	MyStruct(int _ID, std::string _str)
	{
		ID = _ID;
		str = _str;
		std::cout << "调用构造函数\n";
	}

	friend std::ostream &operator<<(std::ostream &out, const MyStruct &a)
	{
		out << a.ID << ' ' << a.str;
		return out;
	}

	MyStruct &operator=(const MyStruct &other)
	{
		if (this == &other)
			return *this;
		this->ID = other.ID;
		this->str = other.str;
		std::cout << "拷贝构造" << std::endl;
		return *this;
	}

	MyStruct(const MyStruct &other)
	{
		this->ID = other.ID;
		this->str = other.str;
		std::cout << "拷贝构造" << std::endl;
	}

	MyStruct &operator=(MyStruct &&other) noexcept
	{
		if (this == &other)
			return *this;
		this->ID = other.ID;
		this->str = other.str;
		other.ID = 0;
		other.str = "";
		std::cout << "移动构造" << std::endl;
		return *this;
	}

	MyStruct(MyStruct &&other) noexcept
	{
		this->ID = other.ID;
		this->str = other.str;
		other.ID = 0;
		other.str = "";
		std::cout << "移动构造" << std::endl;
	}

	~MyStruct()
	{
		std::cout << "析构函数" << std::endl;
	}
};

int main()
{
	MyStruct &&a = MyStruct(0x12345678, "this is a very long str and unable to store on stack directly");
	std::cout << a << std::endl;
	std::cout << &a << std::endl;
}
```

## 正文

上述程序运行的结果为

```
调用构造函数
305419896 this is a very long str and unable to store on stack directly
000000FE765EFDF8
析构函数
```

利用反汇编得到汇编码, 并把两着情况进行比较(一开始其实两个完整的汇编都放了, 不过好像没什么意义就省略了)

我们把重要部分剥离

```assembly
右值引用:
00007FF7AAF4103D | call main.7FF7AAF41180               调用构造函数
00007FF7AAF41042 | mov rax,qword ptr ss:[rbp-48]        
00007FF7AAF41046 | mov qword ptr ss:[rbp+10],rax        
00007FF7AAF4104A | mov rdx,qword ptr ss:[rbp+10]        
00007FF7AAF4104E | lea rcx,qword ptr ds:[7FF7AAF833A0]  
00007FF7AAF41055 | call main.7FF7AAF41240               输出重载
左值拷贝:
00007FF6E70D103D | call main1.7FF6E70D1180              调用构造函数
00007FF6E70D1042 | mov rdx,qword ptr ss:[rbp-50]        
00007FF6E70D1046 | lea rcx,qword ptr ds:[7FF6E71133A0]  
00007FF6E70D104D | call main1.7FF6E70D1240              输出重载
```

很明显, 似乎直接左值拷贝性能更优? 初次看到这个疑惑很正常, 因为被编译器优化了`拷贝省略（Copy Elision）`, 所以直接运行也会发现只调用了构造函数, 关掉优化则需要执行

```bash
# clang/gcc
g++ -fno-elide-constructors -O0 test.cpp  # 强制关闭拷贝省略
# MSVC
cl /Od /GR- test.cpp  # 禁用优化
```

那么关掉后我们再看看(这里如果要观察拷贝构造, 那么需要注释掉移动语义相关的代码, 否则会被编译器优化成移动语义)

直接放上重点代码

```assembly
右值引用:
00007FF6D3E2104A | call main.7FF6D3E21230                调用构造
00007FF6D3E2104F | jmp main.7FF6D3E21051                 
00007FF6D3E21051 | lea rcx,qword ptr ss:[rbp-38]         
00007FF6D3E21055 | call main.7FF6D3E212F0                
00007FF6D3E2105A | lea rax,qword ptr ss:[rbp+8]          
00007FF6D3E2105E | mov qword ptr ss:[rbp+30],rax         
00007FF6D3E21062 | mov rdx,qword ptr ss:[rbp+30]         
00007FF6D3E21066 | lea rcx,qword ptr ds:[7FF6D3E643A0]   
00007FF6D3E2106D | call main.7FF6D3E21320                输出
左值拷贝:
00007FF7252B104A | call main1.7FF7252B1270               构造
00007FF7252B104F | jmp main1.7FF7252B1051                
00007FF7252B1051 | lea rcx,qword ptr ss:[rbp+30]         
00007FF7252B1055 | lea rdx,qword ptr ss:[rbp+8]          
00007FF7252B1059 | call main1.7FF7252B1330               拷贝
00007FF7252B105E | jmp main1.7FF7252B1060                
00007FF7252B1060 | lea rcx,qword ptr ss:[rbp+8]          
00007FF7252B1064 | call main1.7FF7252B13E0               析构
00007FF7252B1069 | lea rcx,qword ptr ss:[rbp-38]         
00007FF7252B106D | call main1.7FF7252B1460               
00007FF7252B1072 | lea rcx,qword ptr ds:[7FF7252F43A0]   
00007FF7252B1079 | lea rdx,qword ptr ss:[rbp+30]        
00007FF7252B107D | call main1.7FF7252B1490               输出
```

可以看到右值引用相比于左值拷贝直接省去了复制的过程, 不过我们继续深入, 发现`rbp-38`处存储着一个指向堆内存的指针, 进入后发现是`std::string`在堆内存的实例, 然后在`rbp+08`找到了我们的对象, 而`this`指针在`rbp+30`, 指向的正是`rbp+08`

```hex
rbp-38 00 C8 CB 6E B7 02 00 00 00 00 00 00 00 00 00 00 .ÈËn·........... 
rbp-28 00 00 00 00 00 00 00 00 0F 00 00 00 00 00 00 00 ................ 
rbp-18 00 C8 CB 6E B7 02 00 00 00 00 00 00 00 00 00 00 .ÈËn·........... 
rbp-08 00 00 00 00 00 00 00 00 0F 00 00 00 00 00 00 00 ................ 
rbp+08 78 56 34 12 F6 7F 00 00 90 C8 CB 6E B7 02 00 00 xV4.ö....ÈËn·... 
```

后来发现汇编看起来还是太吃力了, 既然是自己写的, 干脆看一眼IDA生成的伪代码吧

```c
// Hidden C++ exception states: #wind=2
__int64 __fastcall main()
{
  struct basic_ostream<char,std::char_traits<char> > *(__fastcall *v1)(struct basic_ostream<char,std::char_traits<char> > *); // [rsp+28h] [rbp-58h]
  struct basic_ostream<char,std::char_traits<char> > *(__fastcall *v2)(struct basic_ostream<char,std::char_traits<char> > *); // [rsp+30h] [rbp-50h]
  char v3[32]; // [rsp+48h] [rbp-38h] BYREF
  std::string v4; // [rsp+68h] [rbp-18h] BYREF
  MyStruct v5; // [rsp+88h] [rbp+8h] BYREF
  MyStruct *v6; // [rsp+B0h] [rbp+30h]
  __int64 v7; // [rsp+B8h] [rbp+38h]

  v7 = -2;
  std::string::string(v3);
  std::string::string(&v4);
  MyStruct::MyStruct((int)&v5, (std::string *)0x12345678);
  std::string::~string(v3);
  v6 = &v5;
  v2 = (struct basic_ostream<char,std::char_traits<char> > *(__fastcall *)(struct basic_ostream<char,std::char_traits<char> > *))operator<<((struct basic_ostream<char,std::char_traits<char> > *)&std::cout, &v5);
  std::ostream::operator<<(v2);
  v1 = (struct basic_ostream<char,std::char_traits<char> > *(__fastcall *)(struct basic_ostream<char,std::char_traits<char> > *))std::ostream::operator<<(&std::cout);
  std::ostream::operator<<(v1);
  MyStruct::~MyStruct(&v5);
  return 0;
}
```

左值拷贝:

```c
// Hidden C++ exception states: #wind=3
__int64 __fastcall main()
{
  struct basic_ostream<char,std::char_traits<char> > *(__fastcall *v1)(struct basic_ostream<char,std::char_traits<char> > *); // [rsp+28h] [rbp-58h]
  struct basic_ostream<char,std::char_traits<char> > *(__fastcall *v2)(struct basic_ostream<char,std::char_traits<char> > *); // [rsp+30h] [rbp-50h]
  char v3[32]; // [rsp+48h] [rbp-38h] BYREF
  std::string v4; // [rsp+68h] [rbp-18h] BYREF
  MyStruct v5; // [rsp+88h] [rbp+8h] BYREF
  MyStruct v6; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v7; // [rsp+D8h] [rbp+58h]

  v7 = -2;
  std::string::string(v3);
  std::string::string(&v4);
  MyStruct::MyStruct((int)&v5, (std::string *)0x12345678);
  MyStruct::MyStruct(&v6);
  MyStruct::~MyStruct(&v5);
  std::string::~string(v3);
  v2 = (struct basic_ostream<char,std::char_traits<char> > *(__fastcall *)(struct basic_ostream<char,std::char_traits<char> > *))operator<<((struct basic_ostream<char,std::char_traits<char> > *)&std::cout, &v6);
  std::ostream::operator<<(v2);
  v1 = (struct basic_ostream<char,std::char_traits<char> > *(__fastcall *)(struct basic_ostream<char,std::char_traits<char> > *))std::ostream::operator<<(&std::cout);
  std::ostream::operator<<(v1);
  MyStruct::~MyStruct(&v6);
  return 0;
}
```

### 1. 临时对象的存储位置

从伪代码看临时的对象直接在`main`函数的栈上创建了, 这个和`RVO`相关:

- **对于小对象（满足NRVO条件）**：编译器会直接在目标位置构造（如函数栈帧中）
- **对于大对象或复杂类型**：可能会在返回前先构造在栈上，然后拷贝/移动到目标位置
- **RVO（返回值优化）**：在C++17起成为**强制性**优化
- **NRVO（具名返回值优化）**：虽不是强制，但几乎所有现代编译器都会执行（包括Debug模式）

### 2. 实际是什么?

#### 情况一：`MyStruct &&a = MyStruct(...)` （引用绑定）

- **这是优化吗？** 不，这不是优化，这是**C++的基本语法规则**。
- 发生了什么？
  1. 在栈上分配一块内存（假设地址 `0x100`），构造临时对象。
  2. 在栈上分配一个指针变量 `a`（假设地址 `0x108`）。
  3. 把 `0x100` 这个地址存进 `a` 里。
- **Debug模式下：** 依然如此。因为这就是“引用”的定义——它必须指向某个东西。
- **结论**：这里确实产生了一个临时对象，并且 `a` 只是指向它。

#### 情况二：`MyStruct a = MyStruct(...)` （直接构造）

这里的情况比较复杂，取决于你的C++标准版本。

1. 在 C++17 之前（C++98 / C++11 / C++14）

> 这是一个**“编译器优化（RVO - Return Value Optimization）”**。
>
> - **理论上**：应该先在栈上造一个临时对象，然后把这个临时对象**移动/拷贝**给变量 `a`，然后销毁临时对象。
>
> - 实际上
>
>    - **Release模式**：编译器很聪明，它发现“哎呀，反正都要拷给 `a`，我直接在 `a` 的内存地址上构造不就完了吗？”于是它把中间商（临时对象）消灭了。
>
>    - **Debug模式**：如果你不开优化（`-O0`），或者显式加上 `-fno-elide-constructors`，编译器可能会**老老实实地**创建临时对象，然后调用移动构造函数。**这时候你会看到移动构造被调用。**

2. 在 C++17 及以后（现代标准）

>这是一个**“强制拷贝省略（Guaranteed Copy Elision）”**。
>
>- **规则变了**：C++17 标准直接重新定义了这句话的含义。标准规定：当用一个纯右值（prvalue）初始化同类型的对象时，**不进行临时对象的实质化**。
>- **意味着什么？** `MyStruct(...)` 不再代表“创建一个临时对象”，它只代表“一组初始化参数”。这组参数直接传递给 `a` 的构造函数。
>- **Debug模式下**：**哪怕你处于Debug模式，哪怕你关掉所有优化，甚至哪怕你把移动构造函数设为 `private` 或 `delete`**，这行代码都能完美运行，且**没有任何临时对象产生**，也没有任何移动/拷贝操作。
>- **结论**：在C++17里，这不再是“优化”，这是“法律”。

### 一个反直觉的结论

对比这两种写法（在C++17环境下）：

1. **写法 A (引用)**: `MyStruct &&r = MyStruct(1);`
   - **栈内存消耗**：`sizeof(MyStruct)` (临时对象) + `8字节` (指针 r)。
   - **代价**：多费了8个字节存指针。
2. **写法 B (值)**: `MyStruct a = MyStruct(1);`
   - **栈内存消耗**：`sizeof(MyStruct)` (对象 a)。
   - **代价**：无。直接在 `a` 的地址构造。

**震惊吗？**
你原本以为用“右值引用”(`&&`)能省去拷贝，效率最高。
但实际上，在现代C++中，直接写 `MyStruct a = ...` （写法B）反而更纯粹、更高效（省了一个指针的空间），因为编译器（根据标准）直接把中间环节全砍了。

## 总结

**修正与反思：**

在分析汇编时，我曾担心直接写 `MyStruct a = MyStruct(...)` 会产生额外的拷贝开销，所以尝试用 `MyStruct &&a` 来“手动优化”。

但深入研究后发现，这是一个“过时”的担忧。

- **对于 `MyStruct &&a`**：编译器确实在栈上生成了临时对象，并让 `a` 指向它（本质是指针）。
- **对于 `MyStruct a`**：在 C++17 标准引入“强制拷贝省略（Guaranteed Copy Elision）”后，编译器直接在 `a` 的内存地址上构造对象。

**结论**：在 Debug 模式下（使用 C++17），直接值初始化的效率甚至略高于右值引用绑定，因为它连那个 8 字节的指针存储都省了！这说明在现代 C++ 中，我们要相信编译器和标准，不要过度进行“手动优化”。

---

**版权声明**：本文为原创文章，转载请注明出处。

