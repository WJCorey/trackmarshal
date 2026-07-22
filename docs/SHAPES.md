# SHAPES — TrackMarshal shape catalog (v2)

v2 after review against the WarmHub ontology guidebook (2026-07-16). Headline change: the v1 `TrackPiece` conflated two identities — the **geometric piece type** (what the solver reasons about) and the **retail product/SKU** (what you buy). Carrera sells the same standard straight as a 4-pack (20509) and a 2-pack (20601); pack ≠ piece. Guide Stage 2 ("most ontology failures are identity failures") flushed this out. See ONTOLOGY-REVIEW.md for the full audit.

Epistemic layering (guide §2), mapped without premature repo splits (anti-pattern 7): grounding = `SpecClaim` assertions; identity = the PieceType/Product split; composition = adjudicated geometry + `ProductContent`; belief = the personal repos. Two physical repos, four layers documented.

Naming: tree-then-graph. `PieceType` names lead with the dimension agents narrow by (kind); `Product` names use Carrera's own stable keys. No relationship or mutable state in names.

---

## Layer 1 — public catalog repo (`carrera-catalog`)

### `PieceType/<kind>/<slug>` — thing

One geometric/functional piece type — the unit the solver, inventories, and layouts reason in. Examples: `PieceType/straight/full`, `PieceType/straight/quarter`, `PieceType/curve/r1-60`, `PieceType/curve-banked/r2-30`, `PieceType/special/chicane`, `PieceType/digital/lane-change-left`, `PieceType/digital/control-unit`. Banked curves are distinct PieceTypes, not a flag on flat ones — their projected geometry differs (identity test: two pieces are the same PieceType iff geometrically and functionally interchangeable in a layout).

Naming contract: glob `PieceType/curve/**` = all flat curves; identity-stability — kind and geometry are intrinsic, no name goes false under product-line changes.

| Field | Notes |
|---|---|
| `title` | "Standard straight", "Curve 2/30°" |
| `kind` | `straight \| curve \| curve-banked \| special \| digital \| border \| accessory` (mirrors name segment for filtering) |
| `lengthMm` | straights: centerline length; null for curves |
| `radiusMm`, `arcDeg` | curves: **centerline** radius and arc angle; null otherwise |
| `transform` | `{dxMm, dyMm, dHeadingDeg}` entry→exit centerline rigid-body transform; the solver's input. Stored as left-hand orientation; solver mirrors for right |
| `lanes` | integer, usually 2 |
| `geometryBasis` | short rationale for the adjudicated dimensions + which SpecClaims carry the evidence — the "PreferredLocation with rationale" pattern; per-source values live in SpecClaims, never overwritten |
| `analogCompatible`, `digitalCompatible` | booleans — do not infer from `kind` (anti-inference: "digital" pieces vary in analog behavior) |
| `notes` | quirks, caveats |

### `Product/<partNumber>` — thing

A purchasable retail SKU: single-type packs (20509), kits (20613 hairpin, 30356 pit lane), extension sets (26953), full starter sets. One shape for all of them — they differ only in contents. Serves: "what's in the box?", "cheapest product to get 6 more R2 curves?", inventory seeding.

| Field | Notes |
|---|---|
| `partNumber` | common 5-digit form; name suffix |
| `skuAliases` | e.g. full SKU `20020509`, legacy Exclusiv-era numbers — source-identifier aliasing, never separate Products |
| `title`, `line` | line: `universal \| evolution \| d132 \| d124` |
| `productClass` | `piece-pack \| kit \| extension-set \| starter-set \| accessory` |
| `status` | `current \| discontinued` — in data, never in the name; discontinued Products stay (inventories reference them) |
| `year`, `manualUrl`, `imageUrl` | links only, never bytes |
| `nonTrackContents` | free text: cars, controllers, power supplies in starter sets — out of scope for ProductContent |

### `ProductContent/<partNumber>/<pieceTypeSlug>` — assertion, `about: Pair[Product, PieceType]`

How many of a piece type a product contains. Deterministic name → idempotent pipeline writes. Four-direction test: box contents (subject side) ✓; "which products contain quarter straights?" (object side, `--resolve-collections`) ✓; aggregation ✓; rollup "cheapest in-production product covering my shortfall" ✓.

Data: `quantity`, `partNumber`, `pieceTypeSlug`, `pieceTitle` (human-readable context per guide §1.4; the Pair itself carries the edges), `verified` (boolean — unverified contents stay explicitly unverified, never guessed; guide: unresolved stays unresolved).

### `SpecClaim/<pieceTypeSlug>/<source-slug>` — assertion, `about: PieceType`

Grounding layer: **what a source published about a piece type's geometry**, in the source's own language — not truth. Conflicts between sources are preserved as knowledge; adjudication lives in `PieceType.transform` + `geometryBasis`. Serves: "why do we believe R2 centerline is 495 mm?", "which dims rest on a single non-official source?" (QC).

