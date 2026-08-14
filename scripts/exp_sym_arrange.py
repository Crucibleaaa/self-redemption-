"""EXP-SYM-ARRANGE: 复现成功实验 + 对称排列解释

1. 复现成功: fold_num_v5 基线 (二元中缀判定, acc 0.99+)
2. 对称排列对比: 一元对称组 (succ/translation/prod/inversion) —
   现状排列 (succ 后缀 [a][op], translation 前缀 [op][a]) vs
   统一前缀排列 ([op][a] 全一致), 测训练内 acc 与外推

观测: 排列是否决定一元判定可学习性

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_sym_arrange.exp_sym_arrange
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import api
from train import train_seq
from lab.judge import judge_sequence, Judge
from lab.run_exp import build_samples
from lab.synth_core import make_sample, digits_of, _unary_eval, eval_op

TRAIN_VALUES = list(range(0, 100))
OOD_VALUES = [123, 4567]


def pred_eval(a):
    if a < 1:
        raise ValueError("predecessor(0) 无定义")
    return eval_op(api.eid_by_name("subtraction"), a, 1)


def unary_samples_native(eid, values, eval_fn):
    """现状排列 (assemble_seq 原样: succ 后缀 / translation 前缀)."""
    samples = []
    for a in values:
        try:
            r = eval_fn(a)
        except ValueError:
            continue
        prop = api.assemble_seq(eid, [digits_of(a)])
        seq = api.assemble_seq(api.role_token("equals"), [prop, digits_of(r)])
        samples.append(make_sample(judge_sequence(seq, True), True, 1))
        bad = r + 1 if r + 1 != r else r - 1
        seq_b = api.assemble_seq(api.role_token("equals"), [prop, digits_of(bad)])
        samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    return samples


def unary_samples_prefix(eid, values, eval_fn):
    """统一前缀排列: [op][a] (手工, 与 translation 一致)."""
    samples = []
    for a in values:
        try:
            r = eval_fn(a)
        except ValueError:
            continue
        prop = [eid] + digits_of(a)
        seq = judge_sequence([*prop, api.role_token("equals"), *digits_of(r)], True)
        samples.append(make_sample(seq, True, 1))
        bad = r + 1 if r + 1 != r else r - 1
        seq_b = judge_sequence([*prop, api.role_token("equals"), *digits_of(bad)], False)
        samples.append(make_sample(seq_b, False, 1))
    return samples


def eval_acc(model, samples):
    j = Judge(dim=64, num_layers=2)
    j.model = model.cpu()
    return j.evaluate(samples)["acc"]


def run():
    torch.manual_seed(0)
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    print("=== EXP-SYM-ARRANGE: 复现成功 + 对称排列对比 ===")

    base_samples, _ = build_samples(cfg, 0)
    ops = [
        ("succ", api.eid_by_name("succ"),
         lambda a: _unary_eval(api.eid_by_name("succ"), a)),
        ("translation", api.eid_by_name("translation"),
         lambda a: _unary_eval(api.eid_by_name("translation"), a)),
        ("prod", api.eid_by_name("predecessor"), pred_eval),
    ]

    # 1. 复现成功: fold_num_v5 base
    res_base = train_seq(base_samples, epochs=8, dim=64, num_layers=2, seed=0,
                         token="exp_sym_arrange_base", batch_size=512)
    print(f"[1. 复现] fold_num_v5 base: acc={res_base['acc']:.4f} "
          f"valid={res_base['valid_acc']:.4f} (期望 0.99+)")

    # 2a. 现状排列 (混合: succ 后缀 / translation 前缀)
    train_mixed = base_samples
    for _, eid, fn in ops:
        train_mixed += unary_samples_native(eid, TRAIN_VALUES, fn)
    res_mixed = train_seq(train_mixed, epochs=8, dim=64, num_layers=2, seed=0,
                          token="exp_sym_arrange_mixed", batch_size=512)
    print(f"[2a. 现状排列] 总体 acc={res_mixed['acc']:.4f}")
    for name, eid, fn in ops:
        tr = unary_samples_native(eid, TRAIN_VALUES, fn)
        print(f"     {name:<12} 训练内 acc={eval_acc(res_mixed['model'], tr):.3f}")

    # 2b. 统一前缀排列
    train_prefix = base_samples
    for _, eid, fn in ops:
        train_prefix += unary_samples_prefix(eid, TRAIN_VALUES, fn)
    res_prefix = train_seq(train_prefix, epochs=8, dim=64, num_layers=2, seed=0,
                           token="exp_sym_arrange_prefix", batch_size=512)
    print(f"[2b. 统一前缀] 总体 acc={res_prefix['acc']:.4f}")
    for name, eid, fn in ops:
        tr = unary_samples_prefix(eid, TRAIN_VALUES, fn)
        print(f"     {name:<12} 训练内 acc={eval_acc(res_prefix['model'], tr):.3f}")

    print()
    print("=== 解释: 对称排列 ===")
    print("现状: succ 后缀 [a][op], translation 前缀 [op][a] — 对称组排列不一致")
    print("统一前缀后: 若训练内 acc 显著改善 ⟹ 排列一致是学习前提;")


if __name__ == "__main__":
    run()
