"""EXP-NEG-AUX-INCR: fold_num_v5 (最好 OOD 泛化基线) 上的 neg 辅助 token 增量实验

增量实验设计 (2026-08-14): 在 fold_num_v5 配置 (acc 0.9938, 8 epochs,
OOD 泛化最好基线) 基础上, 增量加入 neg 辅助 token 变体, 观测:
- 总体 acc 是否保持 (增量不破坏 OOD 泛化)
- neg 专项 acc 是否改善 (辅助 token 是否修复 neg 训练不好)

变体矩阵 (辅助 token 有相同有不同):
- base:      fold_num_v5 原样 (基线复现)
- aux1_same: + 1 同义辅助 token (定义 = neg)
- aux2_same: + 2 同义辅助 token
- aux1_diff: + 1 不同义辅助 token (identity)
- aux_mix:   + 同义 + 不同义 (搭配)

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_neg_aux_incr.exp_neg_aux_incr
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import api
from tokenizer.eval.engine import _neg_eid
from train import train_seq
from lab.judge import judge_sequence
from lab.run_exp import build_samples
from lab.synth_core import inject_dual_tokens, make_sample, digits_of, _unary_eval

NEG_DEFN = {"form": "explicit", "arrange": "unary_connective", "policy": "equations",
            "rules": [{"term": ["D:102", ["self", ["self", "arg:0"]], "arg:0"]},
                      {"term": ["D:102", ["D:100", ["self", "arg:0"], "arg:0"], "D:117"]},
                      {"term": ["D:102", ["self", "arg:0"], ["D:101", "D:117", "arg:0"]]}],
            "references": ["D:102", "D:100", "D:117", "D:101"]}
IDENT_DEFN = {"form": "explicit", "arrange": "unary_connective", "policy": "equations",
              "rules": [{"term": ["D:102", ["self", "arg:0"], "arg:0"]}],
              "references": ["D:102"]}


def neg_aux_samples(aux_tokens=(), hi=99):
    """neg 判定样本 (平衡 1:1), 辅助 token 插入 neg 后. 与 fold_num_v5 unary_judge 同源."""
    reps = sorted({0, 1, hi, hi // 2, 10, 99, 10 ** (len(str(max(hi, 99))) - 1)})
    samples = []
    for a in reps:
        try:
            total = _unary_eval(_neg_eid(), a)
        except ValueError:
            continue
        prop = [_neg_eid()] + list(aux_tokens) + digits_of(a)
        seq = judge_sequence([*prop, api.role_token("equals"), *digits_of(total)], True)
        samples.append(make_sample(seq, True, 1))
        bad = total + 1 if total + 1 != total else total - 1
        seq_b = judge_sequence([*prop, api.role_token("equals"), *digits_of(bad)], False)
        samples.append(make_sample(seq_b, False, 1))
    return samples


def neg_acc(model, samples):
    """neg 专项 acc (末尾真值判定)."""
    from lab.judge import Judge
    j = Judge(dim=64, num_layers=2)
    j.model = model
    ev = j.evaluate(samples)
    return ev["acc"]


def run():
    torch.manual_seed(0)
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    print("=== EXP-NEG-AUX-INCR: fold_num_v5 基线上的 neg 辅助 token 增量 ===")

    eids = inject_dual_tokens({"neg_aux_same": NEG_DEFN, "neg_aux_diff": IDENT_DEFN})
    same, diff = eids["neg_aux_same"], eids["neg_aux_diff"]

    base_samples, _ = build_samples(cfg, 0)
    neg_base = neg_aux_samples(())
    print(f"fold_num_v5 基线样本: {len(base_samples)} | neg 样本: {len(neg_base)}")

    configs = [
        ("base",      (),       False),
        ("aux1_same", (same,),  True),
        ("aux2_same", (same, same), True),
        ("aux1_diff", (diff,),  True),
        ("aux_mix",   (same, diff), True),
    ]
    results = {}
    for name, aux, add_neg in configs:
        samples = base_samples
        if add_neg:
            samples = samples + neg_aux_samples(aux)
        res = train_seq(samples, epochs=8, dim=64, num_layers=2, seed=0,
                        token=f"exp_neg_aux_incr_{name}", batch_size=512)
        results[name] = (res["acc"], res["valid_acc"])
        print(f"[{name:<10}] 样本 {len(samples):>5} | acc={res['acc']:.4f} "
              f"valid={res['valid_acc']:.4f}")

    print()
    print("=== 增量对比 (基线 = fold_num_v5) ===")
    base_acc = results["base"][0]
    for name in results:
        d = results[name][0] - base_acc
        marker = "保持" if abs(d) < 0.005 else ("改善" if d > 0.005 else "破坏")
        print(f"  {name:<10}: acc={results[name][0]:.4f} (Δ{d:+.4f}) {marker}")


if __name__ == "__main__":
    run()
