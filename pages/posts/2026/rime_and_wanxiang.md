---
title: Rime输入法和万象拼音Pro的配置
date: '2026-03-18 09:54:29'
updated: '2026-03-18 09:54:29'
categories:
- Rime
tags:
- Rime
---

# Rime输入法和万象拼音Pro的配置

## 前言

为什么要配置`Rime`输入法呢, 这还要从微软的`terminal`说起, 最近似乎是某个更新把terminal更新了, 然后导致我的搜狗输入法无法在`terminal`中出现候选词提示框, 起初我还以为是搜狗的问题, 然后就想着把搜狗输入法干掉...

(理论上这文章年前就应该发了, 不过因为懒就忘了, 最近把Rime搞崩了, 所以又要配置一遍... 然后把先前简陋的教程丰富一遍...)

<!-- 在这里写文章概述 -->

<!-- more -->

目前博客暂时无图, 我还在思考怎么接入图片(其实是要不要放图片)

其实一开始我用的是绿化版的搜狗输入法, 不过很不老实, 然后出事后索性更新到最新版吧, 然后去浏览器下载, 恰好, 被银环病毒搞了(就是火绒发现银环病毒后提醒了我, 这病毒在搜索页的权重甚至超过了官网...), 然后就懒得用的搜狗输入法了.

第二天恰好看到了`Linux.do`上有人推荐用Rime(小狼毫)+万象拼音的输入方案, 刚好又支持小鹤双拼, 然后就跟着教程开始配置.

## 正文

<!-- 在这里开始写正文内容 -->

### 安装

