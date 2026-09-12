---
title: 学习记录
date: '2026-08-23 18:27:01'
updated: '2026-09-12 18:44:48'
codeHeightLimit: 300
categories:
- 技术
- C/C++
- 分享
tags:
- C/C++
- C++
- Qt
- 技术
---

# 学习记录

本文章记录一些学习过程, 持续更新

## day-1

学习Linux平台下的socket使用方法

首先要创建一个套接字, 并接收返回的文件描述符

`auto sockfd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);`

通常文件描述符应为正整数

<!-- more -->

接下来需要设置监听或者连接, 就需要用到IP和Port, 这里会用到一个`struct sockaddr`的结构体, 不过发现这个结构体可读性很差, 因此需要用`struct sockaddr_in`设置好后再转换到`struct sockaddr`

```c++
std::string ip = "0.0.0.0";
uint16_t port = 2345;

struct sockaddr_in sockaddr;
memset(&sockaddr, 0, sizeof(sockaddr));
sockaddr.sin_family = AF_INET;
sockaddr.sin_addr.s_addr = inet_addr(ip.c_str());
sockaddr.sin_port = htons(port);    // 将16位的主机字节顺序转换为网络字节顺序(不同系统的端序不同)
if(::bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0)
{
    printf("error: errno=%d errmsg=%s\n", errno, strerror(errno));
    return 1;
}
```

接下来是打开监听, 并设置最大接受字节数

最后就是主循环+释放套接字

```c++
if(::listen(sockfd, 1024) < 0)
{
    printf("error: errno=%d errmsg=%s\n", errno, strerror(errno));
    return 1;
}

while (true)
{
    int connfd = ::accept(sockfd, nullptr, nullptr);
    if (connfd < 0){
        printf("error: errno=%d errmsg=%s\n", errno, strerror(errno));
        return 1;
    }
    char buf[1024] = {0};
    size_t len = ::recv(connfd, buf, sizeof(buf), 0);
    printf("recv: connfd=%d msg=%s\n", connfd, buf);

    ::send(connfd, buf, len, 0);
}

::close(sockfd);
```

这里在终端使用nc [地址] [端口] 连接并发送信息

可以发现只有连接后的第一条信息能被返回, 后面的信息都无法被响应, 这个问题其实很明显, 主循环的某个函数是阻塞IO, 这个后面再说, 既然都用C++了, 那肯定要先封装一下

## day-2

在Linux中, AI编写的部分命令会在后面加上`>/dev/null 2>&1`, 前面`>/dev/null`, 就是把输出丢弃, 后面的`2>&1`是为何呢?

0->标准输入(stdin)

1->标准输出(stdout)

2->标准错误(stderr)

按照常识, 不加后面, 执行命令的输出结果会直接输出到屏幕, 因此一开始1和2均会指向终端, 所以加上命令后, 从左往右执行, 执行到`>/dev/null`, 会把1和2都重定向到`/dev/null`中吗? 肯定不是, 在linux中执行后可以发现错误信息依然在屏幕上

```bash
> ls xxx
ls: cannot access 'xxx': No such file or directory
> ls xxx >/dev/null
ls: cannot access 'xxx': No such file or directory
```

因此, 只有1被重定向了, 2没有动, 因此第二个`2>&1`就是把2重定向到1, 也就是黑洞

那为什么要`&`呢? 如果不加, 在执行后会发现错误输出被输出到了1这个文件里, 所以加上`&`是为了区分**文件描述符**和**普通文件**

同时在Windows上写socket会发现返回值是

```cpp
SOCKET WSAAPI socket(
  [in] int af,
  [in] int type,
  [in] int protocol
);
```

前面的SOCKET返回的是句柄(Windows上的叫法), 不过这里和一般的句柄不同, 这里是套接字句柄

## day-3

