# EXP-DUAL-PATH: 直觉/结构 × numeral/算符 2×2 消融 — 结果

日期: 2026-08-14 | run_exp 配置驱动 (dual_path_repr kind, 原生 I 层注入)

## 设计

- numeral 载体: 结构 (数位序列) vs 直觉 (itoken 原子 inum_*)
- 算符载体: 结构 (标准 inversion token) vs 直觉 (iop_inversion, interface 无方程)
- 表达: inversion(a) = bracket(power(a, -1))

## 结果

| 配置 | 算符 | numeral | 判定口径 | epoch 末 | epoch_gen_all |
|---|---|---|---|---|---|
| 1 全结构 | 标准 | 数位 | 0.997 | 0.98 | 0.55 0.64 0.74 0.82 0.84 0.85 0.97 0.98 |
| 2 结构算符+直觉num | 标准 | itoken | 0.997 | 0.98 | 0.55 0.64 0.74 0.81 0.84 0.85 0.97 0.98 |
| 3 直觉算符+结构num | iop | 数位 | **1.000** | **1.00** | 0.45 0.67 0.73 0.78 0.84 0.84 0.94 **1.00** |
| 4 全直觉 | iop | itoken | **1.000** | **1.00** | 0.45 0.67 0.73 0.78 0.84 0.84 0.94 **1.00** |

## 结论 (纯实证)

1. **算符载体决定性**: 直觉算符 (iop, 无方程原子) → 判定 **1.000** +
   收敛到 1.0; 结构算符 (标准, 有定义链) → 0.997 + 0.98 (未达 1.0)
2. **numeral 载体无差别**: 结构 numeral vs 直觉 numeral 曲线相同
   (配置 2≈1, 配置 4≈3) — numeral 的直觉化不影响收敛
3. **直觉算符起点更低但收敛更干净**: 0.45 → 1.00 (vs 0.55 → 0.98)
4. **假说支持**: 直觉符号 (无方程原子算符) = 快路径 — 学习更干净
   (1.000); 结构符号 (标准算符, 定义链展开) 有残余误差 (0.997) —
   结构路径更"重"

## 原生注入 (从根上)

- _register.py: ITOKEN_REGISTRY/ITOKEN_BY_NAME + load_itokens() +
  token_eid/token_of/all_eids 查询链含 I 层
- synth_core: ensure_itokens/ensure_iops 惰性原生反馈 (合成请求 →
  tokenizer 自动注入注册)

## 归档

- 训练: archive/log/train/dual_{struct_struct,struct_intuit,intuit_struct,intuit_intuit}_*
- 配置: lab/configs/dual_*.json
- 注入: lab/exp_dual_path/inject_and_gen.py

## 推理速度与所需 token (us, 100 reps)

| 配置 | 推理所需 token | 推理速度 (us/前向) |
|---|---|---|
| 1 全结构 | 21 | 214.3 |
| 2 结构算符+直觉 num | 11 | 191.5 |
| 3 直觉算符+结构 num | 20 | 212.6 |
| 4 全直觉 | **10** | 207.1 |

结论:
- 直觉 numeral 使序列减半 (21→11, 20→10) — 推理所需 token 大幅下降
- 速度与序列长度相关 (小模型前向固定开销主导, 差异 7-23 us)
- 直觉算符 (iop) 对 token 数影响小 (21→20), 直觉 numeral 决定性
- 全直觉: 最短序列 (10 token) + 判定 1.000 无残差

## 残差分析 (per_token_gen)

| 配置 | 未达标 | 残差 token |
|---|---|---|
| 1/2 (结构算符) | 1/31 | **inversion: 0.5** (标准算符 3 位 OOD 残差) |
| 3/4 (直觉算符) | 0/31 | 无残差 |

结论: 残差 = 结构算符 (标准 inversion token) 在 OOD 的判定残差;
直觉算符 (iop) 无残差 — 直觉符号消化更干净
