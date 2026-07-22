"""TrackMarshal designer v1 — inventory-constrained closed-layout generation.

Usage:
  python3 designer.py --inventory inv.json [--room-w 4200 --room-l 3500] [--top 3]

inv.json: {"straight/full": 25, "curve/r1-60": 11, ...} — piece units, solver-ready
slugs only (banked/turnouts are ignored with a warning). Output: JSON proposals,
each with sequence (Layout encoding), lengths, footprint, and unused pieces.
"""

import argparse
import json
import math

import geometry as g

MODEL = "exact-nesting"


def solver_ready(inv):
    ok, skipped = {}, {}
    for slug, n in inv.items():
        if slug in g.DATA["pieceTypes"]:
            ok[slug] = ok.get(slug, 0) + n
        else:
            skipped[slug] = n
    return ok, skipped


def curve_subsets(inv):
    """Yield curve-count dicts whose signed angles can net ±360."""
    slugs = [s for s in inv if g.DATA["pieceTypes"][s]["kind"] == "curve"]
    # enumerate counts per curve slug (small domains), check angle feasibility
    def rec(i, cur):
        if i == len(slugs):
            counts = {s: n for s, n in cur.items() if n}
            if not counts:
                return
            feasible, _ = g.angle_feasible(counts)
            if feasible:
                yield dict(counts)
            return
        s = slugs[i]
        for n in range(inv[s] + 1):
            cur[s] = n
            yield from rec(i + 1, cur)
        cur.pop(s, None)
    yield from rec(0, {})


def propose(inv, room=None, top=3, iters=250_000):
    inv, skipped = solver_ready(inv)
    straights = {s: n for s, n in inv.items() if g.DATA["pieceTypes"][s]["kind"] == "straight"}
    proposals = []
    subsets = sorted(curve_subsets(inv),
                     key=lambda c: -sum(n for n in c.values()))
    for curves in subsets[:12]:
        # try to use as many straights as possible, backing off on misses
        s_full = straights.get("straight/full", 0)
        for use_full in range(s_full, max(s_full - 6, -1), -1):
            counts = dict(curves)
            if use_full:
                counts["straight/full"] = use_full
            for extra in ("straight/third", "straight/quarter"):
                if straights.get(extra):
                    counts[extra] = straights[extra]
            bbox = (room["wMm"], room["lMm"]) if room else None
            seq = g.search_closed(counts, MODEL, max_bbox_mm=bbox, iters=iters)
            if not seq:
                # fractional straights often block closure; retry without them
                counts2 = {k: v for k, v in counts.items() if not k.startswith("straight/t") and not k.startswith("straight/q")}
                seq = g.search_closed(counts2, MODEL, max_bbox_mm=bbox, iters=iters)
                counts = counts2 if seq else counts
            if seq:
                la, lb = g.lane_lengths(seq, MODEL)
                w, d = g.footprint(seq, MODEL)
                if room and (min(w, d) > min(room["wMm"], room["lMm"]) or max(w, d) > max(room["wMm"], room["lMm"])):
                    continue
                used = {}
                for slug, _ in seq:
                    used[slug] = used.get(slug, 0) + 1
                proposals.append({
                    "sequence": [s if h == 0 else f"{s}:{'L' if h > 0 else 'R'}" for s, h in seq],
                    "laneLengthsMm": [round(la, 1), round(lb, 1)],
                    "centerlineM": round((la + lb) / 2000, 3),
                    "laneImbalanceMm": round(abs(la - lb), 1),
                    "footprintMm": [round(w), round(d)],
                    "pieceUsage": used,
                    "unusedPieces": {s: inv[s] - used.get(s, 0) for s in inv if inv[s] - used.get(s, 0) > 0},
                })
                break
        if len(proposals) >= top * 3:
            break
    proposals.sort(key=lambda p: (-p["centerlineM"], p["laneImbalanceMm"]))
    if skipped:
        print(json.dumps({"warning": "ignored non-solver-ready pieces", "skipped": skipped}))
    return proposals[:top]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--room-w", type=float, default=None, help="room width mm")
    ap.add_argument("--room-l", type=float, default=None, help="room length mm")
    ap.add_argument("--top", type=int, default=3)
    args = ap.parse_args()
    inv = json.loads(open(args.inventory).read())
    room = {"wMm": args.room_w, "lMm": args.room_l} if args.room_w and args.room_l else None
    print(json.dumps(propose(inv, room, args.top), indent=2))