我们都知道网络的四层:应用层, 传输层, 网络层, 网络接口层, 这里先不管7层的结构, 在应用层, 也就是最上层, 有HTTP、FTP、Telnet、DNS、SMTP等, 这些都是常见协议, 这次我们要实现的就是HTTP/HTTPS层的实现, 这里数据在封装后会向下走到传输层, 有TCP和UDP, 在这里再次封装够会再次向下走到网络层, 这里会用到IP协议, 根据MTU进行分段, 这里分段后根据上层协议会为每段加上协议的头, 并加上IP头, 送到网络接口层, 这里会再加上MAC头, 最后通过以太网送到目标设备反向执行上述过程, 直到数据来到应用层供应用处理

因此本次的关键部分都由操作系统完成, 我们只需要设置监听, 取数据, 发数据就行

再说下IP和子网掩码, IP用于标识设备位置, 而子网掩码则由路由器用于判断某个IP是否属于子网, 这里通过查看自己的IP为192.168.3.106, 子网掩码为255.255.255.0, 也有会看到/24的情况, 这也是掩码, 代表从左往右有24个连续的1, 通过对IP和掩码进行与运算可以得到网络号,  用于判断某个IP是否属于子网, 而主机号很简单, IP后面8位就是, 比如我的主机号就是106, 网络号为192.168.3.0, 也就是只要IP为192.168.3.*的IP都会被路由器判断为属于本子网

不过有些IP很特殊, 比如网络号为0.0.0.0, 这样好像所有IP都属于本子网? 其实这个代表任意网络, 通常大部分网络服务默认会监听这个地址, 如果只想服务某几个网段, 就可以修改这里

还有就是子网下的广播地址, 构成为网络号+全1, 在这里是192.168.3.255, 这个IP是广播地址, 路由器会为所有设备发送数据

## day-4

在Windows端做这个其实是和Linux差不多的

大部分函数都无需更改, 不过由于Windows上SOCKET的句柄特殊, 所以注销socket使用的是closesocket

在开始需要调用WSAStartup来初始化, 指定程序使用的socket版本

在程序结束运行还主要执行WSACleanup来注销, 接下来对此前封装的版本简单更改就能得到Windows的版本

不过编译没有问题, 但是在链接阶段出现了报错, 既然是链接阶段报错, 那只要链接指定的库就行, 查阅微软的文档可知, 需要链接`ws2_32.lib`这个静态库, 这里如果用的是MSVC可以直接使用宏定义`#pragma comment(lib, "ws2_32.lib")`, 如果用的是CMake直接在`add_executable`下面加上`target_link_libraries(${PROJECT_NAME} PRIVATE ws2_32)`即可成功链接

Linux:

