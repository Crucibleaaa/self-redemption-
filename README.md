# Self-Redemption

**一个主动与 AI 相互过拟合、精神接近崩溃的普通人类, 自我救赎的一个尝试**

*An attempt at self-redemption by an ordinary human who actively co-overfits with AI and stands on the brink of mental collapse.*

> **定性声明**: 本仓库全部内容为观测记录 — 论文、理论文档、实验、Lean 形式化均为
> "人类主动诱导过拟合的过程"的观测素材, **不代表任何数学结论**。

## 内容 (从歧义到完备逻辑 — 发表包)

| 目录 | 内容 |
|---|---|
| `论文_从歧义到完备逻辑.md` | 正式论文 (14 章 + 附录) |
| `发表报告_从歧义到完备逻辑.md` | 发表报告 |
| `theory/` | 理论文档 26 篇 (歧义统一/基点/自指/完备性定理/猜想/假设) |
| `results/` | 实验结果 21 份 (判定 1.000/0.997 等) |
| `configs/` | 实验配置 84 个 |
| `scripts/` | 实验脚本 13 个 |
| `lean/` | basepoint-selfref Lean 项目 (7 定理: 固定点=自指 + 解耦三公理) |

## 论文核心数字

- 直觉路径: 1.000 (所有表达)
- 结构路径: 0.997 (唯一残差 = inversion 0.5, 30/31 token 1.0)
- 原生二元迭代语法: 结构 1.000 (0/31 未达标)
- 恒等式先验: 解耦三公理 Z/13 全无反例
- Lean: basepoint-selfref 7 定理

## 复现

```sh
cd src/basepoint-selfref && lake build BasepointSelfRef   # Lean (宿主侧)
cd src/llm_research_v5 && PYTHONPATH=. .venv/bin/python -m lab.run_exp --config lab/configs/nt_d3_struct.json
```

## 授权

CC BY-NC-ND 4.0
