"""Run the official-layout oracle: adjudicate radius models against Carrera's own
published circuit plans (see fixtures/official-circuits.json) and self-consistency
identities. README decision D5: this replaces physical measurement."""

import json
import math
from pathlib import Path

import geometry as g

FIXTURES = Path(__file__).parent / "fixtures" / "official-circuits.json"


def circle_identities():
    print("== self-consistency: full circles close exactly ==")
    for slug, per_circle in [
        ("curve/r1-60", 6), ("curve/r1-30", 12), ("curve/r2-30", 12),
        ("curve/r3-30", 12), ("curve/r4-15", 24),
    ]:
        for model in g.DATA["radiusModels"]:
            seq = [(slug, 1)] * per_circle
            assert g.is_closed(seq, model, tol_mm=1e-6), (slug, model)
    print("   all radius/angle circle identities pass under both models\n")


def oval_smoke():
    print("== smoke: minimal oval (6x r1-60 + 4 straights) ==")
    seq = ([("straight/full", 0)] * 2 + [("curve/r1-60", 1)] * 3
           + [("straight/full", 0)] * 2 + [("curve/r1-60", 1)] * 3)
    for model in g.DATA["radiusModels"]:
        assert g.is_closed(seq, model, tol_mm=1e-6), model
        la, lb = g.lane_lengths(seq, model)
        w, d = g.footprint(seq, model)
        print(f"   {model:18s} lanes {la/1000:.3f}/{lb/1000:.3f} m, "
              f"footprint {w/1000:.2f} x {d/1000:.2f} m")
    print()


def official_lengths():
    if not FIXTURES.exists():
        print("!! fixtures/official-circuits.json not present yet — skipping")
        return
    fx = json.loads(FIXTURES.read_text())
    circuits = [c for c in fx["circuits"] if c.get("trackLengthM")]
    models = list(g.DATA["radiusModels"])
    print("== official plans: centerline length vs published length ==")
    errs = {m: [] for m in models}
    for c in circuits:
        counts = g.expand_parts(c["parts"])
        feasible, total_arc = g.angle_feasible(counts)
        line = f"   {c['name']:<14s} official {c['trackLengthM']:7.3f} m"
        for m in models:
            L = g.centerline_length(counts, m) / 1000
            errs[m].append(L - c["trackLengthM"])
            line += f" | {m} {L:7.3f} ({(L - c['trackLengthM'])*1000:+6.0f} mm)"
        line += f" | curve-deg {total_arc} net360:{'ok' if feasible else 'NO'}"
        print(line)
    print()
    for m in models:
        e = errs[m]
        rms = math.sqrt(sum(x * x for x in e) / len(e)) * 1000
        bias = sum(e) / len(e) * 1000
        print(f"   {m:18s} rms {rms:7.1f} mm   mean bias {bias:+7.1f} mm  (n={len(e)})")

    # Least-squares radius estimate from published lengths:
    # official_len = straights + sum_r (arc_radians_r * r)  — orientation-independent.
    print("\n== least-squares radius fit from official lengths ==")
    keys = ["r1", "r2", "r3", "r4"]
    rows, rhs = [], []
    for c in circuits:
        counts = g.expand_parts(c["parts"])
        straights = sum(
            n * g.DATA["pieceTypes"][s]["lengthMm"]
            for s, n in counts.items() if g.DATA["pieceTypes"][s]["kind"] == "straight"
        )
        arc = {k: 0.0 for k in keys}
        for s, n in counts.items():
            pt = g.DATA["pieceTypes"][s]
            if pt["kind"] == "curve":
                arc[pt["radiusKey"]] += n * math.radians(pt["arcDeg"])
        rows.append([arc[k] for k in keys])
        rhs.append(c["trackLengthM"] * 1000 - straights)
    used = [k for i, k in enumerate(keys) if any(r[i] for r in rows)]
    idx = [keys.index(k) for k in used]
    A = [[r[i] for i in idx] for r in rows]
    b = rhs
    # normal equations (tiny system)
    n = len(used)
    ata = [[sum(A[r][i] * A[r][j] for r in range(len(A))) for j in range(n)] for i in range(n)]
    atb = [sum(A[r][i] * b[r] for r in range(len(A))) for i in range(n)]
    try:
        x = gauss(ata, atb)
        for k, v in zip(used, x):
            print(f"   {k}: fitted {v:7.1f} mm   (exact-nesting {g.DATA['radiusModels']['exact-nesting'][k]:.0f}, "
                  f"rounded {g.DATA['radiusModels']['marketing-rounded'][k]:.0f})")
        if len(circuits) < len(used) + 1:
            print(f"   note: only {len(circuits)} circuits for {len(used)} unknowns — fit is weak, add fixtures")
    except ZeroDivisionError:
        print("   singular system — need more diverse fixtures")


def gauss(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            raise ZeroDivisionError
        m[col], m[piv] = m[piv], m[col]
        for r in range(n):
            if r != col:
                f = m[r][col] / m[col][col]
                m[r] = [v - f * w for v, w in zip(m[r], m[col])]
    return [m[i][n] / m[i][i] for i in range(n)]


def closure_search():
    if not FIXTURES.exists():
        return
    fx = json.loads(FIXTURES.read_text())
    print("\n== constructive closure search (proof-of-buildability; failure proves nothing) ==")
    for c in fx["circuits"]:
        counts = g.expand_parts(c["parts"])
        bbox = [d * 1000 for d in c["dimensionsM"]] if c.get("dimensionsM") else None
        seq = g.search_closed(counts, "exact-nesting", max_bbox_mm=bbox)
        if seq:
            w, d = g.footprint(seq, "exact-nesting")
            la, lb = g.lane_lengths(seq, "exact-nesting")
            print(f"   {c['name']:<14s} CLOSED: {w/1000:.2f} x {d/1000:.2f} m "
                  f"(official {c['dimensionsM'][0]:.2f} x {c['dimensionsM'][1]:.2f}), "
                  f"lanes {la/1000:.3f}/{lb/1000:.3f} m")
        else:
            print(f"   {c['name']:<14s} no closed arrangement found in budget (inconclusive)")


if __name__ == "__main__":
    circle_identities()
    oval_smoke()
    official_lengths()
    closure_search()