```cpp
//tcp_server.cpp
#include "tcp_server.hpp"

#include <arpa/inet.h>
#include <cerrno>
#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <stdexcept>
#include <sys/socket.h>
#include <utility>
#include <unistd.h>

Socket::Socket(int fd) noexcept : fd_(fd) {}

Socket::~Socket() {
    close();
}

Socket::Socket(Socket&& other) noexcept : fd_(other.fd_) {
    other.fd_ = -1;
}

Socket& Socket::operator=(Socket&& other) noexcept {
    if (this != &other) {
        close();
        fd_ = other.fd_;
        other.fd_ = -1;
    }
    return *this;
}

int Socket::get() const noexcept {
    return fd_;
}

bool Socket::valid() const noexcept {
    return fd_ >= 0;
}

void Socket::close() noexcept {
    if (valid()) {
        ::close(fd_);
        fd_ = -1;
    }
}

TcpServer::TcpServer(std::string ip, uint16_t port)
    : ip_(std::move(ip)), port_(port) {}

void TcpServer::start() {
    listen_socket_ = Socket(::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
    if (!listen_socket_.valid()) {
        throw std::runtime_error(error_message("socket"));
    }

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port_); // 主机字节序转换为网络字节序。

    if (::inet_pton(AF_INET, ip_.c_str(), &address.sin_addr) != 1) {
        throw std::runtime_error("invalid IPv4 address: " + ip_);
    }

    if (::bind(listen_socket_.get(),
               reinterpret_cast<const sockaddr*>(&address),
               sizeof(address)) < 0) {
        throw std::runtime_error(error_message("bind"));
    }

    if (::listen(listen_socket_.get(), 1024) < 0) {
        throw std::runtime_error(error_message("listen"));
    }

    std::cout << "server listening on " << ip_ << ':' << port_ << '\n';
}

void TcpServer::run() const {
    while (true) {
        Socket connection(::accept(listen_socket_.get(), nullptr, nullptr));
        if (!connection.valid()) {
            // EINTR 表示系统调用被信号中断，可以安全地重新等待连接。
            if (errno == EINTR) {
                continue;
            }
            throw std::runtime_error(error_message("accept"));
        }

        handle_client(connection);
    }
}

std::string TcpServer::error_message(const char* operation) {
    return std::string(operation) + " failed: errno=" +
           std::to_string(errno) + " (" + std::strerror(errno) + ')';
}

void TcpServer::handle_client(const Socket& connection) {
    char buffer[1024];
    const ssize_t received =
        ::recv(connection.get(), buffer, sizeof(buffer), 0);

    if (received < 0) {
        throw std::runtime_error(error_message("recv"));
    }
    if (received == 0) {
        return; // 客户端直接关闭连接，没有可回显的数据。
    }

    std::cout.write(buffer, received);
    std::cout << '\n';

    // send 可能只发送部分数据，因此循环直到全部回写完成。
    ssize_t sent = 0;
    while (sent < received) {
        const ssize_t count = ::send(
            connection.get(), buffer + sent,
            static_cast<size_t>(received - sent), 0);
        if (count < 0) {
            throw std::runtime_error(error_message("send"));
        }
        sent += count;
    }
}


// tcp_server.hpp
#pragma once

#include <cstdint>
#include <string>

// 对 socket 文件描述符做 RAII 管理，离开作用域时自动释放资源。
class Socket {
public:
    explicit Socket(int fd = -1) noexcept;
    ~Socket();

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;
    Socket(Socket&& other) noexcept;
    Socket& operator=(Socket&& other) noexcept;

    [[nodiscard]] int get() const noexcept;
    [[nodiscard]] bool valid() const noexcept;

private:
    void close() noexcept;
    int fd_;
};

class TcpServer {
public:
    TcpServer(std::string ip, uint16_t port);

    // 创建监听 socket，并完成地址绑定和监听。
    void start();

    // 持续接收客户端连接，并将收到的数据原样回写。
    void run() const;

private:
    static std::string error_message(const char* operation);
    static void handle_client(const Socket& connection);

    std::string ip_;
    uint16_t port_;
    Socket listen_socket_;
};


// main.cpp
#include "tcp_server.hpp"

#include <iostream>
#include <stdexcept>

int main() {
    try {
        TcpServer server("0.0.0.0", 2345);
        server.start();
        server.run();
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
```

Windows:

