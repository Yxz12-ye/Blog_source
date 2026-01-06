---
title: C++第一次授课文档
date: '2026-01-06 16:40:32'
updated: '2026-01-06 21:24:54'
categories:
- C/C++
tags:
- 技术
---

::: tip

这篇文章是存货, 其实早该发了, 不过一直放到现在..

:::

<!-- more -->

### 结构体

#### C语言中的结构体

- **场景引入**：要管理一个学生的信息，需要姓名、学号、成绩等多个变量
- **问题**：这些变量是分散的，没有逻辑关联
- **解决方案**：结构体将相关的数据成员组织在一起

```C
#include<stdio.h>

struct struct_a
{
    int value;
    char str[10];
};

void m_print(struct struct_a A)
{
    printf("%d\n%s\n", A.value, A.str);
}

int main(int argc, char const *argv[])
{
    // struct_a A; 报错:未定义标识符 "struct_a"C/C++(20)
    struct struct_a A;
    A.value = 10;
    strcpy(A.str, "hello");

    m_print(A);
    return 0;
}

```

```out
10
hello
```

- **只有数据**，没有行为
- **操作数据的函数是分离的**：

```C
void printStudent(struct Student s) {
    printf("姓名：%s，学号：%d，成绩：%.2f\n", s.name, s.id, s.score);
}

void setScore(struct Student* s, double new_score) {
    s->score = new_score;
}
```

#### **C++结构体的改进**

- **不需要struct关键字**：`Student s1;` // 直接使用
- **可以包含函数**：

```C++
#include<iostream>
using namespace std;

struct Student {
    // 数据成员
    string name;
    int id;
    double score;
    
    // 成员函数（行为）
    void printInfo() {
        cout << "姓名：" << name << "，学号：" << id 
             << "，成绩：" << score << endl;
    }
    
    void setScore(double new_score) {
        score = new_score;
    }
};

int main(int argc, char const *argv[])
{
    // 使用
    Student s1;
    s1.name = "李四";
    s1.id = 1002;
    s1.setScore(88.5);
    s1.printInfo();  // 数据和操作在一起了！
    return 0;
}
```

```out
姓名：李四，学号：1002，成绩：88.5
```

- **数据与操作结合**：相关的函数现在与数据定义在一起(简洁)
- **更自然的调用方式**：`s1.printInfo()` 比 `printStudent(s1)` 更符合思维习惯

### 类

#### **1. 类 vs 对象**

- **类（Class）**：蓝图/模板
  - 比如"学生"这个概念
  - 定义了学生应该有哪些属性（数据成员）和行为（成员函数）
- **对象（Object）**：具体的实例
  - 比如"张三"这个具体的学生
  - 根据类的蓝图创建的具体实体

```C++
// 类：蓝图
class Student {
    // ... 成员定义
};

// 对象：实例
Student zhangsan;  // 创建一个Student对象
Student lisi;      // 创建另一个Student对象
```

(似乎和C++结构体挺相似的?)

上述C++结构体可改成:

```C++
#include<iostream>
using namespace std;

// struct改成class, 再加上public:
class Student {
public:
    // 数据成员
    string name;
    int id;
    double score;
    
    // 成员函数（行为）
    void printInfo() {
        cout << "姓名：" << name << "，学号：" << id 
             << "，成绩：" << score << endl;
    }
    
    void setScore(double new_score) {
        score = new_score;
    }
};

int main(int argc, char const *argv[])
{
    // 使用
    Student s1;
    s1.name = "李四";
    s1.id = 1002;
    s1.setScore(88.5);
    s1.printInfo();  // 数据和操作在一起了！
    return 0;
}
```

```out
姓名：李四，学号：1002，成绩：88.5
```

### 访问修饰符

访问修饰符控制类成员的可见性和访问权限，是**封装**的关键。

#### **1. 现有结构体的问题**

```c++
Student s1;
s1.score = -100;  // 成绩可以是负数？不合理！
```

