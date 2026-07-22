"""Top-down SVG rendering of Carrera layouts on a dark drafting-board panel."""

import math

from design_tracks import (PIECES, parse, sample_path, step, total_length,
                           HALFW, LANE)

KIND_COLOR = {
    "straight": "#5f708a",
    "digital-straight": "#2789a8",
    "cu": "#4f9e54",
    "r1": "#d4571c",
    "lc-curve": "#2789a8",
    "banked": "#d4a73a",
    "ramp": "#e5decb",
}

PIECE_CLASS = {
    "straight/full": "straight",
    "straight/third": "straight",
    "straight/quarter": "straight",
    "digital/control-unit": "cu",
    "digital/charging-straight": "digital-straight",
    "digital/lane-change-straight": "digital-straight",
    "digital/double-lane-change": "digital-straight",
    "digital/lane-change-left": "digital-straight",
    "special/ramp-concave": "ramp",
    "special/ramp-convex": "ramp",
    "curve/r1-60": "r1",
    "digital/lane-change-curve-right-oi": "lc-curve",
    "curve-banked/r3-30": "banked",
}


def piece_polyline(pose, slug, hand, per=14):
    p = PIECES[slug]
    pts = []
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
        pts.append((px, py, ph))
    return pts


def corner_groups(seq):
    """Group consecutive same-class curve pieces -> corner list."""
    groups = []
    cur = None
    for i, item in enumerate(seq):
        slug, hand = parse(item)
        cls = PIECE_CLASS[slug]
        if cls in ("r1", "banked", "lc-curve"):
            key = ("r1" if cls in ("r1", "lc-curve") else "banked", hand)
            if cur and cur["key"] == key and cur["end"] == i - 1:
                cur["end"] = i
                cur["pieces"].append(i)
            else:
                cur = {"key": key, "start": i, "end": i, "pieces": [i]}
                groups.append(cur)
        else:
            cur = None
    return groups


