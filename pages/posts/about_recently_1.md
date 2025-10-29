---
title: 关于最近发生的事
data: 2025-10-28 19:25:00
updated: 2025-10-28 19:25:00
categories:
 - 生活
tags:
 - 博客
 - 生活
 - 未来
codeHeightLimit: 300
---

# 关于最近

## 关于博客

起始从博客首页的小字就能知道最近博客发生了什么, 一开始是部署博客服务器提供商疑似跑路了(其实没跑, 不过是换了个域名), 拿到新域名后依然购买了服务器一个月, 但是并没有激活, 客服竟然公然劝我去举报他们公司.......过了一段时间后补偿了一个服务器给我, 不过就没用过了. 不过公网IP似乎没有收回, 不过也用不了.

其实服务器跑路也没什么, 因为博客源代码都在电脑上, 只要有服务器就能马上部署, 之后你也能猜到了, 就是电脑被格了. (老实了, 现在我直接把幸存的代码全上传了)

这里我是真很想去质问小米的官方镜像, 原以为就是普通的重装, 结果直接把整个硬盘都格了(包括分配给Linux系统分区), 重装前还想着什么备份了, 什么还没备份, 哈哈哈, 所以为什么小米的工程师不写清楚, 这会格式化所有硬盘😡, 说是损失惨重吧, 感觉又没什么, 过去两三周也没什么感觉真正的消失了, 对了你一定很想问为什么我要格机. 请看下面

<!-- more -->

```
Microsoft (R) Windows Debugger Version 6.12.0002.633 AMD64
Copyright (c) Microsoft Corporation. All rights reserved.


Loading Dump File [C:\Users\30789\Desktop\101525-10578-01.dmp]
Mini Kernel Dump File: Only registers and stack trace are available

Symbol search path is: srv*D:\Symbol*https://msdl.microsoft.com/download/symbols
Executable search path is: 
Windows 7 Kernel Version 22621 MP (32 procs) Free x64
Product: WinNt, suite: TerminalServer SingleUserTS Personal
Machine Name:
Kernel base = 0xfffff806`6f000000 PsLoadedModuleList = 0xfffff806`6fc13580
Debug session time: Wed Oct 15 14:09:32.146 2025 (UTC + 8:00)
System Uptime: 0 days 0:04:08.827
Loading Kernel Symbols
...............................................................
................................................................
................................................................
...........................................................
Loading User Symbols
Loading unloaded module list
....................
*******************************************************************************
*                                                                             *
*                        Bugcheck Analysis                                    *
*                                                                             *
*******************************************************************************

Use !analyze -v to get detailed debugging information.

BugCheck 3B, {c0000005, fffff8066f2a6034, ffffa005550bd940, 0}

6: kd> !analyze -v
*******************************************************************************
*                                                                             *
*                        Bugcheck Analysis                                    *
*                                                                             *
*******************************************************************************

SYSTEM_SERVICE_EXCEPTION (3b)
An exception happened while executing a system service routine.
Arguments:
Arg1: 00000000c0000005, Exception code that caused the bugcheck
Arg2: fffff8066f2a6034, Address of the instruction which caused the bugcheck
Arg3: ffffa005550bd940, Address of the context record for the exception that caused the bugcheck
Arg4: 0000000000000000, zero.

Debugging Details:
------------------


EXCEPTION_CODE: (NTSTATUS) 0xc0000005 - 0x%p

FAULTING_IP: 
nt!RtlpUnwindPrologue+204
fffff806`6f2a6034 488b08          mov     rcx,qword ptr [rax]

CONTEXT:  ffffa005550bd940 -- (.cxr 0xffffa005550bd940)
rax=0000000000000000 rbx=0000000000000004 rcx=0000000000000000
rdx=ffffa005550bf110 rsi=ffffa005550be360 rdi=fffff8066f07e84c
rip=fffff8066f2a6034 rsp=ffffa005550be360 rbp=ffffa005550be680
 r8=000000000000000f  r9=ffffa005550be738 r10=0000000000000018
r11=fffff8066f000000 r12=00007fffffff0000 r13=00007ffffffeffff
r14=ffffa005550be6a0 r15=fffff8066f762d44
iopl=0         nv up ei ng nz ac po nc
cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00050296
nt!RtlpUnwindPrologue+0x204:
fffff806`6f2a6034 488b08          mov     rcx,qword ptr [rax] ds:002b:00000000`00000000=000000000001c200
Resetting default scope

