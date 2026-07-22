"""Generate a self-contained HTML build sheet for a layout proposal.

Usage:
  python3 buildsheet.py --proposal p.json --out sheet.html \
      [--title "..."] [--description "..."] [--layout-url https://app.warmhub.ai/...] \
      [--room-w 4000 --room-l 3000] [--shopping-html "<p>...</p>"] [--notes-html "<p>...</p>"]

p.json is one designer.py proposal ({"sequence": [...], "laneLengthsMm": [...], ...})
or any object with at least a "sequence" list; all stats are recomputed from the
sequence, so hand-built proposals work too. Closure is re-verified here — the sheet
prints the actual verdict, never an assumed one. Pure stdlib; the output prints fine.
"""

import argparse
import html
import json

import geometry as g
import render

MODEL = "exact-nesting"


def piece_title(slug):
    pt = g.DATA["pieceTypes"].get(slug)
    if pt is None:
        return slug
    if pt["kind"] == "straight":
        name = {"straight/full": "Standard straight", "straight/third": "1/3-straight",
                "straight/quarter": "1/4-straight"}.get(slug, slug)
        return f"{name} ({pt['lengthMm']:g} mm)"
    r = g.DATA["radiusModels"][MODEL][pt["radiusKey"]]
    return f"Curve {pt['radiusKey'].upper()}/{pt['arcDeg']}° (centerline {r:g} mm)"


def step_label(slug, hand):
    t = piece_title(slug)
    return f"{t} — turn {'left' if hand > 0 else 'right'}" if hand else t


def assembly_rows(entries):
    """Compress consecutive identical entries into (first_no, last_no, label) runs."""
    rows, i = [], 0
    while i < len(entries):
        j = i
        while j + 1 < len(entries) and entries[j + 1] == entries[i]:
            j += 1
        slug, hand = render.decode(entries[i])
        rows.append((i + 1, j + 1, step_label(slug, hand)))
        i = j + 1
    return rows


def build(proposal, title, description="", layout_url=None, room=None,
          shopping_html="", notes_html=""):
    entries = proposal["sequence"]
    seq = [render.decode(e) for e in entries]
    closed = g.is_closed(seq, MODEL, tol_mm=5.0, tol_deg=0.5)
    la, lb = g.lane_lengths(seq, MODEL)
    w, d = g.footprint(seq, MODEL)
    used = {}
    for slug, _ in seq:
        used[slug] = used.get(slug, 0) + 1

    stats = [
        ("Lane A / Lane B", f"{la / 1000:.2f} m / {lb / 1000:.2f} m"),
        ("Lane imbalance", f"{abs(la - lb):.0f} mm"),
        ("Centerline", f"{(la + lb) / 2000:.2f} m"),
        ("Footprint", f"{w / 1000:.2f} × {d / 1000:.2f} m"),
        ("Pieces", f"{len(seq)}"),
        ("Closure", "verified ✓ (±5 mm / 0.5°)" if closed else "NOT VERIFIED — do not trust this plan"),
    ]
    if room:
        fits = min(w, d) <= min(room) and max(w, d) <= max(room)
        stats.append(("Room fit", f"{'fits' if fits else 'DOES NOT FIT'} {room[0] / 1000:.2f} × {room[1] / 1000:.2f} m"))

    esc = html.escape
    parts_rows = "\n".join(
        f"<tr><td>{esc(piece_title(s))}</td><td class='n'>{n}</td></tr>"
        for s, n in sorted(used.items(), key=lambda kv: (-kv[1], kv[0])))
    steps = "\n".join(
        f"<li value='{a}'>{esc(label)}{f' <span class=run>× {b - a + 1} (pieces {a}–{b})</span>' if b > a else ''}</li>"
        for a, b, label in assembly_rows(entries))
    stat_rows = "\n".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in stats)
    link = (f"<p class='muted'>Layout on WarmHub: <a href='{esc(layout_url)}'>{esc(layout_url)}</a></p>"
            if layout_url else "")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{esc(title)} — build sheet</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", sans-serif; color: #1a1a1a; max-width: 960px;
         margin: 2rem auto; padding: 0 1rem; line-height: 1.45; }}
  h1 {{ margin-bottom: .2rem; }} h2 {{ margin-top: 2rem; border-bottom: 1px solid #ddd; padding-bottom: .2rem; }}
  .muted {{ color: #555; }} .run {{ color: #555; font-size: .9em; }}
  table {{ border-collapse: collapse; }} td, th {{ padding: .25rem .8rem .25rem 0; text-align: left; vertical-align: top; }}
  td.n {{ text-align: right; }} th {{ font-weight: 600; }}
  .drawing svg {{ width: 100%; height: auto; border: 1px solid #eee; }}
  ol {{ columns: 2; column-gap: 2.5rem; }} ol li {{ break-inside: avoid; }}
  .warn {{ background: #fff3f3; border: 1px solid #c33; padding: .6rem 1rem; }}
  @media print {{ body {{ margin: 0; }} a {{ color: inherit; text-decoration: none; }} }}
</style></head><body>
<h1>{esc(title)}</h1>
{f"<p>{esc(description)}</p>" if description else ""}
{"" if closed else "<p class='warn'><strong>Closure not verified.</strong> The solver could not confirm this sequence closes within tolerance — treat the drawing as a sketch, not a plan.</p>"}
<div class="drawing">{render.svg_string(entries, title)}</div>
<h2>Stats</h2>
<table>{stat_rows}</table>
<h2>Parts list</h2>
<table><tr><th>Piece</th><th class="n">Qty</th></tr>{parts_rows}</table>
<h2>Assembly</h2>
<p class="muted">Numbers match the circles on the drawing; build counter-clockwise from the red start/finish bar.</p>
<ol>{steps}</ol>
{f"<h2>Get more track</h2>{shopping_html}" if shopping_html else ""}
{f"<h2>Notes</h2>{notes_html}" if notes_html else ""}
{link}
<p class="muted">Generated by TrackMarshal — geometry from the open catalog
<a href="https://app.warmhub.ai/orgs/slotcars">slotcars/carrera-catalog</a> (exact-nesting radii).
Not affiliated with or endorsed by Carrera Toys GmbH.</p>
</body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposal", required=True)
    ap.add_argument("--out", default="buildsheet.html")
    ap.add_argument("--title", default="Layout")
    ap.add_argument("--description", default="")
    ap.add_argument("--layout-url", default=None)
    ap.add_argument("--room-w", type=float, default=None)
    ap.add_argument("--room-l", type=float, default=None)
    ap.add_argument("--shopping-html", default="")
    ap.add_argument("--notes-html", default="")
    args = ap.parse_args()
    proposal = json.loads(open(args.proposal).read())
    room = (args.room_w, args.room_l) if args.room_w and args.room_l else None
    doc = build(proposal, args.title, args.description, args.layout_url, room,
                args.shopping_html, args.notes_html)
    open(args.out, "w").write(doc)
    print(args.out)
