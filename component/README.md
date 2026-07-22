# carrera-track-personal — installable WarmHub component

The "build your own personal track repo" component (Greenhouse deliverable 3). Ships the 8 personal-repo shapes (Holding, Room, Layout, PieceUsage, BuildLog, LayoutFeedback, Topic, DesignBelief) + 3 seed Topics (flow, kid-friendly, overtaking). Package validates against the official schema (`wh component validate .` → Valid).

## Register (one-time, needs an authenticated `wh` session)

```bash
cd component
wh login   # session expired 2026-07-17; registration blocked on this
wh component register carrera-track-personal --org slotcars --manifest ./warmhub/manifest.json
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