CUSTOMER_CRASH_COUNT:  1

DEFAULT_BUCKET_ID:  VISTA_DRIVER_FAULT

BUGCHECK_STR:  0x3B

PROCESS_NAME:  sppsvc.exe

CURRENT_IRQL:  0

BAD_PAGES_DETECTED: 1c200

LAST_CONTROL_TRANSFER:  from 0000000000000000 to fffff8066f2a6034

STACK_TEXT:  
ffffa005`550be360 00000000`00000000 : 00000000`00000000 00000000`00000000 00000000`00000000 00000000`00000000 : nt!RtlpUnwindPrologue+0x204


SYMBOL_NAME:  PAGE_NOT_ZERO

FOLLOWUP_NAME:  MachineOwner

MODULE_NAME: Unknown_Module

IMAGE_NAME:  Unknown_Image

DEBUG_FLR_IMAGE_TIMESTAMP:  0

STACK_COMMAND:  .cxr 0xffffa005550bd940 ; kb

BUCKET_ID:  PAGE_NOT_ZERO

Followup: MachineOwner
---------

 *** Memory manager detected 115200 instance(s) of page corruption, target is likely to have memory corruption.
 
6: kd> !process
PROCESS ffff85053250f080
    SessionId: none  Cid: 2e54    Peb: eb391f4000  ParentCid: 05d0
    DirBase: 2d065d000  ObjectTable: ffffb38b1ba95040  HandleCount: <Data Not Accessible>
    Image: sppsvc.exe
    VadRoot ffff850531c49e40 Vads 1 Clone 0 Private 721. Modified 3. Locked 16.
    DeviceMap ffffb38b0eb637ff
    Token                             ffffb38b1c2450a0
    ReadMemory error: Cannot get nt!KeMaximumIncrement value.
fffff78000000000: Unable to get shared data
    ElapsedTime                       00:00:00.000
    UserTime                          00:00:00.000
    KernelTime                        00:00:00.000
    QuotaPoolUsage[PagedPool]         0
    QuotaPoolUsage[NonPagedPool]      0
    Working Set Sizes (now,min,max)  (0, 0, 0) (0KB, 0KB, 0KB)
    PeakWorkingSetSize                0
    VirtualSize                       2101333 Mb
    PeakVirtualSize                   2101333 Mb
    PageFaultCount                    0
    MemoryPriority                    BACKGROUND
    BasePriority                      8
    CommitCharge                      850

        *** Error in reading nt!_ETHREAD @ ffff85052cee1080
```

还挺长的, 就直接折叠了, 简单来说似乎是`sppsvc.exe`访问非法内存导致的, 不过我在很多软件都能遇到这种非法内存访问的, 也不清楚到底是内存条的问题还是系统的问题(反正重装后目前还没出现问题), 所以就想着重装能不能解决.

## 关于生活

因为来回科协麻烦, 平时不在科协也有一定大屏幕查看代码和网页的需求, 所以就斥巨资买了平板, 其实当时还在犹豫到底买不买, 便宜的平板小新, 不过系统太拉, 而小米又太贵, 结果恰好得知小米Pad8要出了, 而且首发(10月8号前)购买的大学生又笔和套拿, 说实话本来还在犹豫, 听到有笔直接拿下(被小米拿下了呜😴, 不过一支笔官网要卖599, 感觉还行其实), 再加上国补, 就拿下了Pad8, 目前体验下来感觉大屏幕就是爽(刷视频和浏览网页这一块确实是手机无法比的), 性能也很能说的过去(晓龙8sGen4, 别吐糟是8s, 但是比手机的7+Gen2要好)

## 关于就业和未来

这个感觉是真的是我犹豫很久无法给出的答案, 目前想着本科就业, 但是却在软件和硬件方面纠结. 两边的招聘信息也都看过, 感觉上自己需要学习的东西很有很多, 不过自己在爱好上可能更偏向软件开发一点, 说实话, 我是真想知道现在的就业市场是怎样的, 到底是不是那种供大于求的状态, 还是计算机会沦落为第二个土木. 在写这篇博客时其实我还在犹豫, 感觉自己站在人生的岔路口, 但是不知道向哪里走, 或许, 在以后的`about recently`能给出我的答案.
