"""Collaborator network for the About page, built from @article entries in publications.bib.

Called by build_publications.py (pre-render). Plain Python (no networkx), deterministic.
Output: publications/_network.md (inline SVG + "Frequent co-authors" table), git-ignored.

Rules
- Nodes: authors of journal articles (CSL type article-journal = BibTeX @article).
- Edge: two authors share at least one article; thickness = number of shared articles.
- Node size = number of articles shared with Rodrigo; Rodrigo is fixed at the centre.
- Name merging: accents, case, hyphens and spaces are ignored in the family name; given
  names must agree on the first initial and, where both are written out, the first name.
  Same family name with a different first name or initial = different people (reported).
- Only Rodrigo and his TOP_N most frequent co-authors are drawn, all labelled; the
  "Frequent co-authors" table lists exactly the same people.
"""

import html
import math
import re
import unicodedata
from collections import defaultdict
from itertools import combinations

TOP_N = 5
ME_FAMILIES = {"gomezfell", "gomez"}          # Gomez-Fell, Gomez Fell, Gómez, Gomez


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def family_key(a):
    fam = (a.get("non-dropping-particle", "") + " " + a.get("family", a.get("literal", ""))).strip()
    return re.sub(r"[^a-z]", "", fold(fam))


def given_parts(a):
    return [p for p in re.split(r"[\s.]+", fold(a.get("given", ""))) if p]


def display(a):
    fam = (a.get("non-dropping-particle", "") + " " + a.get("family", "")).strip()
    return f"{a.get('given', '')} {fam}".strip()


def is_me(a):
    g = given_parts(a)
    return family_key(a) in ME_FAMILIES and bool(g) and g[0][0] == "r"


