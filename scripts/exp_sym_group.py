"""EXP-SYM-GROUP: 对称算符组同时学习观测 (succ/translation/inversion/prod)

对称设计 (2026-08-14, 用户): 一组对称算符, 本应对称地同时学好:
  succ(2) = 3       前向 (后继)
  translation(2) = 3 前向 (平移 +1)
  inversion(2) = 1/2 逆向 (反演 — 分数, v5 整数域不可表示)
  prod(2) = 1       逆向 (前驱)

观测: 同配置训练 (fold_num_v5 基线 + 四算符样本), 各自 10 位内渐进外推 —
是否同时学好 (对称) 还是一个好一个差 (对称破坏)。

v5 边界 (如实报告):
- inversion 分数 (1/2) 不可表示 → 只能生成 a=1 的样本 (1/1=1)
- prod (predecessor) 求值未覆盖 → 实验内补丁: a-1 (用减法求值)

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_sym_group.exp_sym_group
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

OOD_VALUES = [123, 4567, 12345, 99999999, 1234567890]   # 渐进外推 (10 位内)
TRAIN_VALUES = list(range(0, 100))


def pred_eval(a):
    """prod 求值补丁 (实验内): predecessor(a) = a-1 (a ≥ 1)."""
    if a < 1:
        raise ValueError("predecessor(0) 无定义")
    return eval_op(api.eid_by_name("subtraction"), a, 1)


def unary_samples(op_eid, values, eval_fn):
    """一元判定样本 (标准组装): [op][a] equals eval(a), 平衡 1:1."""
    samples = []
    for a in values:
        try:
            r = eval_fn(a)
        except ValueError:
            continue
        prop = api.assemble_seq(op_eid, [digits_of(a)])
        seq = api.assemble_seq(api.role_token("equals"), [prop, digits_of(r)])
        samples.append(make_sample(judge_sequence(seq, True), True, 1))
        bad = r + 1 if r + 1 != r else r - 1
        seq_b = api.assemble_seq(api.role_token("equals"), [prop, digits_of(bad)])
        samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    return samples


def ood_acc(model, op_eid, eval_fn):
    """逐值 OOD acc."""
    j = Judge(dim=64, num_layers=2)
    j.model = model.cpu()
    per = {}
    for v in OOD_VALUES:
        samples = unary_samples(op_eid, [v], eval_fn)
        if samples:
            per[v] = round(j.evaluate(samples)["acc"], 3)
        else:
            per[v] = None
    return per


def run():
    torch.manual_seed(0)
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    print("=== EXP-SYM-GROUP: 对称算符组 (succ/translation/inversion/prod) ===")

    ops = [
        ("succ",        api.eid_by_name("succ"),        lambda a: _unary_eval(api.eid_by_name("succ"), a)),
        ("translation", api.eid_by_name("translation"), lambda a: _unary_eval(api.eid_by_name("translation"), a)),
        ("prod",        api.eid_by_name("predecessor"), pred_eval),
        ("inversion",   api.eid_by_name("inversion"),   lambda a: _unary_eval(api.eid_by_name("inversion"), a)),
    ]
    base_samples, _ = build_samples(cfg, 0)
    train = base_samples
    gen = {}
    for name, eid, fn in ops:
        samples = unary_samples(eid, TRAIN_VALUES, fn)
        gen[name] = len(samples)
        train += samples
        print(f"  {name:<11}: 样本 {len(samples):>3} (可求值范围)")

    res = train_seq(train, epochs=8, dim=64, num_layers=2, seed=0,
                    token="exp_sym_group", batch_size=512)
    model = res["model"]
    print(f"train acc={res['acc']:.4f} valid={res['valid_acc']:.4f}")

    print()
    print("=== 渐进外推 (10 位内) ===")
    print(f"{'值 (位宽)':<12}", end="")
    for name, _, _ in ops:
        print(f"{name:>12}", end="")
    print()
    results = {}
    for v in OOD_VALUES:
        print(f"{v} ({len(str(v))}位)", end="")
        for name, eid, fn in ops:
            samples = unary_samples(eid, [v], fn)
            if not samples:
                print(f"{'不可表示':>12}", end="")
                continue
            j = Judge(dim=64, num_layers=2)
            j.model = model.cpu()
            acc = j.evaluate(samples)["acc"]
            results.setdefault(name, []).append(acc)
            print(f"{acc:>12.3f}", end="")
        print()
    print()
    print("=== 对称性判定 ===")
    for name, vals in results.items():
        avg = sum(vals) / len(vals)
        print(f"  {name:<11}: 平均外推 {avg:.3f} ({len(vals)} 个位宽)")
    print("若 succ/translation 好而 inversion/prod 差 ⟹ 对称组中前向可学、逆向不可学")


if __name__ == "__main__":
    run()