- **数据直接暴露**：外部代码可以随意修改，可能导致无效状态

#### **2. 类的引入 - 访问控制**

```C++
class Student {
private:    // 私有区域：只有类内部的函数可以访问
    string name;
    int id;
    double score;

public:     // 公有区域：外部可以访问
    // 成员函数
    void printInfo() {
        cout << "姓名：" << name << "，学号：" << id 
             << "，成绩：" << score << endl;
    }
    
    void setScore(double new_score) {
        if (new_score >= 0 && new_score <= 100) {  // 数据验证！
            score = new_score;
        } else {
            cout << "无效的成绩！" << endl;
        }
    }
    
    double getScore() {  // 提供受控的访问方式
        return score;
    }
    
    void setName(string new_name) {
        name = new_name;
    }
};
```

- **封装的好处**：
  - **数据保护**：防止无效状态
  - **实现隐藏**：内部实现可以改变而不影响使用者
  - **接口稳定**：公有函数形成稳定接口

| 修饰符      | 类内部 | 派生类 | 类外部 |
| ----------- | ------ | ------ | ------ |
| `public`    | ✅      | ✅      | ✅      |
| `private`   | ✅      | ❌      | ❌      |
| `protected` | ✅      | ✅      | ❌      |

#### **3. 构造函数与析构函数**

- **问题**：创建对象时数据成员是未初始化的
- **解决方案**：构造函数

```C++
#include<iostream>
using namespace std;

class Student {
private:
    string name;
    int id;
    double score;

public:
    // 构造函数：在创建对象时自动调用
    Student(string n, int i, double s) {
        name = n;
        id = i;
        setScore(s);  // 使用setter保证数据有效性
    }
    void setScore(double _score){
        // 实现设置分数的有效性
        score=_score;
    }
    /*
    构造函数 - 使用初始化列表
    **初始化列表**是初始化成员变量的推荐方式，比在构造函数体内赋值更高效。
    初始化 const 成员或引用类型的成员。因为 const 对象或引用类型只能初始化，不能对他们赋值。
    Student(string n, int i, double s):name(n),id(i) { 
    	setScore(s);
    }
    */
    
};

int main(int argc, char const *argv[])
{
    // 使用
    Student s1("张三", 1001, 95.5);  // 创建时直接初始化
    Student s2("李四", 1002, 88.0);
    return 0;
}
```

**析构函数**在对象**销毁时自动调用**，用于清理资源（如释放内存、关闭文件等）。

```C++
~Student(){
    std::cout << "对象已经销毁" << std::endl;
}
```

```C++
#include<iostream>
using namespace std;

class Student {
private:
    string name;
    int id;
    double score;

public:
    // 构造函数：在创建对象时自动调用
    Student(string n, int i, double s) {
        name = n;
        id = i;
        setScore(s);  // 使用setter保证数据有效性
    }
    void setScore(double _score){
        // 实现设置分数的有效性
        score=_score;
    }
    /*
    构造函数 - 使用初始化列表
    Student(string n, int i, double s):name(n),id(i) { 
    	setScore(s);
    }
    */
    ~Student(){
    	std::cout << "对象已经销毁" << std::endl;
	}
    
};

int main(int argc, char const *argv[])
{
    // 使用
    Student s1("张三", 1001, 95.5);  // 创建时直接初始化
    Student s2("李四", 1002, 88.0);
    return 0;
}
```

```out
对象已经销毁
对象已经销毁
```

这里其实没有体现析构函数清理资源的作用, 等到讲到动态内存管理.

面向对象编程（OOP）是C++的核心特性之一。类和对象允许将数据与操作绑定在一起，支持**抽象**、**封装**、**继承**和**多态**。

## 第12章 拷贝语义

拷贝语义定义了对象如何被复制。理解**浅拷贝**和**深拷贝**对于管理动态内存至关重要。

### 浅拷贝