def build(meta, log):
    articles = [(k, e) for k, e in meta.items() if e.get("type") == "article-journal"]
    articles.sort(key=lambda ke: ((ke[1].get("issued", {}).get("date-parts") or [[0]])[0][0], ke[0]))

    # --- identify people -------------------------------------------------------
    people = {}                 # pid -> {"variants": set(), "names": [...], "first": str|None}
    by_family = defaultdict(list)
    paper_people = {}
    truncated = []
    for key, e in articles:
        pids = []
        for a in e.get("author", []):
            if a.get("literal", "").lower() in ("others", "et al.", "et al") or a.get("family", "").lower() == "others":
                truncated.append(key); continue
            if is_me(a):
                pid = "ME"
                people.setdefault(pid, {"variants": set(), "names": [], "first": "rodrigo"})
            else:
                fk, g = family_key(a), given_parts(a)
                first = g[0] if g and len(g[0]) > 1 else None
                initial = g[0][0] if g else ""
                pid = None
                for cand in by_family[fk]:
                    c = people[cand]
                    if c["initial"] != initial:
                        continue
                    if first and c["first"] and first != c["first"]:
                        continue
                    pid = cand; break
                if pid is None:
                    pid = f"{fk}:{initial}:{len(by_family[fk])}"
                    people[pid] = {"variants": set(), "names": [], "first": first, "initial": initial}
                    by_family[fk].append(pid)
                if first and not people[pid]["first"]:
                    people[pid]["first"] = first
            raw = f"{a.get('family', '')}, {a.get('given', '')}"
            people[pid]["variants"].add(raw)
            people[pid]["names"].append(display(a))
            if pid not in pids:
                pids.append(pid)
        paper_people[key] = pids

    # --- counts ----------------------------------------------------------------
    with_me = defaultdict(int)
    pair = defaultdict(int)
    for key, pids in paper_people.items():
        for p in pids:
            if "ME" in pids and p != "ME":
                with_me[p] += 1
        for a, b in combinations(sorted(pids), 2):
            pair[(a, b)] += 1

    def name(pid):   # most complete spelling (longest, prefers accents)
        return max(people[pid]["names"], key=lambda n: (len(n), sum(ord(c) > 127 for c in n)))

    # --- report merges and near-misses ------------------------------------------
    merges = [(name(p), sorted(v["variants"])) for p, v in people.items() if len(v["variants"]) > 1]
    log.append(f"network: {len(articles)} journal articles, {len(people) - 1} co-authors")
    for n, vs in sorted(merges):
        log.append(f"network: merged {' | '.join(vs)} -> {n}")
    for fk, pids in by_family.items():
        if len(pids) > 1:
            log.append("network: kept separate (same family name): " + " / ".join(name(p) for p in pids))
    for k in sorted(set(truncated)):
        log.append(f"network: WARNING truncated author list ('others') in @article {k}")

    # --- keep the top TOP_N collaborators --------------------------------------------
    # Rank by articles shared with Rodrigo; ties broken by the most recent shared article,
    # then by name. Ties at the cut-off are printed so they can be checked.
    year_of = {k: (meta[k].get("issued", {}).get("date-parts") or [[0]])[0][0] for k, _ in articles}
    latest = {p: max(year_of[k] for k in paper_people if p in paper_people[k]) for p in people if p != "ME"}
    ranked = sorted((p for p in people if p != "ME"), key=lambda p: (-with_me[p], -latest[p], name(p)))
    collab, dropped = ranked[:TOP_N], ranked[TOP_N:]
    cutoff = with_me[collab[-1]] if collab else 0
    tied_out = [p for p in dropped if with_me[p] == cutoff]
    log.append(f"network: showing top {len(collab)}: " + ", ".join(f"{name(p)} ({with_me[p]}, latest {latest[p]})" for p in collab))
    if tied_out:
        log.append(f"network: NOTE tied at {cutoff} shared articles but left out by the tie-break: "
                   + ", ".join(f"{name(p)} (latest {latest[p]})" for p in tied_out))
    log.append(f"network: {len(dropped)} other co-authors not drawn")
    keep = set(collab) | {"ME"}

    # --- layout: collaborators on one ring around Rodrigo -------------------------------
    pos = {"ME": (0.0, 0.0)}
    for i, p in enumerate(collab):
        t = -math.pi / 2 + 2 * math.pi * i / max(len(collab), 1)
        pos[p] = (140 * math.cos(t), 140 * math.sin(t))

    # --- SVG ------------------------------------------------------------------------
    def r(p):
        return 13 if p == "ME" else 4 + 3.2 * with_me[p]

    edges = []
    for (a, b), n in sorted(pair.items(), key=lambda x: x[1]):
        if a in keep and b in keep:
            (x1, y1), (x2, y2) = pos[a], pos[b]
            cls = "net-edge net-edge-me" if "ME" in (a, b) else "net-edge"
            edges.append(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-width="{0.8 + 1.6 * (n - 1):.1f}"/>')
    nodes, labels = [], []
    for p in collab + ["ME"]:
        x, y = pos[p]
        cls = "net-node net-me" if p == "ME" else "net-node net-frequent"
        tip = "Rodrigo Gomez-Fell" if p == "ME" else f"{name(p)}: {with_me[p]} shared article{'s' if with_me[p] != 1 else ''}"
        nodes.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r(p):.1f}"><title>{html.escape(tip)}</title></circle>')
        if p == "ME":
            labels.append(f'<text class="net-label net-label-me" x="0" y="{13 + 32}" text-anchor="middle">Me</text>')
        else:   # label on the outer side of each node so neighbouring labels never collide
            if abs(x) < 30:
                lx, ly, anchor = x, (y - r(p) - 12 if y < 0 else y + r(p) + 30), "middle"
            elif x < 0:
                lx, ly, anchor = x - r(p) - 10, y + 10, "end"
            else:
                lx, ly, anchor = x + r(p) + 10, y + 10, "start"
            labels.append(f'<text class="net-label" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">{html.escape(name(p))}</text>')

    desc = (f"Network of Rodrigo Gomez-Fell's {len(collab)} most frequent co-authors on journal articles, with "
            "Rodrigo at the centre: " + "; ".join(f"{name(p)}, {with_me[p]} shared articles" for p in collab)
            + ". Lines join people who wrote an article together; thicker lines mean more shared articles.")
    svg = f'''<figure class="collab-network">
<svg viewBox="-440 -195 880 360" role="img" aria-labelledby="net-title net-desc" preserveAspectRatio="xMidYMid meet">
<title id="net-title">Collaborator network from journal articles</title>
<desc id="net-desc">{html.escape(desc)}</desc>
<g class="net-edges">{"".join(edges)}</g>
<g class="net-nodes">{"".join(nodes)}</g>
<g class="net-labels">{"".join(labels)}</g>
</svg>
</figure>'''

    top = collab
    table = ["| Co-author | Shared journal articles |", "|---|---:|"]
    table += [f"| {name(p)} | {with_me[p]} |" for p in top]
    md = ("<!-- Generated by _scripts/network.py (via build_publications.py). Do not edit. -->\n\n"
          "```{=html}\n" + svg + "\n```\n\n"
          "### Frequent co-authors {.unnumbered}\n\n"
          + "\n".join(table) + "\n\n: Top 5 co-authors by number of journal articles shared with me {.net-table}\n")
    return md
