"""EXP-DUAL-PATH 推理速度测量 (us 单位, 4 配置全测)

测量各双路径配置模型的推理速度 (同路径序列, us/前向) +
推理所需 token (序列长度) + 各配置模型单独进程加载 (注入匹配训练).

用法: PYTHONPATH=. .venv/bin/python -m lab.exp_dual_path.measure_speed
"""
import glob
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab.synth_core import numeral_of, digits_of
from tokenizer import api
from lab.judge import judge_sequence
from train.data import vocab, collate
from train.model import TokenTransformer
import torch


def load(run, inject_kind):
    if inject_kind == "intuit":
        import lab.synth_core as sc
        sc.ensure_itokens(99)
    if inject_kind == "iop":
        import lab.synth_core as sc
        sc.ensure_iops(["inversion"])
    v = vocab()
    m = TokenTransformer(dim=64, num_concepts=len(v), num_layers=2,
                         input_mode="ids", causal=False).eval()
    m.load_state_dict(torch.load(f"{run}/model.pt", weights_only=False,
                                 map_location="cpu"))
    return m


def measure(model, seq, reps=100):
    batch = collate([{"seq": seq, "valid": 1}], input_mode="ids")
    with torch.no_grad():
        model(batch["inputs"], mask=batch["mask"])
        t0 = time.perf_counter()
        for _ in range(reps):
            model(batch["inputs"], mask=batch["mask"])
    return (time.perf_counter() - t0) / reps * 1e6  # us


def seq_variant(op_name, num_kind, a):
    op = api.eid_by_name(op_name)
    nf = (lambda n: [api.eid_by_name(f"inum_{n}")]) if num_kind == "intuit" else numeral_of
    pow_eid = api.eid_by_name("power")
    prop = api.assemble_seq(op, [nf(a)])
    inner = api.assemble_seq(pow_eid, [nf(a), digits_of(-1)])
    result = api.assemble_seq(api.role_token("bracket"), [inner])
    return judge_sequence(api.assemble_seq(api.role_token("equals"), [prop, result]), True)


def run():
    plans = [
        ("dual_struct_struct",   "inversion",     "struct", ""),
        ("dual_struct_intuit",   "inversion",     "intuit", "intuit"),
        ("dual_intuit_struct",   "iop_inversion", "struct", "iop"),
        ("dual_intuit_intuit",   "iop_inversion", "intuit", "intuit+iop"),
    ]
    print("=== 推理速度 (us/前向, 100 reps) 与推理所需 token ===")
    rows = []
    for tag, op, num_kind, inject in plans:
        runs = sorted(glob.glob(f"archive/log/train/{tag}_*"))
        if not runs:
            print(f"  {tag}: 无归档")
            continue
        m = load(runs[-1], inject)
        s = seq_variant(op, num_kind, 5)
        us = measure(m, s)
        rows.append((tag, len(s), us))
        print(f"  {tag:<22}: {us:>8.1f} us/前向 ({len(s)} token)")
    return rows


if __name__ == "__main__":
    run()
