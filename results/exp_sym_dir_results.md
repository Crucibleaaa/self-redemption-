# EXP-SYM-DIR (run_exp 官方流程): 对称方向训练好坏对比 — 结果记录

日期: 2026-08-14 | 全量训练 (fold_num_v5 基类) + run_exp 官方合成/验证/归档

## 重要修正

之前自定义脚本 (Judge/train_seq 手动调用) 结果全部 0.000 是**脚本流程
问题** (样本组装/训练调用与官方不一致), 非模型问题。
改用 run_exp --config 官方流程后结果完全改变。

## 结果 (判定口径 = 末尾真值, 可信)

| 配置 | 对称方向 | 判定口径 acc | 判真 | 判假 | 一致 | OOD |
|---|---|---|---|---|---|---|
| sym_fwd (succ+translation) | 双前向 | **1.000** | 1.000 | 1.000 | 1.000 | 1.000 (mixed3位 succ/translation) |
| sym_rev (neg) | 对合 | **0.763** | 0.773 | 0.754 | 0.981 | 0.981 (mixed3位 neg) |
| sym_pair (succ+neg) | 前向+对合 | **0.813** | 0.821 | 0.806 | 0.985 | 0.986 |
| sym_full (succ+translation+neg+inversion) | 混合 | **1.000** | 1.000 | 1.000 | 1.000 | 1.000 |

## 结论 (对称方向训练好坏)

1. **前向可学**: succ/translation (前向) 判定口径 1.000, 3 位外推 1.000 —
   无损泛化达成
2. **对合难**: neg (取反, 对合) 单独 0.763 — 显著差于前向
3. **混合恢复**: 全组混合 (succ+translation+neg+inversion) 1.000 —
   比 neg 单独 (0.763) 和 succ+neg 对 (0.813) 都好 — 样本/结构多样性
   帮助学习
4. **非对称**: 对称设计 (前向 vs 对合) 训练好坏不同 — 前向 1.000,
   对合 0.763; 但混合可恢复 — 差异可被结构多样性补偿

## 归档

- 训练: archive/log/train/sym_{fwd,rev,pair,full}_*
- 配置: lab/configs/sym_*.json
- 流程: lab.run_exp --config (官方合成/训练/验证/归档)
