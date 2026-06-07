---
title: 使用ESP32S3实现Wake On Lan
date: '2026-06-07 13:59:40'
updated: '2026-06-07 13:59:40'
categories:
- 技术
tags:
- C/C++
---

# 使用ESP32S3实现Wake On Lan

## 前言

最近闲来没事(其实事情一大堆, 忙里偷闲说是), 早上刚好看到`WOL`的技术讲解视频, 想着之前一直想实现WOL, 结果一直失败, 因此感觉很不服, 然后手上刚好有大一玩单片机买的`ESP32S3`(虽然在我上大二后就把它抛弃了), 恰好支持Wi-Fi, 那还说啥了, 直接开造!

## 实现WOL

> 这里先提一下我的方案, 由于WOL迫切需要唤醒设备和被唤醒设备处于同一局域网, 且被唤醒设备必须在关机或休眠等其他状态时**没有关闭网卡**, 只有这样WOL才能正常发挥作用
>
> 本人是笔记本网卡是Intel AX210, 测试下来是完全支持**无线唤醒**的, 有线成功率应该更高

### 电脑端配置

这里参考并总结了三篇文章的设置方法, 由于懒就只放Windows端的了

[通过 Intel 无线网卡远程唤醒台式机 - 喵's StackHarbor](https://sh.alynx.one/posts/Wake-on-WLAN/)

[无线网络唤醒，从入门到放弃 - elmagnifico's blog](https://elmagnifico.tech/2021/05/25/Wake-on-wireless-lan/)

[电脑远程开机：Wake-on-LAN (WoL) 设置方法 - 知乎](https://zhuanlan.zhihu.com/p/1902326594401445022)

首先要进入BIOS(怎么进自己去搜索), 找到WOL相关的内容并打开(本人的BIOS叫网络唤醒, 各个主板名称各不相同, 需要自行查资料)

Windows端打开设备管理器, 在网络适配器中找到自己的无线(有线)网卡, 比如我的无线网卡就是`Intel(R) Wi-Fi 6E AX210 160MHz`, 在电源管理把`允许此设备唤醒计算机(O)`和`只允许幻数据包唤醒计算机(N)`都勾上, 这里不知道为什么, 如果下面那个不勾选电脑会自动从休眠中唤醒(估计是局域网内其他设备的影响)

在高级选项卡中打开和网络唤醒相关的选项, `唤醒幻数据包`和`唤醒模式匹配`, 然后`WoWLAN`的ARP, GTK, NS需要启用

完成后可以先对电脑休眠, 然后尝试发送WOL数据包观察电脑能否正常启动, 如果启动失败就要考虑电脑是否支持WOL或者前面的配置有什么遗漏

### 服务器

远程唤醒服务器是刚需, 由于不需要很高级的功能, 这里直接使用简单的MQTT客户端`Mosquitto`

#### 安装`Mosquitto`(针对Ubuntu)

添加官方源

```bash
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients -y
```

#### 安全配置 (防止被滥用)

暴露在公网的服务，务必进行安全加固。

- 修改配置文件：编辑主配置文件 `/etc/mosquitto/mosquitto.conf`，引入密码文件和ACL文件：

```bash
# /etc/mosquitto/mosquitto.conf 文件末尾新增两行
password_file /etc/mosquitto/pwfile
acl_file /etc/mosquitto/aclfile
```

同时确保 `allow_anonymous` 的值为 `false`。

- 创建密码：使用 `mosquitto_passwd` 命令为你的 ESP32-S3 创建一个独立的用户，比如叫 `esp32_client`：

```bash
sudo mosquitto_passwd -c /etc/mosquitto/pwfile esp32_client
```

系统会提示你输入并确认密码。(**一定要记住**用户名和密码, 后面需要使用)

- 设置访问控制列表 (ACL)：创建 `/etc/mosquitto/aclfile` 文件，写入以下权限规则：
- 这里使用`esp32/wol/command`作为唤醒端点

```bash
user esp32_client
topic readwrite esp32/wol/#
```

ACL 文件用于定义特定用户的读写权限，是保障安全的核心，防止非法用户订阅或发布消息。

- 重启服务：完成所有配置后，重启`Mosquitto`让设置生效：

```bash
sudo systemctl restart mosquitto
```

如果重启出现报错, 需要对上面创建的文件用`chmod 700`

#### 单向认证

这里懒得用双向认证了, 单向认证使用证书+密码的方式验证身份

```bash
mkdir -p ~/mqtt_certs
cd ~/mqtt_certs

# 生成 CA 私钥
openssl genrsa -out ca.key 2048

# 生成 CA 自签名证书（有效期10年）
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt
```

中间问你的问题随便写就行(留空也可以), 密码也随便写就行

```bash
# 生成服务器私钥
openssl genrsa -out server.key 2048

# 生成 CSR
openssl req -new -key server.key -out server.csr
```

同上

**用 CA 签发服务器证书**

```bash
# 创建一个扩展文件，用于指定服务器证书的 SAN（Subject Alternative Name）
cat > server.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = mqtt.yourdomain.com   # 替换成你的实际域名
IP.1 = 你的服务器公网IP        # 如果没有域名，可以用 IP
EOF

# 签发证书（有效期1年）
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile server.ext
```

现在你的目录下应有以下文件：

- `ca.crt` (CA 证书)
- `server.crt` 和 `server.key` (服务器证书和私钥)

接下来把证书复制到`Mosquitto`配置目录

```bash
sudo mkdir -p /etc/mosquitto/certs
sudo cp ~/mqtt_certs/ca.crt ~/mqtt_certs/server.crt ~/mqtt_certs/server.key /etc/mosquitto/certs/
sudo chown -R mosquitto:mosquitto /etc/mosquitto/certs
sudo chmod 600 /etc/mosquitto/certs/server.key   # 私钥权限收紧
```

修改 Mosquitto 配置文件 `/etc/mosquitto/mosquitto.conf`

```bash
# 保留原有的非加密端口（如果你还需要内网明文访问，可以保留）
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/pwfile
acl_file /etc/mosquitto/aclfile

# 添加 MQTTS 加密端口 (默认 8883)
listener 8883 0.0.0.0
protocol mqtt
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
# 如果只需要单向认证，保持下面这行注释掉或设为 false
# require_certificate true
# 如果双向认证，则取消注释 require_certificate true，并指定客户端证书 CA
# tls_version tlsv1.2
```

接下来重启服务`sudo systemctl restart mosquitto`

当然该开的端口肯定是要开的, 8883和1883

### 单片机

这里先要获取刚刚生成的证书并嵌入到单片机

```bash
xxd -i ~/mqtt_certs/ca.crt ~/ca_cert.h
```

把`ca.crt`还有生成的`ca_cert.h`一并传输到电脑后面需要用

这里我用`esp-idf`, 这里不放源代码了, 使用`codex`搓一个还是很快的, 不过有些问题我需要提前说一下:

ESP32S3只支持2.4GHz频段, 如果路由器不支持这个频段那是不行的(很少吧), 且路由器不能开启AP隔离, 否而是收不到唤醒数据包的, **单片机这里需要的物品**有:用户名和密码(就是你创建mqtt时输入的), 生成的证书头文件, 服务器IP和端口, 控制的端点(`esp32/wol/command`), 还有约定的唤醒数据, 比如我用的是("wake"), 最后还有Wi-Fi SSID和密码

### 调试

在手机端安装`Termux`, 并安装`Mosquitto`

执行

```bash
mosquitto_pub -h "你的IP或者HOST" -p 8883 --cafile ~/certs/ca.crt -u "esp32_client" -P "密码" -t "esp32/wol/command" -m "wake"
```

`~/certs/ca.crt`需要自行拷贝到手机的`termux`主目录的`certs`文件夹下

电脑上可以开`wireshark`使用`wol`作为筛选器

如果没有问题就能抓到数据包(没抓到估计是被防火墙拦下来了, 只要放行UDP协议的端口7和9就行)

```bash
33	4.120584	192.168.102.82	192.168.102.255	WOL	144	MagicPacket for Intel_93:d2:b7 (电脑的MAC地址)
```


## 总结

做出来感觉挺有意思, 也省去买开机棒的钱了, 后面可能会考虑接入米家, 不过这就以后再说了.

---

**版权声明**：本文为原创文章，转载请注明出处。

