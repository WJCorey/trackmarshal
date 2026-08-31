# PLAN — TrackMarshal roadmap

Clock: today 2026-07-16 · claim idea in #project-greenhouse now · crunch week Jul 27–31 · demo hour first week of August · real scoreboard end of Q3 (Most Composed-Upon / Most Read).

Greenhouse deliverables mapped: public repo → Phase 1 · live pipeline → Phase 4 · component/skill → Phases 2–3 · blog post → Phase 4.

## Build step 1 — mechanics validation + closure solver ✅ DONE 2026-07-16

Results (details in ONTOLOGY-REVIEW.md § Spike findings and solver/):

1. **Cross-repo `about`: PASS.** `Holding` in `wjcorey/tm-spike-personal` asserted about `wh:wjcorey/tm-spike-catalog/PieceType/straight/full` — traversal works from the personal side AND surfaces on the catalog-side `thing_about` query alongside local Pair assertions. Platform deltas found: inline `{pair:[...]}` about is rejected on MCP — collections are explicit named ops (`kind:collection, type:pair`) asserted about by wref; `+` is reserved in names (we use `--`); array shape fields require `items`.
2. **Radius adjudication: exact-nesting CONFIRMED, rounded model REFUTED.** Least-squares over 4 official circuit plans (Interlagos/Zeltweg/Brands Hatch/Catalunya) fits radius spacing at 197.6/198.6/198.5 mm — the exact-nesting 198 mm, not the rounded model's 200. Adopted: 297/495/693/891 mm. Residual: official plan lengths run a uniform ~+1.9 mm-per-radius (~0.033 mm/curve-degree, near-constant across all four plans) above exact-nesting — recorded as a `SpecClaim` about Carrera's planner convention, not a physical radius. No calipers needed (D5 vindicated).
3. **Solver:** SE(2) composition, circle identities, lane lengths (slot lanes = centerline ∓311 mm on any closed loop — confirms official lengths are centerline), footprint, angle-feasibility DP, randomized closure search (finds small ovals; large-circuit search deferred to the Phase 3 constructive designer). 6 official circuit fixtures captured in solver/fixtures/.

Original step spec follows for reference:

1. **Cross-repo `about` mechanics.** Scratch org: mini-catalog with 3 `PieceType` things, second repo with a `Holding` assertion about a cross-repo wref. Verify both-direction traversal and `--resolve-collections` behavior across repos, and Pair version-pinning behavior (guide §1.3).
2. **Closure solver + dimension adjudication.** ~150 lines of Python: compose SE(2) transforms, check Σheading ≡ 0 (mod 360°) and Σtranslation = 0 within tolerance. Run the **official-layout oracle**: reproduce closed loops from Carrera's circuit PDFs + set manuals using exactly their piece lists, once under the 297/495/693/891 mm radius model and once under rounded 300/500/700/900. Complex layouts (fractional straights compensating S-bend offsets, mixed radii) close only under the true model — this adjudicates the dimensions *without physical measurement* (D5). Simple ovals don't discriminate; use the complex circuit plans (Suzuka, Monza).
3. **Golden objects.** Hand-model the 10 adversarial cases from ONTOLOGY-REVIEW.md in the scratch org; they become permanent regression fixtures.

## Phase 1 — public catalog repo ✅ LOADED 2026-07-16

`slotcars/carrera-catalog` (public) is live: 4 shapes, 67 PieceTypes, 70 Products, 80 ProductContent Pair-assertions, 16 SpecClaims — 313/313 ops applied via `catalog/build_ops.py` (the reproducible generator). Repo README + Agents content set (query cookbook, anti-inference rules, community write rules). Verified: box-contents traversal, per-source provenance traversal (marketing-rounded vs derived claims coexist on r2-30), typed `where` filters on kind/solverReady. Remaining Phase 1 items: starter-set contents enumeration (from set manuals), archive-mining for corroborating SpecClaims (Wayback schlitzflitzer, UR libraries), full 5-question context-free reader test from a cold agent.

Original spec:

