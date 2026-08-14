# EXP-SG: 对称性组补全实验 (结构算符设计方法 2 验证)

日期: 2026-08-14 | run_exp 配置驱动 (recip_aut kind)

## 设计

- sg_baseline: 结构算符 (标准 inversion) + 分数样本 (基线)
- sg_aut: 基线 + 乘法自同构样本 (recip(x·y) = recip(x)·recip(y))
- sg_aut_mix: sg_aut + 直觉算符样本

## 结果

| 配置 | 判定口径 | per_token 未达标 | inversion token |
|---|---|---|---|
| sg_baseline | 0.997 | 1/31 | **0.5** |
| sg_aut | 0.997 | **0/31** | **1.0** ✓ |
| sg_aut_mix | 1.000 | 0/31 | 1.0 |

## 结论

1. **对称性组补全 (方法 2) 有效**: 乘法自同构样本使结构算符
   inversion token 从 **0.5 → 1.0** (per_token_gen 0/31 未达标)
   — 补全二阶性质 (自同构) 修复结构算符的 OOD 泛化
2. **判定口径残余 0.997**: sg_aut 整体判定 0.997 (判真 0.994) —
   残余 0.6% 在混合 OOD 的其他维度 (非 inversion token)
3. **混合 (含直觉) 1.000**: 直觉算符参与时整体完美
4. **方法 2 验证成立**: 结构算符设计 = 补全对称性组 (含二阶性质),
   token 级 OOD 恢复; 整体判定残余需进一步定位 (其他算符混合维度)

## 意义

- 二阶性质 (乘法自同构) 是 reciprocal 定义链缺失的 — 补全后
  结构算符 token 级完美 (1.0) — 支持"不完备 = 结构错误"理论
- 判定口径 0.997 残余: 非 inversion 问题, 是整体 OOD 混合的其他
  算符维度 (待分解)

## 归档

- 训练: archive/log/train/sg_{baseline,aut,aut_mix}_*
- 配置: lab/configs/sg_*.json
- kind: synth_core @register_sample("recip_aut")
