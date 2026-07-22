"""Build the four self-contained track-design HTML pages + index."""

import json
import datetime
from pathlib import Path

import design_tracks as dt
from render_svg import render_track_svg, elevation_svg

OUT = Path(__file__).parent / "html"
OUT.mkdir(exist_ok=True)

TITLES = {
    "straight/full": "Standard straight · 345 mm",
    "straight/third": "1/3 straight · 115 mm",
    "straight/quarter": "1/4 straight · 86.25 mm",
    "digital/control-unit": "Control Unit (power base) · 345 mm",
    "digital/charging-straight": "Charging straight (Wireless+) · 345 mm",
    "digital/lane-change-straight": "Lane-change straight · 345 mm",
    "digital/double-lane-change": "Double lane change · 690 mm",
    "digital/lane-change-left": "Lane change left · 690 mm",
    "special/ramp-concave": "Ramp section, concave · 345 mm",
    "special/ramp-convex": "Ramp section, convex · 345 mm",
    "curve/r1-60": "Curve R1 / 60° · r 297 mm",
    "digital/lane-change-curve-right-oi": "Lane-change curve R1/60° right, out-to-in",
    "curve-banked/r3-30": "High-banked curve R3 / 30° · r 693 mm",
}

CSS = """
:root{
  --bg:#0b1119; --bg-grid:rgba(120,150,190,.05); --surface:#101a29; --surface2:#0d1420;
  --border:rgba(148,175,210,.14); --text:#dce6f2; --dim:#8ea2bb; --faint:#5d7089;
  --r1:#e0641f; --banked:#d4a73a; --teal:#2f9db8; --green:#57a45b; --deck:#e5decb;
  --hero-tint:rgba(224,100,31,.07);
}
@media (prefers-color-scheme: light){
  :root{
    --bg:#f2efe7; --bg-grid:rgba(30,58,95,.06); --surface:#faf8f2; --surface2:#0d1420;
    --border:rgba(30,58,95,.18); --text:#1c2733; --dim:#51617a; --faint:#7c8ba0;
    --hero-tint:rgba(224,100,31,.06);
  }
}
*{box-sizing:border-box;min-width:0}
body{
  margin:0; font-family:'IBM Plex Sans',system-ui,sans-serif; background:var(--bg); color:var(--text);
  background-image:linear-gradient(var(--bg-grid) 1px,transparent 1px),
    linear-gradient(90deg,var(--bg-grid) 1px,transparent 1px);
  background-size:36px 36px; line-height:1.55;
}
.wrap{max-width:1140px;margin:0 auto;padding:34px 26px 80px}
.mono{font-family:'IBM Plex Mono',monospace}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.14em;color:var(--dim);
  text-transform:uppercase;display:flex;align-items:center;gap:9px}
.eyebrow::before{content:'';width:8px;height:8px;border-radius:50%;background:var(--acc)}
h1{font-size:44px;line-height:1.08;margin:10px 0 6px;letter-spacing:-.015em}
.tagline{font-size:18px;color:var(--dim);max-width:760px;margin:0 0 8px}
h2{font-size:15px;font-family:'IBM Plex Mono',monospace;letter-spacing:.13em;text-transform:uppercase;
  color:var(--dim);margin:0 0 16px;display:flex;align-items:center;gap:9px}
h2::before{content:'';width:8px;height:8px;border-radius:50%;background:var(--acc)}
section{margin-top:44px}
.hero{background:linear-gradient(180deg,var(--hero-tint),transparent 80%);border:1px solid var(--border);
  border-radius:14px;padding:30px 30px 24px;margin-top:22px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:18px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 16px}
.kpi .v{font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:600;color:var(--acc)}
.kpi .v small{font-size:14px;color:var(--dim);font-weight:400}
.kpi .k{font-size:12px;color:var(--dim);margin-top:3px;letter-spacing:.05em}
.kpi.big .v{font-size:34px}
.map-panel{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:14px;
  box-shadow:0 18px 40px -22px rgba(0,0,0,.7)}
.map-panel svg{width:100%;height:auto;display:block;border-radius:8px}
.legend{display:flex;flex-wrap:wrap;gap:8px 14px;margin-top:12px;padding:0 4px}
.chip{display:flex;align-items:center;gap:7px;font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--dim)}
.chip i{width:18px;height:8px;border-radius:2px;display:inline-block}
.grid2{display:grid;grid-template-columns:1.15fr .85fr;gap:22px;align-items:start}
@media(max-width:880px){.grid2{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px}
.card h3{margin:0 0 8px;font-size:16px}
.card p{margin:8px 0;color:var(--dim);font-size:14.5px}
.card p strong{color:var(--text)}
.callout{border-left:3px solid var(--acc);background:var(--surface);border-radius:0 10px 10px 0;
  padding:13px 16px;margin:14px 0;font-size:14px;color:var(--dim)}
.callout strong{color:var(--text)}
.callout code{color:var(--acc)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
thead th{position:sticky;top:0;background:var(--surface);text-align:left;font-family:'IBM Plex Mono',monospace;
  font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);
  padding:10px 12px;border-bottom:1px solid var(--border);z-index:2}
tbody td{padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:top}
tbody tr:nth-child(even){background:rgba(128,155,195,.045)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;font-family:'IBM Plex Mono',monospace}
.tbl-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:12px;background:var(--surface)}
.sector-row td{background:rgba(128,155,195,.09)!important;font-family:'IBM Plex Mono',monospace;
  font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--acc)}
.dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:8px;vertical-align:1px}
.ok{color:var(--green)} .warn{color:var(--banked)}
code{font-family:'IBM Plex Mono',monospace;font-size:.92em;background:rgba(128,155,195,.12);
  padding:1px 5px;border-radius:4px}
.navbar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.navbar a{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--dim);text-decoration:none;
  border:1px solid var(--border);border-radius:999px;padding:5px 13px;background:var(--surface)}
.navbar a:hover{color:var(--text);border-color:var(--acc)}
.navbar a.here{color:var(--acc);border-color:var(--acc)}
footer{margin-top:60px;padding-top:18px;border-top:1px solid var(--border);
  font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--faint)}
footer a{color:var(--dim)}
.profile-panel{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:10px}
.profile-panel svg{width:100%;height:auto;display:block}
.fade{opacity:0;transform:translateY(14px);animation:fadeUp .6s ease forwards}
@keyframes fadeUp{to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){.fade{animation:none;opacity:1;transform:none}}
.cards-idx{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.tcard{display:block;text-decoration:none;color:var(--text);background:var(--surface);
  border:1px solid var(--border);border-radius:14px;padding:20px;transition:border-color .2s, transform .2s}
.tcard:hover{border-color:var(--tacc);transform:translateY(-2px)}
.tcard .lbl{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--tacc)}
.tcard h3{margin:6px 0 4px;font-size:20px}
.tcard p{margin:4px 0 10px;font-size:13.5px;color:var(--dim)}
.tcard .m{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--dim)}
"""