| Field | Notes |
|---|---|
| `sourceUrl`, `archiveUrl?` | where, plus durable copy when available |
| `sourceKind` | `official-product-page \| official-pdf \| retailer-tech-page \| community-cad \| community-forum \| own-measurement \| derived-geometrically` — method class, not a confidence float (guide anti-pattern 4: v1's `confidence` field dropped) |
| `claimedValues` | the values as published, source units/wording preserved (e.g. "inside edge 20 cm" — marketing edge-radius, not centerline) |
| `quotedText?` | short verbatim excerpt as locator |
| `observedAt` | ISO-8601 — when we read the source (system time ≠ source time) |
| `pieceTypeSlug` | denormalized identity context |

---

## Layer 2 — personal repo component (`<racer>-track`)

Installable component; additive-only evolution once it has consumers.

### `Holding/<pieceTypeSlug>` — assertion, `about:` catalog `PieceType` (cross-repo wref)

Inventory **in piece units, not packs**: "I own 14 standard straights." Attribution + revision history (append-only growth of the collection) → assertion. One Holding per piece type; quantity changes are revisions.

Data: `quantity`, `condition?`, `storageNote?`, `acquiredNotes?` (free text or Product wrefs — bought-in-box provenance), `pieceTypeSlug`, `pieceTitle`.

### `Room/<slug>` — thing

`widthMm`, `lengthMm`, `obstacles` (rectangles), `notes`. One truth → thing.

### `Layout/<slug>` — thing

A designed/built track. Fields as v1: `title`, `description`, `sequence` (ordered `{pieceTypeWref, orientation, laneSwap}` — one canonical artifact as JSON data; traversal is PieceUsage's job), `laneLengthsMm`, `footprintMm`, `roomWref`, `closureVerified`, `status` (`designed | built | retired`).

### `PieceUsage/<layout-slug>/<pieceTypeSlug>` — assertion, `about: Pair[Layout, PieceType]`

Materialized bill of materials, deterministically regenerated from `sequence` on every Layout revise (regeneration rule lives in the shape description; the importer/designer skill owns it). Earns traversability: "which layouts use the crossing?", "buildable with current Holdings?" = PieceUsage ⋈ Holding arithmetic. Data: `quantity`, `layoutSlug`, `pieceTypeSlug`.

Operational caveat (guide §1.3): Pairs are version-pinned; queries from either endpoint must use `--resolve-collections`, and a revised PieceType yields new Pairs on subsequent assertions — correct provenance, but never look up Pair names directly.

### `BuildLog/<layout-slug>/<date>` — assertion, `about: Layout`

`builtOn`, `whoRaced`, `funRating` (1–10), `issues`, `photos` (links). Single-author event; the evidence stream that keeps DesignBeliefs honest.

### `Topic/<slug>` — thing

Description-only belief anchor (`Topic/flow`, `Topic/kid-friendly`, `Topic/overtaking`).

### `DesignBelief/<slug>` — assertion, `about: Topic`

"One long straight beats two chicanes for kids." Data: `statement`, `strength` (0–1, defined: the author's current subjective weight for the solver's soft objectives — single-author personal repo, so no aggregation semantics needed; if beliefs ever get crowdsourced, promote to binomial propositions + certainty opinions per guide Stage 10), `evidenceLayoutWrefs` (denormalized; first-class `BeliefEvidence` about `Pair[DesignBelief, Layout]` is deferred until the query is real — mechanism confirmed fine, assertions are Things).

---

## Question-coverage audit (competency questions, abbreviated — full CQ list in ONTOLOGY-REVIEW.md)

| Question | Shapes earning it |
|---|---|
| What piece types exist / dims of X? | PieceType |
| Why do we believe dimension D / weakest-sourced dims? | SpecClaim + geometryBasis |
| What's in product Y / cheapest way to get more X? | Product, ProductContent |
| What do I own / enough for layout L? | Holding, PieceUsage |
| What layouts fit my room + inventory? | Layout, Room, PieceUsage, Holding |
| Which layouts use piece type X? | PieceUsage |
| Was the design good in real life? | BuildLog |
| What makes a good track for me? | Topic, DesignBelief |

Deferred (no current question): Racer profile, RaceResult/lap times, BeliefEvidence pairs, price tracking, `Purchase` events.

## Checkpoint status

- Q1 (every shape cites a question): pass, table above.
- Q2 (four-direction): ProductContent and PieceUsage walked above; single-target assertions (SpecClaim, Holding, BuildLog, DesignBelief) each have one real endpoint.
- Q3 (primitives): lookup/geometry = things; attributed/perspectival = assertions; no BDU (no binomial propositions yet — dimension claims are facts with provenance, beliefs are single-author).
- Q4 (foundations): stable names (kind-led PieceType tree, part-number Products); descriptions drafted here → manifest; append-only; no debt-shapes; human-readable identity context on Pair-targeted assertions.
- Q5 (pitfalls + context-free reader): materialization leakage → PieceUsage regeneration rule in shape description. Cross-repo `about` + `--resolve-collections` mechanics validated as build step 1 before any data loads (`about` is immutable).
