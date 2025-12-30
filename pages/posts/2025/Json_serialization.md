---
title: 用C++20实现Json反序列化
date: '2025-12-24 22:55:23'
updated: '2025-12-24 22:55:23'
categories:
- 技术
tags:
- C++
- Json
---

# 用C++20实现Json反序列化

## 概述

其实是2025WoC, 感觉反序列化思路还挺有趣的, 所以就写个文章记录一下

~~(顺便弥补博客多天没更新...)~~

核心思路是**递归下降**, 一开始不理解, 到后面的顿悟, 是个很有趣的过程

<!-- more -->

## 正文

### 深入理解Json

```json
{
    "name": "zhangSan",
    "age": 20,
    "is_student": true,
    "score": 95.5,
    "nothing": null,
    "courses": ["Math", "English"],
    "address": {
        "city": "Beijing",
        "zip": 100000
    }
}
```

上面是一个简单的`Json`示例, 可以看到`Json`的一个核心骨架, 由一个`{...}`包裹, 里面的数据则是很规整的字典类型(Python乱入), 都是`Key:Class`的类型, 而且`Key`是字符串, 后面的东西则可以是字符串(String), 布尔(Boolean), 数字(Number), 空(Null), 数组(Array), 然后?

最后一个似乎是另一个`Json`骨架? 没关系, 我们先跳过, 等到后面就清楚了.

### 思路

作为一个编程菜鸡, 这种复杂的东西还是先给AI跑一遍再说吧(变相参考代码)

```c++
class Json;

using Null = std::monostate;
using Boolen = bool;
using Int = int;
using Double = double;
using String = std::string;
using Array = std::vector<Json>;
using Object = std::map<std::string, Json>;

using JsonValue = std::variant<Null, Boolen, Int, Double, String, Array, Object>;
```

可以发现上面说的类型基本都有, 而且最后一个没对应上的竟然是`Object`, 也就是说其实`Json`本身是一个大`Object`? ~~(反正我一开始就是这么想的)~~, 不过后面写着写着, 发现并非如此.

### 问题

按照我一开始的想法区设计一个`Json`类, 就会想到核心类成员是一个`Object`, 不过简单想想就会发现这种逻辑完全说不通, 前面的`std::string`应该是什么呢? 后面存的为什么又是`Json`自己??

既然是`Key:Class`, 那么

:::warning
施工中
:::

## 总结

<!-- 在这里写总结 -->

---

**版权声明**：本文为原创文章，转载请注明出处。

