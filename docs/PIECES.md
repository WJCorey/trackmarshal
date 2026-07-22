# PIECES — draft seed data for the catalog

Research snapshot 2026-07-16. This is the working piece table that becomes `TrackPiece`/`ProductSet`/`SetContent` things in Phase 1, with every datum's source recorded as a `SpecSource` assertion. ⚑ = unverified, see Open measurements.

Part numbers are the common 5-digit form; official full SKUs prefix `200` (20509 → 20020509). All pieces below are the shared 1:24-width track used by Exclusiv/Pro-X, Evolution, Digital 132, and Digital 124. Carrera GO!!!/Digital 143 is a different, incompatible system (114 mm vs 198 mm width).

## Core geometry model (what the solver consumes)

- Track width **198 mm**; slot centers 49.5 mm from each edge → lane spacing **99 mm**; piece centerline midway between slots.
- Straights: **345 mm** standard; 1/3 = **115 mm**; 1/4 = **86.25 mm** ⚑ (nominal 86; 345/4 = 86.25 — measure one).
- Curves nest exactly in 198 mm steps — centerline radii: **R1 297, R2 495, R3 693, R4 891 mm** ⚑ (fan CAD-measured: R1 slot radii 247.5/346.5 mm on freeslotter; R4 180° outer diameter exactly 198 cm per slotfun.de; marketing pages publish rounded 300/500/700/900). Adjudicated in build step 1 by the official-layout closure oracle — complex official circuit plans close only under the true model (README D5); no physical measurement required.
- Arc angles: R1 60° or 30°; R2/R3 30°; R4 15°. All heading changes are multiples of 15°.
- Every piece end is perpendicular to the centerline → a piece is fully described by (length | radius+angle) + left/right orientation. Closure: Σ heading = 0 mod 360° and Σ translation = 0.
- Ends join via molded lock tabs + press-in clips (85245). Curves are left/right by orientation. ⚑ End keying (does anything constrain flipping a piece?) unverified.

## Straights

| Part # | Name | Length mm | Pack |
|---|---|---|---|
| 20509 | Standard straight | 345 | 4 |
| 20601 | Standard straight | 345 | 2 ⚑ (part # seen only on slottrackpro) |
| 20611 | 1/3 straight | 115 | 2 |
| 20612 | 1/4 straight | 86.25 ⚑ | 2 |
| 30341 | Single-lane straight (pit extension) | 345 | 1 |

## Curves (flat)

| Part # | Name | Angle | Centerline R mm ⚑ | Pack | Full circle |
|---|---|---|---|---|---|
| 20571 | Curve 1/60° | 60° | 297 | 3 | 6 |
| 20577 | Curve 1/30° | 30° | 297 | 6 | 12 |
| 20572 | Curve 2/30° | 30° | 495 | 6 | 12 |
| 20573 | Curve 3/30° | 30° | 693 | 6 | 12 |
| 20578 | Curve 4/15° | 15° | 891 | 12 | 24 |

## Banked curves (same nominal R/angle as flat; ⚑ banking angle and projected footprint unverified — closure math may not treat as flat)

20574 (R1/30°, 6), 20575 (R2/30°, 6), 20576 (R3/30°, 6), 20579 (R4/15°, 12), 20600 (flat↔banked transitions, 4), 20599 (banked end sections, 2 L + 2 R).

## Special sections (analog-compatible)

| Part # | Name | Geometry | Notes |
|---|---|---|---|
| 20516 | Chicane / narrow section | 2 × 345 mm | Slots converge to center |
| 20517 | Lane change (analog crossover) | 2 × 345 mm | Slots swap lanes |
| 20587 | Ramp bridge crossing | 4 pcs (2 convex, 2 concave), 4 × 345 mm inline; ≈93 mm clearance | Over/under, with supports |
| 20613 | Hairpin curve kit | 3 × R1/60° + straights + end pieces ⚑ | Lanes converge at apex; exact geometry unverified |
| 20515 | Evolution connecting section | 345 mm (+1 bonus straight in box) | Analog power base |

## Digital 124/132 (all on 345 mm-multiple footprints)

| Part # | Name | Geometry |
|---|---|---|
| 30343 / 30345 | Lane change left / right | 2 pcs, 690 mm |
| 30347 | Double lane change | 2 pcs, 690 mm |
| 30350 / 30351 | Digital narrow section left / right | 4 pcs, 690 mm ⚑ breakdown |
| 30362–30365 | Lane change curves (L/R × in→out/out→in) | R1/60° footprint |
| 30356 | Pit lane kit | 1035 mm (3 × 345) parallel to main track; turnout entry + exit, 1 straight, 2 single-lane, adapter unit, 2 ends |
| 30361 | Pit stop adapter unit (spare) | — |
| 30352 | Control Unit (digital power base) | 345 mm |
| 30344 | Black Box (legacy digital power base) | 345 mm |
| 30353 | Driver Display | 345 mm |
| 30355 | Lap Counter | 345 mm |
| 30370 | Multistart lane | 345 mm |

## Borders / shoulders (cosmetic + car-retention; no effect on closure; ⚑ apron width unverified)

Straight: 20560 std ×6, 20588 1/3 ×4, 20589 1/4 ×4, 20597 crossing ×4, 20602 pit outside ×3, 20603 narrow outside ×4.
Curve inside: 20551 R1/60°, 20590 R1/30°, 20591 R2, 20592 R3, 20593 R4.
Curve outside: 20561 R1/60°, 20567 R1/30°, 20562 R2, 20563 R3, 20568 R4.
Banked inside: 20569, 20594, 20595, 20596 (R1–R4). Banked outside: 20564, 20565, 20566, 20580 (R1–R4).
End pieces outside shoulder: 20598 (2 L + 2 R).

## Accessories (non-geometric)

85245 connection clips ×20; 21130 tire stacks; 20584/20585 power extension cables 5/10 m; guardrail & fence scenery sets.

## Extension / product sets (seed `ProductSet` + `SetContent`)

| Set # | Contents |
|---|---|
| 26953 | 2 straights + 4 × R1/60° |
| 26955 | 2 straights + 4 × 1/30° |
| 26956 | 4 straights, 2 lane changes, 2 chicanes, 4 × R2/30° ⚑ |
| 30367 | Digital extension set |

Starter-set contents (Evolution and Digital sets each ship a full closed loop) to be enumerated in Phase 1 from official set manuals — these double as the closure-oracle corpus.

## Open geometry items (resolved via oracle + archives, not calipers)

1. 1/4 straight 86 vs 86.25 mm and centerline radii 297/495/693/891 — adjudicated by the closure oracle over official circuit plans (build step 1).
2. Banked curve banking angle + projected footprint; hairpin 20613 exact geometry — excluded from solver v1 (PLAN OQ-5); source hunt continues (official PDFs, Wayback).
3. Border apron widths; connector keying — cosmetic/ergonomic, don't block the solver.
4. Corroborating SpecClaims to mine in Phase 1: Wayback for schlitzflitzer.de dimension table; Ultimate Racer plain-text libraries (verification cross-check only, never bulk extraction); SlotForum dimension threads if accessible.

Note on identity mapping to SHAPES v2: part numbers in these tables are `Product`s; the geometry columns describe `PieceType`s; pack counts become `ProductContent.quantity`.
