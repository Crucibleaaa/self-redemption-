"""EXP-DUAL-PATH: 双路径 2×2 消融 (直觉/结构 × numeral/算符)

设计 (2026-08-14): 直觉路径 vs 结构路径, 在 numeral 与算符两个载体上
做 2×2 消融:
  - numeral: 结构 (数位序列) vs 直觉 (itoken 原子)
  - 算符:   结构 (标准 token) vs 直觉 (注入 iop token)

四配置:
  1. 结构算符+结构numeral (基线, 全结构)
  2. 结构算符+直觉numeral (numeral 直觉化)
  3. 直觉算符+结构numeral (算符直觉化)
  4. 直觉算符+直觉numeral (全直觉)

注入: I 层 inum_1..99 (直觉 numeral), C 层 iop_inversion (直觉算符).
全部经 run_exp 配置驱动 (dual_path_repr kind).

用法: PYTHONPATH=. .venv/bin/python -m lab.exp_dual_path.inject_and_gen
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import token_index, _register, api
from lab.synth_core import inject_dual_tokens

INUM_DEFN = {"form": "interface", "semantics": "constant", "references": []}
IOP_DEFN = {"form": "interface", "semantics": "constant", "references": []}


def inject():
    """原生注入 (I 层): inum_1..99 直觉 numeral + C 层 iop_inversion 直觉算符.

    从根上: I 层注册进 tokenizer 查询链 (token_eid/token_of/all_eids),
    合成器经 eid_by_name 原生查询, 与 C 层同等对待.
    """
    i_rows = [{"eid": f"I:dual{n}", "name": f"inum_{n}", "dtype": "num",
               "value": n, "interface": True,
               "definition": {"form": "interface", "semantics": "constant",
                              "references": []}}
              for n in range(1, 100)]
    token_index.inject_temp("I", i_rows)
    _register.load_itokens()  # 刷新 I 层注册 (含临时注入)
    inject_dual_tokens({"iop_inversion": IOP_DEFN})
    _register.load_derive()
    print(f"原生注入: I 层 inum_1..99 (直觉 numeral) + C 层 iop_inversion (直觉算符)")
    print(f"  验证 inum_5: {api.eid_by_name('inum_5')} | iop_inversion: {api.eid_by_name('iop_inversion')}")
    print(f"  I 层注册数: {len(_register.ITOKEN_REGISTRY)}")


def gen_cfgs():
    base = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "configs", "sym_fr_ti_off.json")))
    combos = {
        "dual_struct_struct": {"num_mode": "struct", "op_mode": "struct"},
        "dual_struct_intuit": {"num_mode": "intuit", "op_mode": "struct"},
        "dual_intuit_struct": {"num_mode": "struct", "op_mode": "intuit"},
        "dual_intuit_intuit": {"num_mode": "intuit", "op_mode": "intuit"},
    }
    for name, modes in combos.items():
        cfg = json.loads(json.dumps(base))
        cfg["name"] = name
        spec = {"kind": "dual_path_repr", "op": "inversion", "hi": 9}
        spec.update(modes)
        cfg["synth"]["samples"] = [s for s in cfg["synth"]["samples"]
            if s.get("kind") not in ("unary_power_repr", "binary_power_repr")] + [spec]
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "configs", f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=1)
        print(f"生成 {name}.json: {modes}")


if __name__ == "__main__":
    inject()
    gen_cfgs()
