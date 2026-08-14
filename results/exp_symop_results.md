# EXP-SYMOP: 对称算子直觉/结构对比 (对称性直觉路径假说验证)

日期: 2026-08-14 | run_exp 配置驱动 (unary_plain kind)

## 设计

对称算子 (neg/translation/succ) × 算符 (struct 标准 / intuit iop 原子),
验证"对称性也是直觉路径"假说。

## 结果

| 算子 | 结构判定 | 直觉判定 | Δ |
|---|---|---|---|
| neg | 0.994 | 0.997 | +0.003 |
| translation | 0.994 | 0.997 | +0.003 |
| succ | 0.996 | 0.998 | +0.002 |

per_token_gen: neg/translation/succ 自身 token 无残差 (两种模式都学会);
**持续未达标 = inversion**: struct 0.0 / intuit 0.5 (与本次算子无关,
来自验证集的其他 token)

## 结论

1. **简单对称算子 (neg/translation/succ) 结构版不歧义**: 定义链简单
   (取反/平移/后继, 无自指循环), 结构 vs 直觉差别小 (+0.003)
2. **假说边界**: "对称性是直觉路径"适用**有自指循环的对称**
   (反演/对合递归); 简单对称无循环 → 结构不歧义
3. **inversion 持续歧义** (struct 0.0 / intuit 0.5): 定义链含自指循环
   (recip∘neg 递归) — 支撑"基点处自指循环 → 歧义"; 但 intuit 0.5
   说明直觉版也未完全越过 (与 iop_inversion 的 1.0 不同 —
   此验证集 inversion 与训练样本的 iop 无直接对应)

## 意义

- 歧义 = 自指循环结构的指纹 (有循环 → 歧义, 无循环 → 干净)
- 对称性直觉路径假说: 部分成立 (简单对称两路皆通),
  边界 = 自指循环 (反演类)

## 归档

- 训练: archive/log/train/symop_*_*
- 配置: lab/configs/symop_*.json
- kind: synth_core @register_sample("unary_plain")
