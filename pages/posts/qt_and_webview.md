---
title: Qt和WebView2结合---Windows窗口系统的学习
data: 2025-11-09 17:20:00
updated: 2025-11-09 17:20:00
password: valaxy
categories:
 - 技术
tags:
 - C/C++
 - Qt
---

## 前言

今天在实现Markdown渲染时想用WebView作为渲染器, 这样就能舍去臃肿的`QtWebEngine`(~~也就是不用在软件里内置浏览器了~~), 虽然Qt貌似支持WebView, 但是我看了一圈也没看到一个能跑起来的项目, 那索性就用Windows平台的WebView2看看吧

## 问题

对于Windows的窗口我一直不是很理解, 各种晦涩难懂的专业词汇直接给我初学带来极大困难(其实高中就想研究的, 不过跟着别人敲了半天代码连什么是窗口句柄都不知道, 后来就放弃了), 既然今天又遇到了那就一次性搞懂吧, 顺便还能去复习之前的COM组件.(博客格了, 所以COM那篇文章也没了)

## WebView为何能无需Qt的接口就能在Qt的Widget里显示

以往写界面无非就是调用Qt里自带的Widgets, 然后用代码去排列, 而WebView呢? 并不属于Qt里的Widget, 想要显示到窗口该怎么办呢? --直接调用Windows的API, 既然Qt能在Windows平台显示窗口和Widget, 那也一定调用了Windows的API接口, 不过被Qt层层封装, 日常应该是接触不到的(其他平台应该同理)

### 专业术语

- 
