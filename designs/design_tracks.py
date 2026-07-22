"""Design engine for Corey's four showcase Carrera D132 layouts.

Built on the adjudicated geometry in wjcorey/carrera-track + slotcars/carrera-catalog:
r1 = 297 mm centerline (60 deg pieces), banked r3 = 693 mm (30 deg, flat plan-view
approximation, solverReady=false in catalog), straights 345 / 115 / 86.25 mm,
lane offset +/-49.5 mm, track half width 99 mm.

Sequences use the repo Layout encoding: '<pieceTypeSlug>[:L|R]'.
"""

import itertools
import json
import math
from pathlib import Path

R1 = 297.0
R3B = 693.0
LANE = 49.5
HALFW = 99.0

# slug -> ('s', length) | ('c', radius, arc_deg)
PIECES = {
    "straight/full": ("s", 345.0),
    "straight/third": ("s", 115.0),
    "straight/quarter": ("s", 86.25),
    "digital/control-unit": ("s", 345.0),
    "digital/charging-straight": ("s", 345.0),
    "digital/lane-change-straight": ("s", 345.0),
    "digital/double-lane-change": ("s", 690.0),
    "digital/lane-change-left": ("s", 690.0),
    "special/ramp-concave": ("s", 345.0),
    "special/ramp-convex": ("s", 345.0),
    "curve/r1-60": ("c", R1, 60.0),
    "digital/lane-change-curve-right-oi": ("c", R1, 60.0),
    "curve-banked/r3-30": ("c", R3B, 30.0),
}

INVENTORY = {
    "straight/full": 16,
    "straight/third": 2,
    "straight/quarter": 2,
    "digital/control-unit": 1,
    "digital/charging-straight": 1,
    "digital/lane-change-straight": 1,
    "digital/double-lane-change": 2,
    "digital/lane-change-left": 1,
    "special/ramp-concave": 2,
    "special/ramp-convex": 2,
    "curve/r1-60": 10,
    "digital/lane-change-curve-right-oi": 1,  # right-hand only
    "curve-banked/r3-30": 6,
}


def parse(item):
    """'slug[:L|R]' -> (slug, hand) with hand +1 left / -1 right / 0 straight."""
    if item.endswith(":L"):
        return item[:-2], 1
    if item.endswith(":R"):
        return item[:-2], -1
    return item, 0


def step(pose, slug, hand):
    x, y, th = pose
    p = PIECES[slug]
    if p[0] == "s":
        return (x + p[1] * math.cos(th), y + p[1] * math.sin(th), th)
    _, r, arc = p
    a = math.radians(arc)
    dx = r * math.sin(a)
    dy = hand * r * (1 - math.cos(a))
    return (
        x + dx * math.cos(th) - dy * math.sin(th),
        y + dx * math.sin(th) + dy * math.cos(th),
        th + a * hand,
    )


def run(seq):
    pose = (0.0, 0.0, 0.0)
    for item in seq:
        pose = step(pose, *parse(item))
    return pose


def closure_error(seq):
    x, y, th = run(seq)
    turns = math.degrees(th) % 360.0
    return math.hypot(x, y), min(turns, 360.0 - turns)


def net_turn_deg(seq):
    return round(math.degrees(run(seq)[2]))


def total_length(seq):
    t = 0.0
    for item in seq:
        slug, _ = parse(item)
        p = PIECES[slug]
        t += p[1] if p[0] == "s" else p[1] * math.radians(p[2])
    return t


def lane_lengths(seq):
    la = lb = 0.0  # la: left slot (+LANE), lb: right slot
    for item in seq:
        slug, hand = parse(item)
        p = PIECES[slug]
        if p[0] == "s":
            la += p[1]
            lb += p[1]
        else:
            _, r, arc = p
            rad = math.radians(arc)
            la += (r - hand * LANE) * rad
            lb += (r + hand * LANE) * rad
    return la, lb


def sample_path(seq, per=10):
    """[(x, y, heading, slug, hand, piece_index, frac)] along centerline."""
    pts = []
    pose = (0.0, 0.0, 0.0)
    for i, item in enumerate(seq):
        slug, hand = parse(item)
        p = PIECES[slug]
        for k in range(per + 1):
            f = k / per
            if p[0] == "s":
                px = pose[0] + f * p[1] * math.cos(pose[2])
                py = pose[1] + f * p[1] * math.sin(pose[2])
                ph = pose[2]
            else:
                _, r, arc = p
                a = math.radians(arc) * f
                dx = r * math.sin(a)
                dy = hand * r * (1 - math.cos(a))
                px = pose[0] + dx * math.cos(pose[2]) - dy * math.sin(pose[2])
                py = pose[1] + dx * math.sin(pose[2]) + dy * math.cos(pose[2])
                ph = pose[2] + a * hand
            pts.append((px, py, ph, slug, hand, i, f))
        pose = step(pose, slug, hand)
    return pts


