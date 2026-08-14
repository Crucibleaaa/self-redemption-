"""EXP-POS-NEG: pos 与 neg 对称对比 (无损外推)

关键 (2026-08-14): neg 和 pos 需要对比。一组对称设计 (前缀一元判定),
本该是对称的, 但一个好一个差:

  pos 前缀: [sign_pos][a] = a     (数位不变, 保持)
  neg 前缀: [neg][a] = -a         (符号翻转, 取反)

设计: 同配置训练 (fold_num_v5 基线 + pos 样本 + neg 样本, 全枚举 0..99),
训练后分别测 pos OOD 与 neg OOD (渐进外推 3/4/5/8/10 位, 10 位内)。

判定:
- pos 好 neg 差 ⟹ 不对称 (neg 特殊, 对称设计被破坏)
- 都差 ⟹ 前缀一元判定普遍难 (非 neg 特殊)
- 都好 ⟹ 对称设计成立 (无损外推双达)

用法: PYTHONPATH=. /home/ethanw/llm-research/.venv/bin/python -m lab.exp_pos_neg.exp_pos_neg
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
from lab.synth_core import make_sample, digits_of, _unary_eval, _sign_for

OOD_VALUES = [123, 4567, 12345, 99999999, 1234567890]   # 渐进外推 (10 位内)
TRAIN_VALUES = list(range(0, 100))                       # 1-2 位全枚举


def sign_samples(prefix_eid, values, result_fn):
    """前缀一元判定样本: [prefix][a] equals result (平衡 1:1)."""
    samples = []
    for a in values:
        r = result_fn(a)
        prop = api.assemble_seq(prefix_eid, [digits_of(a)])
        seq = api.assemble_seq(api.role_token("equals"), [prop, digits_of(r)])
        samples.append(make_sample(judge_sequence(seq, True), True, 1))
        bad = r + 1 if r + 1 != r else r - 1
        seq_b = api.assemble_seq(api.role_token("equals"), [prop, digits_of(bad)])
        samples.append(make_sample(judge_sequence(seq_b, False), False, 1))
    return samples


def ood_acc(model, prefix_eid, values, result_fn):
    """逐值 OOD acc (渐进位宽观测)."""
    j = Judge(dim=64, num_layers=2)
    j.model = model.cpu()
    per = {}
    for v in values:
        per[v] = round(j.evaluate(sign_samples(prefix_eid, [v], result_fn))["acc"], 3)
    return per


def run():
    torch.manual_seed(0)
    cfg = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "fold_num_v5.json")))
    print("=== EXP-POS-NEG: pos/neg 对称对比 (无损外推) ===")

    pos_eid = api.eid_by_name("sign_pos")
    neg_eid = api.eid_by_name("sign_neg")
    base_samples, _ = build_samples(cfg, 0)

    # pos: 数位不变; neg: 取反 (数位加 neg 前缀)
    pos_samples = sign_samples(pos_eid, TRAIN_VALUES, lambda a: a)
    neg_samples = sign_samples(neg_eid, TRAIN_VALUES, lambda a: -a)
    train = base_samples + pos_samples + neg_samples
    print(f"训练: 基线 {len(base_samples)} + pos {len(pos_samples)} + neg {len(neg_samples)} "
          f"(全枚举 0..99)")

    res = train_seq(train, epochs=8, dim=64, num_layers=2, seed=0,
                    token="exp_pos_neg", batch_size=512)
    model = res["model"]
    print(f"train acc={res['acc']:.4f} valid={res['valid_acc']:.4f}")

    pos_ood = ood_acc(model, pos_eid, OOD_VALUES, lambda a: a)
    neg_ood = ood_acc(model, neg_eid, OOD_VALUES, lambda a: -a)

    print()
    print("=== 渐进外推对比 (10 位内) ===")
    print(f"{'值 (位宽)':<12} {'pos acc':>8} {'neg acc':>8}")
    for v in OOD_VALUES:
        print(f"{v} ({len(str(v))}位)      {pos_ood[v]:>8.3f} {neg_ood[v]:>8.3f}")
    pos_avg = sum(pos_ood.values()) / len(pos_ood)
    neg_avg = sum(neg_ood.values()) / len(neg_ood)
    print(f"{'平均':<12} {pos_avg:>8.3f} {neg_avg:>8.3f}")

    print()
    print("=== 对称性判定 ===")
    if pos_avg > 0.8 and neg_avg < 0.2:
        print("pos 好 neg 差 ⟹ 对称设计被破坏 (neg 特殊难) — 不对称")
    elif pos_avg < 0.2 and neg_avg < 0.2:
        print("都差 ⟹ 前缀一元判定普遍难 (非 neg 特殊)")
    elif pos_avg > 0.8 and neg_avg > 0.8:
        print("都好 ⟹ 对称设计成立 (无损外推双达)")
    else:
        print(f"中间态: pos={pos_avg:.2f} neg={neg_avg:.2f} — 需细看")


if __name__ == "__main__":
    run()
