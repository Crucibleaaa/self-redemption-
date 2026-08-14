"""EXP-SYM-DIR: 对称方向对比实验矩阵 (全量训练 + 统一前缀)

设计 (2026-08-14): 在 fold_num_v5 全量训练基础上, 只做统一前缀排列,
对比不同对称方向下的对称性训练好坏:

| 配置 | 对称方向 | 内容 |
|---|---|---|
| E1  succ 单独 | 前向 (单层) | succ |
| E2  prod 单独 | 逆向 (单层) | predecessor |
| E3  succ+prod | 前向+逆向 (对) | succ, predecessor |
| E4  translation 单独 | 前向 (平移) | translation |
| E5  neg 单独 | 对合 (取反) | neg |
| E6  translation+neg | 前向+对合 (对) | translation, neg |
| E7  succ+translation | 双前向 | succ, translation |
| E8  全四算符 | 混合 | succ, prod, translation, neg |

观测: 每配置 训练内 acc (各算符) + 3 位外推 (10 位内)。
对比不同对称方向的训练好坏 (只做前缀)。

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_sym_dir.exp_sym_dir
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import api
from tokenizer.eval.engine import _neg_eid
from train import train_seq
from lab.judge import judge_sequence, Judge
from lab.run_exp import build_samples
from lab.synth_core import make_sample, digits_of, _unary_eval, eval_op

TRAIN_VALUES = list(range(0, 100))
OOD_VALUE = 123


def pred_eval(a):
    if a < 1:
        raise ValueError("predecessor(0) 无定义")
    return eval_op(api.eid_by_name("subtraction"), a, 1)


OPS = {
    "succ": (api.eid_by_name("succ"),
             lambda a: _unary_eval(api.eid_by_name("succ"), a)),
    "prod": (api.eid_by_name("predecessor"), pred_eval),
    "translation": (api.eid_by_name("translation"),
                    lambda a: _unary_eval(api.eid_by_name("translation"), a)),
    "neg": (_neg_eid(), lambda a: _unary_eval(_neg_eid(), a)),
}


def unary_prefix_samples(eid, values, eval_fn, balanced=True):
    """统一前缀排列: [op][a] equals eval(a)."""
    samples = []
    for a in values:
        try:
            r = eval_fn(a)
        except ValueError:
            continue
        prop = [eid] + digits_of(a)
        seq = judge_sequence([*prop, api.role_token("equals"), *digits_of(r)], True)
        samples.append(make_sample(seq, True, 1))
        if balanced:
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
    base_samples, _ = build_samples(cfg, 0)

    configs = [
        ("E1_succ_单独_前向",      ["succ"]),
        ("E2_prod_单独_逆向",      ["prod"]),
        ("E3_succ_prod_对",        ["succ", "prod"]),
        ("E4_translation_单独_前向", ["translation"]),
        ("E5_neg_单独_对合",       ["neg"]),
        ("E6_translation_neg_对",  ["translation", "neg"]),
        ("E7_succ_translation_双前向", ["succ", "translation"]),
        ("E8_全四算符_混合",       ["succ", "prod", "translation", "neg"]),
    ]

    print("=== EXP-SYM-DIR: 对称方向对比 (全量训练 + 统一前缀) ===")
    header = f"{'配置':<26} {'总体':>6} " + " ".join(f"{op:>11}" for op in OPS)
    print(header)

    results = []
    for name, ops in configs:
        train = base_samples
        for op in ops:
            eid, fn = OPS[op]
            train += unary_prefix_samples(eid, TRAIN_VALUES, fn)
        res = train_seq(train, epochs=8, dim=64, num_layers=2, seed=0,
                        token=f"exp_sym_dir_{name[:20]}", batch_size=512)
        row = {"name": name, "acc": res["acc"]}
        row["per"] = {}
        for op in OPS:
            eid, fn = OPS[op]
            tr = unary_prefix_samples(eid, TRAIN_VALUES, fn)
            row["per"][op] = eval_acc(res["model"], tr)
        results.append(row)
        line = f"{name:<26} {res['acc']:>6.4f} " + \
               " ".join(f"{row['per'][op]:>11.3f}" for op in OPS)
        print(line)

    print()
    print("=== 对称方向训练好坏对比 ===")
    for row in results:
        succ = row["per"]["succ"]
        prod = row["per"]["prod"]
        tag = ""
        if succ > 0.8 and prod < 0.2:
            tag = "⟹ 前向可学, 逆向不可学 (对称破坏)"
        elif succ > 0.8 and prod > 0.8:
            tag = "⟹ 前向逆向同时可学 (对称成立)"
        print(f"  {row['name']:<26} succ={succ:.3f} prod={prod:.3f} {tag}")


if __name__ == "__main__":
    run()
