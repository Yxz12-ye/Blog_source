---
title: 如何禁用CSDN重定向
date: '2026-06-30 18:19:11'
updated: '2026-06-30 18:19:11'
categories:
- 技术
tags:
- Web
---

# 如何禁用CSDN重定向

## 事先声明

::: warning

> **不建议**使用CSDN, 本文章只是针对CSDN重定向到登录页面的发现与解决方法!
>
> **不建议**使用CSDN, 本文章只是针对CSDN重定向到登录页面的发现与解决方法!
>
> **不建议**使用CSDN, 本文章只是针对CSDN重定向到登录页面的发现与解决方法!

:::

<!-- more -->

## 正文

### 寻找

直接开始, 先禁用JavaScript和缓存, 加载文章后发现并没有跳转, 也就是说是JavaScript的锅.

接下来想到打开开发人员面板, 在网络窗格上部(针对Edge浏览器)找到保留日志和禁用缓存, 都勾上, 并且把无限制改成慢速4G或3G, 在网页跳转到登录页面时停止记录.

接下来在筛选器里勾选JS, 得到以下日志

```txt
0.a6df606f7bc7c601fa32.js
6.ea6a3a4d3a98014c87ab.jscrypto.min.js
bot-score-v1.js
waf_captcha_embedded_bs.js
wxLogin.js
manifest.735c56048f9f1ee8c57c.js
vendor.b57fb0acd6f6d913b609.js
loginv3.29772909b3376c6c1b08.js
fingerprintjs-botd-v1.js
fingerprintjs-v3.js
```

以上是跳转时请求的日志, 尝试全部阻止请求URL, 发现重新进入文章后依旧会重定向, 也就是说找的JS不对.

重新整理思路, 我们发现跳转后的URL是`https://passport.csdn.net/login?code=applets`

我们取消勾选JS筛选器, 找到该请求

<details open="" aria-label="常规" style="box-sizing: border-box; min-width: 0px; min-height: 0px;"><slot id="details-content" pseudo="details-content" style="display: block;"><div jslog="Section; context: general" style="box-sizing: border-box; min-width: 0px; min-height: 0px;"><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 8px 0px 4px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 196.075px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">请求 URL</div><div id="request-url" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">https://passport.csdn.net/login?code=applets</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 196.075px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">请求方法</div><div id="request-method" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">GET</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 196.075px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">状态代码</div><div id="status-code" class="header-value status green-circle" style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">200 OK</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 196.075px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">远程地址</div><div id="remote-address" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">127.0.0.1:10808</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px 8px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 196.075px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">引用站点策略</div><div id="referrer-policy" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">unsafe-url</div></div></div></slot></details>

在上方发起程序中我们能看调用堆栈, 虽然我不是很能看懂

```txt
	(匿名)	@	g.csdnimg.cn/common/…csdn-login-box.js:1
Promise.then		
s.init	@	g.csdnimg.cn/common/…csdn-login-box.js:1
s	@	g.csdnimg.cn/common/…csdn-login-box.js:1
show	@	g.csdnimg.cn/common/…csdn-login-box.js:2
(匿名)	@	csdnimg.cn/release/b…a2d71eb44d.min.js:8
dispatch	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:3
r.handle	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:3
trigger	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:3
a.event.trigger	@	g.csdnimg.cn/lib/jqu…jquery-migrate.js:2
(匿名)	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:3
each	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:2
each	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:2
trigger	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:3
n.fn.<computed>	@	g.csdnimg.cn/lib/jqu…2.4/jquery.min.js:4
(匿名)	@	userscript.html?name…%25E5%25B9%25…:2643
At	@	(未知)
t.<computed>	@	(未知)
At	@	(未知)
(匿名)	@	(未知)
(匿名)	@	(未知)
At	@	(未知)
t	@	(未知)
message	@	(未知)
message	@	(未知)
(匿名)	@	(未知)
_	@	(未知)
$t	@	content.js:9
h	@	content.js:69
d	@	content.js:72
(匿名)	@	content.js:72
Xn	@	content.js:15
send	@	content.js:72
g	@	content.js:16
m	@	content.js:16
```

但肯定和里面的脚本脱不了关系, 这里搜索`csdn-login-box.js`, 找到请求的URL信息:

<details open="" aria-label="常规" style="box-sizing: border-box; min-width: 0px; min-height: 0px;"><slot id="details-content" pseudo="details-content" style="display: block;"><div jslog="Section; context: general" style="box-sizing: border-box; min-width: 0px; min-height: 0px;"><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 8px 0px 4px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 160px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">请求 URL</div><div id="request-url" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">https://g.csdnimg.cn/common/csdn-login-box/csdn-login-box.js</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 160px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">请求方法</div><div id="request-method" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">GET</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 160px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">状态代码</div><div id="status-code" class="header-value status green-circle" style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">200 OK</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 160px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">远程地址</div><div id="remote-address" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">127.0.0.1:10808</div></div><div class="row " style="box-sizing: border-box; min-width: 0px; min-height: 0px; display: flex; line-height: 18px; padding-left: 8px; gap: 12px; user-select: text; margin: 4px 0px 8px;"><div class="header-name" style="box-sizing: border-box; min-width: 160px; min-height: 0px; color: rgb(71, 71, 71); font: 500 11px / 16px system-ui, sans-serif; width: 160px; max-width: 240px; flex-shrink: 0; text-transform: capitalize;">引用站点策略</div><div id="referrer-policy" class="header-value " style="box-sizing: border-box; min-width: 0px; min-height: 0px; word-break: break-all; display: flex; align-items: center; gap: 2px; font: 400 12px / 16px system-ui, sans-serif;">unsafe-url</div></div></div></slot></details>

尝试阻止请求URL, 重新进入网页发现不再跳转, 也就是说找对脚本了, 接下来就是拦截

### 拦截

这里直接把`*://g.csdnimg.cn/common/csdn-login-box/csdn-login-box.js`扔给AI让他写广告拦截的规则, 这里给出`AdGuard`的规则:`||g.csdnimg.cn/common/csdn-login-box/csdn-login-box.js$script`, 放入后即可解决CSDN重定向的问题.

## 总结

依旧那句话: 不建议使用CSDN

---

**版权声明**：本文为原创文章，转载请注明出处。

