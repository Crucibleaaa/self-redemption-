"""EXP-REPR-POWER: 分数 = 负指数幂表示法 (numeral 幂允许负指数)

用户洞察 (2026-08-14): 分数的本质是幂 — a⁻¹ = 1/a。
允许 numeral 的幂指数为负, 分数即负指数幂的表示:
  inversion(a) = a⁻¹ = [numeral(a)][power][neg][numeral(1)]
  (表示层编码, 无需求值器支持)

对比设计:
- 分数表示法 (frac_bar, 前实验): 0.000 — 手工拼接破坏语法结构
- 负指数幂表示法 (本实验): 走 power 语法组装 (assemble_seq)

验证: 纯结构可学性 → 全量训练 → 外推。

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_repr_power.exp_repr_power
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab.synth_core as sc
from lab.synth_core import make_sample, numeral_of, digits_of
from lab.judge import judge_sequence, Judge
from tokenizer import api
from train import train_seq


def inv_power_samples(vals):
    """inversion(a) = a^(-1): [inversion][numeral(a)] equals [numeral(a)][power][neg][1]."""
    inv = api.eid_by_name("inversion")
    pow_eid = api.eid_by_name("power")
    neg_one = digits_of(-1)   # [neg][1]
    samples = []
    for a in vals:
        prop = api.assemble_seq(inv, [numeral_of(a)])
        result = api.assemble_seq(pow_eid, [numeral_of(a), neg_one])
        seq = api.assemble_seq(api.role_token("equals"), [prop, result])
        samples.append(make_sample(judge_sequence(seq, True), True, 1))
        bad = api.assemble_seq(pow_eid, [numeral_of(a), digits_of(-2)])
        seq_b = api.assemble_seq(api.role_token("equals"), [prop, bad])
        samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    return samples


def run():
    torch.manual_seed(0)
    print("=== EXP-REPR-POWER: 分数 = 负指数幂表示法 ===")
    train_vals = list(range(1, 100))
    s = inv_power_samples(train_vals)
    print(f"样本: {len(s)} (1-99, [a][power][neg][1])")
    print(f"样本格式: {s[0]['seq']}")

    # 1. 纯结构诊断
    res = train_seq(s, epochs=8, dim=64, num_layers=2, seed=0,
                    token="repr_power_alone", batch_size=512)
    j = Judge(dim=64, num_layers=2)
    j.model = res["model"].cpu()
    print(f"纯结构训练内 acc: {j.evaluate(s)['acc']:.3f}")
    ext = inv_power_samples([100, 123])
    print(f"2-3 位外推 acc: {j.evaluate(ext)['acc']:.3f}")

    # 2. 全量训练
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    cfg["name"] = "sym_repr_power"
    keep = [x for x in cfg["synth"]["samples"] if x.get("kind") != "unary_judge"]
    cfg["synth"]["samples"] = keep
    from lab.run_exp import build_samples, _make_verify_fn, _judge_eval
    base, _ = build_samples(cfg, 0)
    full = base + s
    print(f"全量训练: {len(full)} 样本")
    res2 = train_seq(full, epochs=8, dim=64, num_layers=2, seed=0,
                     token="sym_repr_power", batch_size=512)
    print(f"train acc={res2['acc']:.4f} valid={res2['valid_acc']:.4f}")
    ood = _make_verify_fn(cfg, full, 0)(12345, [], None)
    jacc, jt, jf, jcons = _judge_eval(res2["model"], ood)
    print(f"判定口径: acc={jacc:.3f} 一致={jcons:.3f} (n={len(ood)})")
    j2 = Judge(dim=64, num_layers=2)
    j2.model = res2["model"].cpu()
    print(f"全量下负指数幂表示训练内 acc: {j2.evaluate(s)['acc']:.3f}")
    print(f"全量下 2-3 位外推 acc: {j2.evaluate(ext)['acc']:.3f}")


if __name__ == "__main__":
    run()