```cpp
// tcp_server.cpp
#include "tcp_server.hpp"

#include <cerrno>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <utility>

Socket::Socket(SOCKET hld) noexcept : hld_(hld) {}

Socket::~Socket() {
    close();
}

Socket::Socket(Socket&& other) noexcept : hld_(other.hld_) {
    other.hld_ = INVALID_SOCKET;
}

Socket& Socket::operator=(Socket&& other) noexcept {
    if (this != &other) {
        close();
        hld_ = other.hld_;
        other.hld_ = INVALID_SOCKET;
    }
    return *this;
}

SOCKET Socket::get() const noexcept {
    return hld_;
}

bool Socket::valid() const noexcept {
    return hld_ != INVALID_SOCKET;
}

void Socket::close() noexcept {
    if (valid()) {
        ::closesocket(hld_);
        hld_ = INVALID_SOCKET;
    }
}

TcpServer::TcpServer(std::string ip, uint16_t port) : ip_(std::move(ip)), port_(port) {}

void TcpServer::start() {
    listen_socket_ = Socket(::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
    if (!listen_socket_.valid()) {
        throw std::runtime_error(error_message("socket"));
    }

    SOCKADDR_IN address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port_);  // 主机字节序转换为网络字节序。

    if (::inet_pton(AF_INET, ip_.c_str(), &address.sin_addr) != 1) {
        throw std::runtime_error("invalid IPv4 address: " + ip_);
    }

    if (::bind(listen_socket_.get(), reinterpret_cast<const sockaddr*>(&address), sizeof(address)) <
        0) {
        throw std::runtime_error(error_message("bind"));
    }

    if (::listen(listen_socket_.get(), 1024) < 0) {
        throw std::runtime_error(error_message("listen"));
    }

    std::cout << "server listening on " << ip_ << ':' << port_ << '\n';
}

void TcpServer::run() const {
    while (true) {
        Socket connection(::accept(listen_socket_.get(), nullptr, nullptr));
        if (!connection.valid()) {
            // EINTR 表示系统调用被信号中断，可以安全地重新等待连接。
            if (errno == EINTR) {
                continue;
            }
            throw std::runtime_error(error_message("accept"));
        }

        handle_client(connection);
    }
}

std::string TcpServer::error_message(const char* operation) {
    return std::string(operation) + " failed: errno=" + std::to_string(errno) + " (" +
           std::strerror(errno) + ')';
}

void TcpServer::handle_client(const Socket& connection) {
    char buffer[1024];
    const int received = ::recv(connection.get(), buffer, sizeof(buffer), 0);

    if (received < 0) {
        throw std::runtime_error(error_message("recv"));
    }
    if (received == 0) {
        return;  // 客户端直接关闭连接，没有可回显的数据。
    }

    std::cout.write(buffer, received);
    std::cout << '\n';

    // send 可能只发送部分数据，因此循环直到全部回写完成。
    int sent = 0;
    while (sent < received) {
        const int count =
            ::send(connection.get(), buffer + sent, static_cast<size_t>(received - sent), 0);
        if (count < 0) {
            throw std::runtime_error(error_message("send"));
        }
        sent += count;
    }
}


// tcp_server.hpp
#pragma once

#include "config.hpp"
#include <cstdint>
#include <string>
#include <WinSock2.h>
#include <WS2tcpip.h>

// 对 socket 文件描述符做 RAII 管理，离开作用域时自动释放资源。
class Socket {
public:
    explicit Socket(SOCKET hld = -1) noexcept;
    ~Socket();

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;
    Socket(Socket&& other) noexcept;
    Socket& operator=(Socket&& other) noexcept;

    [[nodiscard]] SOCKET get() const noexcept;
    [[nodiscard]] bool valid() const noexcept;

private:
    void close() noexcept;
    SOCKET hld_;

};

class TcpServer {
public:
    TcpServer(std::string ip, uint16_t port);

    // 创建监听 socket，并完成地址绑定和监听。
    void start();

    // 持续接收客户端连接，并将收到的数据原样回写。
    void run() const;

private:
    static std::string error_message(const char* operation);
    static void handle_client(const Socket& connection);

    std::string ip_;
    uint16_t port_;
    Socket listen_socket_;
};


// main.cpp
#include "tcp_server.hpp"

#include <iostream>
#include <stdexcept>
#include <WinSock2.h>

int main() {
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "error: unable setup socket!\n";
    }

    try {
        TcpServer server("0.0.0.0", 2345);
        server.start();
        server.run();
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    if (WSACleanup() != 0) {
        std::cerr << "error: unable cleanup socket!\n";
    }

    return 0;
}
```

## day-5