def render_track_svg(seq, elevated_idx=(), title_note="", width_px=1060,
                     pad_mm=260, sf_index=0):
    """elevated_idx: indices of pieces drawn as elevated deck (bridge/hump)."""
    poses = []
    pose = (0.0, 0.0, 0.0)
    for item in seq:
        poses.append(pose)
        pose = step(pose, *parse(item))

    all_pts = sample_path(seq, per=8)
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    x0, x1 = min(xs) - pad_mm, max(xs) + pad_mm
    y0, y1 = min(ys) - pad_mm, max(ys) + pad_mm
    w_mm, h_mm = x1 - x0, y1 - y0
    s = width_px / w_mm
    height_px = h_mm * s

    def X(x):
        return (x - x0) * s

    def Y(y):
        return height_px - (y - y0) * s  # flip: mm y-up -> svg y-down

    def path_d(pts):
        return "M " + " L ".join(f"{X(px):.1f} {Y(py):.1f}" for px, py, _ in pts)

    svg = []
    svg.append(
        f'<svg viewBox="0 0 {width_px:.0f} {height_px:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Mono, monospace">')
    # defs: grid + shadow
    svg.append(f"""<defs>
<pattern id="grid" width="{500 * s:.2f}" height="{500 * s:.2f}" patternUnits="userSpaceOnUse">
  <path d="M {500 * s:.2f} 0 L 0 0 0 {500 * s:.2f}" fill="none" stroke="#1d2a3f" stroke-width="1"/>
</pattern>
<filter id="lift" x="-30%" y="-30%" width="160%" height="160%">
  <feDropShadow dx="0" dy="{6}" stdDeviation="5" flood-color="#000" flood-opacity="0.55"/>
</filter>
</defs>""")
    svg.append(f'<rect width="{width_px:.0f}" height="{height_px:.0f}" fill="#0d1420"/>')
    svg.append(f'<rect width="{width_px:.0f}" height="{height_px:.0f}" fill="url(#grid)"/>')

    ribbon = 198 * s
    ground = [i for i in range(len(seq)) if i not in elevated_idx]
    deck = [i for i in elevated_idx]

    def draw_piece(i, casing_color, top=False):
        slug, hand = parse(seq[i])
        pts = piece_polyline(poses[i], slug, hand)
        d = path_d(pts)
        color = KIND_COLOR[PIECE_CLASS[slug]]
        flt = ' filter="url(#lift)"' if top else ""
        svg.append(f'<path d="{d}" fill="none" stroke="{casing_color}" '
                   f'stroke-width="{ribbon + 5:.1f}" stroke-linecap="butt"{flt}/>')
        svg.append(f'<path d="{d}" fill="none" stroke="{color}" '
                   f'stroke-width="{ribbon:.1f}" stroke-linecap="butt"/>')
        # lane slots
        for off in (-LANE, LANE):
            lane_pts = [(px - off * math.sin(ph), py + off * math.cos(ph), ph)
                        for px, py, ph in pts]
            svg.append(f'<path d="{path_d(lane_pts)}" fill="none" stroke="#0d1420" '
                       f'stroke-width="{max(2.2, 14 * s):.1f}" stroke-opacity="0.75"/>')
        # joint tick at piece start
        px, py, ph = pts[0]
        tx1 = X(px - HALFW * math.sin(ph)); ty1 = Y(py + HALFW * math.cos(ph))
        tx2 = X(px + HALFW * math.sin(ph)); ty2 = Y(py - HALFW * math.cos(ph))
        svg.append(f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" '
                   f'stroke="#0d1420" stroke-width="1.6" stroke-opacity="0.9"/>')

    for i in ground:
        draw_piece(i, "#26344c")
    for i in deck:
        draw_piece(i, "#f2ede0", top=True)

    # direction arrows every ~1.4 m
    L = total_length(seq)
    n_arrows = max(4, int(L / 1400))
    pts_fine = sample_path(seq, per=20)
    step_n = len(pts_fine) // n_arrows
    for k in range(n_arrows):
        px, py, ph, slug, *_ = pts_fine[(k * step_n + 8) % len(pts_fine)]
        if PIECE_CLASS[slug] == "ramp":
            continue
        ax, ay = X(px), Y(py)
        deg = -math.degrees(ph)
        svg.append(f'<g transform="translate({ax:.1f} {ay:.1f}) rotate({deg:.1f})">'
                   f'<path d="M 7 0 L -4 4.4 L -4 -4.4 Z" fill="#e6edf3" opacity="0.85"/></g>')

    # start/finish checker
    px, py, ph = piece_polyline(poses[sf_index], *parse(seq[sf_index]))[0]
    svg.append(f'<g transform="translate({X(px):.1f} {Y(py):.1f}) rotate({-math.degrees(ph):.1f})">')
    n_sq, sq = 8, (198 * s) / 8
    for r_ in range(2):
        for c_ in range(n_sq):
            fill = "#e6edf3" if (r_ + c_) % 2 == 0 else "#10161f"
            svg.append(f'<rect x="{r_ * sq:.1f}" y="{-99 * s + c_ * sq:.1f}" '
                       f'width="{sq:.1f}" height="{sq:.1f}" fill="{fill}"/>')
    svg.append("</g>")

    # corner badges
    for n, g in enumerate(corner_groups(seq), 1):
        mid = g["pieces"][len(g["pieces"]) // 2]
        slug, hand = parse(seq[mid])
        pts = piece_polyline(poses[mid], slug, hand)
        px, py, ph = pts[len(pts) // 2]
        # offset badge to outside of the turn
        off = -hand * 205
        bx = X(px - off * math.sin(ph)); by = Y(py + off * math.cos(ph))
        color = "#d4a73a" if g["key"][0] == "banked" else "#d4571c"
        svg.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="11" fill="#0d1420" '
                   f'stroke="{color}" stroke-width="1.6"/>')
        svg.append(f'<text x="{bx:.1f}" y="{by + 3.6:.1f}" text-anchor="middle" '
                   f'font-size="10.5" fill="{color}">{n}</text>')

    # scale bar (1 m)
    bar = 1000 * s
    bx, by = width_px - bar - 26, height_px - 22
    svg.append(f'<line x1="{bx:.0f}" y1="{by:.0f}" x2="{bx + bar:.0f}" y2="{by:.0f}" '
               f'stroke="#9fb0c3" stroke-width="2"/>')
    for t in (0, bar / 2, bar):
        svg.append(f'<line x1="{bx + t:.0f}" y1="{by - 4:.0f}" x2="{bx + t:.0f}" '
                   f'y2="{by + 4:.0f}" stroke="#9fb0c3" stroke-width="2"/>')
    svg.append(f'<text x="{bx + bar / 2:.0f}" y="{by - 9:.0f}" text-anchor="middle" '
               f'font-size="11" fill="#9fb0c3">1 m</text>')
    if title_note:
        svg.append(f'<text x="18" y="24" font-size="11" fill="#61718a">{title_note}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def elevation_svg(kind="bridge", width_px=640):
    """Side profile of the 4-ramp assembly. kind: 'bridge' (crossing) or 'hump'."""
    h = 150
    svg = [f'<svg viewBox="0 0 {width_px} {h}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="IBM Plex Mono, monospace">']
    x_left, x_right = 40, width_px - 40
    span = x_right - x_left
    ground_y = h - 34
    crest = 52
    # profile: flat, concave up-start, convex crest, convex, concave, flat
    pts = []
    n = 120
    for i in range(n + 1):
        f = i / n            # 0..1 over 4 ramp pieces (1380 mm)
        # smooth S-curves: height = crest * smoothstep on each half
        if f < 0.5:
            g = f / 0.5
            z = g * g * (3 - 2 * g)
        else:
            g = (1 - f) / 0.5
            z = g * g * (3 - 2 * g)
        pts.append((x_left + f * span, ground_y - crest * z))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    svg.append(f'<rect width="{width_px}" height="{h}" fill="#0d1420"/>')
    svg.append(f'<line x1="0" y1="{ground_y}" x2="{width_px}" y2="{ground_y}" '
               f'stroke="#26344c" stroke-width="2"/>')
    # quarters ticks: piece joints
    for q in range(5):
        x = x_left + span * q / 4
        svg.append(f'<line x1="{x:.0f}" y1="{ground_y}" x2="{x:.0f}" y2="{ground_y + 8}" '
                   f'stroke="#61718a" stroke-width="1.5"/>')
    labels = ["concave", "convex", "convex", "concave"]
    for q, lab in enumerate(labels):
        x = x_left + span * (q + 0.5) / 4
        svg.append(f'<text x="{x:.0f}" y="{ground_y + 22}" text-anchor="middle" '
                   f'font-size="10" fill="#61718a">{lab}</text>')
    svg.append(f'<path d="{d}" fill="none" stroke="#e5decb" stroke-width="7" '
               f'stroke-linecap="round"/>')
    if kind == "bridge":
        # crossing track below the crest
        cx = x_left + span / 2
        svg.append(f'<rect x="{cx - 15}" y="{ground_y - 13}" width="30" height="13" '
                   f'fill="#2789a8"/>')
        svg.append(f'<text x="{cx + 14}" y="{ground_y - crest - 14}" '
                   f'font-size="10" fill="#9fb0c3">~93 mm clearance under the crest</text>')
        svg.append(f'<line x1="{cx}" y1="{ground_y - crest - 10}" x2="{cx}" '
                   f'y2="{ground_y - 14}" stroke="#9fb0c3" stroke-width="1" '
                   f'stroke-dasharray="3 3"/>')
    svg.append(f'<text x="{x_left}" y="24" font-size="11" fill="#61718a">'
               f'RAMP ASSEMBLY - SIDE PROFILE (4 x 345 mm, part 20587)</text>')
    svg.append("</svg>")
    return "\n".join(svg)


if __name__ == "__main__":
    from design_tracks import t1_hexagon_gp, t2_gauntlet
    seq1 = t1_hexagon_gp()
    ramp_idx = [i for i, it in enumerate(seq1) if it.startswith("special/ramp")]
    open("t1.svg", "w").write(render_track_svg(seq1, elevated_idx=ramp_idx))
    open("t2.svg", "w").write(render_track_svg(t2_gauntlet()))
    open("profile.svg", "w").write(elevation_svg("bridge"))
    print("wrote t1.svg t2.svg profile.svg")