```C++
#include <iostream>
using namespace std;

class Student {
public:
    char* name;  // 使用原始指针！
    int age;

    Student(const char* n, int a) : age(a) {
        name = new char[strlen(n) + 1];  // 动态分配内存
        strcpy(name, n);
    }
    
    void print() {
        cout << name << " (" << age << ")" << endl;
    }
    
    // (缺少析构函数！内存泄漏警告！)
};

int main(int argc, char const *argv[])
{
    Student s1("张三", 20);
    Student s2 = s1;
    return 0;
}

```

```txt
s1: [name] --> "张三" 	  [age]:20
                 ↑
s2: [name] ------     	    [age]:20
```

**问题1：双重释放（Double Free）**

**问题2：一个修改影响另一个**

**默认**拷贝构造函数

### **解决方案 - 深拷贝**

```C++
// 深拷贝 - 拷贝赋值运算符
    Student& operator=(const Student& other) {
        if (this != &other) {  // 防止自赋值
            // 1. 释放原有资源
            delete[] name;
            // 2. 分配新资源
            name = new char[strlen(other.name) + 1];
            strcpy(name, other.name);
            age = other.age;
            cout << "拷贝赋值: " << name << endl;
        }
        return *this;
    }
```

```C++
int main() {
    Student s1("张三", 20);
    Student s2 = s1;  // 深拷贝 - 调用拷贝构造函数
    
    s2.setName("李四");
    
    s1.print();  // 张三 (20) ← 不受影响！
    s2.print();  // 李四 (20)
    
    Student s3("王五", 22);
    s3 = s1;     // 深拷贝 - 调用拷贝赋值运算符
    s3.print();  // 张三 (20)
    
    return 0;
}
```

```txt
s1: [name] --> "张三"
s2: [name] --> "李四"  ← 各自有独立的内存
s3: [name] --> "张三"
```

### 三法则（Rule of Three）

如果一个类需要自定义以下任何一个，通常需要自定义全部三个：

1. 析构函数
2. 拷贝构造函数
3. 拷贝赋值运算符

## 动态内存管理

#### 1. new运算符 - 分配内存

```C++
// 分配单个对象
int* ptr = new int;        // 分配一个int，未初始化
int* ptr2 = new int(42);   // 分配并初始化为42
string* str = new string("Hello");

// 分配数组
int* arr = new int[10];    // 分配10个int的数组
double* scores = new double[100];
```

#### **2. delete运算符 - 释放内存**

```C++
// 释放单个对象
delete ptr;
delete ptr2;
delete str;

// 释放数组
delete[] arr;        // 注意：数组要用delete[]
delete[] scores;
```

#### **3. 基本使用示例**

```C++
void basicDemo() {
    // 动态分配单个对象
    int* number = new int(100);
    cout << *number << endl;  // 输出: 100
    
    // 动态分配数组
    int size;
    cout << "输入数组大小: ";
    cin >> size;
    
    int* dynamicArray = new int[size];
    for (int i = 0; i < size; i++) {
        dynamicArray[i] = i * 10;
    }
    
    // 使用完后必须释放！
    delete number;
    delete[] dynamicArray;
}
```

### 内存泄露

内存泄漏发生在分配的内存没有被正确释放时。

```C++
// 示例1：忘记delete
void memoryLeak1() {
    int* ptr = new int(100);
    // 忘记 delete ptr;
    // 内存泄漏！
}

// 示例2：指针被覆盖
void memoryLeak2() {
    int* ptr = new int(100);
    ptr = new int(200);  // 原来的100泄露了！
    delete ptr;  // 只释放了第二个
}

// 示例3：异常导致泄漏
void memoryLeak3() {
    int* ptr = new int(100);
    someFunctionThatMightThrow();  // 如果抛出异常
    delete ptr;  // 这行不会执行！
}
```

#### **2. 其他常见问题**

**双重释放（Double Free）**

