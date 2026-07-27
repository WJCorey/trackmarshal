# CARS-DESIGN — cars, parts & fitment extension (design dossier, v1)

Status: **built 2026-07-27** (steps 1–3 of the build order, same day as the design — see § Build results at bottom). Drafted 2026-07-27 after the car/tire/consumables scoping conversation. Extends SHAPES.md v2; same repo (`slotcars/carrera-catalog`), same epistemic layering, no new repos (guide anti-pattern 7: ~50 CarModels + parts don't justify a split). Personal-layer additions ship as component **v0.2.0, additive-only** — `slotcars/carrera-track-personal` has consumers now.

Thesis: tire fitment is to the car layer what closure geometry was to the track layer — the single most re-derived fact in the hobby, published in vendor charts that disagree and go stale. Same signals that justified the catalog: re-derivation prevention, provenance where sources conflict, owner-verification flywheel.

---

## Question catalog (Gate 1 — every shape cites at least one)

Catalog layer:

- **CQ-C1** What are the tire sizes (front/rear) for car X, with evidence?
- **CQ-C2** Which upgrade tires fit car X — and which of those fitments are owner-verified vs vendor-chart-only?
- **CQ-C3** Which cars does tire/part Y fit? (vendor charts answer per-car; the reverse query is the one nobody publishes)
- **CQ-C4** Is car X analog or digital, does it have lights, is it in production, what liveries exist?
- **CQ-C5** Which consumables (brushes/braids, guide, magnets) does car X take, and what's the cheapest in-production product for each?
- **CQ-C6** Which fitment claims rest on a single non-official source? (QC — mirrors CQ-2 for pieces)
- **CQ-C7** Which cars in the catalog have *no* known upgrade tire? (rollup — catalog gaps as work queue)

Personal layer:

- **CQ-P1** What's in my garage, and what state is each car in (decoder, magnets, current tires)?
- **CQ-P2** When did I last change brushes/tires on car X, and what do I have in spares?
- **CQ-P3** Which car is fastest on layout L? Which layout produces the closest racing between my two cars? (cars × tracks — the query that ties both halves of TrackMarshal together)
- **CQ-P4** Do my lap times support my DesignBeliefs? (evidence loop: beliefs → layouts → LapRecords)

## Identity model (the v1→v2 lesson, applied pre-emptively)

Three candidate grains: **chassis platform** → **car model** (a specific physical car design) → **product** (a livery SKU). Carrera ships many livery SKUs per year; several share one platform, and *fitment attaches to the platform, not the livery*. Asserting fitment per-SKU is the 20509-vs-20601 failure at the next level.

**Adopted: two grains.** `CarModel` (fitment + spec unit) and `Product` (commerce, reused as-is). The platform grain is **deferred**: today's fitment sources speak in car-model terms ("fits Carrera GT3 cars 2020+"), and we can't yet enumerate platforms from public data without guessing. Promotion trigger: when ≥3 CarModels demonstrably share identical rim/axle/guide specs *and* a fitment source addresses the family as a unit, mint the platform thing then and re-hang fitments (retract-and-replay is bounded: fitments are the only dependents). Until then, shared-platform knowledge lives as identical SpecClaim-grounded values on each CarModel — duplicated values with provenance beats a guessed platform taxonomy.

**Golden case #C1 (the 20509/20601 of cars):** one chassis, several liveries — e.g. the 30044 set's two GT3 cars (32001 Ferrari 296 GT3, 32022 Aston Martin Vantage GT3) vs any later livery re-releases of the same cars. Different CarModels (different bodies ≠ interchangeable), possibly identical fitment values — the design must keep "same tire fits both" queryable *without* pretending they're one identity.

## Layer 1 additions — catalog repo

### `CarModel/<system>/<slug>` — thing

One physical car design. System leads the name (identity: the D124 and D132 versions of "the same car" are different physical objects with different parts): `CarModel/d132/ferrari-296-gt3`, `CarModel/evolution/…`. Livery/branding stays in `title` + Product; no year, no state in names. Serves CQ-C1/2/4/5.

| Field | Notes |
|---|---|
| `title` | "Ferrari 296 GT3" |
| `system` | `d132 \| d124 \| evolution` (mirrors name segment) |
| `scale` | `1:32 \| 1:24` — do not infer from system (anti-inference: D132 is 1:32 but "132" is a brand token, not a scale guarantee across lines) |
| `digital`, `lights` | booleans, per the *model as shipped*; conversions are garage state, not catalog facts |
| `tireFrontSpec`, `tireRearSpec` | adjudicated dimensions `{innerDiaMm, outerDiaMm, widthMm}` — the fitment engine's input, each grounded by SpecClaims; null until grounded (absence = ungrounded, not unknown-to-the-world) |
| `fitmentBasis` | rationale + which SpecClaims carry the evidence (mirrors `geometryBasis`) |
| `notes` | quirks (magnet positions, known chassis siblings pending the platform grain) |

### `PartType/<kind>/<slug>` — thing

One functional spare/upgrade part type, mirroring `PieceType` exactly: the unit fitment, stock, and maintenance reason in. Kinds: `tire`, `brush` (sliding contacts/braids — e.g. the 20365 double-slider from the 30044 spares), `guide`, `magnet`, `decoder`, `axle`, `gear`, `motor`. Third-party parts are first-class: `PartType/tire/<vendor>-<model>`. Serves CQ-C2/3/5.

Fields: `title`, `kind` (mirrored), `vendor` (`carrera` or third-party name), dimension fields per kind (tires: `innerDiaMm`, `outerDiaMm`, `widthMm`, `compound: rubber|silicone|urethane`), `specBasis`, `notes`. Same rule as pieces: adjudicated values on the thing, per-source values in SpecClaims.

### `Fitment/<partTypeSlug>/<carModelSlug>` — assertion, `about: Pair[PartType, CarModel]`

The load-bearing new relationship. Deterministic name → idempotent writes; slugs flattened with `-` (pair collections named `<partTypeSlug>--<carModelSlug>`).

| Field | Notes |
|---|---|
| `position` | `front \| rear \| both \| n/a` |
| `basis` | `vendor-chart \| official-listing \| dimensional \| owner-verified` — method class, never a confidence float (anti-pattern 4) |
| `verified` | boolean: a human physically mounted it. Vendor charts start `false` |
| `partTypeSlug`, `carModelSlug`, `partTitle`, `carTitle` | denormalized context-free legibility (guide §1.4) |
| `notes` | fit caveats ("tight on rim, stretch when warm") |

Four-direction test: **subject side** ✓ tires-for-car via about-query on the pair from `CarModel` (CQ-C2); **object side** ✓ cars-for-tire from `PartType` (CQ-C3 — the query vendors never publish); **aggregation** ✓ most-covered tire, per-basis counts (CQ-C6); **rollup** ✓ CarModels with zero Fitments (CQ-C7). Conflicting vendor charts = two Fitment-supporting SpecClaims preserved, adjudication in `verified`/`basis` — same observation-vs-preferred-value pattern as geometry.

### Reused shapes (widened, additive)

- **`Product`** unchanged; `productClass` gains `car` and `spare-part`. Car SKUs keep `skuAliases`, `status` (discontinued cars stay — garages reference them forever).
- **`ProductContent`** widens: `about: Pair[Product, PieceType|CarModel|PartType]` — a box containing a car or tire set is the same contains-relation as a box containing pieces. Additive fields `contentKind` (`pieceType|carModel|partType`) + `contentSlug`; existing rows are implicitly `pieceType` and keep `pieceTypeSlug` (documented legacy denormalization — importer/designer consumers filter on `pieceTypeSlug` and are unaffected). Decision C4: widen one relation rather than mint `ProductContains` vocab-sprawl.
- **`SpecClaim`** widens its `about` to any catalog thing (`PieceType|CarModel|PartType`); name stays `SpecClaim/<subjectSlug>/<source-slug>`. `sourceKind` gains `vendor-fitment-chart`.

## Layer 2 additions — personal component v0.2.0 (additive-only)

### `CarHolding/<carModelSlug>[-<n>]` — assertion, `about:` cross-repo `CarModel`

The garage. Unlike piece Holdings (fungible, quantity-keyed), cars are individuals: one CarHolding per physical car, `-2` suffix for duplicates. Fields: `nickname`, `condition`, `decoderInstalled?`, `magnetsRemoved?`, `currentTiresSlug?` (PartType slug), `acquiredNotes` (provenance: "from set 30044"), denormalized `carModelSlug`, `carTitle`. Serves CQ-P1. Cross-repo about-visibility is the proven Holding mechanic (re-verified 2026-07-22).

### `PartHolding/<partTypeSlug>` — assertion, `about:` cross-repo `PartType`

Spares stock, exactly parallel to `Holding` (which stays piece-only per its shipped description — additive-only forbids retconning it). Fields: `quantity`, `acquiredNotes`, denormalized slugs. Serves CQ-P2.

### `MaintenanceLog/<carModelSlug>/<date>[-<n>]` — assertion, `about: CarHolding`

One entry per service action: `date`, `action` (`tires-changed | brushes-changed | decoder-installed | magnet-adjusted | repair | other`), `partTypeSlug?` (what went on/in), `notes`. The consumable evidence stream (CQ-P2); decrementing PartHolding stock stays the owner's call, never automatic (anti-inference).

### `LapRecord/<carModelSlug>/<layoutSlug>/<date>[-<n>]` — assertion, `about: Pair[CarHolding, Layout]`

The shape that joins TrackMarshal's two halves. Fields: `bestLapMs`, `laps?`, `driver`, `date`, `controller?`, `notes`, denormalized `carModelSlug`, `layoutSlug`. Four-direction: fastest-car-on-layout (from Layout side), car's-history-across-layouts (from CarHolding side), closest-racing-layout (aggregation over per-car bests — CQ-P3), belief-evidence rollup (CQ-P4: `DesignBelief.evidenceLayoutWrefs` gains hard data behind it). Design-time note: the Pair joins two *assertions/things in the same personal repo* — no cross-repo pair members, so standard mechanics apply.

## Write contracts (extends ONTOLOGY-REVIEW)

```yaml
agent: car-catalog-pipeline        # car/part/fitment ingestion (couples to the update pipeline — liveries churn yearly)
writes_only: carrera-catalog
may_create: [Product, ProductContent, PartType(tire only, from vendor pages), Fitment(verified:false), SpecClaim]
may_not_create: [CarModel]         # new physical car designs are human-reviewed, same as PieceType
required_behavior: [never bulk-extract a vendor's fitment chart — per-datum claims with citations (D7 extension:
                    EU database right applies to vendor compilations); conflicting charts preserved, never merged]

agent: garage-skill                # the track-inventory extension (or sibling skill)
writes_only: <racer>-track
may_create: [CarHolding, PartHolding, MaintenanceLog, LapRecord]
may_not_create: [CarModel, PartType, Fitment]   # gaps + owner-verified fitments get REPORTED upstream (flywheel),
                                                # a catalog maintainer applies them citing the owner
```

## Anti-inference rules (additions)

1. Same `title` across systems ≠ same car (`d132` vs `evolution` 296 GT3 are different CarModels).
2. `digital: true` ≠ has lights; `lights: true` ≠ digital.
3. A Fitment with `verified: false` is a *lead*, not a fact — skills must surface the basis.
4. Dimensional match (tire spec ⊆ rim spec) ≠ fitment — compounds/profiles differ; `basis: dimensional` exists precisely to mark that inference as an explicit, weakest-class claim.
5. `MaintenanceLog` never implies stock decrement; `PartHolding` never implies parts are installed.
6. A discontinued car's Fitments remain valid (people race discontinued cars forever).
7. Performance opinions ("silicones grip better on plastic") are `DesignBelief`-family taste, never SpecClaims. If fitment claims are ever crowdsourced at scale with source-trust weighting, that's the Veritas trigger — not before (single-curator adjudication suffices now).

## Golden objects (adversarial fixtures, modeled before load)

- **G-C1** 32001 + 32022: two CarModels from one starter set (ProductContent with `contentKind: carModel`), possibly identical tire specs — same-tire-fits-both must be queryable without merging identities.
- **G-C2** One third-party tire with Fitments to ≥2 CarModels from *different* vendor charts that disagree on one of them — conflict preserved, CQ-C6 finds it.
- **G-C3** The 20365 double-slider: one PartType, `brush` kind, fitting effectively every D132 car — the high-fanout Fitment case (or a documented `fitsSystem` shortcut — see OQ-C3).
- **G-C4** A car bought used with unknown history: CarHolding with null garage-state fields — unknown stays unknown.
- **G-C5** A LapRecord on a retired Layout — must remain traversable (layouts are never deleted, status only).

## Build order

1. **CarModel + Product widening**, seeded from what Corey owns (32001, 32022 + the 30044 `nonTrackContents` promotion) — mirrors the inventory bootstrap.
2. **Tire PartTypes + Fitments** for those two cars, from official listings + one third-party vendor chart, conflicts and all. Proves CQ-C1/2/3 end-to-end. Owner mounts a set → first `owner-verified` Fitment (flywheel demo #2).
3. **Component v0.2.0** (CarHolding, PartHolding, MaintenanceLog, LapRecord) + garage flow in `track-inventory`.
4. **Brushes/guides/magnets/decoders** PartTypes + the shopping-delta extension ("braids 2 races from worn → 20365").
5. **LapRecord-aware designer**: lane-parity and closest-racing objectives from real times.

Sequencing note: car liveries churn ~yearly (vs near-static track geometry), so the **update pipeline should land before or alongside step 1** — a car catalog without the watcher starts rotting immediately.

## Open questions

- **OQ-C1 · RESOLVED 2026-07-27:** official Carrera pages publish NO tire dimensions for either car (nor on tire part 89800) — grounding is vendor/measurement-based. OEM spare-tire association comes from each car's official spare-parts tab (with the recorded caveat that 89800's own title enumerates other car numbers).
- **OQ-C2** OEM spare-tire products: keyed to car models or to chassis families? (Evidence for the deferred platform grain. First datum: both 30044 cars share tire part 89800 but have DIFFERENT axle spares — and Quick Slicks cut a dedicated 296 size while mapping the Vantage to DTM-generic tires, so shared tire-part ≠ shared wheels.)
- **OQ-C3** G-C3 fanout: per-car Fitments only for cars whose official spare tabs list the part (current approach); system-wide compatibility recorded in `PartType.notes`. Revisit `fitsSystem` shortcut if brush Fitments sprawl.
- **OQ-C4 · RESOLVED 2026-07-27:** decoder 26732 (official spare for both cars) modeled as `PartType/decoder/d132-26732`; car-specific decoders 26750/26751 recorded in notes, not minted (no question needs them).
- **OQ-C5** Does `track-inventory` grow the garage flow, or is `garage` a sibling skill? **Resolved: same skill** (§4 Garage added 2026-07-27).

## Checkpoint status

| Gate | Status |
|---|---|
| 1 — every shape cites a question | ✓ table above (CQ-C1…7, CQ-P1…4) |
| 2 — four-direction test per assertion shape | ✓ **runtime-verified 2026-07-27**: Fitment traverses from both endpoints with resolveCollections (CQ-C2 + CQ-C3 live) |
| 3 — correct primitives / about-arity | ✓ Pairs for both new relationships; no flat-string endpoints |
| 4 — universal foundations | ✓ kind-led names, no state/provenance in names, mirrored fields, append-only; shape descriptions live |
| 5 — context-free reader eval | ✓ **passed 2026-07-27**: cold agent answered CQ-C1/2/3 3-for-3 from the graph alone, including per-claim trust grading and the negative fact (stock dims ungrounded) |

## Build results (2026-07-27)

Steps 1–3 built same-day; step 4 partially (brushes/guides/decoders loaded; magnets remain); step 5 (LapRecord-aware designer) open.

- **Catalog live**: 2 CarModels, 10 PartTypes/tires+spares (4 OEM-family, 6 third-party tires), 6 new Products, 14 Fitments, 11 SpecClaims; ProductContent/SpecClaim/Product widened legacy-safe (v2 shapes); 30044 now expands to pieces AND cars. Loader: `catalog/cars/build_cars_ops.py` (73 ops, all applied).
- **Genuine conflicts preserved as designed**: the Paul Gage Vantage-GT3 dispute (20125LM vs 20126LMXD, physically incompatible ribs, neither first-party — G-C2 realized on real data) and the PGT-20115LMXD width conflict (11 mm size-code vs 12 mm dealer tag).
- **Component v0.2.0** registered + fresh-install verified (doctor 17/17) + reconcile-installed onto `wjcorey/carrera-track` (now a true consumer); Corey's two cars are CarHoldings with null garage-state (G-C4 honored).
- **Eval-reported drift risk, accepted**: `CarModel.fitmentBasis` narratively duplicates Fitment conclusions (observation-vs-preferred-value pattern) — Fitment assertions are authoritative; fitmentBasis is commentary and must be re-derived when Fitments change.
- Catalog `Content/Readme` gained the car-layer cookbook + anti-inference rules.
