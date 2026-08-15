# 逐 token 设计矩阵 (68 运算 token 全量)

> 2026-08-15 定稿。用户纪律: 一个 token 的对比实验必须完成一次 0 OOD + 一次 1 OOD (I7ag) 才可宣称;
> token 级报告 (样本全对 + token 对/总数 + 位置正确率), 0 错 token 为成功标准 (I7af)。

## 1. 口径

- 运算 token = arrange ∈ {application, binary_connective, unary_connective} 的概念 token, 共 **68 个** (9 逻辑 + 59 数字域)
- 元数: signature.params 为准 (操作数); rules arg 槽位含**定律自由变量** (如 power 幂律 rule3 引 arg:2) — 槽位数 ≥ 签名元数不是缺陷
- 求值探测: eval_op 全路径 (token 往返), 参数按签名元数

## 2. 本次诊断修复 (8 个原"不可求值" token 定稿)

| token | eid | 签名 | 诊断 | 处置 | 定稿状态 |
|---|---|---|---|---|---|
| power | D:154 | 3→**2** | 签名 3 参但 eval_power 2 参 (数学 a^b 二元) | 修签名 2 参 | ✅ 可求值: 2^3=8, 3^2=9 |
| logarithm | D:162 | 3→**2** | 签名 3 参但 eval_log 2 参 (log_a(x) 二元) | 修签名 2 参 | ✅ 可求值: log2(8)=3, log3(9)=2 |
| exp | D:166 | 2→**1** | 签名 2 参但 eval_exp 1 参 (e^x 一元) | 修签名 1 参; 指数加性律规则保留 (定律验证 2/2) | ✅ exp(0)=1; 非平凡值域超表示 (exp(2)=7.39 正确拒绝) |
| parallel_sum | D:158 | 2 | 原诊断传参错 (审计算法 1/(1/a+1/b) 需同号正参) | — | ✅ 可求值: par(2,2)=1; 分数实例超表示 (par(2,4)=4/3) |
| integral | D:161 | 2 | 分数值域 (int(2,2)=8/3, int(1,1)=1/2) | — | ⚠️ 值域限制: 无整数实例, 超表示拒绝正确 |
| rotation | D:169 | 1 | 复数值域 (rot(x)=ix, 90° 旋转) | — | ⚠️ 值域限制: 无整数实例 (0 不动点无信息量) |
| symmetry_group | D:165 | 1 | 结果非数值 (群对象); 无求值器; 定义 rules 是性质声明 (neg=inversion∘complement 等) | — | ⛔ 结构概念: 数值不可求值, 不发明数学 |
| dummy_op | D:527 | 2 | 故意 axiomatic 无定义 (消融干扰项) | — | ✅ 设计预期: 永不可求值 |

## 3. 全矩阵 (68)

### 3.1 逻辑域 (9) — 真值判定类

| token | eid | 元数 | 求值 | 两极状态 |
|---|---|---|---|---|
| logical_and | D:108 | 2 | 真值表 ✓ | 未做 |
| logical_or | D:109 | 2 | 真值表 ✓ | 未做 |
| logical_not | D:110 | 1 | 真值表 ✓ | 未做 |
| logical_imply | D:111 | 2 | 真值表 ✓ | 未做 |
| logical_iff | D:112 | 2 | 真值表 ✓ | 未做 |
| logical_xor | D:113 | 2 | 真值表 ✓ | 未做 |
| logical_nand | D:114 | 2 | 真值表 ✓ | 未做 |
| logical_nor | D:115 | 2 | 真值表 ✓ | 未做 |
| logical_xnor | D:116 | 2 | 真值表 ✓ | 未做 |

### 3.2 数字域 (59)

#### 3.2.1 可求值 (50)

