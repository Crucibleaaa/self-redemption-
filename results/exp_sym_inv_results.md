# EXP-SYM-INV: 实数轴不对称算符的缺乏结构现象复现 — 结果记录

日期: 2026-08-14 | run_exp 官方流程

## 理论预测 (symmetry_real_complex_audit.md)

ℝ 上不对称的对称性 (反演/旋转/幂/对数) = 需要升维才能闭合 —
预期: 在实数轴表示下训练差 (缺乏结构 → 训练不稳)。

## 实验

- 配置: fold_num_v5 全量 + unary_judge inversion (hi=99)
- inversion (反演): 分数 1/2 不可表示 → 仅 2 样本 = **极端缺乏结构**
- 对照组: sym_fwd (succ/translation, 38 样本, ℝ 对称)

## 结果

| 算符 | ℝ 对称性 | 训练样本 | token gen acc |
|---|---|---|---|
| succ | 对称 (平移) | 38 | **1.0** |
| translation | 对称 (平移) | 38 | **1.0** |
| neg | 对称 (反射, 低多样性) | 38 | 0.054 (单独) / 1.0 (混合) |
| **inversion** | **不对称 (0 奇异, 分数)** | **2** | **0.0** |

sym_inv: per_token_gen 未达标 **1/30 = inversion: 0.0** (其余 29 token 全 1.0)

## 结论

1. **现象复现**: 实数轴上缺乏结构的对称性算符 (inversion, 反演) 训练后
   token gen acc = **0.0** — 比 ℝ 对称算符 (succ/translation 1.0) 显著差,
   训练不好 — 与理论预测一致
2. **根因链**: ℝ 上 0 无逆 (反演奇异) → 分数不可表示 → 样本仅 2 →
   缺乏结构 → 学不会 (0.0)
3. **唯一未达标 token**: 30 个 token 中仅 inversion 0.0 — 定位精确,
   非全局问题
4. **对照**: 相同配置下 succ/translation (ℝ 对称) 1.0 — 结构充足
   则对称算符学会

## 理论确认

"ℝ 上不对称的对称性 = 需要升维才能闭合" 在 token 训练中表现为:
缺乏结构 → 训练不稳 → gen acc 0.0。预测: 若升维 (复数/分数表示)
提供结构, inversion 应恢复 (待验证)。

## 归档

- 训练: archive/log/train/sym_inv_*
- 配置: lab/configs/sym_inv.json
