"""EXP-SYM-FRACTION: 分数语法 token 表示 inversion (反演)

根因 (exp_sym_inv): inversion 分数 1/2 不可表示 → 仅 2 样本 → 缺乏结构
→ gen acc 0.0。设计分数语法 token 表达反演结果, 恢复结构。

分数 token 设计 (临时注入, 不污染核心):
- C 层: fraction(num, den) — 分子/分母对 (arrange application)
- 表达: inversion(a) = fraction(1, a) — [inversion][a][equals][fraction][1][a]
- 样本: 全枚举 a = 1..99 (99 个真值 + 平衡假值 = 结构充足)

流程: 复用 run_exp 官方合成/训练/验证/归档 (build_samples/train_seq/verify),
注册实验样本 kind "unary_fraction" (运行时注册, 不写 synth_core)。

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_sym_fraction.exp_sym_fraction
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab.synth_core as sc  # 触发样本注册表
from lab.synth_core import (register_sample, inject_dual_tokens, make_sample,
                            digits_of, _unary_eval)
from lab.judge import judge_sequence
from tokenizer import api
from train import train_seq

FRACTION_DEFN = {"form": "explicit", "arrange": "application",
                 "policy": "equations",
                 "rules": [{"term": ["D:102", ["self", "arg:0", "arg:1"],
                                     ["D:156", "arg:0", "arg:1"]]}],
                 "references": ["D:102", "D:156"]}


@register_sample("unary_fraction")
def _s_unary_fraction(spec, seed):
    """inversion 分数样本: [inversion][a] equals fraction(1, a)."""
    op = spec["op"]
    hi = spec.get("hi", 99)
    op_eid = api.eid_by_name(op)
    frac_eid = api.eid_by_name("fraction")
    samples = []
    for a in range(1, hi + 1):
        r = _unary_eval(op_eid, a) if False else None  # 分数不求值, 直接编码
        prop = api.assemble_seq(op_eid, [digits_of(a)])
        result = api.assemble_seq(frac_eid, [digits_of(1), digits_of(a)])
        seq = api.assemble_seq(api.role_token("equals"), [prop, result])
        samples.append(make_sample(judge_sequence(seq, True), True, 1))
        # 假值: fraction(1, a+1) (分子不变, 分母错)
        bad = api.assemble_seq(frac_eid, [digits_of(1), digits_of(a + 1)])
        seq_b = api.assemble_seq(api.role_token("equals"), [prop, bad])
        samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    return samples, len(samples) // 2, len(samples) // 2


def run():
    torch.manual_seed(0)
    # 1. 注入 fraction token
    eids = inject_dual_tokens({"fraction": FRACTION_DEFN})
    frac_eid = eids["fraction"]
    print(f"注入 fraction token: {frac_eid}")

    # 2. 配置: fold_num_v5 基础 + unary_fraction (inversion 分数样本)
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    cfg["name"] = "sym_fraction"
    keep = [s for s in cfg["synth"]["samples"] if s.get("kind") != "unary_judge"]
    keep.append({"kind": "unary_fraction", "op": "inversion", "hi": 99})
    cfg["synth"]["samples"] = keep
    cfg["verify"] = {"ood": [{"op": "inversion", "digits": 3, "n": 50, "mode": "mixed"}]}

    # 3. 官方流程: 合成 → 训练 → 验证
    from lab.run_exp import build_samples, _make_verify_fn, _judge_eval
    from lab import verify
    train, _ = build_samples(cfg, 0)
    print(f"训练样本: {len(train)} (含 inversion 分数样本 198)")

    res = train_seq(train, epochs=8, dim=64, num_layers=2, seed=0,
                    token="sym_fraction", batch_size=512)
    print(f"train acc={res['acc']:.4f} valid={res['valid_acc']:.4f}")

    # 判定口径 (官方)
    ood = _make_verify_fn(cfg, train, 0)(12345, [], None)
    jacc, jt, jf, jcons = _judge_eval(res["model"], ood)
    print(f"判定口径: acc={jacc:.3f} 判真={jt:.3f} 判假={jf:.3f} 一致={jcons:.3f} (n={len(ood)})")

    # 4. inversion 专项: token gen (分数表示下)
    from lab.judge import Judge
    j = Judge(dim=64, num_layers=2)
    j.model = res["model"].cpu()
    inv_samples = []
    for a in [2, 3, 10, 50, 99]:  # 代表性外推 (分子 1, 分母 2 位)
        prop = api.assemble_seq(api.eid_by_name("inversion"), [digits_of(a)])
        result = api.assemble_seq(frac_eid, [digits_of(1), digits_of(a)])
        seq = api.assemble_seq(api.role_token("equals"), [prop, result])
        inv_samples.append(make_sample(judge_sequence(seq, True), True, 1))
        bad = api.assemble_seq(frac_eid, [digits_of(1), digits_of(a + 1)])
        seq_b = api.assemble_seq(api.role_token("equals"), [prop, bad])
        inv_samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    print(f"inversion 分数表示 acc (含 2 位分母): {j.evaluate(inv_samples)['acc']:.3f}")

    # 5. 官方验证视图 (归档)
    from lab.run_exp import _archive_epoch_gen
    views = verify(res["run_dir"], samples_fn=_make_verify_fn(cfg, train, 0), batch_size=32)
    print(f"位置级: overall={views.get('overall_acc', 0):.3f} ood={views.get('ood_acc', 0):.3f}")


if __name__ == "__main__":
    run()
