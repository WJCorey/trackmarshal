---
name: track-inventory
description: Set up or grow a personal Carrera slot-car repo on WarmHub — one conversation turns "here's what I own and where I race" into piece-unit Holdings, a garage (cars, spares, maintenance, lap records), a Room, and DesignBeliefs, composed on slotcars/carrera-catalog. Use when the user wants to record their track pieces, sets, kits, or cars, add newly bought products, ask what tires fit their car, log maintenance or race sessions, describe their racing space, or capture track-taste preferences. Also handles the verifier flow when a user's physical box contradicts the catalog.
---

# Track Inventory (TrackMarshal on-ramp)

One conversation, three outcomes: **Holdings** (what they own, in piece units), a **Room** (where the track lives), and **DesignBeliefs** (what they think makes a good track). Everything composes on `slotcars/carrera-catalog` by cross-repo assertion — never copy catalog data.

Write contract (ONTOLOGY-REVIEW.md + CARS-DESIGN.md): reads catalog + personal repo, **writes only the personal repo**. May create Holding, Room, DesignBelief, Topic (sparingly), Layout/PieceUsage/BuildLog, and the garage shapes (CarHolding, PartHolding, MaintenanceLog, LapRecord). May **never** create or edit PieceType, Product, ProductContent, SpecClaim, CarModel, PartType, or Fitment — catalog gaps and owner-verified fitments get *reported*, not patched locally.

## 0. Repo setup

Ask which repo holds their inventory. If none exists:

```bash
wh repo create <them>/my-track --visibility public   # private is fine too; public lets others compose on their layouts
wh component install slotcars/carrera-track-personal --repo <them>/my-track
wh component doctor slotcars/carrera-track-personal --repo <them>/my-track   # expect all-ok: 12 shapes + 3 seed Topics (v0.2.0)
```

(MCP: `warmhub_repo_create` + `warmhub_component_install`.) The worked example is `wjcorey/carrera-track`.

## 1. Pieces & kits intake

The user names what they own in plain language ("the 24h Speed set, a hairpin kit, 6 extra R2 curves"). Resolve each item against the catalog:

