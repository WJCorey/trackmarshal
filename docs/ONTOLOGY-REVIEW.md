# ONTOLOGY-REVIEW — TrackMarshal vs the WarmHub ontology guidebook

Audit of the v1 design against "Building a WarmHub-Native Ontology" (v0.1, 2026-07-08), performed 2026-07-16. Result: v2 SHAPES. This file doubles as the design dossier the guide asks for (naming contracts, anti-inferences, golden objects, agent contracts, decision log deltas).

## Changes made in v2

| # | Guide principle | v1 problem | v2 fix |
|---|---|---|---|
| 1 | Stage 2: identity tests; "most ontology failures are identity failures" | `TrackPiece` conflated geometric piece type with retail SKU. 20509 (4-pack) and 20601 (2-pack) contain the *same piece*; kits contain heterogeneous pieces. Quantities were ambiguous (packs? pieces?) | Split into `PieceType` (geometry, solver unit) and `Product` (SKU) + `ProductContent` about `Pair[Product, PieceType]`. `ProductSet`/`SetContent` merged into Product/ProductContent — a 4-pack and a starter set are the same shape of thing. Holdings/PieceUsage now in unambiguous piece units |
| 2 | Anti-pattern 4: no generic `confidence` dumping ground | `SpecSource.confidence: 0–1`, undefined semantics | Dropped. Replaced by `sourceKind` method classes; conflicts preserved as parallel SpecClaims; adjudicated value on `PieceType` with `geometryBasis` rationale (the LocationObservation → PreferredLocation pattern) |
| 3 | §3 Stage 6: source claims in source language; conflict is knowledge | v1 `SpecSource.values` implied normalized values | `SpecClaim.claimedValues` preserves source wording/units (marketing "inside edge 20 cm" stays distinct from centerline 297 mm), plus `quotedText` locator, `observedAt`, optional `archiveUrl` |
| 4 | §1.5 naming as navigation; tree-then-graph | `TrackPiece/<partNumber>` — flat, and part numbers are SKU keys, wrong axis for geometry | `PieceType/<kind>/<slug>` kind-led tree (`PieceType/curve/**` globs all curves); `Product/<partNumber>` keeps the source's stable key where it belongs |
| 5 | §1.4: don't duplicate Pair endpoints as raw wrefs; do include human-readable context | v1 mirrored `setWref`/`pieceWref` onto Pair assertions | Keep human-readable ids (partNumber, slugs, titles); drop redundant raw wref duplicates |
| 6 | Identity commitment: source id ≠ canonical id | Full SKUs (20020509) and legacy Exclusiv numbers had no home → risk of duplicate Products | `Product.skuAliases` |
| 7 | Unresolved stays unresolved | Uncertain set contents (e.g. 26956 ⚑) would have been entered as facts | `ProductContent.verified: false` — explicit, queryable incompleteness |
| 8 | Banked-curve identity | Banking as a maybe-flag | Distinct `PieceType/curve-banked/**` — projected geometry differs; interchangeability is the identity test |

## Deliberate deviations (documented, not accidental)

- **Two repos, not four.** The guide's four layers (grounding/identity/composition/belief) are epistemic roles, and anti-pattern 7 warns against premature repo splits. At ~50 piece types and ~4 sources, grounding (SpecClaim), identity (PieceType/Product split), and composition (adjudicated geometry, ProductContent) live in one catalog repo with the layers documented per shape; belief is the personal repos. Split later only if operational pain demands it.
- **No SourceArtifact/sha256 ladder in v1.** Full content-hashed artifact provenance is right for regulatory-scale ingestion; for ~4 stable web sources, `sourceUrl + archiveUrl + quotedText + observedAt` on SpecClaim is the proportional rung. Revisit if sources start disappearing (schlitzflitzer.de already did — hence `archiveUrl`).
- **No Veritas/BDU anywhere yet.** Dimension claims are facts with provenance ("epistemologizing the furniture" is anti-pattern 5); DesignBeliefs are single-author. If beliefs get crowdsourced or dimensions get formally contested, promote per Stage 10.
- **`Layout.sequence` as JSON data, not a List collection.** Collections have fixed membership; a layout under active design revises constantly. One canonical artifact (thing, versioned) + materialized PieceUsage for traversal. Matches guide §1.2 "single canonical state."