def footprint(seq):
    pts = sample_path(seq)
    xs, ys = [], []
    for px, py, ph, *_ in pts:
        for side in (-HALFW, HALFW):
            xs.append(px - side * math.sin(ph))
            ys.append(py + side * math.cos(ph))
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def bom(seq):
    counts = {}
    for item in seq:
        slug, _ = parse(item)
        counts[slug] = counts.get(slug, 0) + 1
    return counts


def check_inventory(seq):
    problems = []
    for slug, n in bom(seq).items():
        if n > INVENTORY.get(slug, 0):
            problems.append(f"{slug}: need {n}, own {INVENTORY.get(slug, 0)}")
    return problems


def self_intersections(seq, allow_zones=()):
    """Pairs of far-apart-in-sequence points that come closer than 190 mm.
    allow_zones: list of (cx, cy, radius) circles where crossing is intended."""
    pts = sample_path(seq, per=6)
    n = len(pts)
    step_len = total_length(seq) / n
    bad = []
    for i in range(n):
        for j in range(i + 1, n):
            if (j - i) * step_len < 700 or (n - (j - i)) * step_len < 700:
                continue
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if d < 190:
                x, y = pts[i][0], pts[i][1]
                if any(math.hypot(x - cx, y - cy) < rr for cx, cy, rr in allow_zones):
                    continue
                bad.append((round(x), round(y), round(d)))
    return bad[:8]


# ---------------------------------------------------------------- designs

def t1_hexagon_gp():
    """Longest: alternating banked/flat-corner hexagon. Exact closure by the
    alternating-radii identity: every side's corner-tangent sum is (297+693)/sqrt(3),
    so the equiangular-hexagon closure condition reduces to rational side equations
      (i) B + C = E + F      (ii) A - D = E - B  (and hence C = F + (A - D))
    Sides: A=2070 front, B=1725 ramp-hump climb, C=1236.25, D=2415 back,
    E=1380, F=1581.25. Both bus-stop jogs paired front/back so their sqrt(3)
    advances cancel."""
    F, T, Q = "straight/full", "straight/third", "straight/quarter"
    L, R = "curve/r1-60:L", "curve/r1-60:R"
    BK = "curve-banked/r3-30:L"
    seq = []
    # Side A - front straight, heading 0. S/F, Control Unit, lane-change straight.
    seq += ["digital/control-unit", "digital/lane-change-straight", F]
    seq += [L, R]                                    # bus stop out (jog +297 left)
    seq += ["digital/charging-straight", F]
    seq += ["digital/lane-change-curve-right-oi:R", L]  # bus stop back (LC flipper!)
    seq += [F]
    seq += [BK, BK]                                  # T1 banked sweeper (60)
    seq += [F, "special/ramp-concave", "special/ramp-convex",
            "special/ramp-convex", "special/ramp-concave"]   # Side B: Everest hump
    seq += [L]                                       # T2 flat corner
    seq += [F, T, F, Q, F]                           # Side C
    seq += [BK, BK]                                  # T3 banked sweeper
    # Side D - back straight, heading 180
    seq += ["digital/double-lane-change"]
    seq += [L, R]                                    # jog out
    seq += ["digital/lane-change-left", F]
    seq += [R, L]                                    # jog back
    seq += ["digital/double-lane-change"]
    seq += [L]                                       # T4 flat corner
    seq += [F, F, F, F]                              # Side E
    seq += [BK, BK]                                  # T5 banked sweeper
    seq += [F, T, F, Q, F, F]                        # Side F
    seq += [L]                                       # T6 flat corner -> S/F
    return seq


