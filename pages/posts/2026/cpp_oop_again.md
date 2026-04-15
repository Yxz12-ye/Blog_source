---
title: C++的面向对象的再学习
date: '2026-04-15 15:47:14'
updated: '2026-04-15 15:47:14'
categories:
- 技术
tags:
- C/C++
---

# C++的面向对象的再学习

## 前言

关于我为什么在学习C++很久后又要重新去再学一遍OOP呢? 我感觉就是在实际使用中会碰到各种奇妙的问题, 而这些问题在我初次学习(有学校教的还有自学的)面向对象时其实并没有遇到过, 并且面向对象的精髓我也并没有掌握多少, 于是我就想深入的去学习面向对象, 同时写下这篇文章放到博客.

## 知识回顾

`struct`在C++中相较于C得到了一些扩充, 除了能存储数据外也能封装函数了, 而`class`则又在`struct`的基础上增加了访问权限, 至少我在之前授课的时候就是这么引入`class`的, 那么在引入后就开始讲继承、多态等内容了, 但其实有个问题就是, 为什么要面向对象呢?

<!-- more -->

## 对象

### 为什么要面向对象?

其实熟悉C语言编程的估计都会遇到一个很恨的东西, 那就是满天飞的函数和变量, 随便点一两下就能出现一堆代码提示然后也不知道能用哪个(至少我在单片机编程就是这样的), 而对象通过对数据和函数进行封装, 至少让代码提示变的没有那么凌乱了, 不过呢其实在现实世界中, 几乎每个事物都能看作是**对象**, 在代码中把服务也看成是一个对象**更贴近**现实世界的思维, 比如C语言, 向结构体内增加数据, 只能通过`add(struct*,item)`这样才能加入东西, 这种数据和动实际上并没有那么好理解(同时你也需要去找到底是哪个add函数才能向这个结构体里增加东西), 而面向对象中你知需要知道这个对象就能很快去找到增加的动作, 比如`obj.add(item)`, 这种数据和动作绑定不仅能加快开发效率, 还更符合人类对于世界的认知. 当然面向对象和面向过程本身并**不具有什么可比性**, 面向对象**更多的理念会在后面具体的实例中提及**.

### 为什么需要继承? 多态!

在初次接触继承的时候, 大家遇到第一个示例可能会是`Animal`、`Dog`和`Cat`(当然也可能是`Shape`、`Circle`和`Rectangle`), 通常是`Dog`和`Cat`继承自`Animal`类, 因为在认知中, 狗和猫都属于动物, 那是动物就一定有一些共同的属性, 比如年龄等. 但难道继承就只能减少这些重复的代码吗? 那自然不是的, 试想一下有个动物园里面有很多的动物, 如果为每个动物都单独分配一个变量, 在要对所有动物执行相同操作的时候, 发现需要`a1.xx`、`a2.xx`...这样一个一个调用, 这样就显得太麻烦了, 那有没有办法能做到统一管理, 而不只是只能统一管理某一种动物呢? 答案就是继承了, 在某个动物继承自`Animal`类后这个动物除了具有这种动物的特性, 同时也具有了所有动物的共性, 这样就能做到统一管理. 当然直接说很抽象, 直接上代码.

在没有继承时:

```c++
#include <vector>

class Animal
{
public:
	Animal()=default;
	~Animal()=default;

	void doSomething() { return; };
};

class Dog
{
public:
	Dog()=default;
	~Dog()=default;

	void doSomething() { return; };

};

class Cat
{
public:
	Cat() = default;
	~Cat() = default;

	void doSomething() { return; };

};

// 省略一堆动物的定义 

std::vector<Animal> a;
std::vector<Dog> b;
std::vector<Cat> c;
// 省略一堆具体动物的数组

void manger() {
	for (auto& am : a) am.doSomething();
	for (auto& am : b) am.doSomething();
	for (auto& am : c) am.doSomething();
	// 省略一堆动物的管理
}
```

继承后:

