"""EXP-NEG-OOD: neg 无损外推增量实验 (fold_num_v5 基线上)

目标 (2026-08-14): neg 也需要无损外推 (OOD 泛化, 同 fold_num_v5 标准)。

设计:
- 训练: fold_num_v5 基线 (neg 样本 = unary_judge neg hi=99, 覆盖 1-2 位)
- 外推测试: neg 在训练外位宽的判定 (3 位 123/456/999, 4 位 1234/9999)
- 变体: 辅助 token (同义/不同义/搭配) 是否改善 neg 外推

观测: 每配置的 neg OOD acc (无损外推 = 1.000)

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_neg_ood.exp_neg_ood
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
from lab.synth_core import inject_dual_tokens, make_sample, digits_of, _unary_eval

NEG_DEFN = {"form": "explicit", "arrange": "unary_connective", "policy": "equations",
            "rules": [{"term": ["D:102", ["self", ["self", "arg:0"]], "arg:0"]},
                      {"term": ["D:102", ["D:100", ["self", "arg:0"], "arg:0"], "D:117"]},
                      {"term": ["D:102", ["self", "arg:0"], ["D:101", "D:117", "arg:0"]]}],
            "references": ["D:102", "D:100", "D:117", "D:101"]}
IDENT_DEFN = {"form": "explicit", "arrange": "unary_connective", "policy": "equations",
              "rules": [{"term": ["D:102", ["self", "arg:0"], "arg:0"]}],
              "references": ["D:102"]}

OOD_VALUES = [123, 4567, 12345, 99999999, 1234567890]   # 渐进外推: 3/4/5/8/10 位 (10 位内)


def neg_judge_samples(values, aux_tokens=(), balanced=True):
    """neg 判定样本 (与 fold_num_v5 unary_judge 同源: assemble_seq 标准组装)."""
    samples = []
    for a in values:
        try:
            total = _unary_eval(_neg_eid(), a)
        except ValueError:
            continue
        args = [*aux_tokens, *digits_of(a)]
        prop = api.assemble_seq(_neg_eid(), [args])
        seq_prop = api.assemble_seq(api.role_token("equals"), [prop, digits_of(total)])
        samples.append(make_sample(judge_sequence(seq_prop, True), True, 1))
        if balanced:
            bad = total + 1 if total + 1 != total else total - 1
            seq_b = api.assemble_seq(api.role_token("equals"), [prop, digits_of(bad)])
            samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    return samples


def neg_ood_acc(model, values=OOD_VALUES):
    """neg OOD 外推 acc (逐位宽观测: 每个测试值单独 acc)."""
    j = Judge(dim=64, num_layers=2)
    j.model = model.cpu()
    per_value = {}
    for v in values:
        samples = neg_judge_samples([v], balanced=True)
        per_value[v] = round(j.evaluate(samples)["acc"], 3)
    overall = round(sum(per_value.values()) / len(per_value), 3)
    return overall, per_value


def run():
    torch.manual_seed(0)
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    print("=== EXP-NEG-OOD: neg 无损外推 (fold_num_v5 基线 + 辅助 token) ===")

    eids = inject_dual_tokens({"neg_aux_same": NEG_DEFN, "neg_aux_diff": IDENT_DEFN})
    same, diff = eids["neg_aux_same"], eids["neg_aux_diff"]

    base_samples, _ = build_samples(cfg, 0)
    print(f"基线样本 {len(base_samples)} | neg OOD 测试值 {OOD_VALUES} (训练外 3-4 位)")

    # 训练配置: neg 全枚举 0..99 (1-2 位全覆盖, 200 样本, 显著占比), 变体加辅助 token
    train_neg_vals = list(range(0, 100))
    configs = [
        ("base",      ()),
        ("aux1_same", (same,)),
        ("aux2_same", (same, same)),
        ("aux1_diff", (diff,)),
        ("aux_mix",   (same, diff)),
    ]
    for name, aux in configs:
        samples = base_samples + neg_judge_samples(train_neg_vals, aux, balanced=True)
        res = train_seq(samples, epochs=8, dim=64, num_layers=2, seed=0,
                        token=f"exp_neg_ood_{name}", batch_size=512)
        ood_acc, per_value = neg_ood_acc(res["model"])
        detail = " ".join(f"{v}位:{acc}" for v, acc in per_value.items())
        print(f"[{name:<10}] train acc={res['acc']:.4f} valid={res['valid_acc']:.4f} "
              f"| neg OOD={ood_acc:.3f} [{detail}]")

    print()
    print("=== neg 无损外推判定 ===")
    print("无损外推 = neg OOD acc 1.000 (同 fold_num_v5 标准)")


if __name__ == "__main__":
    run()
