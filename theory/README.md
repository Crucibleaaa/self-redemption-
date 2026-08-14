
## 完整归档 (2026-08-14 补充)

```
power_repr_success/
├── scripts/   13 个实验脚本 (exp_sym_* / exp_repr* / exp_dual_path / exp_neg_*)
├── configs/   32 个 run_exp 配置 (sym_* / dual_* / fp_* / repr_*)
├── results/   11 份实验结果 (判定口径/逐 token/消融/固定点/速度)
├── 理论补强_直觉路径无关与结构错误.md
├── 表示层矩阵_对称性组假说.md
├── 固定点实验_原点统一理论.md
├── 对称中心审计_复平面表现.md
└── exp_sym_power_repr_results.md / exp_dual_path_results.md / sym_power_repr.json
```

复现: 脚本放入 src/llm_research_v5/lab/exp_*/ 对应目录, 配置放入
lab/configs/, 用 run_exp --config 官方流程执行 (PYTHONPATH=src/llm_research_v5).

## 完整归档 (2026-08-14 终版)

```
power_repr_success/
├── scripts/    13 个实验脚本
├── configs/    72 个 run_exp 配置 (全实验矩阵)
├── results/    20 份实验结果 (判定口径/逐token/消融/固定点/速度/基点)
├── 理论补强_直觉路径无关与结构错误.md
├── 表示层矩阵_对称性组假说.md
├── 固定点实验_原点统一理论.md
├── 对称中心审计_复平面表现.md
├── 假说_基点漂移实验证明.md
├── 观点_直觉可用不等于结构正确.md
├── 观点_基点恢复性实验.md
├── 观点_基点恢复需加轴.md
├── 结论_模型认知空间非物理空间.md
├── 二阶逻辑视角_结构算符设计方法.md
├── tokenizer原生适配需求.md
├── 证明_非自然数基点Church错误需深迭代.md
└── 修正_复平面基点i与Church错误证明.md
```

复现: 脚本放入 src/llm_research_v5/lab/exp_*/, 配置放入 lab/configs/,
run_exp --config 官方流程执行。
关键复现 (非自然数基点 Church vs 深迭代): nn_d3_struct/intuit,
church_struct/intuit, deepiter_d3_struct/intuit — 结果全部一致
(struct 0.997 / intuit 1.000; church 1.000 训练可学但定义循环)。