```c++
#include <vector>
#include <iostream>

class Animal
{
public:
	Animal()=default;
	virtual ~Animal()=default;

	virtual void doSomething() { std::cout << "Animal" << std::endl; return; };
};

class Dog : public Animal
{
public:
	Dog()=default;
	~Dog()=default;

	void doSomething() override { std::cout << "Dog" << std::endl; return; };

};

class Cat : public Animal
{
public:
	Cat() = default;
	~Cat() = default;

	void doSomething() override { std::cout << "Cat" << std::endl; return; };

};

// 省略一堆动物的定义 

std::vector<Animal> a;

void addAnimal() {
	a.push_back(Animal());
	a.push_back(Dog());
	a.push_back(Cat());
}

void manger() {
	for (auto& am : a) am.doSomething();
}
```

当然这里其实是用到了**向上转型**, 每个动物的`doSomething`是不同的, 但是运行的时候发现竟然是相同的, 这个问题我们后面再解决(先说一下, 这是**对象切片**的问题, 为什么和怎么解决后面**虚函数表**再说)

## 深入

### 虚函数表

既然是数据, 那肯定是要有结构的, 还有存储的地方. 这里以`clang`去生成虚函数表

```bash
clang++ -c -Xclang -fdump-vtable-layouts -Xclang -fdump-record-layouts -emit-llvm FileName.cpp > layout.txt
```

不过`clang`生成的虚函数表还是可读性太差了, 这里还是用gcc生成的来看

```bash
g++ -fdump-lang-class FileName.cpp
```

为了方便观察, 我们为`Animal`类和`Dog`类增加了成员变量, 并为Animal再加入一个虚函数, 但这次我们不去改写

```c++
class Animal
{
public:
    int age;          // 父类数据
	Animal()=default;
	virtual ~Animal()=default;

    virtual void bark(){std::cout << "Bark" << std::endl; return;};

	virtual void doSomething() { std::cout << "Animal" << std::endl; return; };
};

class Dog : public Animal
{
public:
    int tailLength;   // 子类独有数据
	Dog()=default;
	~Dog()=default;

	void doSomething() override { std::cout << "Dog" << std::endl; return; };

};
```

```
Vtable for Animal
Animal::_ZTV6Animal: 6 entries
0     (int (*)(...))0
8     (int (*)(...))(& _ZTI6Animal)
16    (int (*)(...))Animal::~Animal
24    (int (*)(...))Animal::~Animal
32    (int (*)(...))Animal::bark
40    (int (*)(...))Animal::doSomething

Class Animal
   size=16 align=8
   base size=12 base align=8
Animal (0x0x780eb4cf32a0) 0
    vptr=((& Animal::_ZTV6Animal) + 16)
    
Vtable for Dog
Dog::_ZTV3Dog: 6 entries
0     (int (*)(...))0
8     (int (*)(...))(& _ZTI3Dog)
16    (int (*)(...))Dog::~Dog
24    (int (*)(...))Dog::~Dog
32    (int (*)(...))Animal::bark
40    (int (*)(...))Dog::doSomething

Class Dog
   size=16 align=8
   base size=16 base align=8
Dog (0x0x780eb4cd6c98) 0
    vptr=((& Dog::_ZTV3Dog) + 16)
Animal (0x0x780eb4cf3540) 0
      primary-for Dog (0x0x780eb4cd6c98)

Vtable for Cat
Cat::_ZTV3Cat: 6 entries
0     (int (*)(...))0
8     (int (*)(...))(& _ZTI3Cat)
16    (int (*)(...))Cat::~Cat
24    (int (*)(...))Cat::~Cat
32    (int (*)(...))Animal::bark
40    (int (*)(...))Cat::doSomething

Class Cat
   size=16 align=8
   base size=12 base align=8
Cat (0x0x780eb4cd6d68) 0
    vptr=((& Cat::_ZTV3Cat) + 16)
Animal (0x0x780eb4cf3600) 0
      primary-for Cat (0x0x780eb4cd6d68)
```

> **第一个 0**：虚表偏移量（offset to top），单继承下为 0，用于多重继承时的 `this` 调整。
>
> **两个析构函数** 分别是：
> 不释放内存的析构（用于栈对象销毁）。
> 包含 `delete this` 释放内存的析构（用于 `delete` 指针时）。

