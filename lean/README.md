# basepoint-selfref — 基点自指解耦 (自包含 Lean 形式化项目)

> 自包含项目 (2026-08-14)。零项目依赖 (仅 mathlib 实数基础), 独立 build。
> 主题: 基点 = 自指位置 + 解耦三公理 (R1 排除 / R2 对消 / R3 分层)。

## 定理 (BasepointSelfRef.lean, 全部 0 sorry)

| 定理 | 内容 |
|---|---|
| `fixedpoint_selfref` | 固定点 = 自指位置 (f(x)=x 即自身映射自身) |
| `selfref_not_global` | 自指非全局 (f²(x)≠x 反例, 自指只在基点处) |
| `exclude_axiom` (R1) | a - a = 0 (主体排除) |
| `cancel_axiom` (R2) | (a-b)+(b-a) = 0 (方向对偶对消) |
| `layer_axiom` (R3) | a+(b+c) = (a+b)+c (层级复合) |
| `decouple_synthesis` | 三公理合成: (a-b)+(b-a)+(c-c) = 0 |
| `basepoint_selfref_decoupled` | 基点自指解耦定理 (四段合取) |

## 恒等式先验 (Z/13 枚举, 全部无反例)

- a-a = 0 ✓
- (a-b)+(b-a) = 0 ✓
- a+(b+c) = (a+b)+c ✓ (Z/13; Z/101 heap 有反例 — heap 代数需构造性分层)
- (a-b)+(b-a)+(c-c) = 0 ✓

## 构建 (宿主侧, 沙盒无网无法 fetch mathlib 缓存)

```sh
cd src/basepoint-selfref
lake build BasepointSelfRef   # 期望: Build completed successfully, 0 sorry
```

本地 mathlib: require 指向
`src/relative-recursion/formal/.lake/packages/mathlib` (绝对路径,
lakefile.lean 已配置)。

## 关联

- 猜想: 基点自指的解释是逻辑完备彻底证明的钥匙
- 定理: 任意阶任意元任意主客体逻辑完备性
- 解耦三公理: R1 排除 / R2 对消 / R3 分层 (论文 §9.8)
