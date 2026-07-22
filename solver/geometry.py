"""TrackMarshal closure solver — SE(2) composition over Carrera 124/132 piece geometry.

Every piece is a rigid-body transform entry->exit on the centerline. Both piece ends
are perpendicular to the centerline, so a layout is a sequence of (pieceType, hand)
where hand is L/R for curves. Closure: end pose == start pose (mod 360 heading).
"""

import json
import math
import random
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data.json").read_text())
LANE = DATA["laneOffsetMm"]
HALF_W = DATA["trackHalfWidthMm"]


def resolve_piece(slug, model):
    """-> (lengthMm_or_None, radiusMm_or_None, arcDeg_or_None) under a radius model."""
    pt = DATA["pieceTypes"][slug]
    if pt["kind"] == "straight":
        return pt["lengthMm"], None, None
    radii = DATA["radiusModels"][model]
    return None, radii[pt["radiusKey"]], pt["arcDeg"]


def step(pose, slug, hand, model):
    """Advance pose (x, y, heading_rad) through one piece. hand: +1 left, -1 right."""
    x, y, th = pose
    length, radius, arc = resolve_piece(slug, model)
    if length is not None:
        return (x + length * math.cos(th), y + length * math.sin(th), th)
    a = math.radians(arc) * hand
    # local exit offset for a curve entered along +x
    dx = radius * math.sin(math.radians(arc))
    dy = hand * radius * (1 - math.cos(math.radians(arc)))
    return (
        x + dx * math.cos(th) - dy * math.sin(th),
        y + dx * math.sin(th) + dy * math.cos(th),
        th + a,
    )


def run(seq, model):
    pose = (0.0, 0.0, 0.0)
    for slug, hand in seq:
        pose = step(pose, slug, hand, model)
    return pose


def is_closed(seq, model, tol_mm=1.0, tol_deg=0.5):
    x, y, th = run(seq, model)
    turns = math.degrees(th) % 360.0
    ang_ok = min(turns, 360.0 - turns) <= tol_deg
    return math.hypot(x, y) <= tol_mm and ang_ok


def centerline_length(counts, model):
    """Length from a piece-count multiset alone (orientation-independent)."""
    total = 0.0
    for slug, n in counts.items():
        length, radius, arc = resolve_piece(slug, model)
        total += n * (length if length is not None else radius * math.radians(arc))
    return total


def lane_lengths(seq, model):
    """Per-slot lengths. Lane A is +LANE left of centerline: inner on left turns."""
    la = lb = 0.0
    for slug, hand in seq:
        length, radius, arc = resolve_piece(slug, model)
        if length is not None:
            la += length
            lb += length
        else:
            rad = math.radians(arc)
            la += (radius - hand * LANE) * rad
            lb += (radius + hand * LANE) * rad
    return la, lb


def footprint(seq, model, samples_per_piece=8):
    """Bounding box of the track surface (centerline swept +-HALF_W)."""
    xs, ys = [], []
    pose = (0.0, 0.0, 0.0)
    for slug, hand in seq:
        length, radius, arc = resolve_piece(slug, model)
        for i in range(samples_per_piece + 1):
            f = i / samples_per_piece
            if length is not None:
                px = pose[0] + f * length * math.cos(pose[2])
                py = pose[1] + f * length * math.sin(pose[2])
                ph = pose[2]
            else:
                a = math.radians(arc) * f
                dx = radius * math.sin(a)
                dy = hand * radius * (1 - math.cos(a))
                px = pose[0] + dx * math.cos(pose[2]) - dy * math.sin(pose[2])
                py = pose[1] + dx * math.sin(pose[2]) + dy * math.cos(pose[2])
                ph = pose[2] + a * hand
            for side in (-HALF_W, HALF_W):
                xs.append(px - side * math.sin(ph))
                ys.append(py + side * math.cos(ph))
        pose = step(pose, slug, hand, model)
    return (max(xs) - min(xs), max(ys) - min(ys))


def angle_feasible(counts):
    """Does a left/right assignment of the curves reach net +-360 deg?
    Subset-style DP over 15-degree units."""
    arcs = []
    for slug, n in counts.items():
        pt = DATA["pieceTypes"][slug]
        if pt["kind"] == "curve":
            arcs += [pt["arcDeg"] // 15] * n
    total = sum(arcs)
    reachable = {0}
    for a in arcs:
        reachable = {r + a for r in reachable} | {r - a for r in reachable}
    return (24 in reachable) or (-24 in reachable), total * 15


def expand_parts(parts):
    """Official plan parts dict {partNo: count} -> pieceType counts.
    Normalizes 8-digit full SKUs (20020509) to the common 5-digit form (20509)."""
    counts = {}
    m = DATA["partToPieceType"]
    for part, n in parts.items():
        key = part[3:] if len(part) == 8 and part.startswith("200") else part
        slug = m.get(key)
        if slug is None:
            raise KeyError(f"no pieceType mapping for part {part}")
        counts[slug] = counts.get(slug, 0) + n
    return counts


def search_closed(counts, model, max_bbox_mm=None, iters=200_000, seed=7, tol_mm=0.5):
    """Randomized construction with heading-home bias; returns a closed sequence or None.
    A found sequence PROVES the piece set can close under the model; failure proves nothing.
    """
    rng = random.Random(seed)
    bag = []
    for slug, n in counts.items():
        bag += [slug] * n
    best = None
    for attempt in range(iters // max(len(bag), 1)):
        rng.shuffle(bag)
        pose = (0.0, 0.0, 0.0)
        seq = []
        ok = True
        remaining = list(bag)
        while remaining:
            # bias: prefer moves that shrink distance home late in the build
            frac = 1 - len(remaining) / len(bag)
            choices = []
            for i, slug in enumerate(remaining[: 12]):
                hands = (0,) if DATA["pieceTypes"][slug]["kind"] == "straight" else (1, -1)
                for h in hands:
                    nx, ny, nth = step(pose, slug, h, model)
                    d = math.hypot(nx, ny)
                    choices.append((d, i, slug, h))
            if frac > 0.55:
                choices.sort(key=lambda c: c[0])
                pick = choices[0] if rng.random() < 0.7 else rng.choice(choices[: 4])
            else:
                pick = rng.choice(choices)
            _, i, slug, h = pick
            remaining.pop(i)
            seq.append((slug, h))
            pose = step(pose, slug, h, model)
        if is_closed(seq, model, tol_mm=tol_mm):
            if max_bbox_mm:
                w, d = footprint(seq, model)
                if max(w, d) > max(max_bbox_mm) + 50 or min(w, d) > min(max_bbox_mm) + 50:
                    continue
            return seq
    return best
