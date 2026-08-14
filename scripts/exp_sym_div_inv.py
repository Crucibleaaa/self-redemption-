"""EXP-SYM-DIV-INV: 反演与除法联合训练 (共享分数结构)

假设 (2026-08-14): 反演与除法一起训练, 除法和反演总能得到相同的分数 —
  division(a, b) = fraction(a, b)
  inversion(a)   = division(1, a) = fraction(1, a)
两者共享 fraction 结构, 联合训练应互相促进 (反演是除法特例)。

设计:
1. 注入 fraction token (C 层, inject_temp)
2. 注册样本 kind:
   - binary_fraction: [division][a][b] equals fraction(a, b) (全枚举 1..99)
   - unary_fraction:  [inversion][a]   equals fraction(1, a) (全枚举 1..99)
3. 训练: fold_num_v5 + division 分数样本 + inversion 分数样本
4. 观测: inversion/division token acc + 判定口径 + 专项外推

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_sym_div_inv.exp_sym_div_inv
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab.synth_core as sc
from lab.synth_core import (register_sample, inject_dual_tokens, make_sample,
                            digits_of, numeral_of, _unary_eval)
from lab.judge import judge_sequence, Judge
from tokenizer import api
from train import train_seq

FRACTION_DEFN = {"form": "explicit", "arrange": "application",
                 "policy": "equations",
                 "rules": [{"term": ["D:102", ["self", "arg:0", "arg:1"],
                                     ["D:156", "arg:0", "arg:1"]]}],
                 "references": ["D:102", "D:156"]}


def _frac_result(num, den):
    # numeral_of 带 sign_pos 前缀 (与成功样本 nested_seq 一致)
    return api.assemble_seq(api.eid_by_name("fraction"), [numeral_of(num), numeral_of(den)])


@register_sample("unary_fraction")
def _s_unary_fraction(spec, seed):
    """inversion 分数样本: [inversion][a] equals fraction(1, a)."""
    op = api.eid_by_name(spec["op"])
    hi = spec.get("hi", 99)
    samples = []
    for a in range(1, hi + 1):
        prop = api.assemble_seq(op, [numeral_of(a)])
        seq = api.assemble_seq(api.role_token("equals"), [prop, _frac_result(1, a)])
        samples.append(make_sample(judge_sequence(seq, True), True, 1))
        bad = api.assemble_seq(api.role_token("equals"), [prop, _frac_result(1, a + 1)])
        samples.append(make_sample(judge_sequence(bad, False), False, 1))
    return samples, len(samples) // 2, len(samples) // 2


@register_sample("binary_fraction")
def _s_binary_fraction(spec, seed):
    """division 分数样本: [division][a][b] equals fraction(a, b)."""
    op = api.eid_by_name(spec["op"])
    hi = spec.get("hi", 9)
    samples = []
    for a in range(1, hi + 1):
        for b in range(1, hi + 1):
            prop = api.assemble_seq(op, [numeral_of(a), numeral_of(b)])
            seq = api.assemble_seq(api.role_token("equals"), [prop, _frac_result(a, b)])
            samples.append(make_sample(judge_sequence(seq, True), True, 1))
            bad = api.assemble_seq(api.role_token("equals"), [prop, _frac_result(a, b + 1)])
            samples.append(make_sample(judge_sequence(bad, False), False, 1))
    return samples, len(samples) // 2, len(samples) // 2


def run():
    torch.manual_seed(0)
    inject_dual_tokens({"fraction": FRACTION_DEFN})
    print(f"注入 fraction: {api.eid_by_name('fraction')}")

    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    cfg["name"] = "sym_div_inv"
    keep = [s for s in cfg["synth"]["samples"]
            if s.get("kind") not in ("unary_judge", "unary_fraction", "binary_fraction")]
    keep.append({"kind": "binary_fraction", "op": "division", "hi": 9})
    keep.append({"kind": "unary_fraction", "op": "inversion", "hi": 99})
    cfg["synth"]["samples"] = keep
    cfg["verify"] = {"ood": [{"op": "inversion", "digits": 3, "n": 50, "mode": "mixed"}]}

    from lab.run_exp import build_samples, _make_verify_fn, _judge_eval
    train, _ = build_samples(cfg, 0)
    print(f"训练样本: {len(train)} (division 分数 {81*2} + inversion 分数 {198})")

    res = train_seq(train, epochs=8, dim=64, num_layers=2, seed=0,
                    token="sym_div_inv", batch_size=512)
    print(f"train acc={res['acc']:.4f} valid={res['valid_acc']:.4f}")

    ood = _make_verify_fn(cfg, train, 0)(12345, [], None)
    jacc, jt, jf, jcons = _judge_eval(res["model"], ood)
    print(f"判定口径: acc={jacc:.3f} 判真={jt:.3f} 判假={jf:.3f} 一致={jcons:.3f} (n={len(ood)})")

    # inversion 专项 (训练内 + 2 位分母外推)
    j = Judge(dim=64, num_layers=2)
    j.model = res["model"].cpu()
    inv_eid = api.eid_by_name("inversion")
    for label, vals in [("训练内 1-99", list(range(1, 100))),
                        ("2 位分母", [10, 50, 99])]:
        s = []
        for a in vals:
            prop = api.assemble_seq(inv_eid, [digits_of(a)])
            seq = api.assemble_seq(api.role_token("equals"), [prop, _frac_result(1, a)])
            s.append(make_sample(judge_sequence(seq, True), True, 1))
            bad = api.assemble_seq(api.role_token("equals"), [prop, _frac_result(1, a + 1)])
            s.append(make_sample(judge_sequence(bad, False), False, 1))
        print(f"inversion ({label}): acc={j.evaluate(s)['acc']:.3f}")


if __name__ == "__main__":
    run()
