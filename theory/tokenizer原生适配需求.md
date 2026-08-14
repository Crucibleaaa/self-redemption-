# Tokenizer 原生适配需求 (自造算符实验暴露)

日期: 2026-08-14

## 结论

自造算符实验 (alien_op, 不在已知数学空间) 暴露 tokenizer 需要
**原生适配** — 当前实验注入机制 (inject_temp/inject_dual_tokens)
不足以支撑动态/自造算符的原生使用。

## 实验暴露的 3 个适配点

### 1. 动态概念注册 (eid 冲突)

- 问题: inject_dual_tokens 固定 eid 前缀 "D:dual{N}", 多次调用重复
  注入 → ValueError: D:dual0 eid 重复 (alien_2d 报错)
- 适配: 原生注册机制 — 动态概念分配唯一 eid, 幂等注入
  (重复注入同名 → 覆盖而非冲突)

### 2. 无规则算符的组装 (算子被吞)

- 问题: assemble_seq(alien, [arg]) 对 rules=[] 的 unary_connective
  组装吞掉算子 (prop 输出无 alien token) — 需手工拼接
- 适配: 组装器原生支持无规则原子算符 (arrange 驱动, 非 rules 驱动)

### 3. 自造算符求值 (查表支撑)

- 问题: alien 求值需合成器内手工查表 (f[n] 随机映射),
  无 tokenizer 原生求值路径
- 适配: 原生 interface/查表求值 (definition form=interface
  或查表语义), 合成器经 api.eval_op 统一求值

## 原生适配方案

| 适配点 | 方案 |
|---|---|
| 注册 | token_index 动态 eid 分配 + 幂等注入 (原生概念注册 API) |
| 组装 | arrange 驱动组装 (无 rules 原子算符不被吞) |
| 求值 | interface 语义求值 (查表), 与引擎统一路径 |

## 意义

- 自造算符 (不在已知数学空间) 是检验 tokenizer 原生能力的探针:
  若原生支持动态算符注册/组装/求值, 则实验可配置驱动完全原生
- 全维度可达前提 (前结论): 自造算符加轴实验 (alien_2d) 需在
  原生适配完成后重跑