def t2_gauntlet():
    """Most technical: double-hairpin serpentine with two chicane jogs threading
    three parallel legs 297 mm apart. Exact closure: east legs + east jog advance
    = west leg + west jog advance; jog sqrt(3) advances cancel one-per-heading."""
    F, T, Q = "straight/full", "straight/third", "straight/quarter"
    L, R = "curve/r1-60:L", "curve/r1-60:R"
    seq = []
    seq += ["digital/control-unit", "digital/lane-change-straight", F]  # leg 1 east, y=0
    seq += [L, L, L]                                  # H1 hairpin (east end)
    seq += [Q]                                        # leg 2 west, y=594
    seq += [R, L]                                     # jog outward to y=891
    seq += ["digital/double-lane-change", T, "digital/double-lane-change", F]
    seq += [L, L, L]                                  # H2 hairpin (west end) -> y=297
    seq += [T]                                        # leg 3 east, y=297
    seq += ["digital/lane-change-curve-right-oi:R", L]  # jog down to y=0 (LC flick)
    seq += [Q, F, F]
    return seq


def walks(start_heading, end_headings, max_pieces, allow_banked=False):
    """Turn sequences: items 'L'/'R' (R1 60) and optionally 'bL'/'bR'
    (banked 60-deg corner = 2 x 30-deg r693). Headings stay on the 60-lattice."""
    out = []

    def rec(heading, seq, used_banked):
        if seq and heading % 360 in end_headings:
            out.append(tuple(seq))
        if len(seq) >= max_pieces:
            return
        rec(heading + 60, seq + ["L"], used_banked)
        rec(heading - 60, seq + ["R"], used_banked)
        if allow_banked and used_banked < 3:
            rec(heading + 60, seq + ["bL"], used_banked + 1)
            rec(heading - 60, seq + ["bR"], used_banked + 1)

    rec(start_heading, [], 0)
    return out


TOKEN_PIECES = {
    "L": ["curve/r1-60:L"],
    "R": ["curve/r1-60:R"],
    "bL": ["curve-banked/r3-30:L"] * 2,
    "bR": ["curve-banked/r3-30:R"] * 2,
}
TOKEN_TURN = {"L": 60, "R": -60, "bL": 60, "bR": -60}


def token_r1_count(tokens):
    return sum(1 for t in tokens if t in ("L", "R"))


def stock_values(max_len=2400):
    """Achievable plain-straight totals (full/third/quarter) -> piece list."""
    vals = {}
    for nf in range(8):
        for nt in range(3):
            for nq in range(3):
                length = 345 * nf + 115 * nt + 86.25 * nq
                if 0 < length <= max_len:
                    key = round(length * 100)
                    pieces = (["straight/full"] * nf + ["straight/third"] * nt
                              + ["straight/quarter"] * nq)
                    if key not in vals or len(pieces) < len(vals[key]):
                        vals[key] = pieces
    return vals


STOCK = stock_values()


def crossing_info(seq):
    """Where does the grade path cross the deck line (y=0 within |x|<=700)?
    Returns (x_cross, angle_deg), ignoring the deck pieces themselves
    (first 2 / last 2 pieces of the sequence)."""
    pts = sample_path(seq, per=12)
    best = None
    n_pieces = len(seq)
    for (x1, y1, h1, s1, hd1, i1, f1), (x2, y2, *_2) in zip(pts, pts[1:]):
        if i1 < 2 or i1 >= n_pieces - 2:
            continue
        if y1 == 0 and y2 == 0:
            continue
        if (y1 <= 0 < y2) or (y2 <= 0 < y1):
            f = y1 / (y1 - y2)
            xc = x1 + f * (x2 - x1)
            if abs(xc) <= 700:
                cand = (abs(xc), xc, math.degrees(h1) % 180)
                if best is None or cand[0] < best[0]:
                    best = cand
    return (best[1], best[2]) if best else None


def arc_disp_exact(token, heading_deg):
    """Displacement of an arc token entered at a 60-lattice heading, split as
    (x_rat, x_irr, y_rat, y_irr) with value = rat + irr*sqrt(3). Exact for
    halves-based trig values."""
    h = heading_deg % 360
    HALF = {0: (1.0, 0.0), 60: (0.5, 0.0), 120: (-0.5, 0.0), 180: (-1.0, 0.0),
            240: (-0.5, 0.0), 300: (0.5, 0.0)}
    SINE = {0: (0.0, 0.0), 60: (0.0, 0.5), 120: (0.0, 0.5), 180: (0.0, 0.0),
            240: (0.0, -0.5), 300: (0.0, -0.5)}
    c, s = HALF[h], SINE[h]  # cos, sin as (rat, irr)
    r = R1 if token in ("L", "R") else R3B
    hand = 1 if token in ("L", "bL") else -1
    # 60-deg arc: local dx = r*sin60 = r*(0, .5), dy = hand*r*(1-cos60)
    dxl, dyl = (0.0, 0.5 * r), (hand * 0.5 * r, 0.0)

    def mul(a, b):  # (rat,irr)*(rat,irr) with irr*irr -> 3*rat
        return (a[0] * b[0] + 3.0 * a[1] * b[1], a[0] * b[1] + a[1] * b[0])

    def sub(a, b):
        return (a[0] - b[0], a[1] - b[1])

    def add(a, b):
        return (a[0] + b[0], a[1] + b[1])

    dx = sub(mul(dxl, c), mul(dyl, s))
    dy = add(mul(dxl, s), mul(dyl, c))
    return dx, dy


