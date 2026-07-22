# solver — closure geometry engine + official-layout oracle

- `data.json` — piece geometry (both candidate radius models kept for the adjudication record), part→pieceType mapping for official plan parts lists.
- `geometry.py` — SE(2) transform composition, closure check, centerline/lane lengths, footprint, angle-feasibility DP, randomized closure search.
- `oracle.py` — run `python3 oracle.py`: circle identities, official-plan length comparison, least-squares radius fit, closure search.
- `fixtures/official-circuits.json` — 6 official Carrera circuit plans (piece lists + published dims/lengths) extracted from carrera-toys.com PDFs.
- `designer.py` — inventory-constrained closed-layout generation (curve-subset angle enumeration + closure search + room filter + length/fairness ranking).
- `render.py` — layout sequence → exact-geometry SVG (track surface, dashed slot lanes, numbered pieces, start/finish bar); `svg_string()` for embedding.
- `buildsheet.py` — proposal → self-contained printable HTML build sheet (SVG drawing, stats, parts list, run-compressed assembly steps, optional shopping/notes sections). Re-verifies closure at render time and prints the honest verdict.

## Adjudication result (2026-07-16)

Least-squares radii from 4 official plan lengths: r1 298.9, r2 496.5, r3 695.1, r4 893.6 mm — spacing ≈198 mm confirms the exact-nesting model (297/495/693/891); the rounded 300/500/700/900 model (200 mm spacing) is refuted. The uniform ~+1.9 mm/radius residual is constant per curve-degree (~0.033 mm/°) across all four plans → a Carrera-planner length convention, not a physical radius difference. Adopted catalog values: exact-nesting. Solver closure tolerance ±5 mm absorbs the residual.

Slot lanes are exactly centerline ∓311 mm (2π·49.5) on any closed loop, so published lengths are centerline lengths.

Known limitation: the randomized search proves small piece-sets closable but doesn't reconstruct 60-piece official circuits — the Phase 3 designer builds layouts constructively (design *for* closure) instead of searching arbitrary bags.