| token | eid | 元数 | 求值样例 | 两极状态 |
|---|---|---|---|---|
| succ | D:179 | 1 | 3 | ✅ 已两极 (I7h 平移 / I7q 矩阵 / E12 桥接 0/32↔32/32) |
| pred | D:196 | 1 | 3→2 | ✅ 已两极 (I7h 同族) |
| iterate | D:167 | 2 | — | 未做 (iterate_expr 原子) |
| addition | D:100 | 2 | 2+3=5 | ✅ 已两极 (I7ae 元完备 + I7aj 结合 0 OOD) |
| subtraction | D:101 | 2 | 2-3=-1 | 未做 |
| multiplication | D:142 | 2 | 2×3=6 | ✅ 已两极 (I7ae + I7aj 分配 0 OOD) |
| power | D:154 | 2 | 2^3=8 | **本次修复** — 未做 |
| root | D:155 | 2 | root(2,2) 无理 | 未做 (值域: 无理超表示) |
| division | D:156 | 2 | 2/3 | 未做 (分数值域) |
| reciprocal | D:153 | 1 | 1/2 | 未做 (分数值域) |
| complement | D:157 | 1 | 1-2=-1 | 未做 |
| parallel_sum | D:158 | 2 | par(2,2)=1 | **本次澄清** — 未做 |
| differential | D:160 | 2 | 12 | 未做 |
| integral | D:161 | 2 | 8/3 | **值域限制** — 不可训 (无整数实例) |
| logarithm | D:162 | 2 | log2(8)=3 | **本次修复** — 未做 |
| translation | D:163 | 1 | 2+1=3 | 未做 |
| inversion | D:164 | 1 | -1/2 | 未做 (分数值域) |
| exp | D:166 | 1 | exp(0)=1 | **本次修复** — 值域限制 (除 exp(0) 全超表示, 不可训) |
| fixpoint | D:168 | 1 | 2 | 未做 |
| rotation | D:169 | 1 | 2j | **值域限制** — 不可训 (复数) |
| tetration | D:170 | 2 | 2↑↑2=4 | 未做 (超运算, 溢出风险) |
| super_root | D:171 | 2 | 1.48 | 未做 (无理值域) |
| super_log | D:172 | 2 | 1 | 未做 |
| coupled_fixpoint | D:173 | 2 | -1 | 未做 |
| scale | D:174 | 2 | 2×2²=8 | 未做 |
| recursion | D:175 | 2 | 5 | 未做 |
| modulo | D:508 | 2 | 2%4=2 | 未做 |
| num_concat | D:505 | 2 | concat(2,3)=515 | 未做 (位置定权) |
| fold | D:506 | 2 | 2 | 未做 |
| unfold | D:507 | 3 | 14 | 未做 |
| ring_addition | D:509 | 2 | 2+3=5 | 未做 |
| basepoint_move | D:510 | 2 | -1 | 未做 |
| teleport | D:511 | 2 | 5 | 未做 |
| involution | D:512 | 1 | 0 | 未做 |
| orthogonal | D:513 | 2 | 0 | 未做 |
| self_inverse_gate | D:514 | 1 | 0 | 未做 |
| hadamard | D:515 | 1 | 0 | 未做 |
| cnot | D:516 | 3 | 2 | 未做 |
| toffoli | D:517 | 4 | 2 | 未做 |
| qft | D:518 | 2 | 2 | 未做 |
| period_axis | D:519 | 2 | 2 | 未做 |
| measure | D:520 | 2 | 2 | 未做 |
| time_reversal | D:521 | 1 | -2 | 未做 |
| summon | D:522 | 3 | 14 | 未做 |
| flip | D:523 | 2 | 0 | 未做 |
| storage_is_computation | D:524 | 3 | 1 | 未做 |
| midpoint | D:525 | 2 | 5 | 单极 (R163 结论 600 样本 1.000, 无 0 OOD) |
| relpos | D:526 | 2 | 1 | ✅ 已两极 (I7ae 主客体 1 OOD + I7ah 轴 b 0 OOD) |
| carry | D:180 | — | 4 | 内部概念 (进位, digit 层) |
| congruence | D:181 | — | 4 | 内部概念 (同余, digit 层) |

#### 3.2.2 内部概念 (3) — digit_eval 路径, 非 eval_op 数值路径

| token | eid | 说明 |
|---|---|---|
| digit_add | D:151 | 数位加法 (digit 层内部) |
| numeral_value | D:148 | 数位定值 (digit 层内部) |
| place_contribution | D:147 | 位置贡献 (digit 层内部) |

#### 3.2.3 结构概念 (5) — 语法角色/结构声明, 数值不可求值

| token | eid | 说明 |
|---|---|---|
| symmetry_group | D:165 | 群对象 (结果非数值); 本次定稿 |
| question | D:188 | 问题标记 (语法) |
| derive | D:193 | 派生声明 (语法) |
| cardinality | D:146 | 基数 (计数结构, 禁 Nat 预设) |
| is_true | D:137 | 真值判定 (判定谓词非运算) |

#### 3.2.4 故意 axiomatic (1)

| token | eid | 说明 |
|---|---|---|
| dummy_op | D:527 | 消融干扰项, 永不可求值 (设计预期) |

## 4. 两极对比状态汇总

- **已两极 (宣称合规, 5 token)**: succ, pred, addition, multiplication, relpos
  (另 neg 经 I7ai 对合两极; 完备性三维度 I7ah/I7ae 覆盖 succ/addition/multiplication/relpos)
- **单极 (1)**: midpoint (600 样本 1.000 无 0 OOD 对照 — 需补: 无运算训练对照态)
- **本次修复后待两极 (2)**: power, logarithm (修后已可求值, 需 1 OOD + 0 OOD 各一次)
- **值域限制不可训 (5)**: integral, rotation, exp, root, super_root, division, reciprocal, inversion (分数/无理/复数值域 — 设计上样本不可表示, 两极实验不适用)
- **未做 (53)**: 其余全部

## 5. 下一步

1. power/logarithm 两极对比 (修后第一优先 — 定义准确后按 I7ag 补齐)
2. midpoint 补 0 OOD 对照
3. 逻辑域 9 token 两极 (真值表 OOD: 组合留出 1 OOD + 缺组合 0 OOD)
4. 迭代链上层 (tetration/root/division 族) 按值域限制设计可训子集