```C++
void doubleFree() {
    int* ptr = new int(100);
    delete ptr;
    // ... 一些代码
    delete ptr;  // 错误！同一块内存释放两次
}
```

**悬空指针（Dangling Pointer）**

```c++
void danglingPointer() {
    int* ptr = new int(100);
    delete ptr;  // 内存已释放
    // *ptr = 50;  // 危险！访问已释放的内存
    // cout << *ptr;  // 未定义行为！
}
```

**用delete释放new[]分配的数组**

```C++
void detectMemoryLeak() {
    for (int i = 0; i < 100000; i++) {
        int* leak = new int[100];
        delete leak;
    }
    // 程序运行期间内存持续增长！
}
```

### 智能指针

智能指针自动管理内存，避免内存泄漏和悬空指针问题。

#### unique_ptr - 独占所有权

```C++
#include <memory>

void uniquePtrDemo() {
    // 创建unique_ptr
    std::unique_ptr<int> ptr1 = std::make_unique<int>(42);
    std::unique_ptr<string> ptr2 = std::make_unique<string>("Hello");
    
    // 使用方式与原始指针类似
    cout << *ptr1 << endl;  // 42
    cout << ptr2->length() << endl;  // 5
    
    // 自动管理内存，不需要手动delete！
    
    // 所有权转移（移动语义）
    std::unique_ptr<int> ptr3 = std::move(ptr1);  // ptr1变为nullptr
    if (!ptr1) {
        cout << "ptr1已经转移所有权" << endl;
    }
    
} // 离开作用域时自动释放内存
```

**unique_ptr的特点：**

- **独占所有权**：同一时间只有一个unique_ptr指向对象
- **禁止拷贝**：只能移动（std::move）
- **零开销**：与原始指针性能几乎相同

#### **shared_ptr - 共享所有权**

```C++
void sharedPtrDemo() {
    // 创建shared_ptr
    std::shared_ptr<int> ptr1 = std::make_shared<int>(100);
    
    {
        std::shared_ptr<int> ptr2 = ptr1;  // 共享所有权，引用计数+1
        cout << "引用计数: " << ptr1.use_count() << endl;  // 2
        
        std::shared_ptr<int> ptr3 = ptr1;  // 引用计数+1
        cout << "引用计数: " << ptr1.use_count() << endl;  // 3
        
    } // ptr2, ptr3析构，引用计数-2
    
    cout << "引用计数: " << ptr1.use_count() << endl;  // 1
    
} // ptr1析构，引用计数为0，释放内存
```

**shared_ptr的特点：**

- **共享所有权**：多个shared_ptr可以指向同一对象
- **引用计数**：跟踪有多少个shared_ptr指向对象
- **计数为0时自动释放**

#### **weak_ptr - 打破循环引用**

**std::weak_ptr** 是 C++11 引入的一种智能指针，定义在 **memory** 头文件中。它是一种非拥有性的弱引用指针，主要用于监视由 **std::shared_ptr** 管理的资源，而不会影响资源的引用计数。

```C++
#include <memory>
#include <string>
#include <iostream>
using namespace std;

struct Student
{
    string name;
    shared_ptr<Student> best_friend; // 我的好朋友
    Student(string _name) { name = _name; cout<<"对象创建"<<endl;}
    ~Student(){cout<< "对象销毁"<<endl;}
};

int main(int argc, char const *argv[])
{

    // 创建两个学生
    auto zhangsan = make_shared<Student>("张三");
    auto lisi = make_shared<Student>("李四");

    // 互相设为好朋友
    zhangsan->best_friend = lisi; // 张三的好朋友是李四
    lisi->best_friend = zhangsan; // 李四的好朋友是张三

    return 0;
}
```

```out
对象创建
对象创建
```

**问题来了：**

- 张三引用李四 → 李四的引用计数=1
- 李四引用张三 → 张三的引用计数=1
- 两人互相拉着，谁都释放不了！**内存泄漏！**

