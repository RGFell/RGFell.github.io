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
- Collaborators with >= LABEL_MIN shared articles are labelled; others are small dots.
- At most MAX_NODES nodes; the least-connected are dropped (reported).
"""

import html
import math
import re
import unicodedata
from collections import defaultdict
from itertools import combinations

LABEL_MIN = 2
MAX_NODES = 40
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

    # --- cap ----------------------------------------------------------------------
    collab = sorted((p for p in people if p != "ME"), key=lambda p: (-with_me[p], name(p)))
    dropped = collab[MAX_NODES - 1:]
    collab = collab[:MAX_NODES - 1]
    log.append(f"network: {len(collab) + 1} nodes drawn, {len(dropped)} dropped"
               + (": " + ", ".join(name(p) for p in dropped) if dropped else ""))
    keep = set(collab) | {"ME"}

    # --- layout: radial, grouped by first shared paper ----------------------------
    order = [k for k, _ in articles]
    home = {p: min(i for i, k in enumerate(order) if p in paper_people[k]) for p in collab}
    inner = [p for p in collab if with_me[p] >= LABEL_MIN]
    outer = [p for p in collab if with_me[p] < LABEL_MIN]
    pos = {"ME": (0.0, 0.0)}

    def ring(members, radius, offset):
        members = sorted(members, key=lambda p: (home[p], name(p)))
        n = len(members)
        for i, p in enumerate(members):
            t = offset + 2 * math.pi * i / max(n, 1)
            pos[p] = (radius * math.cos(t), radius * math.sin(t))

    ring(inner, 120, -math.pi / 2)
    ring(outer, 205, -math.pi / 2 + math.pi / max(len(outer), 1))

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
        cls = "net-node net-me" if p == "ME" else ("net-node net-frequent" if with_me[p] >= LABEL_MIN else "net-node net-other")
        tip = "Rodrigo Gomez-Fell" if p == "ME" else f"{name(p)}: {with_me[p]} shared article{'s' if with_me[p] != 1 else ''}"
        nodes.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r(p):.1f}"><title>{html.escape(tip)}</title></circle>')
        if p == "ME":
            labels.append(f'<text class="net-label net-label-me" x="0" y="{13 + 26}" text-anchor="middle">Me</text>')
        elif with_me[p] >= LABEL_MIN:
            d = math.hypot(x, y) or 1
            lx, ly = x + (x / d) * (r(p) + 6), y + (y / d) * (r(p) + 6) + 5
            anchor = "start" if x > 20 else "end" if x < -20 else "middle"
            if anchor == "middle":
                ly += 8 if y > 0 else -4
            labels.append(f'<text class="net-label" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">{html.escape(name(p))}</text>')

    n_lab = sum(1 for p in collab if with_me[p] >= LABEL_MIN)
    desc = (f"Network of co-authors on {len(articles)} journal articles. Rodrigo Gomez-Fell is at the centre. "
            f"{n_lab} people with two or more shared articles are labelled on the inner ring; "
            f"{len(collab) - n_lab} people with one shared article are small unlabelled dots on the outer ring. "
            "Lines join people who wrote an article together; thicker lines mean more shared articles.")
    svg = f'''<figure class="collab-network">
<svg viewBox="-410 -250 820 500" role="img" aria-labelledby="net-title net-desc" preserveAspectRatio="xMidYMid meet">
<title id="net-title">Collaborator network from journal articles</title>
<desc id="net-desc">{html.escape(desc)}</desc>
<g class="net-edges">{"".join(edges)}</g>
<g class="net-nodes">{"".join(nodes)}</g>
<g class="net-labels">{"".join(labels)}</g>
</svg>
</figure>'''

    top = collab[:10]
    table = ["| Co-author | Shared journal articles |", "|---|---:|"]
    table += [f"| {name(p)} | {with_me[p]} |" for p in top]
    md = ("<!-- Generated by _scripts/network.py (via build_publications.py). Do not edit. -->\n\n"
          "```{=html}\n" + svg + "\n```\n\n"
          "### Frequent co-authors {.unnumbered}\n\n"
          + "\n".join(table) + "\n\n: Top 10 co-authors by number of journal articles shared with me {.net-table}\n")
    return md
