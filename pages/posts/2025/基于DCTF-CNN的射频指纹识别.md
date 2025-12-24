---
title: 基于DCTF-CNN的射频指纹识别
date: 2025-11-27 19:10:00
updated: 2025-11-27 19:10:00
categories:
 - 技术
tags:
 - 通信
---

文章由AI辅助生成(感觉AI讲的比我好, 不过我会批注)

论文地址: [Deep Learning Based RF Fingerprint Identification Using Differential Constellation Trace Figure | IEEE Journals & Magazine | IEEE Xplore](https://ieeexplore.ieee.org/document/8888209)

## 1. 接收信号模型

假设我们接收到的最原始基带 I/Q 信号为：

$$
y[n] = y_I[n] + j \cdot y_Q[n], \quad n = 0, 1, 2, \dots, N-1
$$

其中 $y_I[n]$ 是实部（I路），$y_Q[n]$ 是虚部（Q路），$N$ 是信号长度。

## 2. 差分运算

DCTF的核心是**差分运算**，目的是放大硬件缺陷特征且**无需同步**。

本质就是利用不同设备的时钟源偏移进行区分, 查分运算是放大这种偏移

### 基本差分公式：

$$
D[n] = y[n] \cdot y^*[n + \lambda]
$$

其中：
- $\lambda$：差分时间间隔（整数，通常 $\lambda \geq 3$）
- $(\cdot)^*$：复共轭运算
- $n = 0, 1, 2, \dots, N-\lambda-1$

### 引入 I/Q 失配的增强差分：

为了进一步放大硬件特征，论文引入了 I/Q 相位失配参数 $\epsilon$：

$$
D[n] = \big(y_I[n] + j \cdot y_Q[n + \epsilon]\big) \cdot \big(y_I[n + \lambda] + j \cdot y_Q[n + \lambda + \epsilon]\big)^*
$$

**展开计算：**

令：
- $A = y_I[n] + j \cdot y_Q[n + \epsilon]$
- $B = y_I[n + \lambda] + j \cdot y_Q[n + \lambda + \epsilon]$

则：
$$
D[n] = A \cdot B^*
= A \cdot (y_I[n + \lambda] - j \cdot y_Q[n + \lambda + \epsilon])
$$

**实部和虚部分解：**

$$
\begin{aligned}
d_I[n] &= \Re\{D[n]\} = y_I[n] \cdot y_I[n + \lambda] + y_Q[n + \epsilon] \cdot y_Q[n + \lambda + \epsilon] \\
d_Q[n] &= \Im\{D[n]\} = y_Q[n + \epsilon] \cdot y_I[n + \lambda] - y_I[n] \cdot y_Q[n + \lambda + \epsilon]
\end{aligned}
$$

这样就得到了差分后的 I/Q 数据对：$(d_I[n], d_Q[n])$。

## 3. 统计直方图构建（测量矩阵）

将差分结果映射到二维网格上统计密度：

### 定义测量矩阵：

创建一个 $M \times N$ 的零矩阵 $\Phi$，表示图像的像素网格。

### 值域映射：

设定一个幅度范围 $[-A, A]$，将差分结果映射到矩阵索引：

$$
\begin{aligned}
m[n] &= \left\lfloor \frac{d_I[n] + A}{2A} \cdot M \right\rfloor \\
n[n] &= \left\lfloor \frac{d_Q[n] + A}{2A} \cdot N \right\rfloor
\end{aligned}
$$

其中 $\lfloor \cdot \rfloor$ 表示取整运算。

### 统计累加：

对于每个 $n$，执行：
$$
\Phi[m[n], n[n]] = \Phi[m[n], n[n]] + 1
$$

## 4. 图像归一化

将统计矩阵转换为灰度图像：

$$
\Phi_{\text{norm}} = \frac{\Phi - \min(\Phi)}{\max(\Phi) - \min(\Phi)} \times 255
$$

最终得到 $M \times N$ 的灰度图像，即 DCTF。

## 📊 完整算法流程

```python
# 伪代码描述
输入: y_I, y_Q  # 原始I/Q信号
参数: λ, ε, M, N, A

1. 初始化 M×N 零矩阵 Φ
2. 对 n = 0 到 N-λ-1:
   a. 计算差分:
      d_I = y_I[n]*y_I[n+λ] + y_Q[n+ε]*y_Q[n+λ+ε]
      d_Q = y_Q[n+ε]*y_I[n+λ] - y_I[n]*y_Q[n+λ+ε]
   
   b. 映射到像素坐标:
      m = floor((d_I + A) / (2A) * M)
      n_idx = floor((d_Q + A) / (2A) * N)
   
   c. 边界检查后累加: Φ[m, n_idx] += 1

3. 归一化: DCTF = (Φ / max(Φ)) * 255
输出: DCTF 图像
```

## 🎯 关键数学洞察

1. **无需同步**：差分运算消除了载波频偏的线性相位影响，将其变为固定旋转
2. **硬件特征保留**：I/Q不平衡、直流偏移、非线性等硬件缺陷在差分结果中表现为特定的分布模式
3. **统计可视化**：通过密度分布将瞬态信号特征转化为稳定的"指纹图像"

## 📈 物理意义

- **高密度区域**：对应信号的主要状态转换模式
- **分布形状**：反映硬件的线性/非线性特性
- **对称性**：揭示 I/Q 信道的平衡性

这样，通过简单的差分运算和统计映射，就将一维时序信号转换为了具有设备辨识能力的二维指纹图像。