首先, 下载Rime, 其[官网](https://rime.im/)和GitHub都能下载, 这里就省略了(其实整个安装就没啥难度)

接下来去万象拼音的[GitHub仓库](https://github.com/amzxyz/rime_wanxiang)下载最新的release, 在[release页面](https://github.com/amzxyz/rime_wanxiang/releases/tag)还能看到万象模型的下载链接(叫做`wanxiang-lts-zh-hans.gram`), 下载下来, 接下来右键Rime的系统托盘, 然后点击用户文件夹, 把模型和配置文件扔进去然后部署, 完成后再右键, 输入法配置, 选中万象拼音即可使用

如果你只是想要使用全拼或基础的双拼, 则下载`rime-wanxiang-base.zip`即可

如果要用pro方案则下载方案的压缩包, 比如我用的是小鹤双拼, 那么下载`rime-wanxiang-flypy-fuzhu.zip`

### 配置你的输入法(覆盖的工作方式)

通过查看custom文件夹下的`patch方法论.md`可知, 用户文件夹的`custom.yaml > schema.yaml > default.yaml`, 并且如果要自己patch就需要创建对应文件的`xxx.custom.yaml`, 然后编写patch即可.

由于本人习惯使用小鹤双拼, 然后用音形进行辅助, 所以在选择方案时需要选中**万象拼音Pro**, 接下来打开`wanxiang_algebra.yaml`, 里面存有模糊音的配置, 定位到模糊音, ~~然后把不需要的注释掉即可~~, 直接注释已经过时了, 不用patch后面难以更新, 我们发现模糊音处于根节点下, 默认全开

根据所学的patch方法论, 我们新建一个名为`wanxiang_algebra.custom.yaml`, 然后填写(这里以前后鼻音为例, 如果你有其他需要则添加即可)

```yaml
patch:
  模糊音:
    # en - eng
    - derive/(ē|é|ě|è|e)ng(.*)$/$1n$2
    - derive/(ē|é|ě|è|e)n(.*)$/$1ng$2
    # in - ing
    - derive/(ī|í|ǐ|ì|i)ng(.*)$/$1n$2
    - derive/(ī|í|ǐ|ì|i)n(.*)$/$1ng$2
```

不过模糊音默认关闭, 所以还需要开启(方案也是)

然后打开`wanxiang_pro.schema.yaml`, 找了一会后发现

```yaml
# 拼写设定
speller:
# table_translator翻译器，支持自动上屏。例如 “zmhu”可以自动上屏“怎么回事”
#  auto_select: true
#  auto_select_pattern: ^[a-z]+/|^[a-df-zA-DF-Z]\w{3}|^e\w{4}
  # 如果不想让什么标点直接上屏，可以加在 alphabet，或者编辑标点符号为两个及以上的映射
  alphabet: zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA1234567890`;/\
  # initials 定义仅作为始码的按键，排除 ` 让单个的 ` 可以直接上屏
  initials: zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA/
  delimiter: " '"  # 第一位<空格>是拼音之间的分隔符；第二位<'>表示可以手动输入单引号来分割拼音。
  visual_delimiter: " "  # super_preedit.lua配置：是否让分隔符号跟着一起转换，例如nǐ'hǎo 在实际使用中表现出视觉拥挤，我们可以让delimiter平时是'转换为拼音的时候使用空格nǐ hǎo，更符合实际。
  algebra:
    __patch:
      #- 模糊音             #模糊音选择性开启
      - wanxiang_algebra:/pro/自然码     #拼音转双拼码
      - wanxiang_algebra:/pro/直接辅助     #辅助码部分
```

模糊音被注释, 并且初始的双拼规则居然是自然码

同上, 我们创建`wanxiang_pro.custom.yaml`, 根据所学, 写出如下patch

```yaml
patch:
  speller/algebra:
    __patch:
      - wanxiang_algebra:/模糊音      # 确保段落名正确
      - wanxiang_algebra:/pro/小鹤双拼
      - wanxiang_algebra:/pro/直接辅助
```

这里模糊音前面必须要加`wanxiang_algebra:/` 否则会没效果(整个patch都没效果, 因为人家不知道你的模糊音是哪来的), 直接辅助和间接辅助按个人习惯选用

之后重新构建后即可应用

## 更多

如果你还想配置中英切换方式, 则打开(或者新建)`default.custom.yaml`

根据patch去更改喜欢的键位(注释有很多, 就略了)

对于某些开关(比如输入法默认状态, 和标点的默认状态)也能patch, 比如`wanxiang_pro.schema.yaml`里的switches, 我想要把第一个和第二个参数设成, 默认后者, patch后应该长这样

```yaml
# 开关
# reset: 默认状态。注释掉后，切换窗口时不会重置到默认状态。
# states: 方案选单显示的名称。可以注释掉，仍可以通过快捷键切换。
# abbrev: 默认的缩写取 states 的第一个字符，abbrev 可自定义一个字符
switches:
  - name: ascii_mode                   # 中英输入状态
    states: [ 中文, 英文 ]
    reset: 1
  - name: ascii_punct                  # 中英标点
    states: [ 中标, 英标 ]
    reset: 1
```

那么patch可以这么写

```yaml
patch:
  switches/@0/reset: 1
  switches/@1/reset: 1
```

# Trime的输入预测

对于用惯了手机端的用户, 可能会需要这个, 依旧从万象的release里下载`wanxiang-lts-zh-hans-predict.db`放到用户文件夹下, 然后去[这里](https://github.com/rime/librime-predict)下载预测插件, 根据教程和patch可以写出如下patch(`wanxiang_pro.custom.yaml`)

```yaml
patch:
  engine/processors/@before 0: predictor
  engine/translators/@before 0: predict_translator
  switches/@before 2:
    name: prediction
    states: [ 关闭预测, 开启预测 ]
    reset: 0 # 这里电脑端为0(电脑端设成1也没用)
  predictor:
    # predict db file in user directory/shared directory
    # default to 'predict.db'
    db: wanxiang-lts-zh-hans-predict.db
    # max prediction candidates every time
    # default to 0, which means showing all candidates
    # you may set it the same with page_size so that period doesn't trigger next page
    max_candidates: 5
    # max continuous prediction times
    # default to 0, which means no limitation
    max_iterations: 1
```

重新部署后就能在手机端看到预测了(配置文件跨平台的, 电脑上的配置文件能不做改动直接放到手机上使用)

## 总结

<!-- 在这里写总结 -->

略略略, (好久没写了好像..)

---

**版权声明**：本文为原创文章，转载请注明出处。

