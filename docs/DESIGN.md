# TrackMarshal — Carrera slot-car track knowledge on WarmHub

Working name: **TrackMarshal** (the marshal is the official who walks the track). Name check against existing projects still needed before registering anything — see PLAN OQ-1.

## The problem

Corey races Carrera 1:32/1:24 slot cars (Evolution / Digital 132 / Digital 124 — all three product lines share the same track system; this is *not* the smaller 1:43 GO!!! track). Designing a track layout that (a) closes geometrically, (b) fits the room, and (c) uses only pieces you actually own is a real constraint-satisfaction problem. The apps that used to solve it are abandoned. An agent could solve it — but only if it knows:

1. **The universe of pieces** — every part number, its dimensions, and how pieces connect. Public, factual, shared by every Carrera racer on earth.
2. **Your pieces** — what you own, how many, what condition. Private, per-racer.
3. **Your taste** — beliefs about what makes a good track for *your* races (kids vs. adults, flow vs. technical), and the build history that backs those beliefs up.

That split — one public catalog everyone shares, many personal repos composed on top — is the WarmHub thesis in miniature, and the Project Greenhouse brief almost verbatim.

## Architecture: two layers, three deliverables

```
┌──────────────────────────────────────────────────────┐
│  PUBLIC: carrera-catalog (one repo, community-owned) │
│  PieceType/curve/r1-60 (geometry, solver unit)       │
│  Product/20509 (retail SKU) + ProductContent (Pair)  │
│  SpecClaim (per-source dimension grounding)          │
└──────────────────────────▲───────────────────────────┘
                           │ cross-repo wrefs (assert about, never copy)
┌──────────────────────────┴───────────────────────────┐
│  PERSONAL: <racer>-track (many repos, one per racer) │
│  Holding (inventory in piece units), Layout,         │
│  PieceUsage, BuildLog, DesignBelief, Room            │
└──────────────────────────────────────────────────────┘
```

The catalog repo internally carries the ontology guidebook's four epistemic layers without premature repo splits: grounding (`SpecClaim`), identity (`PieceType` ≠ `Product`), composition (adjudicated geometry, `ProductContent`); the personal repos are the belief layer. Full audit in `ONTOLOGY-REVIEW.md`.

1. **`carrera-catalog`** — public WarmHub repo: every piece type and retail product, with geometry precise enough to compute layout closure, and per-source provenance for every dimension (official doc vs. community CAD vs. derived).
2. **A personal-repo component + importer skill** — installable shape bundle so any racer spins up their own repo in minutes ("I own set 20025240 plus 6 extra R2 curves" → seeded `Holding`s). This is the one-repo-becomes-ten mechanism.
3. **A track-designer skill** — geometry engine (closure solver) + graph reader: takes your Holdings, Room, and DesignBeliefs, proposes buildable Layouts, writes them back with PieceUsage edges.

## Key decisions

- **D1 — Facts in the catalog, opinions in personal repos.** Geometry is a thing field (one adjudicated truth with `geometryBasis` rationale). Where sources disagree, `SpecClaim` assertions preserve the competing published values in source language — conflict is knowledge, adjudication is separate.
- **D2 — Personal repos assert about catalog things, never copy them.** `Holding/straight-full` is an assertion whose `about` is the catalog's `PieceType/straight/full` (cross-repo wref). No mirrored data beyond human-readable identity context.
- **D3 — Geometry math lives in the skill, not the graph.** Closure validation is computation. The graph stores each piece's rigid-body transform (the *knowledge*); the solver that composes transforms and checks loop closure is code shipped with the track-designer skill.
- **D4 — Layout sequence is data; per-piece usage is materialized as Pair assertions.** The ordered piece sequence is a JSON field on `Layout` (it's one canonical artifact). `PieceUsage` assertions (`about: Pair[Layout, PieceType]`) are deterministically regenerated from the sequence on every revise, so "which layouts use piece X" and "can I still build layout L" stay graph traversals.
- **D5 — Closure oracle for QC, not calipers.** Carrera's own set manuals and downloadable circuit PDFs show closed loops with exact piece lists. Candidate dimension models either reproduce those closures or they don't — official layouts mathematically discriminate between e.g. the 297/495/693/891 mm and rounded 300/500/700/900 radius models without measuring a single piece. Physical measurement is a last-resort tie-breaker only.
- **D6 — Personal shapes ship as a foundation component (additive-only evolution).** Once other racers install it, field renames are forbidden; schema changes are additive.
- **D7 — Compile facts, never extract compilations.** Dimensions/part numbers are unprotectable facts; proprietary app piece libraries are protected compilations (EU database right). Every datum cites its source via `SpecClaim`. Dataset CC-BY-SA, code MIT.
- **D8 — Piece type ≠ product.** The solver, inventories, and layouts reason in `PieceType` units; commerce (packs, kits, sets, part numbers, discontinuations) lives on `Product`. Forced by the 20509-vs-20601 golden case (see ONTOLOGY-REVIEW.md).

## Docs

- `PLAN.md` — build roadmap against the Greenhouse clock (crunch week last week of July, demo first week of August), open questions, decision log.
- `SHAPES.md` — field-by-field shape catalog for both layers, with four-direction-test rationale on every assertion.
- `ONTOLOGY-REVIEW.md` — audit against the WarmHub ontology guidebook: v1→v2 changes, deliberate deviations, anti-inference rules, golden objects, naming + agent contracts, competency questions.
- `DATA-SOURCES.md` — where dimensions come from, licensing matrix, pipeline design.
- `PIECES.md` — draft seed data (piece tables, geometry model, open items).

## Status

2026-07-16: design v2 complete; build step 1 done (cross-repo mechanics validated, exact-nesting radii adjudicated from official circuit plans — no measurement needed; solver + 6 oracle fixtures in `solver/`). **Phase 1 catalog LIVE: [slotcars/carrera-catalog](https://app.warmhub.ai/orgs/slotcars) (public)** — 68 PieceTypes, 71 Products (incl. starter set 30044, researched), ~87 ProductContents, 16 SpecClaims; generated by `catalog/build_ops.py` + follow-up commits. **Phase 2 largely done:** `wjcorey/carrera-track` (public worked example) carries the 7 personal shapes + Corey's real 18-Holding inventory; solver confirms it closes an ~11.4 m layout in 3.7 × 4.1 m. Component packaged + schema-valid in `component/`; designer skill v1 shipped (`solver/designer.py` + `.claude/skills/track-designer/`). Idea not yet claimed in #project-greenhouse.

2026-07-22: **component registered — public `slotcars/carrera-track-personal` v0.1.0**, full lifecycle verified on a scratch repo (install → doctor 13/13 ok → teardown released all 8 shapes); registry source points at github.com/WJCorey/trackmarshal. Anyone can now: `wh repo create <them>/my-track` + `wh component install slotcars/carrera-track-personal --repo <them>/my-track`.