FONT_LINK = ('<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;'
             '500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">')

LEGEND = """
<div class="legend">
<span class="chip"><i style="background:#5f708a"></i> straight</span>
<span class="chip"><i style="background:#4f9e54"></i> control unit (power + S/F)</span>
<span class="chip"><i style="background:#2789a8"></i> digital lane-change / charging</span>
<span class="chip"><i style="background:#d4571c"></i> curve R1/60&deg;</span>
<span class="chip"><i style="background:#d4a73a"></i> banked R3/30&deg;</span>
<span class="chip"><i style="background:#e5decb;border:1px solid #999"></i> ramp deck (elevated)</span>
<span class="chip"><i style="background:#0d1420;border:1px solid #5f708a"></i> slot lanes &plusmn;49.5 mm</span>
</div>"""


def navbar(here):
    pages = [("index", "Overview"), ("marathon-hex", "01 Longest"),
             ("gauntlet", "02 Technical"), ("skybridge", "03 Coolest"),
             ("equalizer", "04 Fairest")]
    return '<nav class="navbar">' + "".join(
        f'<a href="{f}.html" class="{"here" if f == here else ""}">{t}</a>'
        for f, t in pages) + "</nav>"


def build_sheet(seq, sectors):
    """sectors: {start_index: label}; -> table rows with piece runs collapsed."""
    rows = []
    i = 0
    n = 1
    while i < len(seq):
        if i in sectors:
            rows.append(f'<tr class="sector-row"><td colspan="4">{sectors[i]}</td></tr>')
        slug, hand = dt.parse(seq[i])
        j = i
        while (j + 1 < len(seq) and seq[j + 1] == seq[i] and (j + 1) not in sectors):
            j += 1
        count = j - i + 1
        handtxt = {1: "LEFT", -1: "RIGHT", 0: ""}[hand]
        color = {"straight": "#5f708a", "cu": "#4f9e54", "digital-straight": "#2789a8",
                 "r1": "#d4571c", "lc-curve": "#2789a8", "banked": "#d4a73a",
                 "ramp": "#b9ae95"}[__import__("render_svg").PIECE_CLASS[slug]]
        rows.append(
            f'<tr><td class="num">{n}{"&ndash;" + str(n + count - 1) if count > 1 else ""}</td>'
            f'<td><span class="dot" style="background:{color}"></span>{TITLES[slug]}</td>'
            f'<td class="num">{count}&times;</td>'
            f'<td class="mono" style="color:var(--dim)">{handtxt}</td></tr>')
        n += count
        i = j + 1
    return ("<div class='tbl-wrap'><table><thead><tr><th class='num'>#</th><th>Piece</th>"
            "<th class='num'>Qty</th><th>Hand</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></div>")


