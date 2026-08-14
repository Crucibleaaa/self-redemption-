# EXP-DIR-DIV: 新方向实验 (分数下的另一除法 × n元数 × 结构/直觉)

日期: 2026-08-14 | run_exp 配置驱动 (dir_div kind)

## 设计

新方向: 分数下的另一个除法 (分子分母对调的两方向):
- 方向1: a/(b/c) = a·c·recip(b)
- 方向2: a/(c/b) = a·b·recip(c)
变量:
- ndim: 提供 n元数 (方向 token dir_one/dir_two 显式) vs 不提供
- op_mode: 结构 (标准) vs 直觉 (iop)

## 结果

| 配置 | n元数 | 算符 | 判定口径 |
|---|---|---|---|
| ndim_struct | 提供 | 结构 | **1.000** |
| ndim_intuit | 提供 | 直觉 | **1.000** |
| no_ndim_struct | 不提供 | 结构 | **1.000** |
| no_ndim_intuit | 不提供 | 直觉 | **1.000** |

全部 1.000 — 新方向在提供/不提供 n元数、结构/直觉下都学会。

## 结论

1. **该新方向不需要 n元数**: 提供/不提供方向 token 无差别 (全 1.000) —
   分数除法对偶方向结构简单 (整数整除表达), 无歧义
2. **结构与直觉无差别**: 简单方向 (无自指循环) 两路皆通 —
   与 succ/translation 结论一致
3. **n元数的必要性边界**: 需要 n元数表达的方向 = 结构复杂 (含
   自指循环/非交换) 的方向; 简单方向不需要

## 原生适配 (实验暴露并修复)

- inject_dual_tokens 幂等 (同名跳过) + 全局唯一 eid (跨调用递增) —
  修复 D:dual0 重复冲突 — tokenizer 原生适配点 1 落地

## 归档

- 训练: archive/log/train/dirdiv_*_*
- 配置: lab/configs/dirdiv_*.json
- kind: synth_core @register_sample("dir_div")
