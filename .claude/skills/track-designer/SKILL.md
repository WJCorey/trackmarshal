---
name: track-designer
description: Design buildable Carrera slot-car track layouts from the user's real WarmHub inventory (wjcorey/carrera-track composed on slotcars/carrera-catalog). Use when the user asks to design a track, plan a layout, see what tracks they can build, or fit a track to a room. Runs the closure solver, presents ranked proposals, and on approval writes the Layout + PieceUsage back to WarmHub.
---

# Track Designer (TrackMarshal Phase 3, v1)

Engine: `solver/` (geometry.py = SE(2) closure math, designer.py = inventory-constrained generation). Radii are adjudicated exact-nesting values — never use rounded marketing radii.

## Procedure

1. **Read inventory.** Via WarmHub MCP (`warmhub_thing_head` on `wjcorey/carrera-track`, shape `Holding`), collect `{pieceTypeSlug: quantity}`. Convert to solver units — geometry.py's pieceTypes are the solver-ready set; functional units map to straight-equivalents: `digital/control-unit`, `digital/charging-straight`, `digital/lane-change-straight` → 1× `straight/full` each; `digital/double-lane-change`, `digital/lane-change-left` → 2× `straight/full` each (690 mm units); `digital/lane-change-curve-*` → 1× `curve/r1-60`. Ignore (and tell the user you're ignoring) non-solver-ready pieces: `curve-banked/*` (banking angle unverified), pit lane pieces, ramps, borders, accessories.
2. **Read constraints.** `Room` things (widthMm × lengthMm) and `DesignBelief`s (apply as soft preferences when ranking/choosing: e.g. "long straight" → prefer proposals with the longest consecutive straight run). If no Room exists and the user mentions a space, offer to save it as a `Room` first.
3. **Generate.** Write the inventory dict to a temp JSON and run:
   `python3 solver/designer.py --inventory <file> [--room-w <mm> --room-l <mm>] --top 3`
   Each proposal has: `sequence` (Layout encoding `'<slug>[:L|R]'`), per-lane lengths, centerline length, lane imbalance, footprint, piece usage, unused pieces.
4. **Present** proposals with the numbers that matter: length, footprint vs room, lane imbalance (fairness), pieces left over. Digital-racing note: place the user's lane-change units on straights before corners for overtaking (v1 solver treats them as plain straights — placement within the sequence is a manual/agent judgment).
5. **On approval, write back** to `wjcorey/carrera-track` in one commit:
   - `Layout/<slug>` thing: title, description, sequence, laneLengthsMm, footprintWidthMm/LengthMm, roomWref if used, `closureVerified: true`, `status: "designed"`.
   - Per used piece type: a `pair` collection (`<layout-slug>--<piece-slug>`, members `[Layout/<slug>, wh:slotcars/carrera-catalog/PieceType/<path>]`) + `PieceUsage/<layout-slug>/<piece-slug>` assertion about it (quantity + denormalized slugs). Remember: collections are explicit named ops (no inline pairs; `+` reserved, use `--`).
6. **After they physically build it**, prompt for a `BuildLog` (builtOn, funRating, issues) — that's the evidence stream for DesignBeliefs.

## Honesty rules

- Never mark a Layout `closureVerified: true` unless geometry.py `is_closed()` passed on the exact sequence written.
- Solver tolerance ±5 mm / 0.5° absorbs the official-planner residual; report anything looser as unverified.
- If the user asks for banked curves or the pit lane in a layout, say plainly those aren't closure-verifiable yet (catalog `solverReady: false`) and design the flat core, noting where they'd attach.
