# carrera-track-personal — installable WarmHub component

The "build your own personal track repo" component (Greenhouse deliverable 3). Ships the 12 personal-repo shapes — track side: Holding, Room, Layout, PieceUsage, BuildLog, LayoutFeedback, Topic, DesignBelief; garage side (v0.2.0, per docs/CARS-DESIGN.md): CarHolding, PartHolding, MaintenanceLog, LapRecord — plus 3 seed Topics (flow, kid-friendly, overtaking).

**Registered and live: `slotcars/carrera-track-personal` (public, v0.2.0).** v0.1.0 lifecycle verified 2026-07-22 on a scratch repo (validate → install → doctor 13/13 ok → teardown clean); v0.2.0 verified 2026-07-27 (fresh install → doctor 17/17 ok; reconcile-install onto the pre-component `wjcorey/carrera-track` added the 4 garage shapes without touching existing data). Registry metadata points at this GitHub repo as source.

Re-publishing a new version (additive-only — the component has consumers once anyone installs it):

```bash
wh component registry update slotcars/carrera-track-personal --manifest ./component/warmhub/manifest.json
```

## How anyone then sets up their repo

```bash
wh repo create <you>/my-track --public
wh component install slotcars/carrera-track-personal --repo <you>/my-track
```

(or via MCP: `warmhub_repo_create` + `warmhub_component_install` with component `slotcars/carrera-track-personal`)

Then seed Holdings by telling an agent which sets/packs you own — it expands them into piece units via the catalog's `ProductContent` assertions (see `wjcorey/carrera-track` as the worked example).

## Notes

- Component id: `com.slotcars.CarreraTrackPersonal` (reverse-DNS per schema); version 0.1.0.
- `wjcorey/carrera-track` predates the component (shapes committed directly); new consumers get identical shapes via install. Additive-only evolution from here — the component has consumers once anyone installs it.
- Feedback model: `LayoutFeedback` about a Layout — repo members write it in-repo; everyone else asserts the same shape from their own repo about the layout's canonical wref (cross-repo assertions surface on the layout's about-query; verified in the 2026-07-16 spike).