## Anti-inference rules (put these in agent prompts)

1. Marketing radii ("20/40 cm") are *rounded edge* values — never feed them to the solver; centerline transform comes from adjudicated `PieceType` fields only.
2. A part number is a *product*, not a piece: quantity 1 of Product 20509 = 4 standard straights.
3. Same arc angle ≠ interchangeable (R1/30° ≠ R2/30°); same radius ≠ interchangeable (flat R2 ≠ banked R2).
4. `kind: digital` ≠ unusable on analog, and analog ≠ usable on digital — read the compatibility booleans, never infer from kind or line.
5. `status: discontinued` ≠ incompatible or invalid in layouts/inventories.
6. Box art / set photos ≠ authoritative contents; only `ProductContent` with `verified: true`.
7. A piece type appearing in a kit ≠ purchasable individually (hairpin components).
8. Absence of a SpecClaim ≠ dimension unknown to the world — it means *we haven't grounded it yet*.
9. Piece counts in official circuit-PDF plans are facts about that plan, not about product availability.

## Golden objects (hand-model before bulk load; permanent regression fixtures)

1. **20509 vs 20601** — two Products, one PieceType. The case that forced the split.
2. **20020509 vs 20509** — skuAliases, one Product.
3. **Legacy Exclusiv-era number for the same profile** — alias or discontinued Product, same PieceType; never a duplicate PieceType.
4. **Flat R2 vs banked R2** — same nominal radius, distinct PieceTypes.
5. **Pit lane kit 30356** — one Product → 6 heterogeneous PieceTypes (turnouts, single-lane straights, adapter, ends).
6. **Hairpin 20613** — kit-only PieceTypes with no single-piece Product.
7. **Control Unit 30352** — electronics that is also a 345 mm straight geometrically; digital-only compatibility.
8. **Starter set** — track ProductContent + `nonTrackContents` (cars, controllers) out of scope.
9. **Discontinued 20515** — a Holding referencing a discontinued Product's pieces must stay fully valid.
10. **26956 with unverified contents** — `verified: false`, not guessed quantities.

## Naming contracts

```yaml
shape: PieceType
name_template: PieceType/{kind}/{geometry-slug}
example: PieceType/curve/r1-60
identity_stability_test: >
  Product-line changes, discontinuation, or new SKUs must never make this name false.
  Kind and geometry are intrinsic to the piece.
representative_globs: ["PieceType/curve/**", "PieceType/{straight,curve}/**", "PieceType/digital/**"]

shape: Product
name_template: Product/{part-number}   # Carrera's own stable key, 5-digit form
example: Product/20509
identity_stability_test: pack size, price, and status changes never touch the name.

# Personal repos
Holding/{pieceTypeSlug} · Layout/{slug} · PieceUsage/{layout}/{pieceTypeSlug} ·
BuildLog/{layout}/{iso-date} · DesignBelief/{slug} · Topic/{slug} · Room/{slug}
```

Ten-question naming review: convention inferable from examples ✓ · nearby Things predictable ✓ · glob-selectable subtrees ✓ · subscription boundaries reuse them (pipeline watches `Product/**`) ✓ · segments meaningful/stable ✓ · natural grain (kind for geometry, SKU for retail) ✓ · no relationships in names ✓ · no identity-preserving change breaks a name ✓ · predictable depth per shape ✓ · no deeper than needed ✓.

## Agent write contracts

