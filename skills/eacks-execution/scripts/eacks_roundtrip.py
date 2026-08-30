#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eacks_roundtrip.py — EACKS S7 round-trip 引擎（工具层，确定性部分）

定位：eacks-s7-semantic-loss 的工具底座。执行 S→K̂ 反向重建的保真度评估。
LLM 部分（重述生成 T̂、从重述重建 R̂）由调用者（agent）提供，本脚本做
确定性计算：结构比对（relation 三元组级）+ ROUGE-L + fidelity 组装 + τ 判定。

用法：
    from eacks_roundtrip import assess_fidelity
    result = assess_fidelity(S_relations, R_relations, S_text, T_text)

无第三方依赖（纯标准库）。ROUGE-L 为 LCS 实现。
"""

import math
from difflib import SequenceMatcher

TAU_SELECT = 0.85  # fidelity 低于此 → 高风险，强制全项检查
ALPHA = 0.7        # fidelity = α·structure_f1 + (1−α)·rouge_l


# ---------- ROUGE-L（LCS 实现，token 级） ----------

def _tokenize(text):
    """简单中英分词：英文按词，中文按字串切分（保留连续中文字符为一个单元）。"""
    import re
    # 中文连续片段作为一个 token（避免单字切碎导致 LCS 失真）
    parts = re.findall(r'[\u4e00-\u9fff]+|[A-Za-z0-9_]+', text.lower())
    return parts


def _lcs_length(a, b):
    """两序列的最长公共子序列长度（DP）。"""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


def rouge_l(reference, hypothesis):
    """ROUGE-L F1（token 级 LCS）。reference/hypothesis 为字符串。"""
    ref = _tokenize(reference)
    hyp = _tokenize(hypothesis)
    if not ref or not hyp:
        return 0.0
    lcs = _lcs_length(ref, hyp)
    prec = lcs / len(hyp)
    rec = lcs / len(ref)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


# ---------- 结构比对（EACKS 对象级） ----------

def _norm_relation(r):
    """归一化 relation 为可比较三元组：(source, type, target)。

    r 支持两种形态：
      dict: {"source":..,"type":..,"target":..,"condition":..}（EACKS Relation 表行）
      tuple/list: (source, type, target) 或 (source, type, target, condition)
    """
    if isinstance(r, dict):
        src = str(r.get("source", "")).strip()
        typ = str(r.get("type", "")).strip()
        tgt = str(r.get("target", "")).strip()
        cond = str(r.get("condition", "")).strip()
    else:
        seq = list(r)
        src = str(seq[0]).strip()
        typ = str(seq[1]).strip() if len(seq) > 1 else ""
        tgt = str(seq[2]).strip() if len(seq) > 2 else ""
        cond = str(seq[3]).strip() if len(seq) > 3 else ""
    # condition 参与比较（Condition Loss 检测的机械部分）
    key = (src, typ, tgt)
    return key, cond


def compare_relations(S_relations, R_relations):
    """S 与重建结构 R̂ 的关系集合比对。

    返回：precision/recall/f1（方向敏感三元组匹配）+ 缺失/新增/方向反转列表。
    """
    s_map = {}
    for r in S_relations:
        key, cond = _norm_relation(r)
        s_map.setdefault(key, []).append(cond)
    r_map = {}
    for r in R_relations:
        key, cond = _norm_relation(r)
        r_map.setdefault(key, []).append(cond)

    matched = 0
    reversed_hits = []
    missing = []
    added = []

    for key, conds in s_map.items():
        if key in r_map:
            # 匹配数按条件一致性计（condition 字段也一致才算全匹配）
            r_conds = r_map[key]
            for c in conds:
                if c in r_conds:
                    matched += 1
                    r_conds.remove(c)
                else:
                    matched += 0.5  # 结构匹配但条件丢失 → 半匹配（Condition Loss 信号）
            # 该 key 在 R 中多余的条件（新添加）
        else:
            # 方向反转检查：翻转三元组是否在 R 中
            flipped = (key[2], key[1], key[0])
            if flipped in r_map:
                reversed_hits.append((key, flipped))
            else:
                missing.append(key)

    for key in r_map:
        if key not in s_map:
            flipped = (key[2], key[1], key[0])
            if flipped not in s_map:
                added.append(key)

    # 计数修正：reversed 的条目不算 missing
    for key, _ in reversed_hits:
        if key in missing:
            missing.remove(key)

    total_s = len(s_map)
    total_r = len(r_map)
    if total_r == 0:
        prec = 1.0 if total_s == 0 else 0.0
    else:
        prec = matched / total_r
    if total_s == 0:
        rec = 1.0 if total_r == 0 else 0.0
    else:
        rec = matched / total_s
    if prec + rec == 0:
        f1 = 0.0
    else:
        f1 = 2 * prec * rec / (prec + rec)

    return {
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "matched": matched,
        "missing": missing,
        "added": added,
        "reversed": reversed_hits,
    }


# ---------- fidelity 组装与判定 ----------

def assess_fidelity(S_relations, R_relations, S_text=None, T_text=None,
                    alpha=ALPHA, tau=TAU_SELECT):
    """完整 fidelity 评估。

    fidelity = α·structure_f1 + (1−α)·rouge_l(S_text, T_text)
    文本缺省时退化为结构 f1（仍可判定）。

    返回 dict：fidelity / tau_verdict / structure / rouge / 诊断列表。
    """
    struct = compare_relations(S_relations, R_relations)
    structure_f1 = struct["f1"]

    if S_text and T_text:
        rl = rouge_l(S_text, T_text)
    else:
        rl = None

    if rl is not None:
        fidelity = alpha * structure_f1 + (1 - alpha) * rl
    else:
        fidelity = structure_f1

    verdict = "PASS" if fidelity >= tau else "HIGH_RISK"
    diag = []
    if struct["reversed"]:
        diag.append(f"方向反转 {len(struct['reversed'])} 处: {struct['reversed'][:3]}")
    if struct["missing"]:
        diag.append(f"缺失 {len(struct['missing'])} 条: {struct['missing'][:5]}")
    if struct["added"]:
        diag.append(f"新增 {len(struct['added'])} 条: {struct['added'][:5]}")
    if verdict == "HIGH_RISK":
        diag.append("fidelity < τ → 强制全项损失检查")

    return {
        "fidelity": round(fidelity, 4),
        "tau": tau,
        "tau_verdict": verdict,
        "structure_f1": structure_f1,
        "rouge_l": rl,
        "structure_detail": struct,
        "diagnostics": diag,
    }


# ---------- 自测 ----------

if __name__ == "__main__":
    # 自测：正常重建（应 PASS）
    S = [("A", "causal", "B"), ("C", "causal", "D")]
    R_ok = [("A", "causal", "B"), ("C", "causal", "D")]
    r1 = assess_fidelity(S, R_ok)
    print("正常重建:", r1["fidelity"], r1["tau_verdict"])

    # 自测：方向反转（应检出 reversed + 低 f1）
    R_bad = [("B", "causal", "A"), ("C", "causal", "D")]
    r2 = assess_fidelity(S, R_bad)
    print("方向反转:", r2["fidelity"], r2["tau_verdict"], r2["structure_detail"]["reversed"])

    # 自测：缺失 + 新增（应检出）
    R_miss = [("C", "causal", "D"), ("X", "causal", "Y")]
    r3 = assess_fidelity(S, R_miss)
    print("缺失/新增:", r3["fidelity"], r3["structure_detail"]["missing"], r3["structure_detail"]["added"])

    # 自测：ROUGE-L 中文
    print("ROUGE-L:", round(rouge_l("甲改变了乙", "甲改变了乙"), 4),
          round(rouge_l("甲改变了乙", "甲未改变乙"), 4))