- **Part number** → `wh thing view Product/<num> --repo slotcars/carrera-catalog`. Legacy 8-digit numbers (20030044-style) are `skuAliases` — find them with full-text `wh thing search "<number>"` (the typed index can't serve array fields).
- **Product by name** → `wh thing search "<words>"` on the catalog; confirm the match with the user before expanding.
- **Loose pieces by description** → resolve to a `PieceType` directly (`thing query --shape PieceType --where kind=<kind>`, or search). "R2 curves" → `PieceType/curve/r2-30` — check which arc they mean; loose curves are usually 30°.

**Expand box contents** via ProductContent Pairs:

```bash
wh thing about Product/<num> --repo slotcars/carrera-catalog --resolve-collections --shape ProductContent
```

(MCP: `warmhub_thing_about` with `resolveCollections: true`.) Rules:

- `verified: false` contents → tell the user, and ask them to sanity-check counts against the physical box if it's handy. Their answer feeds the verifier flow (§5).
- Contents marked UNRESOLVED in the product notes → **never guess.** Ask the user to enumerate their box; record their enumeration in `acquiredNotes` and report it upstream (§5).
- Product not in the catalog at all → record nothing for it yet; file a catalog-gap report (§5) with everything the user can tell you (part number, box title, contents). Do not mint a local stand-in.
- Non-track contents (cars, controllers, transformers) get no Holdings unless a PieceType exists for them (precedent: `digital/charging-straight` in the Wireless+ 10109 — geometrically a standard straight, so it counts toward layouts).

## 2. Write Holdings

Aggregate across everything they named: **one Holding per PieceType, quantity in individual piece units, never packs.** Name by slug with slashes flattened to dashes:

```bash
wh assertion create --name curve-r1-60 --shape Holding \
  --about "wh:slotcars/carrera-catalog/PieceType/curve/r1-60" \
  --data '{"quantity": 10, "pieceTypeSlug": "curve/r1-60", "pieceTitle": "Curve 1/60°", "acquiredNotes": "10 from set 30044"}' \
  --repo <them>/my-track
```

(`--name` takes the *bare* name when `--shape` is given — `--name Holding/curve-r1-60` would create `Holding/Holding/curve-r1-60`. Verified 2026-07-22.)

- `about` is the **canonical cross-repo wref** into the catalog — this is what makes their inventory visible on the piece's about-query, and the whole composition story.
- `acquiredNotes` carries provenance per source: `"11 from set 30044, 4 from extension 30367, 2 loose"`.
- **Later additions are revisions, not new Holdings** (`wh assertion revise Holding/<slug> --data '{...}'` with the new total and updated acquiredNotes) — append-only history shows the collection growing.
- Batch loads: `wh commit submit --file <ops.jsonl>` is fine; ops are per-op applied, so make names deterministic and re-submittable.

## 3. Room & taste

**Room** — ask for the *usable* footprint in mm (not the room's nominal size), obstacles, surface:

```bash
wh thing create basement --shape Room \
  --data '{"title": "Basement", "widthMm": 4000, "lengthMm": 3000, "obstacles": ["0,0,600,600,support post"], "notes": "carpet; track stored assembled"}'
```

Obstacle encoding is `'xMm,yMm,widthMm,lengthMm,label'`, origin at a room corner (array items must be strings — platform limit).

**DesignBeliefs** — a short interview, not a form. Good questions: *Who races — kids, adults, mixed? Are crashes funny or frustrating? Sprints or endurance? (digital) How much do you care about overtaking spots?* Map answers to beliefs about the three seeded Topics (`Topic/flow`, `Topic/kid-friendly`, `Topic/overtaking`):

```bash
wh assertion create --name kids-forgiving --shape DesignBelief \
  --about "Topic/kid-friendly" \
  --data '{"statement": "Layouts must forgive a 6-year-old: no R1 after a long straight", "strength": 0.9}'
```

`strength` is the user's own 0–1 weight — ask "how strongly?" in plain terms and translate. Create a new Topic only when a belief genuinely fits none of the seeds; reuse beats minting.

## 4. Garage — cars, spares, maintenance (component ≥0.2.0)

Cars are **individuals, not quantities**: one `CarHolding` per physical car (`-2` suffix for duplicates), about the catalog `CarModel` cross-repo:

```bash
wh assertion create --name d132-ferrari-296-gt3 --shape CarHolding \
  --about "wh:slotcars/carrera-catalog/CarModel/d132/ferrari-296-gt3" \
  --data '{"nickname": "the red one", "acquiredNotes": "from set 30044", "carModelSlug": "d132/ferrari-296-gt3", "carTitle": "Ferrari 296 GT3"}' \
  --repo <them>/my-track
```

- Resolve cars the same way as products (§1): part number → `Product` (`productClass: car`) → the `CarModel` it realizes via ProductContent (`contentKind: carModel`); or by name via search. Starter-set cars arrive through box expansion — a set's ProductContent now includes its cars.
- Garage state is *their* state, never catalog fact: `decoderInstalled`, `magnetsRemoved`, `currentTiresSlug`. **Unknown stays null** — a used car with unknown history is honest data; never default to false.
- Spares stock → `PartHolding` about the catalog `PartType` (quantity in units, revisions on change — exactly like piece Holdings).
- Service actions → `MaintenanceLog` about the CarHolding (`date`, `action`, `partTypeSlug?`). **Never auto-decrement PartHolding stock** — ask the owner.
- Race sessions → `LapRecord` about `Pair(CarHolding, Layout)` (pair named `<carModelSlug>--<layoutSlug>`, slashes flattened): `bestLapMs`, `driver`, `date`. This is the cars×tracks join — offer it whenever they mention "we raced last night."

**Tire question ("what tires fit my car?"):** traverse Fitments from the CarModel (`wh thing about CarModel/<path> --repo slotcars/carrera-catalog --resolve-collections --shape Fitment`). Always surface `basis` and `verified` — a `vendor-chart, verified:false` fitment is a lead, not a fact. When the owner physically mounts a part: that's an **owner-verified fitment observation → report upstream** (§5), the highest-value datum the flywheel produces.

## 5. Verifier flow (the flywheel)

Every new user is a catalog verifier. When their physical box contradicts the catalog (wrong counts, missing pieces, an item the listing doesn't show):

1. **Record their observation locally** — their real counts go in the Holding, their enumeration in `acquiredNotes`.
2. **Report upstream, never write the catalog.** Produce a discrepancy report: product, field, what the catalog claims (and which SpecClaim/source backs it), what the owner observed, date. Hand it to the user to file — or, in a session where a catalog maintainer is present, offer it as an explicit separate step for *them* to apply.

Precedent: the 30356 pit-lane end-piece conflict — web research said 2 end pieces, the owner's box had none; the owner's physical count adjudicated it and the bogus claim was retracted *by a catalog maintainer, citing the count*. That loop is the product working as designed.

## Honesty rules

- Quantities are piece units. If the user says "a pack of R2s," expand via the product; if ambiguous ("some R2 curves"), ask for a count — never estimate.
- Unknown stays unknown: unresolved box contents and unmatched products are reported, not guessed.
- Surface `verified: false` when expanding — the user should know which counts rest on unconfirmed research.
- Don't touch Holdings that a design session wants to change — the track-designer never mutates inventory, and inventory changes always come from the owner saying so.

## Next

Inventory + Room + beliefs in place → hand off to `/track-designer` for layout proposals against what they actually own.