```C++
struct Student {
    string name;
    weak_ptr<Student> best_friend;  // 改成weak_ptr！
};

auto zhangsan = make_shared<Student>("张三");
auto lisi = make_shared<Student>("李四");

zhangsan->best_friend = lisi;    // weak_ptr，不增加引用计数
lisi->best_friend = zhangsan;    // weak_ptr，不增加引用计数
```

## 第15章 内联函数

内联函数是C++的一种优化机制，可以减少函数调用开销。

### 15.1 什么是内联函数？

内联函数是对编译器的优化建议：在调用处直接展开函数体，以减少调用开销。是否真正内联由编译器决定。

**函数调用的开销主要包括时间开销、内存开销和栈帧管理等，优化方法包括使用内联函数和宏。**

要点：

- 在类内定义的成员函数天然是内联候选
- 使用 inline 关键字表达意图，但不强制
- 适用于体积小、逻辑简单、频繁调用的函数；递归/复杂控制流通常不会被内联

**完整示例 - 内联自由函数与内联成员：**

```C++
#include <iostream>

inline int add(int a, int b) { return a + b; }

struct Rect {
    int w{ 0 }, h{ 0 };
    inline int area() const { return w * h; } // 类内定义，内联候选
};

int main() {
    std::cout << "=== 内联函数示例 ===\n";
    int a = 0;
    a = add(2, 3);
    std::cout << a << "\n"; // 5
    Rect r{ 3, 4 };
    std::cout << r.area() << "\n";  // 12
}
```

无内敛(`Debug` 无优化): (VS的反汇编视图)

```hex
    a = add(2, 3);
00007FF7378F23C9  mov         edx,3  
00007FF7378F23CE  mov         ecx,2  
00007FF7378F23D3  call        add (07FF7378F1393h)  <----------
00007FF7378F23D8  mov         dword ptr [a],eax  
```

call        add (07FF7378F1393h)   -> 调用函数, 造成函数调用开销

有内敛(`Release`有优化):

```txt
    int a = 0;
    a = add(2, 3);
    std::cout << a << "\n"; // 5
00007FF6A09B1017  mov         rcx,qword ptr [__imp_std::cout (07FF6A09B3080h)]  
00007FF6A09B101E  mov         edx,5  
00007FF6A09B1023  call        qword ptr [__imp_std::basic_ostream<char,std::char_traits<char> >::operator<< (07FF6A09B3088h)]  
00007FF6A09B1029  mov         rcx,rax  
00007FF6A09B102C  lea         rdx,[string "\n" (07FF6A09B32CCh)]  
00007FF6A09B1033  call        std::operator<<<std::char_traits<char> > (07FF6A09B1060h)  
```

并没有去调用`add`函数

删除`inline`关键字:

```txt
    int a = 0;
    a = add(2, 3);
    std::cout << a << "\n"; // 5
00007FF7B3CB1017  mov         rcx,qword ptr [__imp_std::cout (07FF7B3CB3080h)]  
00007FF7B3CB101E  mov         edx,5  
00007FF7B3CB1023  call        qword ptr [__imp_std::basic_ostream<char,std::char_traits<char> >::operator<< (07FF7B3CB3088h)]  
00007FF7B3CB1029  mov         rcx,rax  
00007FF7B3CB102C  lea         rdx,[string "\n" (07FF7B3CB32CCh)]  
00007FF7B3CB1033  call        std::operator<<<std::char_traits<char> > (07FF7B3CB1060h) 
```

和上面**一模一样**

**何时使用内联：**

- 小且频繁调用的工具函数（如访问器、简单计算）
- 不要为追求“零开销”而滥用；现代编译器会自行做更优的决定

## **Lambda表达式——匿名函数的魔法**

Lambda表达式基础

```txt
[捕获列表](参数列表) -> 返回类型 { 函数体 }
```

