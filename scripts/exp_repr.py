"""EXP-REPR: 实数轴多种表达法设计 (分数表示法诊断)

用户洞察 (2026-08-14): fraction 的语法不是 op (算子), 而是一种
**表示法** (representation, 像 numeral 一样是值的编码)。

设计: 实数轴上多种表达法
1. 整数表示法: numeral = sign_pos + 数位 (已有)
2. 分数表示法: [num][frac_bar][den] — frac_bar 是表示法标记 (非算子)
3. (预留) 小数表示法 / 混合数表示法

诊断: 纯表示法结构可学性 (无 fold_num_v5 干扰):
- [frac_bar][1][a] 作为 inversion(a) 的结果表示
- 若可学 ⟹ 表示法设计成立, 再入全量训练

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_repr.exp_repr
"""
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab.synth_core as sc
from lab.synth_core import inject_dual_tokens, make_sample, numeral_of
from lab.judge import judge_sequence, Judge
from tokenizer import api
from train import train_seq

# 表示法 token (非算子): frac_bar = 分数表示法标记 (atom, 无方程)
REPR_DEFNS = {
    "frac_bar": {"form": "explicit", "arrange": "atom", "policy": "equations",
                 "rules": [], "references": []},
}


def inversion_repr_samples(vals):
    """inversion(a) = [numeral(1)][frac_bar][numeral(a)] (分数表示法)."""
    inv = api.eid_by_name("inversion")
    bar = api.eid_by_name("frac_bar")
    samples = []
    for a in vals:
        prop = api.assemble_seq(inv, [numeral_of(a)])
        result = [*numeral_of(1), bar, *numeral_of(a)]
        seq = judge_sequence([*prop, api.role_token("equals"), *result], True)
        samples.append(make_sample(seq, True, 1))
        bad = [*numeral_of(1), bar, *numeral_of(a + 1)]
        seq_b = judge_sequence([*prop, api.role_token("equals"), *bad], False)
        samples.append(make_sample(seq_b, False, 1))
    return samples


def run():
    torch.manual_seed(0)
    eids = inject_dual_tokens(REPR_DEFNS)
    bar = eids["frac_bar"]
    print(f"注入表示法 token frac_bar: {bar}")

    # 1. 纯结构诊断 (无 fold_num_v5): 表示法可学性
    train_vals = list(range(1, 100))
    s = inversion_repr_samples(train_vals)
    print(f"纯表示法样本: {len(s)} (1-99 全枚举)")
    res = train_seq(s, epochs=8, dim=64, num_layers=2, seed=0,
                    token="repr_frac_alone", batch_size=512)
    j = Judge(dim=64, num_layers=2)
    j.model = res["model"].cpu()
    tr_acc = j.evaluate(s)["acc"]
    print(f"纯表示法训练内 acc: {tr_acc:.3f}")

    # 2. 外推 (2 位分母, 训练外)
    ext = inversion_repr_samples([100, 123])
    print(f"2-3 位外推 acc: {j.evaluate(ext)['acc']:.3f}")

    # 3. 全量训练 (fold_num_v5 + 表示法样本)
    cfg = json_load = __import__("json").load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    cfg["name"] = "sym_repr"
    keep = [s for s in cfg["synth"]["samples"] if s.get("kind") != "unary_judge"]
    cfg["synth"]["samples"] = keep
    from lab.run_exp import build_samples, _make_verify_fn, _judge_eval
    base, _ = build_samples(cfg, 0)
    full = base + s
    print(f"全量训练样本: {len(full)} (含表示法 {len(s)})")
    res2 = train_seq(full, epochs=8, dim=64, num_layers=2, seed=0,
                     token="sym_repr", batch_size=512)
    print(f"train acc={res2['acc']:.4f} valid={res2['valid_acc']:.4f}")
    j2 = Judge(dim=64, num_layers=2)
    j2.model = res2["model"].cpu()
    print(f"全量下 inversion 表示法训练内 acc: {j2.evaluate(s)['acc']:.3f}")
    print(f"全量下 2-3 位外推 acc: {j2.evaluate(ext)['acc']:.3f}")


if __name__ == "__main__":
    run()
