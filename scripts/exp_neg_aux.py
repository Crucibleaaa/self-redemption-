"""EXP-NEG-AUX: neg 辅助 token 实验 (A/B 观测)

背景 (2026-08-14): neg 取反一直训练不好。观测: 给 neg 增加辅助 token
(多个辅助 token, 有相同语义有不同语义), 观察每种 token 训练后的执行
结果, 以及搭配结果。

实验矩阵 (全部同配置训练, Judge dim=64 layers=2 epochs=15):
- base:      无辅助 token (基线, 标准 neg 判定样本)
- aux1_same: neg + 1 个同义辅助 token (定义 = neg 定义)
- aux2_same: neg + 2 个同义辅助 token
- aux1_diff: neg + 1 个不同义辅助 token (identity 定义)
- aux_mix:   neg + 同义 + 不同义 (搭配)

样本: [neg][aux?][a][equals][result] 一元判定 (代表值 0/1/9/10/99 等)

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_neg_aux.exp_neg_aux
"""
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import api
from tokenizer.eval.engine import _neg_eid
from lab.judge import Judge, judge_sequence
from lab.synth_core import inject_dual_tokens, make_sample, digits_of, _unary_eval

NEG_DEFN = {"form": "explicit", "arrange": "unary_connective", "policy": "equations",
            "rules": [{"term": ["D:102", ["self", ["self", "arg:0"]], "arg:0"]},
                      {"term": ["D:102", ["D:100", ["self", "arg:0"], "arg:0"], "D:117"]},
                      {"term": ["D:102", ["self", "arg:0"], ["D:101", "D:117", "arg:0"]]}],
            "references": ["D:102", "D:100", "D:117", "D:101"]}
IDENT_DEFN = {"form": "explicit", "arrange": "unary_connective", "policy": "equations",
              "rules": [{"term": ["D:102", ["self", "arg:0"], "arg:0"]}],
              "references": ["D:102"]}


def neg_samples(aux_tokens=(), hi=9):
    """neg 一元判定样本: 全枚举 [0,hi] + 多位代表值, 每真 3 假 (多样化)."""
    reps = sorted({0, 1, hi, hi // 2, 10, 99, 10 ** (len(str(max(hi, 99))) - 1)})
    values = list(range(hi + 1)) + [v for v in reps if v > hi]
    samples = []
    for a in values:
        try:
            total = _unary_eval(_neg_eid(), a)
        except ValueError:
            continue
        prop = [_neg_eid()] + list(aux_tokens) + digits_of(a)
        seq = judge_sequence([*prop, api.role_token("equals"), *digits_of(total)], True)
        samples.append(make_sample(seq, True, 1))
        # 1 个假样本/真 (平衡 1:1, 防全判假捷径 0.75)
        bad = total + 1 if total + 1 != total else total - 1
        seq_b = judge_sequence([*prop, api.role_token("equals"), *digits_of(bad)], False)
        samples.append(make_sample(seq_b, False, 1))
    return samples


def run():
    torch.manual_seed(0)
    print("=== EXP-NEG-AUX: neg 辅助 token 实验 ===")

    # 注入辅助 token (实验临时, 不污染主数据)
    eids = inject_dual_tokens({"neg_aux_same": NEG_DEFN, "neg_aux_diff": IDENT_DEFN})
    same, diff = eids["neg_aux_same"], eids["neg_aux_diff"]
    print(f"注入辅助 token: 同义 neg_aux_same (定义=neg), 不同义 neg_aux_diff (identity)")

    configs = [
        ("base",      ()),
        ("aux1_same", (same,)),
        ("aux2_same", (same, same)),
        ("aux1_diff", (diff,)),
        ("aux_mix",   (same, diff)),
    ]
    results = {}
    for name, aux in configs:
        samples = neg_samples(aux)
        j = Judge(dim=64, num_layers=2, epochs=30, seed=0)
        j.train(samples, archive_token=f"exp_neg_aux_{name}", archive=True)
        ev = j.evaluate(samples)
        results[name] = ev["acc"]
        curve = j.train_curve
        print(f"[{name:<10}] 样本 {len(samples):>3} | 末 5 epoch: "
              f"{' '.join(f'{c:.2f}' for c in curve[-5:])} | acc={ev['acc']:.3f}")

    print()
    print("=== 对比 (执行结果) ===")
    base = results["base"]
    for name in results:
        d = results[name] - base
        marker = "优于基线" if d > 0.03 else ("差于基线" if d < -0.03 else "无差别")
        print(f"  {name:<10}: acc={results[name]:.3f} (Δ{base:+.3f} → {d:+.3f}) {marker}")


if __name__ == "__main__":
    run()