def bom_table(seq):
    counts = dt.bom(seq)
    rows = []
    order = list(TITLES)
    for slug in order:
        used = counts.get(slug, 0)
        own = dt.INVENTORY.get(slug, 0)
        if used == 0:
            continue
        spare = own - used
        cls = "ok" if spare >= 0 else "warn"
        rows.append(f"<tr><td>{TITLES[slug]}</td><td class='mono' style='color:var(--faint)'>{slug}</td>"
                    f"<td class='num'>{used}</td><td class='num'>{own}</td>"
                    f"<td class='num {cls}'>{spare:+d}</td></tr>")
    return ("<div class='tbl-wrap'><table><thead><tr><th>Piece type</th><th>Catalog slug</th>"
            "<th class='num'>Used</th><th class='num'>Owned</th><th class='num'>Spare</th></tr>"
            "</thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def metrics_kpis(seq, extra=None):
    la, lb = dt.lane_lengths(seq)
    _, _, w, h = dt.footprint(seq)
    corners = len(__import__("render_svg").corner_groups(seq))
    delta = abs(la - lb)
    delta_txt = "0<small> mm — equal</small>" if delta < 0.01 else f"{delta:.0f}<small> mm/lap</small>"
    k = [
        ("big", f"{dt.total_length(seq) / 1000:.2f}<small> m</small>", "lap length (centerline)"),
        ("", f"{w / 1000:.2f} &times; {h / 1000:.2f}<small> m</small>", "floor footprint"),
        ("", f"{len(seq)}", "track pieces"),
        ("", f"{corners}", "corners"),
        ("", delta_txt, "lane length difference"),
    ]
    if extra:
        k.extend(extra)
    return '<div class="kpis">' + "".join(
        f'<div class="kpi {c}"><div class="v">{v}</div><div class="k">{lbl}</div></div>'
        for c, v, lbl in k) + "</div>"


def page(fname, acc, eyebrow, title, tagline, seq, sectors, design_html,
         elevated_idx=(), sf_index=0, profile_kind=None, closure_note="",
         map_note=""):
    la, lb = dt.lane_lengths(seq)
    svg = render_track_svg(seq, elevated_idx=elevated_idx, sf_index=sf_index,
                           title_note=map_note)
    profile = ""
    if profile_kind:
        profile = f"""
<section class="fade" style="animation-delay:.25s">
  <h2>Ramp elevation</h2>
  <div class="profile-panel">{elevation_svg(profile_kind)}</div>
</section>"""
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Carrera D132 track design</title>{FONT_LINK}
<style>{CSS}
:root{{--acc:{acc}}}
</style></head><body><div class="wrap">
{navbar(fname)}
<header class="hero fade">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <p class="tagline">{tagline}</p>
  {metrics_kpis(seq)}
</header>

<section class="fade" style="animation-delay:.1s">
  <h2>Track map</h2>
  <div class="map-panel">{svg}</div>
  {LEGEND}
</section>

<section class="fade" style="animation-delay:.2s">
  <h2>Design notes</h2>
  {design_html}
</section>
{profile}
<section class="fade" style="animation-delay:.3s">
  <h2>Assembly sheet — follow in driving direction from the start line</h2>
  {build_sheet(seq, sectors)}
</section>

<section class="fade" style="animation-delay:.35s">
  <h2>Bill of materials vs. your inventory</h2>
  {bom_table(seq)}
  <div class="callout">{closure_note}</div>
</section>

<footer>
  Designed from live inventory in
  <a href="https://app.warmhub.ai/orgs/wjcorey/repos/carrera-track">wjcorey/carrera-track</a>
  &middot; geometry from <a href="https://app.warmhub.ai/orgs/slotcars">slotcars/carrera-catalog</a>
  &middot; solver-verified {datetime.date.today().isoformat()}
</footer>
</div></body></html>"""
    (OUT / f"{fname}.html").write_text(html)
    print("wrote", fname, f"{dt.total_length(seq)/1000:.2f} m")


def main():
    today = datetime.date.today().isoformat()

    # ---------------------------------------------------------------- T1
    seq1 = dt.t1_hexagon_gp()
    ramp1 = [i for i, it in enumerate(seq1) if it.startswith("special/ramp")]
    sectors1 = {
        0: "Sector 1 — start/finish straight with bus-stop chicane",
        11: "Turn 1 — banked sweeper (60°, r 693)",
        13: "Sector 2 — the Everest climb (ramp hump)",
        18: "Turn 2 — flat R1 corner",
        19: "Sector 3 — ridge run",
        24: "Turn 3 — banked sweeper",
        26: "Sector 4 — back straight: lane-change alley + bus stop",
        33: "Turn 4 — flat R1 corner",
        34: "Sector 5 — valley straight",
        38: "Turn 5 — banked sweeper",
        40: "Sector 6 — return run",
        46: "Turn 6 — flat R1 corner onto the start line",
    }
    design1 = """
<div class="grid2">
<div class="card">
<h3>Every usable piece, one exact hexagon</h3>
<p>This layout puts <strong>your entire drivable collection on the floor at once</strong> —
all 16 standard straights, both 1/3 and both 1/4 straights, every lane changer, the
Control Unit, the charging straight, all 11 R1 curve pieces, all 6 banked curves and the
full 4-piece ramp kit as an airborne hump. Total: 16.0 m of racing line, roughly double
the starter-set oval.</p>
<p>The shape is an equiangular hexagon whose corners <strong>alternate banked R3 sweepers
with flat R1 corners</strong>. That alternation is not styling — it is the closure proof.
Each 60° corner behaves like two tangent stubs of length <code>r/√3</code>; because every
side sits between one banked (693 mm) and one flat (297 mm) corner, all six sides get the
same tangent sum and the hexagon closes if the sides satisfy two simple length equations:</p>
<p class="mono" style="font-size:13px">B + C = E + F&emsp;and&emsp;A − D = E − B</p>
<p>with A=2070, B=1725, C=1236.25, D=2415, E=1380, F=1581.25 mm. The solver confirms
closure to 0.000 mm.</p>
</div>
<div>
<div class="callout"><strong>Bus stops that cancel.</strong> The two chicane jogs on the
front straight and the two on the back straight advance the car by 297·√3 mm each — an
irrational number that can never be trimmed away with straight pieces. They are placed
two-per-straight in opposite directions so the √3 terms cancel exactly.</p></div>
<div class="callout"><strong>The hump is real airtime.</strong> The 4 ramp pieces
(concave–convex–convex–concave) form an up-and-over crest on the climb side. Support the
crest joint per the 20587 kit instructions and brake before Turn 2.</div>
<div class="callout"><strong>Banked caveat.</strong> The catalog marks banked R3 pieces
<code>solverReady:false</code> — plan-view geometry uses the flat-R3 approximation, so
expect to absorb a few mm of joint flex around the three banked apexes. Everything else
is exact.</div>
</div>
</div>"""
    page("marathon-hex", "#e0641f", f"Carrera Digital 132 · Track 01 · The Longest",
         "Marathon Hex GP",
         "A 16-metre, six-corner grand-prix hexagon that uses every drivable piece you "
         "own — three banked apexes, two bus-stop chicanes, a lane-change alley and a "
         "flying ramp hump.",
         seq1, sectors1, design1, elevated_idx=ramp1, sf_index=0,
         profile_kind="hump",
         closure_note="<strong>Closure:</strong> exact (0.000 mm, 0.000°) under the "
         "adjudicated exact-nesting radii, banked apexes using the documented flat-R3 "
         "plan approximation. Net turning +360°, so the outer slot runs 622 mm further "
         "per lap — put the faster driver on the outside, or rotate lanes each heat.",
         map_note="TRACK 01 - MARATHON HEX GP - 16.0 M - FOOTPRINT 5.9 x 3.8 M")

    # ---------------------------------------------------------------- T2
    seq2 = dt.t2_gauntlet()
    sectors2 = {
        0: "Sector 1 — launch: Control Unit + lane-change straight",
        3: "Hairpin 1 — 180° left, r 297",
        6: "Sector 2 — chicane approach",
        7: "Chicane A — right-left flick, +297 mm offset",
        9: "Sector 3 — passing alley: two double lane changes",
        13: "Hairpin 2 — 180° left into the corridor",
        16: "Sector 4 — the corridor: 99 mm wall-to-wall gap",
        17: "Chicane B — lane-change flick down to the finish line",
        19: "Sector 5 — run to the line",
    }
    design2 = """
<div class="grid2">
<div class="card">
<h3>Ten corners in seven metres</h3>
<p>The Gauntlet packs <strong>10 of your 11 R1 curve pieces</strong> into 6.96 m: two full
180° hairpins and two offset chicanes threading <strong>three parallel straights stacked
297 mm apart</strong> — edge-to-edge clearance between lanes is just 99 mm, so the middle
corridor feels like racing through a canyon.</p>
<p>Braking rhythm is everything: launch, hard left hairpin, quarter-straight flick
right-left, then the only real passing window (two double-lane-changers back to back),
another hairpin, and a lane-change flick that spits you across your rival's nose onto the
finish straight.</p>
<p>Closure is exact and purely rational: east legs (1035 + 891.25 mm) equal the west leg
(1926.25 mm), and the two chicanes' irrational √3 advances sit on opposite headings, so
they cancel piece-for-piece.</p>
</div>
<div>
<div class="callout"><strong>Why it's the technical one.</strong> Corner density: one
direction change every 70 cm of track. No straight is longer than 690 mm except the
passing alley — throttle discipline beats top speed here.</div>
<div class="callout"><strong>Digital race craft.</strong> Both double lane changes sit on
the one genuine flat-out zone, and the exit chicane uses the out-to-in lane-change curve:
three overtaking chances per lap on a table-top footprint of 3.2 × 1.1 m.</div>
<div class="callout"><strong>Setup tip.</strong> Use the four border end-pieces on the
outside of both hairpins — deslots concentrate there.</div>
</div>
</div>"""
    page("gauntlet", "#c2410c", "Carrera Digital 132 · Track 02 · The Most Technical",
         "The Gauntlet",
         "A double-hairpin canyon run: three straights stacked 99 mm apart, two chicane "
         "flicks, and every braking zone earned. Fits on a big table.",
         seq2, sectors2, design2, sf_index=0,
         closure_note="<strong>Closure:</strong> exact (0.000 mm, 0.000°) — all pieces "
         "solver-ready, no banked or ramp approximations. Marked "
         "<code>closureVerified: true</code> in the repo. Net turning +360°: outer lane "
         "is 622 mm longer per lap — run heats both directions or use the lane changers.",
         map_note="TRACK 02 - THE GAUNTLET - 6.96 M - FOOTPRINT 3.2 x 1.1 M")

    # ---------------------------------------------------------------- T4
    seq4 = json.load(open(Path(__file__).parent / "t4_final.json"))
    ramp4 = [i for i, it in enumerate(seq4) if it.startswith("special/ramp")]
    sectors4 = {
        0: "Bridge descent — leaving the crest eastbound",
        2: "Banked cascade — banked/flat/banked/flat left sweep",
        8: "Underpass straight — passes beneath the bridge deck",
        13: "Esses right",
        15: "Pit straight — Control Unit, S/F line, charging zone",
        20: "Lane-change corner (out-to-in flick)",
        21: "Runout",
        23: "Right-hand loop",
        28: "Banked finale into the climb",
        31: "Bridge ascent — back over your own track",
    }
    design4 = """
<div class="grid2">
<div class="card">
<h3>Both lanes: 11 876.28 mm. Difference: zero.</h3>
<p>On any closed loop each slot's length is the centerline length plus 49.5 mm times the
<em>net signed</em> turning angle. A normal circuit must turn a full ±360°, so the outer
lane is always <strong>2π · 2 · 49.5 ≈ 622 mm longer per lap</strong> — about two car
lengths of free advantage, decided by lane draw.</p>
<p>The only fix is a track that turns as much right as it does left — net 0° — and a
closed loop with zero net turning <em>must cross itself</em>. That's what the ramp bridge
kit is for: The Equalizer crosses over its own back straight at 60°, balancing 690° of
left turning against 690° of right turning. Lane A and Lane B measure
<strong>identical to the micrometre</strong>, and this stays true regardless of the
banked pieces' small plan-view tolerance, because lane difference depends only on the
molded arc angles.</p>
<p>The search that found it enumerated 3 280 exactly-closing figure-eights over your
inventory; this one scored best on crossing placement (53 mm from the deck crest — the
point of maximum clearance) and footprint.</p>
</div>
<div>
<div class="callout"><strong>Fair by symmetry of arcs, not mirror-image looks.</strong>
Each lobe mixes banked sweepers and flat R1 corners, but signed arc totals cancel:
6 banked-left pieces + 7 R1 lefts vs 8 R1 rights = 0° net. Check:
(6·30 + 7·60) − 8·60 = 690 − 690 = 0.</div>
<div class="callout"><strong>Racing equity extras.</strong> Both double lane changes are
included, one per lobe, and the out-to-in lane-change curve gives a passing line into the
right-hand loop. Cars swap inside/outside roles every lap anyway — that's the point.</div>
<div class="callout"><strong>Build the bridge first.</strong> Assemble the four ramp
pieces flat on the floor axis, then thread the underpass straight beneath the ascent
ramp before closing either lobe. ~93 mm of clearance at the crossing point.</div>
</div>
</div>"""
    page("equalizer", "#57a45b", "Carrera Digital 132 · Track 04 · The Fairest",
         "The Equalizer",
         "A banked over-under figure-eight with net-zero turning: both slots measure "
         "exactly 11 876.28 mm. No lane draw luck — the track itself is the handicapper.",
         seq4, sectors4, design4, elevated_idx=ramp4, sf_index=15,
         profile_kind="bridge",
         closure_note="<strong>Closure:</strong> exact to 10<sup>-12</sup> mm in plan "
         "view; banked pieces use the documented flat-R3 approximation "
         "(<code>solverReady:false</code> in the catalog) so allow a few mm of joint "
         "flex at the two banked cascades. Lane equality is unaffected — it depends "
         "only on arc angles. Net turning: 0°.",
         map_note="TRACK 04 - THE EQUALIZER - 11.88 M - LANES EXACTLY EQUAL")

    # ---------------------------------------------------------------- T3
    t3_path = Path(__file__).parent / "t3_final.json"
    if t3_path.exists():
        cfg = json.load(open(t3_path))
        seq3 = cfg["seq"]
        ramp3 = [i for i, it in enumerate(seq3) if it.startswith("special/ramp")]
        sectors3 = {int(k): v for k, v in cfg["sectors"].items()}
        page("skybridge", "#d4a73a", "Carrera Digital 132 · Track 03 · The Coolest",
             cfg["title"], cfg["tagline"], seq3, sectors3, cfg["design_html"],
             elevated_idx=ramp3, sf_index=cfg["sf_index"], profile_kind="bridge",
             closure_note=cfg["closure_note"], map_note=cfg["map_note"])

    # ---------------------------------------------------------------- index
    tracks_meta = []
    for fname, name, acc, tag, seq in [
        ("marathon-hex", "Marathon Hex GP", "#e0641f",
         "The Longest — 6 corners, 3 banked apexes, a flying hump, every piece you own", seq1),
        ("gauntlet", "The Gauntlet", "#c2410c",
         "The Most Technical — double hairpins + a 99 mm canyon corridor", seq2),
        ("skybridge", "Skybridge Thunder", "#d4a73a",
         "The Coolest — banked speedway sweeps over a flying crossover",
         json.load(open(t3_path))["seq"] if t3_path.exists() else None),
        ("equalizer", "The Equalizer", "#57a45b",
         "The Fairest — net-zero turning, both lanes mathematically identical", seq4),
    ]:
        if seq is None:
            continue
        la, lb = dt.lane_lengths(seq)
        _, _, w, h = dt.footprint(seq)
        corners = len(__import__("render_svg").corner_groups(seq))
        tracks_meta.append((fname, name, acc, tag, dt.total_length(seq) / 1000,
                            w / 1000, h / 1000, len(seq), corners, abs(la - lb)))

    cards = "".join(f"""
<a class="tcard" href="{f}.html" style="--tacc:{acc}">
  <div class="lbl">Track 0{i + 1}</div><h3>{name}</h3><p>{tag}</p>
  <div class="m">{L:.2f} m &middot; {w:.1f}&times;{h:.1f} m &middot; {p} pieces
  &middot; &Delta;lanes {0 if d < .01 else round(d)} mm</div>
</a>""" for i, (f, name, acc, tag, L, w, h, p, c, d) in enumerate(tracks_meta))

    rows = "".join(
        f"<tr><td><a href='{f}.html' style='color:var(--text)'>{name}</a></td>"
        f"<td class='num'>{L:.2f} m</td><td class='num'>{w:.2f} &times; {h:.2f} m</td>"
        f"<td class='num'>{p}</td><td class='num'>{c}</td>"
        f"<td class='num'>{'0 — equal' if d < .01 else f'{d:.0f} mm'}</td></tr>"
        for f, name, acc, tag, L, w, h, p, c, d in tracks_meta)

    index_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Corey's Carrera D132 — four showcase track designs</title>{FONT_LINK}
<style>{CSS}
:root{{--acc:#2f9db8}}
</style></head><body><div class="wrap">
{navbar("index")}
<header class="hero fade">
  <div class="eyebrow">Carrera Digital 132 · designed {today} from live WarmHub inventory</div>
  <h1>Four tracks, one box of pieces</h1>
  <p class="tagline">Every layout below is solver-verified to close exactly, uses only
  pieces in your <a href="https://app.warmhub.ai/orgs/wjcorey/repos/carrera-track"
  style="color:var(--acc)">wjcorey/carrera-track</a> inventory, and comes with a full
  assembly sheet. Build one at a time — they all share the same collection.</p>
</header>
<section class="fade" style="animation-delay:.1s">
  <h2>The lineup</h2>
  <div class="cards-idx">{cards}</div>
</section>
<section class="fade" style="animation-delay:.2s">
  <h2>Side by side</h2>
  <div class="tbl-wrap"><table><thead><tr><th>Track</th><th class="num">Lap</th>
  <th class="num">Footprint</th><th class="num">Pieces</th><th class="num">Corners</th>
  <th class="num">Lane &Delta;</th></tr></thead><tbody>{rows}</tbody></table></div>
  <div class="callout"><strong>Lane &Delta; explained.</strong> On a normal loop the outer
  slot is 622 mm longer per lap (2π &times; 99 mm slot spacing). Only a track that crosses
  itself can be perfectly fair — that's The Equalizer's whole reason to exist.</div>
</section>
<section class="fade" style="animation-delay:.3s">
  <h2>Shared build notes</h2>
  <div class="grid2">
  <div class="card"><h3>Power &amp; digital</h3>
  <p>The Control Unit is placed in every layout (green piece, start/finish). The
  Wireless+ charging straight appears where there's a low-speed zone. Lane-change pieces
  are positioned to give at least two passing opportunities per lap.</p></div>
  <div class="card"><h3>What stays in the box</h3>
  <p>Pit-lane turnouts, the pit adapter and the two single-lane straights aren't
  solver-verified yet (catalog <code>solverReady:false</code>) — add the pit lane as an
  off-circuit spur next to any start/finish straight if you want pit stops. Border
  end-pieces: put them on hairpin and banked-curve exits.</p></div>
  </div>
</section>
<footer>
  Inventory: <a href="https://app.warmhub.ai/orgs/wjcorey/repos/carrera-track">wjcorey/carrera-track</a>
  &middot; piece geometry: <a href="https://app.warmhub.ai/orgs/slotcars">slotcars/carrera-catalog</a>
  &middot; closure solver: designs/design_tracks.py
</footer>
</div></body></html>"""
    (OUT / "index.html").write_text(index_html)
    print("wrote index")


if __name__ == "__main__":
    main()
