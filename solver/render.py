"""Render a layout sequence to SVG: top-down track drawing + numbered pieces.

Usage: python3 render.py --sequence seq.json --out track.svg [--title "..."]
seq.json: ["curve/r1-60:L", "straight/full", ...] (Layout encoding)
Pure stdlib; the SVG embeds cleanly in HTML build sheets and prints at scale.
"""

import argparse
import json
import math

import geometry as g

MODEL = "exact-nesting"


def decode(entry):
    if ":" in entry:
        slug, hand = entry.rsplit(":", 1)
        return slug, 1 if hand == "L" else -1
    return entry, 0


def sample_piece(pose, slug, hand, n=24):
    """Centerline points + headings through one piece."""
    length, radius, arc = g.resolve_piece(slug, MODEL)
    pts = []
    for i in range(n + 1):
        f = i / n
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
        pts.append((px, py, ph))
    return pts


def svg_string(seq_entries, title="Layout"):
    seq = [decode(e) for e in seq_entries]
    pose = (0.0, 0.0, 0.0)
    pieces = []
    for slug, hand in seq:
        pts = sample_piece(pose, slug, hand)
        pieces.append((slug, hand, pts))
        pose = g.step(pose, slug, hand, MODEL)

    all_pts = [(x, y, h) for _, _, pts in pieces for x, y, h in pts]
    hw = g.HALF_W
    xs = [x - hw * math.sin(h) for x, y, h in all_pts] + [x + hw * math.sin(h) for x, y, h in all_pts]
    ys = [y + hw * math.cos(h) for x, y, h in all_pts] + [y - hw * math.cos(h) for x, y, h in all_pts]
    x0, x1, y0, y1 = min(xs) - 60, max(xs) + 60, min(ys) - 60, max(ys) + 60
    scale = 900 / max(x1 - x0, y1 - y0)
    W, H = (x1 - x0) * scale, (y1 - y0) * scale

    def tx(x, y):  # flip y for SVG
        return (x - x0) * scale, H - (y - y0) * scale

    def path(pts, off):
        d = []
        for i, (x, y, h) in enumerate(pts):
            px, py = tx(x - off * math.sin(h), y + off * math.cos(h))
            d.append(f"{'M' if i == 0 else 'L'}{px:.1f},{py:.1f}")
        return " ".join(d)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H + 40:.0f}" font-family="sans-serif">']
    svg.append(f'<text x="12" y="24" font-size="20" font-weight="bold">{title}</text>')
    body = []
    for slug, hand, pts in pieces:
        body.append(f'<path d="{path(pts, 0)}" stroke="#333" stroke-width="{2 * hw * scale:.1f}" fill="none" stroke-linecap="butt"/>')
    for slug, hand, pts in pieces:
        for lane_off in (g.LANE, -g.LANE):
            body.append(f'<path d="{path(pts, lane_off)}" stroke="#fff" stroke-width="1.2" fill="none" stroke-dasharray="6,5"/>')
    for i, (slug, hand, pts) in enumerate(pieces):
        mx, my, _ = pts[len(pts) // 2]
        cx, cy = tx(mx, my)
        body.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="10" fill="#fff" stroke="#c33"/>')
        body.append(f'<text x="{cx:.0f}" y="{cy + 4:.0f}" font-size="10" text-anchor="middle" fill="#c33">{i + 1}</text>')
    sx, sy = tx(*pieces[0][2][0][:2])
    body.append(f'<rect x="{sx - 4:.0f}" y="{sy - 14:.0f}" width="8" height="28" fill="#c33"/>')
    svg.append(f'<g transform="translate(0,36)">{"".join(body)}</g>')
    fw, fd = (x1 - x0 - 120) / 1000, (y1 - y0 - 120) / 1000
    svg.append(f'<text x="12" y="{H + 34:.0f}" font-size="13" fill="#555">footprint ≈ {fw:.2f} × {fd:.2f} m — start/finish at red bar, pieces numbered in build order</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def render(seq_entries, title="Layout", out="track.svg"):
    open(out, "w").write(svg_string(seq_entries, title))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True)
    ap.add_argument("--out", default="track.svg")
    ap.add_argument("--title", default="Layout")
    args = ap.parse_args()
    entries = json.loads(open(args.sequence).read())
    print(render(entries, args.title, args.out))
