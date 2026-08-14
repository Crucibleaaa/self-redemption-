# EXP-SYM-COMP: token 收敛竞争实证 — inversion/division 单独 vs 合训

日期: 2026-08-14 | run_exp 配置驱动 (纯实证, 无 Lean)

## 设计

- inv 单独: fold_num_v5 + 仅 unary_power_repr inversion
- div 单独: fold_num_v5 + 仅 binary_power_repr division
- 合训: fold_num_v5 + 两者 (基线 sym_fr_ti_off)
- 观测: 各算符收敛 epoch (首次达 1.0)

## 结果 (收敛 epoch)

| 条件 | inversion | division |
|---|---|---|
| inversion 单独 | **4** | — |
| division 单独 | — | **4** |
| inv+div 合训 | **5** | **4** |

## 竞争判定

- **inversion: 单独 4 → 合训 5 = 竞争 (合训慢)** ✓
- division: 单独 4 → 合训 4 = 无竞争
- **单向竞争**: division 拖慢 inversion, inversion 不影响 division

## 猜想 (CONJECTURE, 纯实证)

**token 收敛竞争意味着二者存在不同的内部逻辑结构, 导致结果无法
(快速) 收敛。**

实证支撑:
1. inversion 与 division 共享 power 组件 (分数表达都含 power(x,-1))
2. 但内部逻辑不同: inversion 中 power 是**结果本体**; division 中
   power 是**中间组件** (mul(a, power(b,-1)))
3. 合训时 division 的二元上下文占用 power 表示 → inversion 收敛变慢
   (4→5) — 竞争 = 共享组件被不同内部逻辑使用
4. 单向性: division (二元, power 内嵌) 吸收共享表示, inversion
   (一元, power 直接) 受扰 — 不对称竞争

预测 (可证伪): 分离表示 (inversion 用独立组件而非共享 power) 应消除
竞争 (inversion 合训收敛回到 4); 若竞争加剧 (更多共享算符) 可能到
"无法收敛" (epoch 内不达 1.0)。

## 归档

- 训练: archive/log/train/sym_comp_{inv_only,div_only}_*
- 配置: lab/configs/sym_comp_{inv_only,div_only}.json
- 基线: sym_fr_ti_off (合训)