```yaml
agent: catalog-pipeline           # monthly new-product/discontinuation watcher
subscribes_to: []                 # cron, not event-driven
reads: [carrera-catalog, carrera-toys.com, carreraslots.com]
writes_only: carrera-catalog
may_create: [Product, ProductContent(verified:false), SpecClaim]
may_not_create: [PieceType]       # new geometry = human-reviewed; new SKUs usually reuse existing types
required_behavior: [idempotent deterministic names, propose status:discontinued never delete,
                    every geometric datum lands with a SpecClaim]

agent: importer-skill             # inventory seeding + PieceUsage regeneration (shipped as track-inventory)
reads: [carrera-catalog, <racer>-track]
writes_only: <racer>-track
may_create: [Holding, Layout, PieceUsage, BuildLog, Room, DesignBelief, Topic(sparingly — prefer the 3 seeded)]
may_not_create: [PieceType, Product, ProductContent, SpecClaim]   # catalog gaps get reported, not patched locally
required_behavior: [quantities in piece units, regenerate PieceUsage on every Layout write]

agent: track-designer-skill
reads: [carrera-catalog, <racer>-track]
writes_only: <racer>-track
may_create: [Layout, PieceUsage]
may_not_create: [Holding]         # designing a track never mutates inventory
```

## Spike findings (2026-07-16, `wjcorey/tm-spike-catalog` + `tm-spike-personal`)

Verified platform behavior to design against (guidebook §1.3: "verify the collections behavior at build time, every time"):

1. **Cross-repo `about` works and is bidirectionally visible.** A `Holding` in the personal repo about `wh:wjcorey/tm-spike-catalog/PieceType/straight/full` is returned by `thing_about` queried from the personal repo (canonical target) *and* appears in the catalog-side `thing_about` on the piece, alongside local Pair assertions. "Everything known about this piece across repos" is one query. `aboutWref` is version-pinned (`@v1`) as documented.
2. **No inline collection `about` on MCP.** `about: {pair:[...]}` is rejected; create the collection as its own named op (`{kind:"collection", type:"pair", name, members}`) and assert about `Pair/<name>`. Deterministic pair names use `--` as separator — `+` is reserved for the historical auto-name namespace.
3. **Shape field arrays need `items`** (`{"type":"array?", "items":{"type":"string"}}`). A failed shape op cascades NOT_FOUND to every dependent op in the same commit; ops are validated in order and commits are per-op (partial application is normal — design ops to be idempotent and re-submittable).
4. Golden case #1 (20509 vs 20601 → one PieceType, two Products) modeled and queryable from the PieceType side with `resolveCollections:true`.
5. **Array fields can't have object items** — `items.type` accepts only `number|string|boolean|wref|array`. Structured sequences get documented string encodings instead: `Layout.sequence` items are `'<pieceTypeSlug>[:L|R]'`, `Room.obstacles` items are `'xMm,yMm,widthMm,lengthMm,label'`. (Discovered 2026-07-16 loading `wjcorey/carrera-track`.)

## Competency questions (formalized; each is an acceptance test)

- CQ-1 dims/transform of piece type X, with basis (PieceType + geometryBasis → SpecClaims)
- CQ-2 which dimensions rest on a single non-official source (SpecClaim aggregation by sourceKind)
- CQ-3 contents of product P / products containing piece type X (ProductContent, both directions)
- CQ-4 cheapest current Product covering a piece shortfall (ProductContent ⋈ status rollup)
- CQ-5 my full inventory in piece units (Holding aggregation)
- CQ-6 can I build layout L with what I own; what's missing (PieceUsage ⋈ Holding)
- CQ-7 which of my layouts fit room R (Layout.footprint vs Room)
- CQ-8 which layouts use piece type X (PieceUsage object side)
- CQ-9 which built layouts scored funRating ≥ 8 and what do they share (BuildLog → Layout)
- CQ-10 what does this racer believe about good tracks, with what evidence (DesignBelief → Layouts)
- CQ-11 why do we believe R2 centerline = 495 mm (SpecClaim traversal — the provenance acceptance bar)
- CQ-12 what changed in the catalog this month (version history + pipeline commits)

Context-free reader test: CQ-1, 3, 5, 6, 11 must be answerable by an MCP agent with no session context, from repo descriptions alone.
