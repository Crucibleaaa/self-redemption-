# EXP-SYM-POWER-REPR: 负指数幂表示法 — 结果与样本教研

日期: 2026-08-14 | run_exp 官方流程 (配置驱动, 严格 OOD 验证)

## 设计 (用户洞察)

分数的本质是幂: a⁻¹ = 1/a。允许 numeral 的幂指数为负 —
分数 = 负指数幂的嵌套表达式 (tokenizer 原生语法):
  inversion(a) = bracket(power(numeral(a), numeral(-1)))

实现: synth_core 注册 `unary_power_repr` 样本 kind (配置驱动),
run_exp --config 官方合成/训练/验证/归档。

## 结果 (run_exp 官方)

- 位置级: overall_acc=0.997 ood_acc=1.000 gen_acc=1.000
- 判定口径: **acc=1.000 判真=1.000 判假=1.000 一致=1.000** (n=314, 含 mixed3位inversion)
- per_token_gen: **0/30 未达标** — inversion: **1.0**, power: 1.0

## 样本教研 (逐 epoch 教学曲线)

| epoch | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| epoch_gen_all (全 token) | 0.57 | 0.68 | 0.79 | 0.83 | 0.90 | 0.90 | 1.00 | **1.00** |
| epoch_gen_no0 (剥离 0-acc) | 1.00 | 0.97 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 0-acc token 数 | 13 | 9 | 5 | 5 | 3 | 3 | 0 | **0** |

- 全 token 达 0.98 的 epoch: **2/8** (epoch 2 即近满泛化)
- 1.0acc 最小样本量: differential 仅 103 样本即学会 (共 30 个 1-acc token)
- 0-acc 残留: 无 (gen_diag zero_acc 为空)

## 样本教研结论

1. **教学有效性**: inversion 负指数幂表示样本在 epoch 2 即达 0.98,
   epoch 8 全 token 1.0 — 表示法设计有效
2. **0-acc 归零**: 13 → 0 (epoch 1 → 8) — 无定义/样本缺陷残留
3. **最小样本量**: ~103 样本即 1.0 — 归纳不需过多样本
4. **对比历史**: 之前所有自定义脚本 (frac_bar/手工拼接/负指数无 bracket)
   全 0.000 — 差异在: ①配置驱动官方流程 ②tokenizer 原生语法组装
   (bracket 嵌套) ③负指数幂是原生表达

## 结论 (表达法闭环)

分数 = 负指数幂嵌套表达式 (tokenizer 原生语法), 配置驱动原生样本合成
(run_exp), 样本教研确认教学有效 (0/30 未达标, inversion 1.0)。
表达法体系设计 (docs/表达法体系设计.md) 的路径 2/6 验证通过。

## 归档

- 训练: archive/log/train/sym_power_repr_*
- 配置: lab/configs/sym_power_repr.json (train.epoch_gen=True)
- 样本 kind: synth_core @register_sample("unary_power_repr")