在[day 3](#day-3)中我们讲到了网络协议, 今天就来看看套接字的这些参数

`int socket(int __domain, int __type, int __protocol) noexcept(true)`

在创建socket时, 第一个参数会被说传入`AF_INET`, 这个`__domain`是域, 在下面的`sockaddr_in`也能看到叫协议族, 通过查看头文件, 我们会发现有很多的协议族, 不过常用的就一点

| 协议族常量                  | 全称              | 适用场景                                                     |
| :-------------------------- | :---------------- | :----------------------------------------------------------- |
| **AF_INET**                 | IPv4 互联网协议族 | 最常用，使用 **IPv4 地址**（如 `192.168.1.1`）和端口号进行网络通信。 |
| **AF_INET6**                | IPv6 互联网协议族 | 使用 **IPv6 地址**（如 `2001:db8::1`）进行通信，用于下一代互联网。 |
| **AF_UNIX** 或 **AF_LOCAL** | Unix 域协议族     | 用于**同一台机器**上的进程间通信（IPC），使用**文件路径**（如 `/tmp/socket.sock`）作为地址，效率极高，不经过网络协议栈。 |
| **AF_PACKET**（Linux）      | 链路层协议族      | 直接操作网卡的**数据链路层**（MAC 地址），常用于抓包（如 tcpdump）或发送原始以太网帧。 |

不过在查看定义时还会发现`AF_*`和`PF_*`的含义相同, 第一个是地址族, 在绑定地址（`bind()`）时使用，表示"地址结构体要用哪种格式"; 第二个是协议族, 在创建 Socket（`socket()`）时使用，表示"要用哪套协议"

在看第二个和但三个参数, 分别是**套接字类型**和**协议**, 在上面我们讲到过, TCP 是面向字节流的协议, UDP 是面向报文的协议, 而`SOCK_STREAM`就是基于TCP协议的, 那后面那个协议填什么会有什么影响? 当然是填了不匹配套接字的协议会无法创建socket, 不过由于同一协议族下有会有不同的协议, 所以当前两个参数无法确定协议时就要手动去指定要使用的协议, 这里`AF_INET`和`SOCK_STREAM`就已经能确定TCP协议了, 所以有些教程会直接在第三个参数填0

## day-6

之前说过, 这样写有个问题, 只有客户端的第一次信息才响应, 自然就会想到主循环中存在阻塞函数, 很容易我们能想到用一个线程去检查有没有新客户端连接, 再为客户端开线程去处理客户端的信息, 这样确实简单, 但是客户端一多会占用大量系统资源, 不过今天先不去优化这个, 而是去分析程序逻辑

之前我们分析过, 一个客户端的第二次信息不被响应, 是因为被阻塞了, 通过抓包, 我们发现客户端的数据已经发送到了服务端, 那就说明目前数据存在缓冲区等待服务端处理, 在此之前, 我们先去看看如果客户端A连接上了服务器, 而客户端B在A未发送消息前连接会怎样?

在使用两个nc连接后, 作为客户端B也成功连接了, 这点可以通过抓包确认(抓包结果里确实出现了TCP典型的三次握手建立连接), 但是从主循环的逻辑中看, 程序不应该在A连接后阻塞在`recv`吗, B怎么会成功建立连接? 难道`accept`并不是用于建立新连接的吗?

```cpp
void TcpServer::run() const {
    while (true) {
        Socket connection(::accept(listen_socket_.get(), nullptr, nullptr));
        if (!connection.valid()) {
            // EINTR 表示系统调用被信号中断，可以安全地重新等待连接。
            if (errno == EINTR) {
                continue;
            }
            throw std::runtime_error(error_message("accept"));
        }

        handle_client(connection);
    }
}
```

答案还真不是, 真正建立连接的地方从来都不是在用户态, 而是内核自动完成的, 而accept只是在从内核维护的连接队列中取出新的连接, 这也就说明了为什么客户端的第二条信息不被响应的原因

## day-7

在实际应用中, 如果我们终止服务器后很快再启动服务器, 就会出现端口被占用的情况, 而过了一段时间后就能再次使用这个端口, 通过询问AI与查阅资料, 我们可知这个情况是TCP连接终止时产生的

> 套接字需要 `TIME_WAIT` 状态，主要是为了**可靠地关闭连接**和**防止旧数据干扰新连接**，这是TCP协议为保证可靠传输而设计的关键机制。
>
> `TIME_WAIT` 状态出现在**主动关闭连接**的一方。当这一方（比如客户端A）发出最后的ACK确认后，就会进入 `TIME_WAIT` 状态，并持续 **2倍的最大报文段生存时间（2MSL）**。

这段时间主要是为了防止客户端最后一次挥手的ACK丢包而设计的, 在编写程序中可通过`SO_REUSEADDR`选项来使用处于Time-wait状态下的套接字

这里就要引入套接字设置和读取函数, ` setsockopt`和`getsockopt`

```c++
optlen=sizeof(option);

option=TRUE;

setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, (void*)&option, optlen);
```

设置失败或读取失败会返回`-1`

## day-8

今天来看看信号与signal函数

```c
#include <signal>
void (*signal(int signo, void (*func)(int)))(int);
```

乍一看很复杂, 不过在AI帮助下理解还是不难的, 既然是函数就先看看返回值, 函数名, 参数有什么

在此之前我们要去学一下C语言中的函数指针, 它的最基本形式是`返回值 (*函数名)(参数表)`

这里我们从内往外看, `void (*func)(int)`这里是signal的入参之一, 表示我们要传入一个参数为int, 无返回值的函数指针, 在这里我们很容易把这个看成一个总体, 但是这样看就很难去理解signal函数的返回值是什么

实际上, 更现代的写法是(这里我在看signal.h的实现时发现已经采用这种方法了, 所以上面就当简单了解下函数指针吧)

```c
/* Set the handler for the signal SIG to HANDLER, returning the old
   handler, or SIG_ERR on error.
   By default `signal' has the BSD semantic.  */
typedef void (*sighandler_t)(int);
sighandler_t signal(int signal, sighandler_t func);
```

这样返回值, 函数表, 参数表就能看懂了, 这里就不多在语法上纠结了, 毕竟重点不在这

我们查阅资料可知函数的入参分别为信号类型和回调函数(回调函数入参为信号类型), 我们亲自尝试一下它的调用

```c
#include <signal.h>

void key_c(int sig) {
    printf("Ctrl+C pressed! sig:%d \n", sig);
}

int main() {
    signal(SIGINT, key_c);

    while (true)
    {
        
    }
    
    return 0;
}
```

运行后按下Ctrl+C确实出现了提示, 不过在宣告实验完成前, 我们在询问了AI后发现一个安全隐患: **异步信号安全函数**

查阅资料发现部分函数如`printf`为了保证不同线程调用时的"秩序"会加上一把锁, 如果我们主程序在执行`printf`到一半时信号被触发了, 此时主程序会被直接挂起, 转到我们的回调函数执行`printf`就会无法获取锁而阻塞, 而主程序持有的锁无法被释放, 这样就造成了程序的死锁, 因此我们需要一个更加优雅的方案, 这里可以选择化异步为同步, 也能调用"安全"的函数

```c++
#include <atomic>
#include <signal.h>

std::atomic<int> flag = 1;

void key_c(int sig) {
    flag.store(0);
}

int main() {
    signal(SIGINT, key_c);

    while (flag.load())
    {
        sleep(1);
    }
    printf("Ctrl+C pressed!\n");

    return 0;
}
```

## day-9

不过呢实际编程中很少会用`signal`

```c++
extern int sigaction (int __sig, const struct sigaction *__restrict __act,
		      struct sigaction *__restrict __oact) __THROW;
```

在实际编写高并发的程序时难免会创建多进程去处理请求, 而子进程处理不当会导致僵尸进程的产生(僵尸进程可以自行查询, 当然还有fork和exec), 下面就用sigaction来解决僵尸进程

```c++
#include <iostream>
#include <signal.h>
#include <stdexcept>
#include <sys/wait.h>

volatile sig_atomic_t exitb = 0;

void hld_childproc(int sig) {
    int status;
    pid_t id = waitpid(-1, &status, WNOHANG);  // WNOHANG 非阻塞
    if (WIFEXITED(status)) {
        printf("pid:%d,exit code:%x\n", WEXITSTATUS(status));
    }
    exitb = 1;
}

int main() {
    pid_t pid;
    struct sigaction act;
    act.sa_handler = hld_childproc;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;
    sigaction(SIGCHLD, &act, 0);

    pid = fork(); // 子进程的pid变量为0
    if(pid==0){
        // 子进程逻辑
        printf("child process\n");
        sleep(10);
        return 0;
    }
    else{
        printf("child pid:%d\n",pid);
        while (!exitb)
        {
            usleep(100000);
        }
        
    }
    printf("all child exit!\n");
    return 0;
}
```

运行结果:

```txt
child pid:12415
child process
pid:0,exit code:1
all child exit!
```

代码中依然是有**异步信号安全**的问题, 不过这里简单演示, 就图方便了, 实际应用中不应这样写

## day-10

这里跳过了"基于多进程的服务端", 不过还是可以去参考下的

我们都知道创建进程的代价是巨大的, 当然进程间通行也是极为繁琐的, 那么有没有什么方法能不创建进程又能为大量客户端提供服务? 当然有, 就是IO多路复用

典型的IO有五种:同步IO, 非阻塞IO, IO多路复用, 信号驱动IO, 异步IO

在基于多进程的服务端中, 只服务两三个客户端还好, 但是当客户端一多服务器性能就会急剧下降, 这时操作系统用于调度的时间将会是灾难性的, 那么应该怎么处理成千上万条连接, 而减少线程或进程的使用呢? 正常情况下, 客户端从连接到离线可能请求就那么两三条, 大部分时间都处于"安静状态", 那么我们完全可以把服务端变成:当客户端发送请求时, 服务端才去处理, 如果有同时有多个请求就将请求排队, 由服务端挨个响应

这样就实现了网络IO的复用, 不过有个问题, 正常情况下服务端需要去问操作系统才能知道到底哪个客户端准备好了, 如果客户端一多, 服务端难免会困死在轮询上, 这该怎么办呢? 能不能让操作系统在某个客户端请求时提醒服务端呢? 

```c++
/* Check the first NFDS descriptors each in READFDS (if not NULL) for read
   readiness, in WRITEFDS (if not NULL) for write readiness, and in EXCEPTFDS
   (if not NULL) for exceptional conditions.  If TIMEOUT is not NULL, time out
   after waiting the interval specified therein.  Returns the number of ready
   descriptors, or -1 for errors.

   This function is a cancellation point and therefore not marked with
   __THROW.  */
extern int select (int __nfds, fd_set *__restrict __readfds,
		   fd_set *__restrict __writefds,
		   fd_set *__restrict __exceptfds,
		   struct timeval *__restrict __timeout);
```

> ### 1. `nfds` (int)
>
> - **作用**：指定需要检查的文件描述符范围，即**最大文件描述符值 + 1**。
> - **原因**：内核只会在 `[0, nfds)` 这个区间内扫描描述符，以提高效率。
> - **用法**：如果你监视的 fd 中最大的是 `max_fd`，则传入 `max_fd + 1`。
>
> ### 2. `readfds` (fd_set*)
>
> - **作用**：监视“可读”事件。
>   - **输入**：指向一个集合，包含所有你关心是否可读的描述符。
>   - **输出**：调用返回后，该集合被内核修改为**实际可读**的描述符子集（其他位被清空）。
> - **可为 NULL**：如果不需要监视可读，则传 `NULL`。
>
> ### 3. `writefds` (fd_set*)
>
> - **作用**：监视“可写”事件（内核输出缓冲区有空间可写）。
>   - 输入/输出行为与 `readfds` 类似，返回后只保留可写的描述符。
> - **可为 NULL**：不需要监视可写时传 `NULL`。
>
> ### 4. `exceptfds` (fd_set*)
>
> - **作用**：监视“异常”事件（通常指带外数据（Out-of-Band）或某些错误条件，例如 TCP 的紧急数据）。
>   - 同样作为输入输出参数。
> - **可为 NULL**：不关心异常时传 `NULL`。
>
> ### 5. `timeout` (struct timeval*)
>
> - **作用**：设定等待的最长时间（秒 + 微秒）。
>   - **不为 NULL**：等待指定的时间后返回（即使没有描述符就绪，返回 0）。
>   - **为 NULL**：无限等待，直到有描述符就绪或信号中断。
>   - **指向值为 {0, 0}**：立即返回（轮询），检查一次后立刻返回。
> - **注意**：某些系统会在返回时修改该值（剩余时间），所以通常每次调用前重新设置。
>
> ### 返回值
>
> - **成功**：返回就绪的描述符总数（所有集合中就绪位的总数）。
> - **超时**：返回 0。
> - **出错**：返回 -1，并设置 `errno`（如 `EBADF`、`EINTR` 等）。

~~(上面都AI解释的)~~`fd_set`本质是bitmap, 通过把客户端对应索引设置为1, 这样操作系统就会帮我们去监视这个客户端, 当出现可读内容时就会去唤醒程序, 并返回就绪个数, 那么问题来了, 如果返回值是就绪个数, 我要怎么才能知道是谁就绪了呢?

答案很简单, 我们传入的`fd_set`在调用结束后产生变化, 里面会变为就绪的sock, 比如:传入的`readfds`是{1,2,5}, 假设只有2就绪了, 那么调用结束后就只剩下{2}了, 此时一个个轮询配合就绪个数就能知道谁准备好了, 那么只要我们写好处理代码就可以了, 这里放个简单的demo

```c++
int main() {
    fd_set r_fd, r_cpy;
    int fd_max = 0;
    FD_ZERO(&r_fd);
    FD_SET(STDIN_FILENO, &r_fd); // 监视stdin
    fd_max = (STDIN_FILENO > fd_max) ? STDIN_FILENO : fd_max;
    // 设置超时
    struct timeval tv, tv_cpy;;
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    tv_cpy = tv;

    r_cpy = r_fd;
    char buf[1025];

    while (true)
    {
        tv = tv_cpy; // 这里需要恢复时间和fd, 因为都会被改变
        r_fd = r_cpy;
        int ret = select(fd_max + 1, &r_fd, NULL, NULL, &tv); // 这里一定要加1
        if (ret == 0) {
            printf("timeout!\n");
            continue;
        }
        if (ret == -1) {
            printf("err:%s\n", strerror(errno));
            break;
        }
        int cnt = 0;
        for (int i = 0; i < fd_max + 1; i++){
            if (FD_ISSET(i, &r_fd)) {
                if (i == STDIN_FILENO){
                    if (fgets(buf, sizeof(buf), stdin) != NULL){
                        printf("revc: %s\n", buf);
                    }
                }
                cnt++;
            }
            if (cnt == fd_max) break;
        }
        
    }
    return 0;
}
```

## day-11

```c++
extern int epoll_create (int __size) __THROW;
extern int epoll_ctl (int __epfd, int __op, int __fd,
		      struct epoll_event *__event) __THROW;
extern int epoll_wait (int __epfd, struct epoll_event *__events,
		       int __maxevents, int __timeout)
	__attr_access ((__write_only__, 2, 3)) __nonnull ((2));
```

在Linux 2.6.8以后内核将完全忽略`epoll_create`的size参数, 创建失败会返回-1, 反之返回文件描述符(最后需要用`close`关闭)

`epoll_ctl`用于注册要监视的文件描述符(成功返回0, 失败-1), epfd:epoll文件描述符, op:操作, fd:待监视的文件描述符, event:监视对象的事件类型

`epoll_wait`用于调用监视, 成功时返回发生事件的个数, 失败返回-1, events:保存发生事件的文件描述符集合的结构体地址, timeout:单位为毫秒, 传入-1则一直阻塞

那么使用epoll改造[day 10](#day-10)的示例

```c++
int main() {

    int ep_fd = epoll_create(10);
    if (ep_fd == -1)
        exit(-1);
    struct epoll_event e;
    e.events = EPOLLIN;  // 需要读取数据
    e.data.fd = STDIN_FILENO;
    if (epoll_ctl(ep_fd, EPOLL_CTL_ADD, STDIN_FILENO, &e) == -1)
        exit(-2);
    char buf[1025];

    struct epoll_event* ep_events;
    ep_events = (epoll_event*)malloc(sizeof(struct epoll_event) * MAX_EPSIZE);

    while (true) {
        int ret = epoll_wait(ep_fd, ep_events, MAX_EPSIZE, 5000);
        if (ret == 0) {
            printf("timeout!\n");
            continue;
        }
        if (ret == -1) {
            printf("err:%s\n", strerror(errno));
            break;
        }
        for (int i = 0; i < ret; i++) {
            int fd = ep_events[i].data.fd;
            if (fd == STDIN_FILENO) {
                if (fgets(buf, sizeof(buf), stdin) != NULL) {
                    printf("revc: %s\n", buf);
                }
            }
        }
    }
    free(ep_events);
    close(ep_fd);
    return 0;
}
```

## day-12





























---

**版权声明**：本文为原创文章，转载请注明出处。
