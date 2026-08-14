# EXP-SYM-FR-CURVE: 分数表示下逐 token 收敛对比 (有/无平移反演)

日期: 2026-08-14 | run_exp 配置驱动 (sym_fr_ti_on / sym_fr_ti_off)

## 配置

- 有平移反演 (ti_on): fold_num_v5 + unary_judge{neg,translation,inversion}
  + 分数样本 (inversion⁻¹ / division / power⁻¹)
- 无平移反演 (ti_off): 同上但**无 unary_judge** (无 translation/inversion 原生样本)
- 两者 train.epoch_gen=True, 同 seed/epochs=8

## 逐 token 收敛 (首次达 1.0 的 epoch)

| 算符 | 有平移反演 | 无平移反演 | 曲线 (0/1 序列) |
|---|---|---|---|
| multiplication | **epoch 1** | epoch 1 | [0 1 1 1 1 1 1 1] |
| power | epoch 3 | epoch 3 | [0 0 0 1 1 1 1 1] |
| division | epoch 4 | epoch 4 | [0 0 0 0 1 1 1 1] |
| inversion | **epoch 5** | epoch 5 | [0 0 0 0 0 1 1 1] |

(总体: 两配置 epoch_gen_all 0.55→1.00, 0-acc 14→0, 判定口径 1.000)

## 结论

1. **有/无平移反演无差别**: 平移反演组 (unary_judge translation/inversion)
   的有无不影响各算符收敛 — 收敛完全一致
2. **收敛序 (小→大)**: multiplication (1) < power (3) < division (4)
   < inversion (5)
3. **inversion 收敛最大 (最慢)**: 与 ℝ 上最不对称 (0 奇异, 分数表示)
   一致 — 需要最多 epoch 教学
4. **multiplication 收敛最小 (最快)**: 与 ℝ 上对称 (缩放群) 一致

## 归档

- 训练: archive/log/train/sym_fr_ti_on_* / sym_fr_ti_off_*
- 配置: lab/configs/sym_fr_ti_on.json / sym_fr_ti_off.json
- 样本 kind: synth_core @register_sample("unary_power_repr"/"binary_power_repr")