在+8位置处的是RTTI, 用于区分对象用的

|         内存起始地址         |
| :--------------------------: |
|        `vptr`(8字节)         |
|         `age`(4字节)         |
| `padding`(4字节, 内存对齐用) |
|    `tailLength`(4个字节)     |
| `padding`(4字节, 内存对齐用) |

这里的`vptr`会指向一个**装满函数内存地址的数组**, 而这个**就是虚函数表(vtable).**到这里估计就清晰了一点, 从日志看`vptr=((& Dog::_ZTV3Dog) + 16)`, `vptr`指向的不就是`Dog`吗, 而且里面除了有重写的`doSomething`, 还有没被重写的`Animal::bark`, 因此就很容易理解了, 多态实际上就是为每个对象生成虚函数表, 调用的时候会去查对应类的虚函数表, 改写与否就能很轻松的看出来了. (**补充:**普通成员函数是共享一篇内存的, 通过this指针去访问特定对象的数据成员, 因此不会去查虚表, 而是在编译时就写死了, **当然从名字就能看出来虚函数表那一定是存虚函数的表**)

好, 那么回到上面的多态失效的问题, 这是什么原因导致的呢? 不难发现我们`Dog()`会创建一个临时对象, 然后赋值给了一个`Animal`对象, 因为派生类一定比基类大, 所以势必会发生数据丢失, 那如果只是简单的内存切片, `vptr`指向的应该还是`Dog`的虚函数表才对啊, 就算丢失了`Dog`的成员也不应该会出现多态失效的问题. 那么问题出在哪呢? 难道`vptr`就只是简单的拷贝吗?

**绝对不是！如果编译器真的连 `vptr` 都拷贝过去，程序就会崩溃！**

让我们做一个危险的假设：**如果**编译器把 `Dog` 的 `vptr` 拷贝给了 `a`，会发生什么？

1. 你调用 `a.doSomething()`。
2. 顺着 `Dog` 的 `vptr`，去执行 `Dog::doSomething()`。
3. 在 `Dog::doSomething()` 的代码里，假设访问了`Dog`的成员变量。
4. 但是！此时的 `this` 指向的是 `a`！`a` 的内存里根本没有 `tailLength` 这个变量（它刚才被物理切片丢弃了）。
5. 结果：程序访问了越界的内存，**段错误崩溃（Segfault）**。

因此绝对不是内存拷贝那么简单, 这个赋值过程实际上漏了一步, 那就是调用调用 `Animal` 的**拷贝构造函数** `Animal(const Animal& other)`。虽然我们没写, 但是编译器会为每个函数都生成一个默认的, 而在这个函数里, 会把`Dog`的`age`赋值给`Animal.age`, 然后**重置**`vptr`. 因此也就丢失了派生类的一切! 那最终的解决方法其实也很简单, 这里就不做过多赘述了(提示:指针或引用, 具体可以去问问AI).

### 向下类型转换

~~*(其实我应该先讲这个的, 因为比较简单)*~~

OK, 有个情景, 是在Qt里的, 我们有个Tab管理的类, 我们能向这个类里插入`QWidget`类, 我们想要访问里面的页面(继承自`QWidget`的类)的数据成员应该怎么办呢? 回顾知识, 我们只能拿到基类的指针, 而这个指针只能用于访问基类的成员还有派生类重写的虚函数, 但是`QWidget`类并不是我们写的, 那该怎么办呢? 这里就需要用到**向下类型转换(Downcasting)**, 分为`dynamic_cast`和`static_cast`, 两者的区别就是`dynamic_cast`会检查能否进行类型转换(毕竟你也不知道到底是谁继承自`QWidget`), 如果转换失败则会返回nullptr, 相应的, 性能也差一点, 而`static_cast`不会检查, 只在你能100%确定一定是这个派生类才使用, 否则会产生未定义行为.

示例:

```c++
// 增加页面定义
int QTabWidget::addTab(QWidget *widget, const QString &);
// 获取活动页面
QWidget *QTabWidget::currentWidget() const
```

这里我很明显只能拿到`QWidget*`, 那就不得不去进行类型转换了(这里的`qobject_cast`和`dynamic_cast`差不多, 不过是专门针对Qt这种元对象系统优化的, 性能会比使用`dynamic_cast`要好很多)

```c++
connect(pageContiner, &ElaTabWidget::currentChanged, this, [=](int index) {
    qDebug() << "page " << index << " clicked";
    auto p = pageContiner->currentWidget();
    EditorView* m = qobject_cast<EditorView*>(p);
    if (m) {
        // 你的逻辑
    }
});
```

### 模板和类的结合

在初次接触STL的我, 使用`list<...>`时会对尖括号感到疑惑, 当时也没有多想, 就简单的抄个代码了事. 不过呢现在知道这其实就是模板.

定义一个模板类很简单

```c++
template<typename T>
class MyClass
{
// 成员还有函数
};
```

### 模板特化

施工中, 不过其实不难理解, 可能不会施工

### 类型萃取

施工中

### CRTP

**CRTP**是C++编译时多态的体现, 一般的多态是程序运行时利用虚函数表去查询对应函数, 然后调用, 而**CRTP**在编译时就能确定确定派生类要调用的函数, 从而省略查虚函数表的步骤.

一个简单的CRTP示例:

```c++
template<typename Derived>
class Base {
public:
    void interface() {
        // 通过 static_cast 调用派生类的实现（编译期多态）
        static_cast<Derived*>(this)->impl();
    }
};

class Derived : public Base<Derived> {
public:
    void impl() { /* 具体实现 */ }
};
```

#### 静态多态

>  当需要一组类型提供相同接口，但又不想承担虚函数调用开销时（例如实时系统、游戏引擎、高频交易），CRTP 是一种零成本抽象。

什么意思呢? 这会打乱 CPU 缓存机制（Cache Line），每次调用 虚函数 还要经历找 `vptr` -> 查表的跳跃，导致严重的 **CPU Cache Miss**。也就是降低CPU缓存命中率, 这在小软件系统中是无所谓的, 但是来到性能要求极高的系统(如游戏和高并发系统), 查表带来的性能开销往往不容忽视, 那既然派生类每次调用的函数都一样, 那能否直接跳过查表这个阶段呢? 当然可以, 这就是CRTP的第一个用处.

```c++
// 糟糕的设计
class Particle {
public:
    float x, y, z;
    // 仅仅为了方便拓展，加了一个虚函数
    virtual void update() {} 
};
```

**工程解决方案：CRTP（奇特的递归模板模式）**
在极致性能要求下，工程中会彻底抛弃 `virtual`，转而使用模板来实现**“静态多态”**。既有继承的复用性，又**没有任何 `vptr` 的开销**。

```c++
template <typename Derived>
class BaseParticle {
public:
    void update() {
        // 编译期绑定，没有 vptr，没有查表开销，直接 inline！
        static_cast<Derived*>(this)->doUpdate();
    }
};

class FireParticle : public BaseParticle<FireParticle> {
public:
    void doUpdate() { /* 真正逻辑，位于代码段 */ }
};
```

示例代码:

```c++
#include<iostream>

template<typename T>
class Shape {
public:
    void draw() const {
        static_cast<const T*>(this)->draw_impl();
    }
};

class Circle : public Shape<Circle> {
public:
    void draw_impl() const { std::cout << "Circle\n"; }
};

class Square : public Shape<Square> {
public:
    void draw_impl() const { std::cout << "Square\n"; }
};

// 使用模板函数统一调用
template<typename ShapeType>
void render(const Shape<ShapeType>& s) {
    s.draw();  // 编译期确定调用哪个 draw_impl
}

void main() {
    Circle a;
    Square b;
    render(a);
    render(b);
}
```

#### 代码复用与 Mixin 风格

还有很多, 我都略了

## 总结

有点累了, 不想写总结了...

---

**版权声明**：本文为原创文章，转载请注明出处。

