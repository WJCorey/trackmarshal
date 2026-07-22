---
name: track-designer
description: Design buildable Carrera slot-car track layouts from the user's real WarmHub inventory (wjcorey/carrera-track composed on slotcars/carrera-catalog). Use when the user asks to design a track, plan a layout, see what tracks they can build, or fit a track to a room. Runs the closure solver, presents ranked proposals with an HTML build sheet, and on approval writes the Layout + PieceUsage back to WarmHub.
---

# Track Designer (TrackMarshal Phase 3, v2)

Engine: `solver/` (geometry.py = SE(2) closure math, designer.py = inventory-constrained generation, render.py = exact-geometry SVG, buildsheet.py = self-contained HTML build sheet). Radii are adjudicated exact-nesting values — never use rounded marketing radii.

## Procedure

1. **Ask what they want before solving.** A short conversation, not a form: *biggest possible track, or a specific vibe? Racing with kids? Sprint or endurance feel? (digital) Where do you want overtaking to happen?* Map answers to solver choices (room bounds, which proposals to favor) — and when an answer states a durable preference ("crashes frustrate my daughter"), offer to persist it as a `DesignBelief` on the seeded Topics so future sessions inherit it. Session-only preferences don't get written.
2. **Read inventory.** Via WarmHub MCP (`warmhub_thing_head` on `wjcorey/carrera-track`, shape `Holding`) or `wh thing query --shape Holding --all`, collect `{pieceTypeSlug: quantity}`. Convert to solver units — geometry.py's pieceTypes are the solver-ready set; functional units map to straight-equivalents: `digital/control-unit`, `digital/charging-straight`, `digital/lane-change-straight` → 1× `straight/full` each; `digital/double-lane-change`, `digital/lane-change-left` → 2× `straight/full` each (690 mm units); `digital/lane-change-curve-*` → 1× `curve/r1-60`. Ignore (and tell the user you're ignoring) non-solver-ready pieces: `curve-banked/*` (banking angle unverified), pit lane pieces, ramps, borders, accessories.
3. **Read constraints.** `Room` things (widthMm × lengthMm) and `DesignBelief`s (apply as soft preferences when ranking/choosing: e.g. "long straight" → prefer proposals with the longest consecutive straight run). If no Room exists and the user mentions a space, offer to save it as a `Room` first.
4. **Generate.** Write the inventory dict to a temp JSON and run:
   `python3 solver/designer.py --inventory <file> [--room-w <mm> --room-l <mm>] --top 3`
   Each proposal has: `sequence` (Layout encoding `'<slug>[:L|R]'`), per-lane lengths, centerline length, lane imbalance, footprint, piece usage, unused pieces.
5. **Present** proposals with the numbers that matter: length, footprint vs room, lane imbalance (fairness), pieces left over. Digital-racing note: place the user's lane-change units on straights before corners for overtaking (v2 solver still treats them as plain straights — placement within the sequence is a manual/agent judgment; say where you'd put them).
6. **Build sheet for the chosen proposal:**
   `python3 solver/buildsheet.py --proposal <p.json> --out <name>.html --title "..." [--description "..."] [--room-w --room-l] [--layout-url <app.warmhub.ai link>] [--shopping-html "..."] [--notes-html "..."]`
   Self-contained HTML: exact-geometry SVG with numbered pieces, stats, parts list, assembly steps (runs compressed), print-ready. It **re-verifies closure itself** and prints the real verdict — never edit that. Save it under `designs/` and open it.
   - **Shopping delta** (`--shopping-html`): when a longer/better proposal died for lack of pieces, say what unlocks it and traverse the catalog for the cheapest in-production source — `ProductContent` assertions about the needed `PieceType` (`--resolve-collections`), filter `status: current`, e.g. "2 more R1 curves → layout B (+1.2 m); cheapest current product: 20572 (×3)."
7. **On approval, write back** to `wjcorey/carrera-track` in one commit:
   - `Layout/<slug>` thing: title, description, sequence, laneLengthsMm, footprintWidthMm/LengthMm, roomWref if used, `closureVerified: true`, `status: "designed"`.
   - Per used piece type: a `pair` collection (`<layout-slug>--<piece-slug>`, members `[Layout/<slug>, wh:slotcars/carrera-catalog/PieceType/<path>]`) + `PieceUsage/<layout-slug>/<piece-slug>` assertion about it (quantity + denormalized slugs). Remember: collections are explicit named ops (no inline pairs; `+` reserved, use `--`).
   - Then regenerate the build sheet with `--layout-url` pointing at the saved Layout.
8. **After they physically build it**, prompt for a `BuildLog` (builtOn, funRating, issues) — that's the evidence stream for DesignBeliefs.

## Honesty rules

- Never mark a Layout `closureVerified: true` unless geometry.py `is_closed()` passed on the exact sequence written.
- Solver tolerance ±5 mm / 0.5° absorbs the official-planner residual; report anything looser as unverified.
- If the user asks for banked curves or the pit lane in a layout, say plainly those aren't closure-verifiable yet (catalog `solverReady: false`) and design the flat core, noting where they'd attach.
- The build sheet's closure verdict comes from re-verification at render time; a sheet that says "NOT VERIFIED" must never be handed over as buildable.

## v2 gaps (known, stated)

- Fractional straights (1/3, 1/4) rarely enter closures — random search struggles with their offsets; a constructive algorithm is the fix.
- Lane-change *placement* is agent judgment, not solver-optimized.
- Banked curves and pit lane stay outside closure math until their projected geometry is verified (OQ-5).