| 部分          | 说明                   | 是否必需               |
| ------------- | ---------------------- | ---------------------- |
| `[捕获列表]`  | 指定如何捕获外部变量   | 必需                   |
| `(参数列表)`  | 函数参数，类似普通函数 | 可选（无参数时可省略） |
| `-> 返回类型` | 指定返回类型           | 可选（编译器可推导）   |
| `{ 函数体 }`  | 函数的实现代码         | 必需                   |

简单示例:

```C++
// 最简单的Lambda
auto hello = []() { 
    cout << "Hello Lambda!" << endl; 
};
hello();  // 调用：输出 Hello Lambda!

// 带参数的Lambda
auto add = [](int a, int b) { // auto自动推导为 class lambda [](int a, int b)->int
    return a + b;
};
cout << add(3, 5) << endl;  // 输出 8
```

#### 捕获列表

```C++
void mixedCapture() {
    int a = 1, b = 2, c = 3, d = 4;
    
    // a值捕获，b引用捕获，c值捕获，d引用捕获
    auto lambda1 = [a, &b, c, &d]() {
        // a, c是副本；b, d是引用
    };
    
    // 简写：所有变量值捕获，但b引用捕获
    auto lambda2 = [=, &b]() {
        // 除了b是引用，其他都是值捕获
    };
    
    // 简写：所有变量引用捕获，但a值捕获  
    auto lambda3 = [&, a]() {
        // 除了a是值捕获，其他都是引用捕获
    };
}
```

| 捕获语法  | 说明                            | 示例            |
| --------- | ------------------------------- | --------------- |
| `[]`      | 不捕获任何变量                  | `[]() { }`      |
| `[=]`     | 按值捕获所有外部变量            | `[=]() { }`     |
| `[&]`     | 按引用捕获所有外部变量          | `[&]() { }`     |
| `[x]`     | 按值捕获变量x                   | `[x]() { }`     |
| `[&x]`    | 按引用捕获变量x                 | `[&x]() { }`    |
| `[=, &x]` | 按值捕获所有变量，但x按引用捕获 | `[=, &x]() { }` |
| `[&, x]`  | 按引用捕获所有变量，但x按值捕获 | `[&, x]() { }`  |
| `[this]`  | 捕获当前对象的this指针          | `[this]() { }`  |

[16.3 Lambda表达式的实际应用](https://njupt-sast.feishu.cn/docx/O37Dd68Eso4afJxGYdScZX74nCb#doxcnEZ8BybnMdWigVlDNU2I8jf)

## **左值 vs 右值——值的身份证明**

**基本概念：**

- **左值（lvalue）**：可以出现在赋值语句左边的表达式，有持久的内存地址，可以取地址
- **右值（rvalue）**：只能出现在赋值语句右边的表达式，临时的、即将销毁的值，不能取地址

#### 1. 左值（Lvalue） - "有名字的变量"

```c++
int a = 10;           // a是左值
string name = "张三"; // name是左值
vector<int> vec;      // vec是左值

// 左值的特点：
a = 20;              // 可以放在赋值号左边
int& ref = a;        // 可以取地址 &a
```

#### **2. 右值（Rvalue） - "临时的值"**

```c++
int a = 10;          // 10是右值
string s = "hello";  // "hello"是右值

// 右值的特点：
// 10 = a;          // 错误！不能放在赋值号左边
// int& ref = 10;   // 错误！不能取地址 &10
```

**简单判断方法：**

- 能对表达式取地址（`&`）→ 左值
- 不能对表达式取地址 → 右值

```c++
// 左值示例：
int a = 1;              // a是左值
int& ref = a;           // ref是左值引用（绑定到左值）
const int& cref = 10;   // const左值引用可以绑定到右值

// 右值示例：
int b = 2;              // 2是右值  
int c = a + b;          // (a + b)是右值
string s = "hello";     // "hello"是右值

// 右值引用（C++11新特性）：
int&& rref = 42;        // 右值引用（绑定到右值）
string&& sref = getName(); // 右值引用绑定到临时对象
```

## 17.2 左值引用和右值引用
