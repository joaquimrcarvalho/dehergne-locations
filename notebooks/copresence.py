"""Co-presence analysis: "who was at the same place at the same time."

Thin wrapper over the generic ``temporal_semantics`` engine. The engine
classifies attribute types by temporal role (INTERVAL, POINT, INTERVAL_END,
etc.) and builds stay intervals. This module adds:

  - person normalization (effective_id for partially-linked databases)
  - co-presence rendering (markdown table + Mermaid Gantt)
  - networkx export (GraphML/JSON)

See ``temporal_semantics_spec.md`` for the full design.
"""

import re
from collections import defaultdict

from dehergne_util import (
    build_biography, fetch_wikidata_labels,
    effective_id, normalize_persons,
)
from temporal_semantics import (
    build_intervals, detect_overlaps,
    DEFAULT_VOCABULARY, _place_grouping_fn,
    _date_to_iso, _add_years,
)


# ---------------------------------------------------------------------------
# Interval estimation (wraps the generic engine)
# ---------------------------------------------------------------------------

def estimate_stay_intervals(model, *, vocabulary=DEFAULT_VOCABULARY):
    """Estimate stay intervals for one person.

    Thin wrapper over ``temporal_semantics.build_intervals`` with the
    default place-based grouping function.
    """
    bio = build_biography(model)
    pid = effective_id(model)
    pname = model.get_description()
    intervals = build_intervals(
        bio["timeline"], pid, pname,
        vocabulary=vocabulary,
        grouping_fn=_place_grouping_fn,
    )
    return [iv.to_dict() for iv in intervals]


# ---------------------------------------------------------------------------
# Co-presence detection (wraps the generic overlap engine)
# ---------------------------------------------------------------------------

def detect_copresence(persons, include_open=False):
    """Detect co-presence pairs across all persons and places.

    Normalizes persons by ``effective_id`` (partially linked database):
    when both an occurrence and its real entity are in the set, only one
    contributes intervals.

    Returns a dict { qid: [copresence_dict, ...] }.
    """
    persons, _ = normalize_persons(persons)
    all_intervals = []
    for p in persons:
        ivs = estimate_stay_intervals(p)
        for iv_dict in ivs:
            if iv_dict.get("is_open") and not include_open:
                continue
            all_intervals.append(iv_dict)

    # group by qid and detect overlaps
    by_qid = defaultdict(list)
    for iv in all_intervals:
        by_qid[iv["group_key"]].append(iv)

    result = defaultdict(list)
    for qid, ivs in by_qid.items():
        ivs.sort(key=lambda x: x["start"])
        n = len(ivs)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = ivs[i], ivs[j]
                if a["person_id"] == b["person_id"]:
                    continue
                if a["start"] < b["end"] and b["start"] < a["end"]:
                    ov_s = max(a["start"], b["start"])
                    ov_e = min(a["end"], b["end"])
                    result[qid].append({
                        "person_a_id": a["person_id"],
                        "person_a_name": a["person_name"],
                        "person_b_id": b["person_id"],
                        "person_b_name": b["person_name"],
                        "qid": qid,
                        "place_name": a["group_label"],
                        "overlap_start": ov_s,
                        "overlap_end": ov_e,
                        "overlap_start_str": _date_to_iso(ov_s),
                        "overlap_end_str": _date_to_iso(ov_e),
                    })
    return dict(result)


def cluster_copresence(intervals):
    """Cluster overlapping intervals into maximal co-presence groups."""
    if not intervals:
        return []
    sorted_iv = sorted(
        (iv for iv in intervals if iv.get("start") is not None),
        key=lambda x: x["start"])
    groups = []
    current_group = [sorted_iv[0]]
    current_end = sorted_iv[0]["end"]
    for iv in sorted_iv[1:]:
        if iv["start"] < current_end:
            current_group.append(iv)
            current_end = max(current_end, iv["end"])
        else:
            if len(current_group) >= 2:
                groups.append({
                    "start": min(x["start"] for x in current_group),
                    "end": current_end,
                    "persons": current_group,
                })
            current_group = [iv]
            current_end = iv["end"]
    if len(current_group) >= 2:
        groups.append({
            "start": min(x["start"] for x in current_group),
            "end": current_end,
            "persons": current_group,
        })
    return groups


