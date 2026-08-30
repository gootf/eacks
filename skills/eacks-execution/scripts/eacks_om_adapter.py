#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eacks_om_adapter.py — onto_merger 适配层（EACKS S2/S5 工具接线）

定位：把 onto_merger 的对齐引擎用作 EACKS 候选生成层（L2），并执行
方向反转（默认合并 → 默认分化）。onto_merger 的 merges 输出不得直接采用。

循环导入通过预注册空 alignment 包绕过。

用法：
    from eacks_om_adapter import om_candidate_pairs, direction_reversal_filter
    pairs = om_candidate_pairs(concepts_csv)          # → EACKS 候选对
    result = direction_reversal_filter(pairs, evidence)  # → 分化裁决

依赖：L2 通道需 candidates/onto_merger/ 源码 + networkit（`pip install networkit`）；L1 通道零依赖。
onto_merger 或 networkit 缺失时自动降级（_OM_AVAILABLE=False，om_candidate_pairs 报错提示，
lightweight_candidates 不受影响）。
"""

import os
import sys
import types
import csv

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'candidates'))
_ROOT = os.path.join(BASE, 'onto_merger')

# L2 通道（onto_merger 完整管线）：可选加载。依赖 candidates/onto_merger 源码
# + networkit（pip install networkit）。缺失时降级（_OM_AVAILABLE=False），不阻断 L1。
_OM_AVAILABLE = False
_OM_IMPORT_ERROR = None
try:
    sys.path.insert(0, _ROOT)
    import onto_merger  # noqa: E402  (纯 docstring 包)

    # 预注册空 alignment 包，绕过 alignment/__init__.py 的循环 re-export
    _pkg = types.ModuleType('onto_merger.alignment')
    _pkg.__path__ = [os.path.join(_ROOT, 'onto_merger', 'alignment')]
    sys.modules['onto_merger.alignment'] = _pkg

    from onto_merger.data.data_manager import DataManager  # noqa: E402
    from onto_merger.data.dataclasses import DataRepository, NamedTable  # noqa: E402
    from onto_merger.alignment.alignment_manager import AlignmentManager  # noqa: E402
    _OM_AVAILABLE = True
except Exception as _e:  # noqa: BLE001 — 降级而非崩溃
    _OM_IMPORT_ERROR = f"{type(_e).__name__}: {_e}"


def _make_project_structure(concepts_csv_path, workdir):
    """EACKS Concept 表 → onto_merger 标准项目结构。

    <workdir>/input/{config.json, nodes.csv, mappings.csv, edges_hierarchy.csv, nodes_obsolete.csv}
    <workdir>/output/
    每个概念作为独立 namespace（来源书标识），候选映射由引擎生成（mappings 空表）。
    """
    import json as _json

    rows = []
    with open(concepts_csv_path, 'r', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows.append(r)

    input_dir = os.path.join(workdir, 'input')
    output_dir = os.path.join(workdir, 'output')
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # config.json
    cfg = {
        "domain_node_type": "Concept",
        "seed_ontology_name": "EACKS_SEED",
        "mappings": {
            "type_groups": {
                "equivalence": ["equivalent_to", "merge"],
                "database_reference": ["database_cross_reference", "xref"],
                "label_match": []
            }
        }
    }
    with open(os.path.join(input_dir, 'config.json'), 'w', encoding='utf-8') as f:
        _json.dump(cfg, f, ensure_ascii=False, indent=2)

    # nodes.csv: default_id, namespace_default_id
    with open(os.path.join(input_dir, 'nodes.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['default_id', 'namespace_default_id'])
        for r in rows:
            w.writerow([r['id'], r['source_book']])

    # mappings.csv: 空（候选由引擎生成）
    with open(os.path.join(input_dir, 'mappings.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['source_id', 'target_id', 'relation', 'prov',
                    'namespace_source_id', 'namespace_target_id', 'source_to_target'])

    # edges_hierarchy.csv / nodes_obsolete.csv: 空表
    for name, header in [('edges_hierarchy.csv',
                          ['source_id', 'target_id', 'relation', 'prov',
                           'namespace_source_id', 'namespace_target_id', 'source_to_target']),
                         ('nodes_obsolete.csv', ['default_id', 'namespace_default_id'])]:
        with open(os.path.join(input_dir, name), 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(header)

    return workdir


def om_candidate_pairs(concepts_csv_path, workdir, name='eacks_concepts'):
    """完整调用 onto_merger 对齐引擎，返回 EACKS 候选概念对。

    返回 list[dict]: {concept_a, concept_b, candidate_score, om_source}
    （candidate_score 仅为候选信号，非判定结论——判定属 S2 guard。）
    """
    if not _OM_AVAILABLE:
        raise RuntimeError(
            'L2 通道不可用（onto_merger 未加载）：' + (_OM_IMPORT_ERROR or '')
            + '。请确认 candidates/onto_merger 存在且 networkit 已安装（pip install networkit）；'
              '或改用 lightweight_candidates（L1）。'
        )
    _make_project_structure(concepts_csv_path, workdir)

    dm = DataManager(project_folder_path=workdir)
    cfg = dm.load_alignment_config()

    # 手动构造表（dtype=str 强制 object 列——空表不会被推断为 float64）
    import pandas as pd

    def _load(path):
        p = os.path.join(workdir, 'input', path)
        if not os.path.exists(p):
            return None
        return pd.read_csv(p, dtype=str)

    repo = DataRepository()
    for tname, tpath in [('nodes', 'nodes.csv'),
                         ('mappings', 'mappings.csv'),
                         ('edges_hierarchy', 'edges_hierarchy.csv'),
                         ('nodes_obsolete', 'nodes_obsolete.csv')]:
        df = _load(tpath)
        if df is not None:
            # 空表也注入（onto_merger 内部硬依赖这些表存在；dtype=str 保持 object 列）
            repo.update(table=NamedTable(name=tname, dataframe=df))

    mgr = AlignmentManager(alignment_config=cfg, data_repo=repo, data_manager=dm)
    out_repo, priority = mgr.align_nodes()

    # 提取候选（mappings 表输出；若表名不同则探测）
    cands = []
    for name_, t in out_repo.data.items():
        df = t.dataframe
        if df is None or len(df) == 0:
            continue
        cols = [str(c).lower() for c in df.columns]
        if 'node1' in ' '.join(cols) or 'source' in ' '.join(cols):
            # 尝试识别候选对列
            a_col = next((c for c in df.columns if 'node1' in str(c).lower() or 'source' in str(c).lower()), None)
            b_col = next((c for c in df.columns if 'node2' in str(c).lower() or 'target' in str(c).lower()), None)
            score_col = next((c for c in df.columns if 'score' in str(c).lower() or 'weight' in str(c).lower()), None)
            if a_col and b_col:
                for _, row in df.iterrows():
                    cands.append({
                        'concept_a': str(row[a_col]),
                        'concept_b': str(row[b_col]),
                        'candidate_score': float(row[score_col]) if score_col else None,
                        'om_source': name_,
                    })
    return cands


def lightweight_candidates(concepts_csv_path):
    """L1 候选生成（轻量通道）：名称归一化 + token 重合。

    EACKS 概念表（几十~几百概念）的现实选择：生成候选对 + overlap 分数 +
    Jingle 风险标记（消歧后缀同基名）。onto_merger 完整管线（om_candidate_pairs）
    保留给带真实 mappings/层级数据的大规模场景。

    返回 list[dict]: {concept_a, concept_b, candidate_score, overlap, jingle_risk}
    """
    import re as _re

    rows = []
    with open(concepts_csv_path, 'r', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows.append(r)

    norm = []
    for r in rows:
        name = r['name']
        base = _re.sub(r'[\[\]（）()].*$', '', name).strip()  # 去消歧后缀
        # 双语 token：中文连续片段 + 英文单词（lowercase）
        tokens = set(_re.findall(r'[\u4e00-\u9fff]+', base)) | \
                 set(_re.findall(r'[a-z]+', base.lower()))
        norm.append({'id': r['id'], 'name': name, 'base': base,
                     'tokens': tokens, 'row': r})

    pairs = []
    for i in range(len(norm)):
        for j in range(i + 1, len(norm)):
            a, b = norm[i], norm[j]
            common = a['tokens'] & b['tokens']
            union = a['tokens'] | b['tokens']
            if not union:
                continue
            overlap = len(common) / len(union)
            if overlap <= 0:
                continue
            jingle = (a['base'] == b['base'] and a['id'] != b['id'])
            pairs.append({
                'concept_a': a['id'],
                'concept_b': b['id'],
                'candidate_score': round(overlap, 4),
                'overlap': round(overlap, 4),
                'jingle_risk': jingle,
                'a_name': a['name'],
                'b_name': b['name'],
            })

    pairs.sort(key=lambda p: p['candidate_score'], reverse=True)
    return pairs


def direction_reversal_filter(candidate_pairs, evidence_records):
    """方向反转核心：候选层 → EACKS 决策层。

    evidence_records: dict {(concept_a, concept_b): {correspondence_type, evidence_ok}}
    规则：
      - 全部候选默认进入 correspondence_candidates（保持分离）
      - 仅 evidence_ok=True 且 correspondence_type=equivalent 的候选允许 merges
      - 同名候选（Jingle 风险）自动标记 need_disambiguation
    返回: {"correspondence_candidates": [...], "allowed_merges": [...], "flagged": [...]}
    """
    correspondence = []
    merges = []
    flagged = []

    seen = set()
    for p in candidate_pairs:
        key = (p['concept_a'], p['concept_b'])
        if key in seen or (key[1], key[0]) in seen:
            continue
        seen.add(key)
        ev = evidence_records.get(key) or evidence_records.get((key[1], key[0])) or {}
        ctype = ev.get('correspondence_type', 'unresolved')
        ev_ok = ev.get('evidence_ok', False)

        entry = {
            'concept_a': p['concept_a'],
            'concept_b': p['concept_b'],
            'candidate_type': ctype,
            'default_action': 'keep_separate',
            'om_score': p.get('candidate_score'),
        }
        # Jingle 风险：候选层标记（同名基不同概念）或原始 ID 相同
        if p.get('jingle_risk') or p['concept_a'] == p['concept_b']:
            entry['need_disambiguation'] = True
            flagged.append(entry)

        if ctype == 'equivalent' and ev_ok:
            entry['default_action'] = 'merge'
            merges.append(entry)
        else:
            correspondence.append(entry)

    return {
        'correspondence_candidates': correspondence,
        'allowed_merges': merges,
        'flagged': flagged,
    }


def to_eacks_correspondence(pairs, source_book_map):
    """候选对 → EACKS Correspondence 表行（补来源书/章节字段）。

    source_book_map: dict {concept_id: 来源书}
    """
    rows = []
    for p in pairs:
        rows.append({
            'concept_a': p['concept_a'],
            'concept_b': p['concept_b'],
            'correspondence_type': p.get('candidate_type', 'unresolved'),
            '证据': p.get('evidence_note', '（候选层，待 S2 判定）'),
            '默认分化标记': p.get('default_action', 'keep_separate'),
            '状态': 'active',
            '来源书/章节': f"{source_book_map.get(p['concept_a'], '?')} vs {source_book_map.get(p['concept_b'], '?')}",
        })
    return rows


# ---------- 自测 ----------

if __name__ == '__main__':
    import tempfile
    # 方向反转过滤器自测（不依赖 onto_merger 的完整对齐）
    pairs = [
        {'concept_a': '概念A[理论定义]', 'concept_b': '概念A[自称]',
         'candidate_score': 0.95},   # 同名不同义 → Jingle 风险
        {'concept_a': '概念A[理论定义]', 'concept_b': '概念B',
         'candidate_score': 0.85},   # 异名同义候选
    ]
    evidence = {
        ('概念A[理论定义]', '概念A[自称]'):
            {'correspondence_type': 'different', 'evidence_ok': False},
        ('概念A[理论定义]', '概念B'):
            {'correspondence_type': 'overlapping', 'evidence_ok': False},
    }
    res = direction_reversal_filter(pairs, evidence)
    print('方向反转过滤自测:')
    print('  correspondence:', len(res['correspondence_candidates']), '条（保持分离）')
    print('  allowed_merges:', len(res['allowed_merges']), '条（需 equivalent+证据）')
    print('  flagged:', [f["concept_a"] for f in res["flagged"]])