def token_walk_ok(tokens, start_heading):
    """Sum exact arc displacements; return (x_irr, y_rat) sums + heading list."""
    h = start_heading
    xi = yr = 0.0
    headings = []
    for t in tokens:
        headings.append(h % 360)
        dx, dy = arc_disp_exact(t, h)
        xi += dx[1]
        yr += dy[0]
        h += TOKEN_TURN[t]
    return xi, yr, headings, h % 360


def slot_headings(tokA, tokB, endH):
    """Headings of every straight-leg slot around the circuit.
    Slots: after descend (h0), between A tokens, crossing (endH),
    between B tokens, before ascend (h0)."""
    slots = [("a", 0, 0.0)]
    h = 0
    for i, t in enumerate(tokA):
        h += TOKEN_TURN[t]
        slots.append(("a", i + 1, h % 360))
    slots.append(("x", 0, endH))  # crossing leg through X
    h = endH
    for i, t in enumerate(tokB):
        h += TOKEN_TURN[t]
        slots.append(("b", i + 1, h % 360))
    return slots


def assemble_fig8(tokA, tokB, slot_fills):
    """slot_fills: dict slot_index -> piece list. Slot order per slot_headings."""
    seq = ["special/ramp-convex", "special/ramp-concave"]
    idx = 0
    seq += slot_fills.get(idx, [])
    for t in tokA:
        seq += TOKEN_PIECES[t]
        idx += 1
        seq += slot_fills.get(idx, [])
    idx += 1
    seq += slot_fills.get(idx, [])  # crossing slot (same index as last a-slot +1)
    for t in tokB:
        seq += TOKEN_PIECES[t]
        idx += 1
        seq += slot_fills.get(idx, [])
    seq += ["special/ramp-concave", "special/ramp-convex"]
    return seq


def search_fig8(allow_banked, require_net_zero, label, max_tokens=6,
                extra_fill_opts=None, limit_print=12):
    """Global search: token pairs with exact-cancelling arc sums, then legs.
    Two slots are solved exactly (crossing slot + one independent slot);
    other slots enumerated from a small option set."""
    results = []
    end_opts = (60, 120, 240, 300)
    fill_opts = extra_fill_opts or [
        [], ["straight/full"], ["straight/full", "straight/full"],
        ["digital/double-lane-change"], ["straight/third"],
    ]
    for endH in end_opts:
        walksA = walks(0, {endH}, max_tokens, allow_banked)
        walksB = walks(endH, {0}, max_tokens, allow_banked)
        pre = []
        for tokA in walksA:
            xiA, yrA, _, _ = token_walk_ok(tokA, 0)
            pre.append((tokA, xiA, yrA))
        preB = []
        for tokB in walksB:
            xiB, yrB, _, _ = token_walk_ok(tokB, endH)
            preB.append((tokB, xiB, yrB))
        for tokA, xiA, yrA in pre:
            for tokB, xiB, yrB in preB:
                if abs(xiA + xiB) > 1e-9 or abs(yrA + yrB) > 1e-9:
                    continue
                n_r1 = token_r1_count(tokA) + token_r1_count(tokB)
                n_bk = sum(2 for t in tokA + tokB if t in ("bL", "bR"))
                if n_r1 > 11 or n_bk > 6:
                    continue
                if allow_banked and n_bk == 0:
                    continue
                net = sum(TOKEN_TURN[t] for t in tokA + tokB)
                if require_net_zero and net != 0:
                    continue
                if not require_net_zero and abs(net) != 360:
                    continue
                slots = slot_headings(tokA, tokB, endH)
                n_slots = len(slots)
                cross_idx = len(tokA) + 1
                # second solved slot: independent heading from crossing
                for solve2 in range(n_slots):
                    if solve2 == cross_idx:
                        continue
                    h2 = slots[solve2][2]
                    if h2 % 180 == endH % 180:
                        continue
                    # enumerate fills for up to two other slots
                    other = [i for i in range(n_slots)
                             if i not in (cross_idx, solve2)]
                    for extra1, extra2 in itertools.combinations(
                            other + [None], 2):
                        for f1 in (fill_opts if extra1 is not None else [[]]):
                            for f2 in (fill_opts if extra2 is not None else [[]]):
                                fills = {}
                                if extra1 is not None and f1:
                                    fills[extra1] = f1
                                if extra2 is not None and f2:
                                    fills[extra2] = f2
                                r = _solve_and_check(
                                    tokA, tokB, endH, slots, cross_idx,
                                    solve2, fills, require_net_zero)
                                if r:
                                    results.append(r)
    dedup = {}
    for r in results:
        key = (r["tokens"], round(r["len"]))
        if key not in dedup or r["score"] > dedup[key]["score"]:
            dedup[key] = r
    results = sorted(dedup.values(), key=lambda r: -r["score"])
    print(f"\n== {label}: {len(results)} candidates ==")
    for r in results[:limit_print]:
        print(f"  {r['tokens']} endH={r['endH']} len={r['len']:.0f}"
              f" net={r['net']} cross_x={r['cross_x']} angle={r['cross_angle']}"
              f" foot={r['foot']} pieces={r['pieces']} score={r['score']:.1f}")
    return results


