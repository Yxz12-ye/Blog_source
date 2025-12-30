---
title: CodeRegistration和MetadataRegistration的获取
date: 2025-11-16 20:02:00
updated: 2025-11-16 20:02:00
categories:
 - 技术
tags:
 - C#
---

## Unity游戏CodeRegistration和MetadataRegistration的获取

:::tip
前因是我在玩蓝途王子, 打翻译Mod时需要反编译Il2Cpp, 而BepInex还不支持v31的元数据, 遂用Il2CppDumper, 结果一开始选错文件导致一直反编译失败, 所以一些内容我就删了, 以免造成误导.
:::

那么直接开始吧

首先用IDA Pro打开游戏的GameAssembly.dll

在字符串视图搜索`global-metadata.dat`, (如果没搜到就是加密了, 目前还不会解密)

可以得到:

```
.rdata:0000000182CC0660 67 6C 6F 62 61 6C 2D 6D 65 74     aGlobalMetadata db 'global-metadata.dat',0
```

<!-- more -->

接着右键查找交叉引用(xrefs to)

我们可以看到一个清晰的引用图(本人IDA 9.2版本, 交叉引用有清晰的引用图)

可以知道(A->B, 表示A调用了B)

```
sub_180291260->sub_1802A5CC0->sub_180290BE0->aGlobalMetadata
```

(以下内容参考大佬的博客[Il2cppDumper Manually Finding CodeRegistration and MetadataRegistration | Tomorrowisnew](https://tomorrowisnew.com/posts/Finding-CodeRegistration-and-MetadataRegistration/))

可知il2cpp调用metadata方式如下

```
il2cpp::vm::Runtime::Init->il2cpp::vm::MetadataCache::Initialize->global-metadata.dat
```

那么就在调用`il2cpp::vm::Runtime::Init`的上方就能找到`CodeRegistration`和`MetadataRegistration`

返回IDA Pro, 我们得知`sub_180291260`函数会调用`sub_1802A5CC0`,而这里`sub_1802A5CC0`就是`il2cpp::vm::Runtime::Init`, 因此调用`sub_1802A5CC0`的位置上面就是我们需要的东西

进入`sub_180291260`, 搜索text : `sub_1802A5CC0`

```
.text:00000001802914D0 258 48 8D 0D 49 87 51 02          lea     rcx, unk_1827A9C20
.text:00000001802914D7 258 48 89 0D 9A B1 EE 02          mov     cs:qword_18317C678, rcx
.text:00000001802914DE 258 48 8D 05 FB E8 87 02          lea     rax, unk_182B0FDE0
.text:00000001802914E5 258 48 89 05 A4 B1 EE 02          mov     cs:qword_18317C690, rax
.text:00000001802914EC 258 48 89 0D 85 B0 EE 02          mov     cs:qword_18317C578, rcx
.text:00000001802914F3 258 48 89 05 8E B0 EE 02          mov     cs:qword_18317C588, rax
.text:00000001802914FA 258 48 8D 05 07 87 51 02          lea     rax, unk_1827A9C08
.text:0000000180291501 258 48 89 05 68 B0 EE 02          mov     cs:qword_18317C570, rax
.text:0000000180291508 258 E8 B3 47 01 00                call    sub_1802A5CC0
```

可以看到`lea     rcx, unk_1827A9C20`和`lea     rax, unk_182B0FDE0`

而`1827A9C20`和`182B0FDE0`分别就是`CodeRegistration`和`MetadataRegistration`

