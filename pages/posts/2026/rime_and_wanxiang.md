---
title: Rime输入法和万象拼音Pro的配置
date: '2026-02-14 09:54:29'
updated: '2026-02-14 09:54:29'
categories:
- Rime
tags:
- Rime
---

# Rime输入法和万象拼音Pro的配置

## 前言

为什么要配置`Rime`输入法呢, 这还要从微软的`terminal`说起, 最近似乎是某个更新把terminal更新了, 然后导致我的搜狗输入法无法在`terminal`中出现候选词提示框, 起初我还以为是搜狗的问题, 然后就想着把搜狗输入法干掉...

<!-- 在这里写文章概述 -->

<!-- more -->

其实一开始我用的是绿化版的搜狗输入法, 不过很不老实, 然后出事后索性更新到最新版吧, 然后去浏览器下载, 恰好, 被银环病毒搞了(就是火绒发现银环病毒后提醒了我, 这病毒在搜索页的权重甚至超过了官网...), 然后就懒得用的搜狗输入法了.

第二天恰好看到了`Linux.do`上有人推荐用Rime(小狼毫)+万象拼音的输入方案, 刚好又支持小鹤双拼, 然后就跟着教程开始配置.

## 正文

<!-- 在这里开始写正文内容 -->

### 安装

首先, 下载Rime, 其官网和GitHub都能下载, 这里就省略了(其实整个安装就没啥难度)

接下来去万象拼音的GitHub仓库下载最新的release, 在release页面还能看到万象模型的下载链接, 下载下来, 接下来右键Rime的系统托盘, 然后点击用户文件夹, 把模型和配置文件扔进去然后部署, 完成后再右键, 输入法配置, 选中万象拼音即可使用

### 覆盖的工作方式

通过查看custom文件夹下的`patch方法论.md`可知, 用户文件夹的`custom.yaml > schema.yaml > default.yaml`, 并且如果要自己patch就需要创建对应文件的`xxx.custom.yaml`, 然后编写patch即可, 这里以开启模糊音和设置小鹤音形为例子

由于本人习惯使用小鹤双拼, 然后用音形进行辅助, 所以在选择方案时需要选中**万象拼音Pro**, 接下来打开`wanxiang_algebra.yaml`, 里面存有模糊音的配置, 定位到模糊音, 然后把不需要的注释掉即可, 就以前后鼻音为例, 除了

```yaml
    # en - eng
    - derive/(ē|é|ě|è|e)ng(.*)$/$1n$2
    - derive/(ē|é|ě|è|e)n(.*)$/$1ng$2
    # in - ing
    - derive/(ī|í|ǐ|ì|i)ng(.*)$/$1n$2
    - derive/(ī|í|ǐ|ì|i)n(.*)$/$1ng$2
```

其余注释即可


```yaml
模糊音:
  __append:
    # n - l
    #- derive/^l/n
    #- derive/^n/l
    # r - y     开头
    #- derive/^y/r
    #- derive/^r/y
    # h - f     开头
    #- derive/^h/f
    #- derive/^f/h
    # r - l     开头
    #- derive/^r/l
    #- derive/^l/r
    # k - g     开头
    #- derive/^k/g
    #- derive/^g/k
    # en - eng
    - derive/(ē|é|ě|è|e)ng(.*)$/$1n$2
    - derive/(ē|é|ě|è|e)n(.*)$/$1ng$2
    # in - ing
    - derive/(ī|í|ǐ|ì|i)ng(.*)$/$1n$2
    - derive/(ī|í|ǐ|ì|i)n(.*)$/$1ng$2
    # c - ch
    #- derive/^c([^h]*)/ch$1
    #- derive/^ch/c
    # z - zh
    #- derive/^z([^h]*)/zh$1
    #- derive/^zh/z
    # s - sh
    #- derive/^s([^h]*)/sh$1
    #- derive/^sh/s
```

然后打开`wanxiang_pro.custom.yaml`, 填写:

```yaml
patch:
  speller/algebra:
    __patch:
      - wanxiang_algebra:/模糊音 # 这里启用后，本文件末尾可配置具体条目
```

即可为**万象拼音Pro**开启模糊音, 然后双拼方案开启(还有辅助码)则要加上

```yaml
      - wanxiang_algebra:/pro/小鹤双拼 #拼音转双拼码
      - wanxiang_algebra:/pro/直接辅助 #辅助码部分
```

之后重新构建后即可应用

## 总结

<!-- 在这里写总结 -->

略略略, (好久没写了好像..)

---

**版权声明**：本文为原创文章，转载请注明出处。

