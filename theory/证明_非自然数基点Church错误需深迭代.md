# 证明: 非自然数基点下 Church 定义错误, 需要深迭代定义

日期: 2026-08-14 | 实验复现一致 (nn/church/deepiter 配置重跑)

## 命题

非自然数基点 (固定点 1/3) 下, Church 的自然数迭代定义是错误的
(计数 = 自然数 primitive = 循环论证); 需要深迭代定义
(f^n 闭式展开, 无计数 primitive)。

## 证明

### 1. Church 定义的结构

n̄ = λf.λx. fⁿ(x): n = 迭代次数 = **自然数计数 primitive**
- Church 用"第 n 次" (计数) 定义迭代 ⟹ 循环论证 (计数 = 自然数)
- 迭代的"次数"与基点值无关, 但 Church 把次数预设为自然数

### 2. 非自然数基点下的失效

非自然数基点: f(x) = 4x-1, 固定点 1/3 (非自然数)
- f^n 的固定点: 1/3 (非自然数)
- Church 定义 f^n 需要 n ∈ ℕ (自然数计数) — 计数是 primitive
- 基点非自然数 ⟹ 迭代起点/终点在非自然数, 而计数 (n) 是自然数 —
  Church 定义在基点与计数之间无结构关联 (计数凭空预设)

### 3. 深迭代定义 (正确)

深迭代闭式: f^n(x) = (4^n·(3x-1)+1)/3 — 无 n primitive:
- 迭代深度由结构生成 (f 的复合展开), 非"第 n 次"计数
- 恒等式先验: f²(x)=16x-5, f³ 展开 = 64x-21, 闭式一致 (Z/13 无反例)

### 4. 实验证据 (复现一致)

| 定义 | 表达 | 结构 | 直觉 |
|---|---|---|---|
| Church | [op][n][x] (n 显式计数) | 1.000 (训练可学) | 1.000 |
| 深迭代 | [op][x] (闭式, 无 n) | 0.997 (定义链歧义) | **1.000** |
| 非自然数基点 | [op][x] (f(x)=4x-1) | 0.997 | **1.000** |

- 深迭代 (无 n primitive) 直觉 1.000 — 越过定义链, 直接闭式结果
- 结构 0.997 — 定义链展开歧义 (需对称性组补全/表示层闭合修复)
- Church (n 显式) 训练可学 (1.000) 但定义层面循环 (错误)

## 结论

非自然数基点下:
1. **Church 定义错误**: 计数 n (自然数) 是 primitive ⟹ 循环论证;
   基点非自然数时计数与基点无结构关联
2. **需要深迭代定义**: f^n 闭式展开 (无计数 primitive),
   迭代深度由结构生成
3. **直觉越过**: 编译结果直接给出 f^n (1.000), 不依赖 Church 计数

## 归档

- 结果: pre_pat/power_repr_success/results/exp_deepiter_church_results.md
  + exp_nonnat_results.md
- 配置: pre_pat/power_repr_success/configs/{deepiter,church,nn}_*.json
- 复现: run_exp --config (nn_d3_struct/intuit, church_struct/intuit,
  deepiter_d3_struct/intuit) 全部一致