- Register org/repo on WarmHub (name pending OQ-1), manifest from SHAPES.md v2 with full shape+field descriptions.
- Load PIECES.md: ~30 `PieceType`, ~50 `Product` (packs, kits, extension + starter sets) with `ProductContent`, every geometric datum with its `SpecClaim` (source-language values + observedAt + archiveUrl where available).
- Also mine remaining archive sources for corroborating SpecClaims: Wayback for schlitzflitzer.de's dimension table; Ultimate Racer's plain-text piece libraries as *verification cross-checks only* (read a value to confirm a fact; never bulk-extract their compilation — D7).
- Repo description written for a context-free reader; non-affiliation note.
- Context-free reader test (checkpoint Q5): CQ-1/3/5/6/11 answered via MCP by an agent with no session context.

## Phase 2 — personal-repo component + importer skill — PARTIALLY DONE 2026-07-16

Done: `wjcorey/carrera-track` (public, the worked example) with all 8 shapes (LayoutFeedback added 2026-07-17 — others' takes on layouts, in-repo or cross-repo); Corey's real inventory seeded — 20 Holdings in piece units from 30044, 30356, 30367, 20576, 20587, 20611, 20612, 10109 (incl. the Wireless+ charging straight; end-piece count owner-adjudicated to 4). Solver confirms the inventory closes an ~11.4 m layout in 3.7 × 4.1 m. Component packaged in `component/` (id com.slotcars.CarreraTrackPersonal): 8 shapes + 3 seed Topics; **registered 2026-07-22 as public `slotcars/carrera-track-personal` v0.1.0**, full lifecycle verified on a scratch repo (install → doctor all-ok → teardown clean). Importer shipped 2026-07-22 as `.claude/skills/track-inventory/` (repo setup via the registered component, product/alias resolution, ProductContent expansion, piece-unit Holdings with provenance, Room + DesignBelief interview, catalog-verifier reporting flow; all quoted CLI commands smoke-tested live). **Phase 2 complete.**

Original spec:

- Package Layer-2 shapes (SHAPES.md) as an installable component; additive-only evolution from day one.
- **Importer skill:** conversational inventory seeding — "I have set 20025240, plus 6 extra R2 curves and a pit lane" → `Holding`s (piece units) via `ProductContent` expansion. Owns `PieceUsage` regeneration on layout writes. Write contracts per ONTOLOGY-REVIEW.md.
- Dogfood: Corey's real inventory becomes the first personal repo (public, as the worked example — decide OQ-3).

## Phase 3 — track-designer skill — v2 SHIPPED 2026-07-22

v2 adds: design-time preference conversation (durable answers persist as DesignBeliefs; session-only ones don't), self-contained HTML build sheets (`solver/buildsheet.py` — exact-geometry SVG, stats, parts list, run-compressed assembly steps, optional shopping-delta section, closure re-verified at render time with the verdict printed honestly), and post-save build-sheet regeneration with the WarmHub Layout link. Verified end-to-end on the real inventory (11.7 m proposal → `designs/whittaker-speedway-v2-buildsheet.html`); negative path (non-closing sequence → NOT VERIFIED warning) tested. Still open from v1 gaps: fractional-straight utilization, lane-change placement optimization, banked/pit attachment (OQ-5).

### v1 (2026-07-17)

`solver/designer.py` (inventory-constrained closed-layout generation: curve-subset angle enumeration + closure search + room filter + length/lane-fairness ranking) + project skill `.claude/skills/track-designer/SKILL.md` (reads Holdings/Room/DesignBeliefs via MCP, runs designer, writes Layout + PieceUsage back, honesty rules). First run on Corey's real inventory: 11.7 m centerline in 4.8 × 2.6 m using 10/11 curves + all straight-equivalents. v1 gaps → v2: fractional-straight utilization (search rarely closes with them), lane-change placement optimization, belief-aware scoring in the solver itself, banked/pit attachment. Original spec:

- Solver hardened from build step 1: inventory-constrained search over owned pieces, room-footprint constraint (`Room`), per-lane lengths, borders bill-of-materials, shopping-list delta when the best layout needs pieces you lack (→ cheapest in-production `Product`, via ProductContent traversal).
- Reads `DesignBelief`s as soft objectives (long straight, flow, overtaking spots for digital lane changers).
- Writes back `Layout` + `PieceUsage`; after a real build, prompts for `BuildLog`.
- v1 scope cut: banked curves excluded from the solver until their projected footprint is measured (OQ-5); bridge crossing 20587 treated as 4 straights inline.

## Phase 4 — pipeline, blog, demo (crunch week → demo hour)

- Monthly new-product/discontinuation pipeline + QC gates per DATA-SOURCES.md; handover doc so WarmHub can run it.
- Blog post: "The apps died. The knowledge shouldn't have." — abandoned-planner story, open-catalog-as-graph, agent designing a track that actually closes on the living-room floor, photo of the built track.
- Demo: live — agent reads inventory + room + beliefs, proposes layout, closure-verifies, prints piece list; build it.

## Phase 5 — cars, parts & fitment — BUILT 2026-07-27 (same day as design)

Full dossier + build results: **CARS-DESIGN.md**. Catalog: CarModel/PartType/Fitment shapes live, 73 ops applied (2 CarModels from Corey's 30044 cars, 6 third-party tires with the Paul Gage Vantage dispute preserved as designed, 14 Fitments, 11 SpecClaims); ProductContent/SpecClaim/Product widened legacy-safe. Component v0.2.0 (CarHolding/PartHolding/MaintenanceLog/LapRecord) registered, verified, reconcile-installed onto `wjcorey/carrera-track`; garage flow in `track-inventory` §4. Gate-5 cold-reader eval passed 3/3. Remaining: magnets PartTypes, LapRecord-aware designer objectives (step 5), and the standing pipeline dependency — **car liveries churn yearly, so the update pipeline is now the most urgent unbuilt piece**.

## Open questions

- **OQ-1 · Names.** Public WarmHub org: `slotcars` (Corey's call; confirmed available 2026-07-16; broad enough to host other track systems later). Repo: `slotcars/carrera-catalog`. "TrackMarshal" stays the project codename — full collision check still pending if used publicly.
- **OQ-2 · Radius confirmation. RESOLVED 2026-07-16:** exact-nesting (297/495/693/891 mm) adopted; rounded model refuted by least-squares over official plan lengths. The ~+1.9 mm/radius official-planner residual is documented as its own SpecClaim.
- **OQ-3 · Is Corey's personal repo public?** As the worked example it should be; check nothing sensitive (home room dimensions are borderline — probably fine).
- **OQ-4 · BeliefEvidence as first-class Pair assertion** vs denormalized wrefs on `DesignBelief`. Deferred until the "which beliefs are well-evidenced" query is real.
- **OQ-5 · Banked curves in the solver.** Excluded v1; needs banking angle + projected-footprint measurement.
- **OQ-6 · Interop.** Export layouts as printable plan + piece list at minimum; investigate whether SoftyBP/Race Track Lab have import formats worth targeting. Do not scrape their libraries (D7).
- **OQ-7 · Where does it live?** GitHub: graduate to its own repo (likely `warmautomation/…`) once Phase 0 passes, per coreypersonal conventions. WarmHub org: same question as AgentGM's registration.

## User actions (Corey)

1. ~~Create the `slotcars` org~~ — done 2026-07-16 (https://app.warmhub.ai/orgs/slotcars).
2. Post the idea in **#project-greenhouse** to claim it (Slack MCP isn't authorized in this session, so this one's manual).
3. ~~List sets + loose pieces~~ — done 2026-07-17; inventory is live in `wjcorey/carrera-track`.

## Decision log

- 2026-07-16 · D1–D8 in README.md (facts-vs-opinions split, cross-repo assertions, math-in-skill, materialized PieceUsage, closure-oracle-not-calipers, additive-only component, compile-facts-never-compilations, piece-type ≠ product).
- 2026-07-16 · v1 → v2 shape redesign after ontology-guidebook audit; deltas and deliberate deviations in ONTOLOGY-REVIEW.md.
- 2026-07-16 · v1 solver scope = flat pieces only; banked/hairpin deferred.
- 2026-07-16 · No trial phase — full build green-lit by Corey; build step 1 is engineering order, not a fit experiment.
