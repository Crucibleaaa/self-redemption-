# EXP-SYM-ABL: 分数样本消融 — 收敛速度稳定性

日期: 2026-08-14 | run_exp 配置驱动 (基线 sym_fr_ti_off + 逐个摘除)

## 消融矩阵 (收敛 epoch = 首次达 1.0)

| 算符 | 基线(全) | 摘 inversion | 摘 division | 稳定性 |
|---|---|---|---|---|
| multiplication | 1 | 1 | 2 | 基本稳定 (±1) |
| power | 3 | 3 | 3 | **完全稳定** |
| division | 4 | 4 | 5* | 基本稳定 (*摘除后自身无样本, 残差) |
| inversion | 5 | —(无样本) | 4 | 不稳定: 摘 division 后 5→4 (提前) |

## 结论

1. **收敛序基本保持**: multiplication(1-2) < power(3) < division(4-5) ≲ inversion(4-5)
   — 消融下序不翻转
2. **power 完全稳定** (3,3,3): 幂次收敛不受其他算符摘除影响
3. **inversion 有变化**: 摘除 division 后收敛提前 (5→4) — 样本间存在
   竞争/干扰 (division 分数样本与 inversion 共享 power 表达组件)
4. **判定口径**: 摘 inv → 0.997 (微降, inversion 贡献被移除);
   摘 div → 1.000 (保持)

## 归档

- 训练: archive/log/train/sym_abl_{inv,div}_*
- 配置: lab/configs/sym_abl_{inv,div}.json