# ---------------------------------------------------------------------------
# Output 1: Co-presence section (markdown table)
# ---------------------------------------------------------------------------

MAX_OPEN_STAY_YEARS = 15  # kept for the method note text

def render_copresence_section(qid, label_info, copresence_data):
    """Render the '### Co-presence' markdown section for a QID page."""
    pairs = copresence_data.get(qid, [])
    if not pairs:
        return ""

    decade_groups = defaultdict(set)
    for p in pairs:
        decade = (p["overlap_start"] // 10000 // 10) * 10
        decade_groups[decade].add((p["person_a_id"], p["person_a_name"]))
        decade_groups[decade].add((p["person_b_id"], p["person_b_name"]))

    lines = []
    lines.append("### Co-presence")
    lines.append("")
    lines.append("These persons were plausibly at this place during "
                 "overlapping periods (interval estimation from stay dates; "
                 "rough — see method note below).")
    lines.append("")
    lines.append("| Period | Persons |")
    lines.append("|--------|---------|")
    for decade in sorted(decade_groups):
        persons = sorted(decade_groups[decade], key=lambda x: x[1])
        links = ", ".join(f"[{name}]({pid})" for pid, name in persons)
        lines.append(f"| {decade}s | {links} |")
    lines.append("")
    n_pairs = len(pairs)
    n_persons = len({p["person_a_id"] for p in pairs} |
                    {p["person_b_id"] for p in pairs})
    lines.append(f"*{n_pairs} overlapping pair(s) involving "
                 f"{n_persons} person(s). "
                 f"Method: interval start = stay event date; "
                 f"end = next embarque/partida/different-place event, "
                 f"or death, or +{MAX_OPEN_STAY_YEARS}yr cap.*")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output 3: Mermaid Gantt chart
# ---------------------------------------------------------------------------

def render_timeline_mermaid(qid, label_info, persons_intervals):
    """Render a Mermaid Gantt chart of stays at this QID."""
    if not persons_intervals:
        return ""

    sorted_iv = sorted(persons_intervals, key=lambda x: x["start"])
    shown = sorted_iv

    label = (label_info or {}).get("label") or qid
    lines = []
    lines.append("```mermaid")
    lines.append("gantt")
    lines.append(f"    title Stays at {label} ({qid})")
    lines.append("    dateFormat YYYY-MM-DD")
    lines.append("    axisFormat %Y")
    current_decade = None
    for iv in shown:
        decade = (iv["start"] // 10000 // 10) * 10 if iv["start"] else 0
        if decade != current_decade:
            current_decade = decade
            lines.append(f"    section {decade}s")
        name = iv["person_name"]
        safe_name = re.sub(r"[;,:#|]", " ", name).strip()
        start_iso = _mermaid_date(iv["start"])
        end_iso = _mermaid_date(iv["end"])
        lines.append(f"    {safe_name} :{start_iso}, {end_iso}")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def _mermaid_date(sort_key):
    if sort_key is None:
        return "0001-01-01"
    s = str(sort_key)
    y, mo, da = s[:4], s[4:6], s[6:8]
    if mo == "00": mo = "01"
    if da == "00": da = "01"
    return f"{y}-{mo}-{da}"


# ---------------------------------------------------------------------------
# Output 2: Network export
# ---------------------------------------------------------------------------

def build_copresence_network(persons, include_open=False):
    """Build a networkx co-presence graph."""
    try:
        import networkx as nx
    except ImportError:
        raise ImportError("networkx is required (pip install networkx)")

    copresence = detect_copresence(persons, include_open=include_open)
    G = nx.Graph()

    persons_in_network = {}
    for qid, pairs in copresence.items():
        for p in pairs:
            for prefix in ("a", "b"):
                pid = p[f"person_{prefix}_id"]
                pname = p[f"person_{prefix}_name"]
                if pid not in persons_in_network:
                    persons_in_network[pid] = pname
                    G.add_node(pid, name=pname, label=pname)

    edge_data = defaultdict(lambda: {"places": [], "total_years": 0})
    for qid, pairs in copresence.items():
        for p in pairs:
            pair_key = tuple(sorted([p["person_a_id"], p["person_b_id"]]))
            # minimum 1 year for any overlap (sub-year overlaps are still real)
            years = max(1, (p["overlap_end"] - p["overlap_start"]) // 10000)
            place_str = f"{p['place_name']} ({p['overlap_start_str']}–{p['overlap_end_str']})"
            edge_data[pair_key]["places"].append(place_str)
            edge_data[pair_key]["total_years"] += years

    for (a, b), data in edge_data.items():
        G.add_edge(a, b,
                   weight=data["total_years"],
                   places="; ".join(data["places"][:5]),
                   n_places=len(data["places"]))
    return G


def export_copresence_network(persons, output_path, include_open=False):
    """Export the co-presence network to GraphML."""
    import os
    G = build_copresence_network(persons, include_open=include_open)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    import networkx as nx
    nx.write_graphml(G, output_path)
    return len(G.nodes), len(G.edges)


def build_bipartite_network(persons, include_open=False):
    """Build a bipartite (two-mode) network: persons + places.

    Nodes:
      - Person nodes (bipartite=0): id, name, label
      - Place nodes (bipartite=1): QID, name, label

    Edges: person → place, with attributes:
      - weight: number of years at that place
      - dates: the stay interval
    """
    try:
        import networkx as nx
    except ImportError:
        raise ImportError("networkx is required (pip install networkx)")

    persons, _ = normalize_persons(persons)
    G = nx.Graph()

    for p in persons:
        ivs = estimate_stay_intervals(p)
        pid = None
        pname = p.get_description()
        for iv in ivs:
            if iv.get("is_open") and not include_open:
                continue
            if iv["start"] is None:
                continue
            pid = iv["person_id"]
            pname = iv["person_name"]
            qid = iv["group_key"]
            place = iv["group_label"]
            years = max(1, (iv["end"] - iv["start"]) // 10000)

            # add person node (bipartite=0)
            if pid not in G:
                G.add_node(pid, name=pname, label=pname,
                           bipartite=0, node_type="person")
            # add place node (bipartite=1)
            if qid not in G:
                G.add_node(qid, name=place, label=place,
                           bipartite=1, node_type="place")
            # add edge
            G.add_edge(pid, qid,
                       weight=years,
                       start=iv["start_str"],
                       end=iv["end_str"],
                       edge_type="stayed_at")
    return G


def export_bipartite_network(persons, output_path, include_open=False):
    """Export the bipartite (person-place) network to GraphML."""
    import os
    G = build_bipartite_network(persons, include_open=include_open)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    import networkx as nx
    nx.write_graphml(G, output_path)
    n_persons = sum(1 for _, d in G.nodes(data=True)
                    if d.get("bipartite") == 0)
    n_places = sum(1 for _, d in G.nodes(data=True)
                   if d.get("bipartite") == 1)
    return n_persons, n_places, G.number_of_edges()


def export_copresence_json(persons, output_path, include_open=False):
    """Export the co-presence network to JSON."""
    import json, os
    G = build_copresence_network(persons, include_open=include_open)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    nodes = [{"id": n, "name": d.get("name", n)}
             for n, d in G.nodes(data=True)]
    edges = [{"source": u, "target": v, "weight": d.get("weight", 1)}
             for u, v, d in G.edges(data=True)]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f,
                  ensure_ascii=False, indent=1)
    return len(nodes), len(edges)
