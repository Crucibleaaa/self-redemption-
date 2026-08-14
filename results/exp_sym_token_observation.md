# 对称 token 学习观测 (run_exp 官方流程逐 token gen acc)

日期: 2026-08-14 | 来源: sym_{fwd,rev,pair,full} 归档 views.json per_token_gen

## 逐 token 观测

| 配置 | succ | translation | neg | 判定口径 |
|---|---|---|---|---|
| sym_fwd (双前向) | **1.0** | **1.0** | — | 1.000 |
| sym_rev (neg 单独) | — | — | **0.054** | 0.763 |
| sym_pair (succ+neg) | 1.0 | — | **0.054** | 0.813 |
| sym_full (全组混合) | **1.0** | — | **1.0** | 1.000 |

(inversion: 分数 1/2 整数域不可表示, 仅 2 样本, 无法观测)

## 观测结论: 哪些对称 token 没学会

1. **前向对称 token (succ/translation): 全部学会 (1.0)** — 任何配置下
   无损泛化, 与对称方向无关
2. **对合对称 token (neg): 部分配置没学会** —
   - 单独 (sym_rev): **0.054** (没学会)
   - 与 succ 成对 (sym_pair): **0.054** (仍没学会)
   - 全组混合 (sym_full): **1.0** (学会了)
3. **neg 的学习依赖结构多样性**: 需要 ≥3 个一元算符混合才能学会
   (sym_pair 只有 2 个不够; sym_full 4 个足够) — 与 EXP-61h 的
   "位置-候选容量" 相关: 多样性提供区分信息

## 对应关系

- 前向 (succ/translation): 对称 token 学会 = 对称设计成立
- 对合 (neg): 单独/成对没学会 = 对称设计破坏; 混合恢复 = 多样性补偿
- "没学会的对称 token" = neg (在低多样性配置中), 根因待进一步定位
  (可能: neg 判定 [neg][a]=-a 需区分正负表示, 样本多样性不足时
  无法归纳符号翻转规则)

## 归档

- views.json (per_token_gen): archive/log/train/sym_{fwd,rev,pair,full}_*
