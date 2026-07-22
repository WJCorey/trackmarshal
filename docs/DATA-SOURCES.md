# DATA-SOURCES — where the numbers come from, and what we may republish

Research snapshot 2026-07-16 (two web-research passes; unverified items flagged in PIECES.md).

## Source matrix

| Source | What it provides | License posture | Use |
|---|---|---|---|
| carrera-toys.com product pages + operating-instruction PDFs (`/en-eu/products/200<part>-…`, `/en-eu/pages/operating-instructions`) | Official part numbers, titles, pack counts, some dimensions; per-piece assembly PDFs on Carrera's Azure CDN | Facts extractable; documents/photos © Carrera — link, never copy | Primary `SpecSource/official-doc` |
| carreraslots.com (`/slot-car/<part>.html`) | US importer pages: inside/outside edge radii, angles, pack counts | Same posture | Secondary official-adjacent source |
| slottrackpro.com/carrera-track/ | Best single-page unofficial inventory of current pieces | Facts fine; don't copy prose | Cross-check + discovery |
| slotfun.de tech-info page | Exact-nesting anchors (R4 180° outer Ø = 198 cm) | Facts | `community-measurement` |
| freeslotter.de thread "Abmessungen der Carrera 132 Schienen" | CAD measurements: slot 49.5 mm from edge, R1 slot radii 247.5/346.5 mm | Facts (direct fetch 403s; verify via Wayback or re-measure) | `community-measurement` |
| Carrera "Circuits to download" PDFs + boxed-set manuals | Famous-circuit and starter-set layouts with piece lists | Piece lists are facts; PDFs © Carrera | **Closure-oracle validation corpus** |
| github.com/keebah/carreraTrackGenerator (MIT) | Minimal hardcoded geometry (345 mm straight, 60° corners) + closure approach | MIT | Algorithmic reference |
| github.com/KaptajnFjaesing/CarreraTrackDesign | Generative closed-layout model; lap/orientation tolerance approach | **No license** — read for ideas, copy nothing | Algorithmic reference only |
| Our own calipers | Disputed dims (86.25 mm quarter straight; 297/495/693/891 mm radii; banking) | Ours, CC-licensed | `community-measurement`, tie-breaker |

## Licensing rules (decision D7)

1. **Dimensions, radii, angles, part numbers are unprotectable facts** (US: Feist v. Rural). A self-compiled dataset with our own selection/arrangement is safe to publish.
2. **EU sui generis database right (96/9/EC):** never bulk-extract the piece library of a proprietary app (Autorennbahnplaner, SoftyBP, Ultimate Racer, TrackPower, Race Track Lab, AnyRail, SmartRace). Compile from official pages, forums-as-pointers, and our own measurements; cite the source per datum via `SpecSource`.
3. **Trademark:** "Carrera" is Carrera Toys GmbH's mark. Nominative use ("dimensions of Carrera-brand track pieces") with a non-affiliation note in the repo description.
4. **Never copy:** Carrera PDFs, product photos, marketing prose. `imageUrl` links only.
5. **Dataset license:** CC-BY-SA (consistent with the AgentGM OQ-6 precedent of accepting CC-BY-SA), code MIT.
6. Every datum lands with a `SpecSource` assertion → the licensing story is auditable in the graph itself, which is also the Greenhouse "real provenance" showpiece.

## Competitive landscape (why this doesn't already exist)

- **Official Carrera Windows planner: discontinued**, installer only survives on a hobbyist archive site. Official mobile Race App: discontinued, and never did track planning. This is the abandonment the project premise rests on.
- **Desktop third-party:** Ultimate Racer (abandoned, site down; notable: its piece libraries were plain text files), TrackPower (abandoned, unlock passwords lost), SlotMan (dormant freeware), Autorennbahnplaner (€24.95, maintained, closed data), AnyRail (model-rail tool with a partial Carrera 124 library).
- **Web:** SoftyBP (free, active, German, ~140k published layouts, closed) and **Race Track Lab** (free+premium, active since ~2024, real-time closure validation, inventory matching, community library, closed data/SPA).
- **Open data: none.** No openly licensed machine-readable Carrera piece dataset exists anywhere we could find. The two GitHub generators hardcode a handful of constants. **An open, source-cited catalog is novel regardless of the WarmHub layer.**
- Positioning vs Race Track Lab: they built a better GUI; we're building the *knowledge substrate* — open data any agent or app (including theirs) can consume, plus the personal-graph layer (inventory provenance, build history, beliefs) no GUI models. Don't clone their app; consider exporting layouts in a shareable format instead (PLAN OQ-6).
- Community layout DBs (SmartRace 253 layouts — reuse requires permission; SoftyBP; SlotRacer Online) are browse-only; useful as inspiration and as future partnership targets, not as data sources.

## Live-update pipeline (Greenhouse requirement 2)

Data that goes stale: new pieces/sets (~yearly product cycle), discontinuations, manual URLs.

- **Cadence:** monthly scheduled run (cheap; the domain moves slowly).
- **Job:** diff carrera-toys.com and carreraslots.com track-category listings against the catalog; new part number → draft `TrackPiece`/`ProductSet` + `SpecSource` flagged for review; vanished listing → propose `status: discontinued` (never delete).
- **QC gates (run on every write, not just pipeline):**
  1. *Closure oracle:* every `ProductSet` whose manual shows a closed loop must close under the solver using exactly its `SetContent` — catches both bad dimensions and bad set data.
  2. Full-circle identity per radius (e.g. 12 × R2/30° sums to 360° and zero translation).
  3. Part-number uniqueness; every geometric field backed by ≥1 `SpecSource`; link-rot check on `manualUrl`/`imageUrl`.
- **Handover:** pipeline is a scheduled agent + these QC checks in the repo; documented so WarmHub can run it without us. Bounded cost: a few page fetches/month.