def _solve_and_check(tokA, tokB, endH, slots, cross_idx, solve2, fills,
                     require_net_zero):
    # linear solve for crossing-slot and solve2-slot lengths
    base = assemble_fig8(tokA, tokB, fills)
    ex, ey, eth = run(base)
    h1 = math.radians(slots[cross_idx][2])
    h2 = math.radians(slots[solve2][2])
    u1 = (math.cos(h1), math.sin(h1))
    u2 = (math.cos(h2), math.sin(h2))
    det = u1[0] * u2[1] - u1[1] * u2[0]
    if abs(det) < 1e-9:
        return None
    s1 = (-ex * u2[1] + ey * u2[0]) / det
    s2 = (-u1[0] * ey + u1[1] * ex) / det
    if s1 < 344.9 or s2 < -0.001:
        return None
    k1, k2 = round(s1 * 100), round(s2 * 100)
    if k1 not in STOCK or (k2 != 0 and k2 not in STOCK):
        return None
    all_fills = dict(fills)
    all_fills[cross_idx] = STOCK[k1]
    if k2:
        all_fills[solve2] = fills.get(solve2, []) + STOCK[k2]
    seq = assemble_fig8(tokA, tokB, all_fills)
    derr, terr = closure_error(seq)
    if derr > 0.01 or terr > 0.01:
        return None
    if check_inventory(seq):
        return None
    cross = crossing_info(seq)
    if not cross or abs(cross[0]) > 280:
        return None
    xz, _ = cross
    if self_intersections(seq, allow_zones=[(xz, 0, 460)]):
        return None
    _, _, w, h = footprint(seq)
    if max(w, h) > 4600:
        return None
    length = total_length(seq)
    net = net_turn_deg(seq)
    # score: prefer length, small crossing offset, compactness
    score = length / 1000.0 - abs(cross[0]) / 100.0 - max(w, h) / 2000.0
    return {
        "tokens": ("".join(tokA), "".join(tokB)), "endH": endH,
        "seq": seq, "cross_x": round(cross[0], 1),
        "cross_angle": round(cross[1], 1), "len": length,
        "net": net, "foot": (round(w), round(h)),
        "pieces": len(seq), "score": score,
    }


if __name__ == "__main__":
    for name, seq in [("T1 Hexagon GP", t1_hexagon_gp()), ("T2 Gauntlet", t2_gauntlet())]:
        derr, terr = closure_error(seq)
        la, lb = lane_lengths(seq)
        x0, y0, w, h = footprint(seq)
        print(f"\n== {name} ==")
        print(f"closure: {derr:.3f} mm, {terr:.3f} deg | net turn {net_turn_deg(seq)}")
        print(f"length {total_length(seq):.1f} mm | lanes {la:.1f} / {lb:.1f} (d={abs(la-lb):.1f})")
        print(f"footprint {w:.0f} x {h:.0f} mm | pieces {len(seq)}")
        print("inventory problems:", check_inventory(seq) or "none")
        print("self-intersections:", self_intersections(seq) or "none")

    t4 = search_fig8(False, True, 11, "T4 fair figure-8 (R1 only, net 0)")
    t3 = search_fig8(True, False, 11, "T3 cool figure-8 (banked block)")
