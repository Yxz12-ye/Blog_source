---
title: 逆向获取狼途T88电量(通过HID)
date: '2026-10-26 18:40:46'
updated: '2026-10-26 19:45:00'
categories:
- 技术
- 逆向
tags:
- 逆向
- HID
- Python
codeHeightLimit: 300
---

# 逆向获取狼途T88电量(通过HID)

## 概述

笔者刚买了狼途 T88, 在 B 站上看到有人借助 AI 逆向官方驱动, 拿到私有协议后成功读出了键盘电量. 不过每把键盘的协议都不太一样, 网上也没人做过这把键盘的驱动逆向, 那就由我来试一下吧.

<!-- more -->

## 准备工作

::: warning

本文仅用于技术学习与交流. 不同批次、不同固件版本的 T88, 报文内容都可能不一样, 如果对不上, 请以自己 dump 到的数据为准.

:::

- 狼途 T88 与官方驱动(主程序 `devicedriver.exe`)
- [IDA](https://hex-rays.com/ida-free) 与 [x32dbg](https://x64dbg.com/)
- Python 3 与 [hidapi](https://pypi.org/project/hidapi/) (`pip install hidapi`, 代码里 `import hid`)
- [USB Device Tree Viewer](https://www.codertools.net/tools/usb-device-viewer.php?lang=zh), 用来查看 HID 描述符

整个流程大致是: 先在 IDA 里静态分析, 定位到关键函数; 再用 x32dbg 动态调试, 还原出报文格式; 最后用 Python 复现.

## 正文

### 从字符串入手

用 IDA 打开 `devicedriver.exe`, 在字符串窗口搜索 `battery`, 能搜到几条被 MSVC 修饰过的符号名:

```txt
.rdata:00AF4904	00000029	C	?SetShowBattery@BatteryCtrl@MUI@@QAEXH@Z
.rdata:00AF6E30	0000002D	C	?SetBatteryIcon@BatteryCtrl@MUI@@QAEHPB_W0@Z
.rdata:00AF72A4	0000002A	C	?SetBatteryInfo@BatteryCtrl@MUI@@QAEXHH@Z
```

也就是说, 程序里残留了开发者自己写的 MUI 界面库的符号信息(真正的调试符号并没有随安装包发布). 这一串修饰名可读性很差, 不过交给 AI 翻译一下, 函数原型就清楚了:

```cpp
void MUI::BatteryCtrl::SetShowBattery(int);
int  MUI::BatteryCtrl::SetBatteryIcon(const wchar_t*, const wchar_t*);
void MUI::BatteryCtrl::SetBatteryInfo(int, int);
```

MUI 这个名字是不是有点眼熟? 注意到驱动目录下还有一个 `mui.dll`, 电量的显示逻辑多半就封装在里面. 这样一来光靠静态分析就有点吃力了, 直接上动态调试.

### 定位相关代码

打开 x32dbg 启动驱动, 在内存视图里确实能看到它加载了 `mui.dll`, 同时 `devicedriver.exe` 的加载基址是 `0x960000`. 回到 IDA, 用 `Edit → Segments → Rebase program` 把基址改成 `0x960000`, 两边的地址就对上了, 方便对照调试.

再用 IDA 打开 `mui.dll`, 在 Functions 窗口搜索 `battery`, 刚才在 exe 里出现的那几个函数都能找到. 其中 `MUI::BatteryCtrl::SetBatteryInfo(int, int)` 的嫌疑最大, 就先从它下手.

~~在反汇编视图里, 我们能很轻松地知道函数的地址是 `.text:10020270`; 接下来需要手动换算成 x32dbg 里的内存地址, 从 Memory Map 可知这个 DLL 实际加载在 `0x6C2D0000`, 计算得到内存中是 `0x6C2F0270`.~~

上面这段来自后期的我: 后来才发现, x32dbg 上方的符号(Symbols)选项卡里直接就能看到 `mui.dll` 的所有符号, 搜一下双击就跳过去了, 根本不用手算.

### 下断点, 看电量从哪来

在 `SetBatteryInfo` 上打下断点, 运行后程序果然断了下来. 查看 `eax`, 值是 `0x5B`, 也就是十进制的 91, 和软件界面上显示的电量正好对得上. 再看调用点的参数, 第二个参数是 0, 从命名和上下文推断多半表示是否在充电.

接下来查看调用栈:

```txt
08D4F96C  009A394A  返回到 devicedriver.009A394A 自 devicedriver.009BDC60
```

调用点附近的代码:

```asm
009A3924 | lea eax,dword ptr ss:[ebp-48]           | 报文缓冲区
009A3927 | push 0                                  |
009A3929 | push eax                                |
009A392A | call <JMP.&memset>                      |
009A392F | add esp,8                               |
009A3932 | mov word ptr ss:[ebp-47],120            | 小端写入 0x20 0x01
009A3938 | lea eax,dword ptr ss:[ebp-48]           |
009A393B | push 41                                 | 0x41 = 65 字节
009A393D | push eax                                |
009A393E | call devicedriver.974000                |
009A3943 | mov ecx,eax                             |
009A3945 | call devicedriver.9BDC60                |
009A394A | test al,al                              |
009A394C | je devicedriver.9A398E                  |
009A394E | cmp byte ptr ss:[ebp-48],20             | 响应首字节应为 0x20
009A3952 | jne devicedriver.9A398E                 |
009A3954 | mov al,byte ptr ss:[ebp-45]             | 偏移 3: 电量
009A3957 | test al,al                              |
009A3959 | je devicedriver.9A398E                  |
009A395B | movzx eax,al                            |
009A395E | mov ecx,64                              | 64:'d'
009A3963 | cmp eax,ecx                             | 和 100 比较
009A3965 | push 0                                  |
009A3967 | cmova eax,ecx                           | 超过 100 就截断
009A396A | mov ecx,dword ptr ds:[esi+2EC]          | this
009A3970 | push eax                                | 电量
009A3971 | call dword ptr ds:[<MUI::BatteryCtrl::SetBatteryInfo(int,int)>]
```

可以看到, 调用前先把缓冲区清零, 再用 `mov word ptr [ebp-47], 0x120` 按小端写入 `0x20 0x01`, 加上 memset 出来的 `0x00`, 报文开头正好是 `00 20 01 00 …`; 传给 `devicedriver.974000` 的长度是 `0x41`, 说明这块报文缓冲区有 65 字节. 电量则从 `[ebp-45]`(即缓冲区偏移 3)取出, 超过 100 就截断, 最后交给 `SetBatteryInfo` 显示.

顺着调用栈追下去, 这个 91 是从 `devicedriver.9BDC60` 里带出来的, 核心逻辑多半就在那儿.

### 还原收发逻辑

打开 IDA 跳到 `sub_9BDC60`, 按 F5 生成伪代码:

```c
char __thiscall sub_9bdc60(_DWORD *this, __int128 *a2, unsigned int i, int a4)
{
  char result; // al
  char v5; // dl
  unsigned int j; // ecx
  char v7; // al
  char v8; // al
  char v9; // al
  __int128 v10; // xmm0
  int n20; // edi
  char v12; // al
  __int128 v13; // xmm0
  char v14; // cl
  int v16; // [esp+8h] [ebp-50h]
  __int128 v17; // [esp+10h] [ebp-48h] BYREF
  __int128 v18; // [esp+20h] [ebp-38h]
  __int128 v19; // [esp+30h] [ebp-28h]
  __int128 v20; // [esp+40h] [ebp-18h]
  char v21; // [esp+50h] [ebp-8h]

  if ( !*this )
    return 0;
  *(this + 1) = 1;
  v16 = sub_9BE5A0();
  if ( !v16 )
    return 0;
  v5 = 0;
  for ( j = 0; j < i; v5 += v7 )
    v7 = *((_BYTE *)a2 + j++);
  *((_BYTE *)a2 + 32) = v5;
  v8 = *((_BYTE *)a2 + 64);
  v17 = *a2;
  v21 = v8;
  v18 = a2[1];
  v19 = a2[2];
  v20 = a2[3];
  if ( sub_9BF990(33) > 0 )
    goto LABEL_9;
  Sleep(0xAu);
  v9 = *((_BYTE *)a2 + 64);
  v17 = *a2;
  v10 = a2[1];
  v21 = v9;
  v18 = v10;
  v19 = a2[2];
  v20 = a2[3];
  if ( sub_9BF990(33) <= 0 )
  {
LABEL_13:
    result = 0;
  }
  else
  {
LABEL_9:
    Sleep(5u);
    n20 = 0;
    while ( 1 )
    {
      v12 = *((_BYTE *)a2 + 64);
      v17 = *a2;
      v13 = a2[1];
      v21 = v12;
      v18 = v13;
      v19 = a2[2];
      v20 = a2[3];
      sub_9bdc60(v16, &v17, 0x21u, 5);
      if ( *(_WORD *)((char *)a2 + 1) == (_WORD)v17 && *((_BYTE *)a2 + 3) == BYTE2(v17) )
        break;
      ++n20;
      Sleep(0xAu);
      if ( n20 >= 20 )
        goto LABEL_13;
    }
    v14 = v19;
    result = 1;
    *a2 = v17;
    a2[1] = v18;
    *((_BYTE *)a2 + 32) = v14;
  }
  *(this + 1) = 0;
  return result;
}
```

这一坨看着确实头大, 直接丢给 AI 分析. 这个函数的核心就是"发一包请求 → 轮询读响应 → 校验命令头 → 把响应写回 a2":

```txt
上层业务代码
  │
  │ 1. 组包: 33 字节 = Report ID(0) + 32 字节载荷
  │    载荷开头 00 20 01 00, 其余补 0
  ▼
sub_9BDC60(this, a2, i, retries)
  ├─ if (!*this) return 0;                  // 设备没打开
  ├─ *(this+1) = 1;                         // 置忙
  ├─ v16 = sub_9BE5A0();                    // 取设备上下文, 失败返回 0
  ├─ 计算校验和:
  │     v5 = sum(a2[0..i-1]);               // 此时 a2[32] 仍为 0
  │     a2[32] = v5;                        // 载荷的最后一字节
  ├─ sub_9BF990(33)                         // 发请求
  │     失败则 Sleep(10ms) 补发一次, 仍失败则返回 0
  ├─ sub_9BFA70(v16, &v17, 33, 5)           // 读响应, 超时 5ms
  │     ├─ ReadFile 到 readBuf
  │     ├─ WaitForSingleObject(hEvent, 5ms)
  │     ├─ GetOverlappedResult(..., bWait=1)
  │     ├─ readBuf[0] != 0: 复制 33 字节
  │     └─ readBuf[0] == 0: 跳过 Report ID, 复制 32 字节
  ├─ 校验响应头:
  │     v17[0..1] == a2[1..2] && v17[2] == a2[3]
  │     不匹配则 Sleep(10ms) 重试, 最多 20 次
  ├─ 成功: 把响应写回 a2, return 1
  └─ 失败: return 0

上层再从 a2[3] 取电量
```

伪代码里 `sub_9bdc60(v16, &v17, 0x21u, 5)` 那一行看起来像递归, 但结合参数和上下文, 它实际是读包函数 `sub_9BFA70` 的调用(IDA 对这种相邻函数的识别偶尔会出错). 不管怎样, 关键信息已经够了: 请求 33 字节(含 Report ID), 响应载荷 32 字节, 电量在偏移 3.

### 抓一包真实报文

最后在 `sub_9BDC60` 入口下断点, dump 出 `a2` 指向的缓冲区:

```txt
00 20 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

注意这里是在函数入口断下来的, 校验和还没算出来, 所以偏移 32 的那一字节是 0; 按上面的逻辑, 它应该是前 32 字节的累加和, 而这段报文里只有 `0x20` 和 `0x01` 非零, 所以实际发出去时是 `0x21`.

把这段报文和从 [USB Device Tree Viewer](https://www.codertools.net/tools/usb-device-viewer.php?lang=zh) 读到的 HID 描述符一起发给 AI, 让它帮忙写一份测试代码. 这次拿到的关键信息是:

- VID `0x05AC`、PID `0x024F`, Usage Page `0xFF60`
- `0xFF60` 是厂商自定义的 Usage Page, 键盘的普通键鼠接口不是它, 私有协议只走这一路
- `0x05AC` 其实是 Apple 的 VID, 这类键盘为了免驱兼容 macOS 常直接借用 Apple 的 VID/PID, 所以看到它别以为自己插了个苹果键盘
- 报文首字节 `0x00` 是 Report ID, `hidapi` 的 `write()` 会把它当成 Report ID, 所以请求要写 33 字节; 读回来的响应则只有 32 字节, 不含 Report ID

于是得到下面这份 Python 测试代码:

```python
import time

import hid

VID = 0x05AC
PID = 0x024F
USAGE_PAGE = 0xFF60
BATTERY_OFFSET = 3
CHECKSUM_OFFSET = 31  # 响应载荷的最后一字节(32 字节载荷, 从 0 开始)


def find_path():
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == USAGE_PAGE:
            return d["path"]
    return None


def get_battery():
    path = find_path()
    if not path:
        return None

    dev = hid.device()
    dev.open_path(path)
    dev.set_nonblocking(1)
    try:
        # 33 字节请求: Report ID(0) + 32 字节载荷
        frame = bytearray([0x00, 0x20, 0x01, 0x00] + [0x00] * 28)
        frame.append(0x00)                 # 先占位
        frame[32] = sum(frame[:32]) & 0xFF  # 校验和, 结果为 0x21
        dev.write(bytes(frame))

        # 轮询读, 最多等 200ms
        deadline = time.time() + 0.2
        while time.time() < deadline:
            res = dev.read(64, 0)
            if res and len(res) >= 32:
                cs = sum(res[:CHECKSUM_OFFSET]) & 0xFF
                if cs != res[CHECKSUM_OFFSET]:
                    print(f"[warn] 校验和异常: calc={cs:#04x}, recv={res[CHECKSUM_OFFSET]:#04x}")
                return res[BATTERY_OFFSET]
            time.sleep(0.01)
    finally:
        dev.close()

    return None


if __name__ == "__main__":
    bat = get_battery()
    if bat is None:
        print("获取电量失败")
    else:
        print(f"键盘电量: {bat}%")
```

解释几个容易踩坑的地方:

- `hid.enumerate(VID, PID)` 会把同一 VID/PID 下的所有 HID 接口都列出来, 键盘的普通键鼠接口也在其中, 必须用 `usage_page == 0xFF60` 过滤; 打开错接口的话, 写进去的私有协议包会被当成按键
- 请求包的最后一字节是校验和, 这里按 `sub_9BDC60` 的算法补上(结果就是 `0x21`), 和官方驱动发的一致
- 响应格式为 `20 01 00 [电量] ... [校验和]`, 第 4 个字节(偏移 3)是电量, 末字节是校验和; 对不上只打印提示, 不影响取值

运行后:

```bash
$ python battery.py
键盘电量: 91%
```

到这里, 不开官方驱动也能读到电量了.

## 总结

这次逆向比想象中顺利, 总结几点:

- 官方驱动没做太强的混淆, 字符串里直接残留了 `MUI::BatteryCtrl` 的符号, 顺着 `mui.dll` 就能定位到电量显示的位置
- 真正的协议在 `devicedriver.exe` 里, 借助 x32dbg 的调用栈和 IDA 的伪代码, 很快就能还原出帧格式
- 协议本质就是"发一包 33 字节请求, 收一包 32 字节响应", 用 `hidapi` 按 Usage Page 找到设备就能复现, 完全不需要驱动常驻
- 整个过程里 AI 更多是当翻译和讲解用, 定位问题还是得靠断点、栈回溯和自己动手验证

最后留一张协议速查表:

| 项目 | 值 |
| --- | --- |
| VID / PID | `0x05AC` / `0x024F` |
| Usage Page | `0xFF60` |
| 请求长度 | 33 字节(含 Report ID `0x00`) |
| 响应长度 | 32 字节(不含 Report ID) |
| 请求头 | `00 20 01 00` |
| 电量偏移 | `3` |
| 校验和 | 载荷最后一字节, 前 31 字节之和 |

当然, 这套结论只对笔者手上这把 T88 有效, 换固件或换批次都可能不灵.

---

**版权声明**：本文为原创文章，转载请注明出处。
