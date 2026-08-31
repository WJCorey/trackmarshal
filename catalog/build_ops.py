"""Generate WarmHub commit operations for slotcars/carrera-catalog.

Emits chunked ops JSON files (ops-1-shapes.json, ops-2-piecetypes.json, ...) for
submission via warmhub_commit_submit. Deterministic names throughout: re-running
and re-submitting is safe (adds on existing names error harmlessly; revises are
idempotent). Data provenance: PIECES.md / DATA-SOURCES.md; radius adjudication:
solver/README.md (exact-nesting confirmed 2026-07-16).
"""

import json
from pathlib import Path

OUT = Path(__file__).parent
TODAY = "2026-07-16"

# ---------------------------------------------------------------- shapes

SHAPES = [
    {"operation": "add", "kind": "shape", "name": "PieceType", "data": {
        "description": ("One geometric/functional Carrera 124/132 track piece type — the unit "
                        "solvers, inventories, and layouts reason in. Distinct from Product (retail SKU): "
                        "the same piece type is sold in several pack sizes and kits. Identity test: two "
                        "pieces are the same PieceType iff geometrically and functionally interchangeable "
                        "in a layout (banked and flat curves of the same radius are DIFFERENT types). "
                        "Assert your inventory about these things cross-repo (Holding shape); per-source "
                        "dimension evidence lives in SpecClaim assertions here."),
        "fields": {
            "title": {"type": "string", "description": "Human-readable name, e.g. Standard straight"},
            "kind": {"type": "string", "description": "straight | curve | curve-banked | special | digital | border | accessory"},
            "lengthMm": {"type": "number?", "description": "Centerline length for straight-footprint pieces; null for curves and non-track accessories"},
            "radiusMm": {"type": "number?", "description": "Centerline radius for curves — adjudicated exact-nesting value (r1 297 / r2 495 / r3 693 / r4 891); edge radii are ±99 mm. Do NOT use rounded marketing radii (20/40 cm etc.) for geometry"},
            "arcDeg": {"type": "number?", "description": "Arc angle for curves"},
            "solverReady": {"type": "boolean", "description": "true = geometry sufficient for closure computation; false = piece exists but its transform is not yet verified (banked, turnouts, hairpin)"},
            "geometryBasis": {"type": "string?", "description": "Rationale for the adjudicated dimensions; evidence detail is in SpecClaim assertions about this thing"},
        }}},
    {"operation": "add", "kind": "shape", "name": "Product", "data": {
        "description": ("A purchasable Carrera retail SKU: piece pack, kit, extension set, starter set, "
                        "or accessory. Box contents are ProductContent assertions about Pair[Product, "
                        "PieceType]. A Product with no ProductContent has unresolved contents — that is "
                        "explicit, never guessed. status changes are revisions; names never change."),
        "fields": {
            "partNumber": {"type": "string", "description": "Common 5-digit article number; mirrors the name suffix"},
            "skuAliases": {"type": "array?", "items": {"type": "string"}, "description": "Other identifiers for the same product (full 8-digit SKU 200xxxxx, legacy numbers). Never separate Products"},
            "title": {"type": "string", "description": "Product title"},
            "productClass": {"type": "string", "description": "piece-pack | kit | extension-set | starter-set | accessory"},
            "status": {"type": "string", "description": "current | discontinued — discontinued products stay: inventories reference them"},
            "notes": {"type": "string?", "description": "Caveats, e.g. unresolved contents, non-track box items"},
        }}},
    {"operation": "add", "kind": "shape", "name": "ProductContent", "data": {
        "description": ("Quantity of a PieceType inside a Product. about = Pair (ordered: Product first, "
                        "PieceType second). Query from either endpoint needs resolveCollections:true. "
                        "Counts are individual pieces, never packs — anti-inference: one Product 20509 "
                        "contains FOUR standard straights."),
        "fields": {
            "quantity": {"type": "number", "description": "Individual pieces of this type in the box"},
            "partNumber": {"type": "string", "description": "Denormalized product part number"},
            "pieceTypeSlug": {"type": "string", "description": "Denormalized piece type path"},
            "pieceTitle": {"type": "string", "description": "Denormalized piece title"},
            "verified": {"type": "boolean", "description": "false = contents not confirmed against an official source yet; unresolved stays unresolved"},
        }}},
    {"operation": "add", "kind": "shape", "name": "SpecClaim", "data": {
        "description": ("Grounding layer: what one source published/measured about a PieceType's "
                        "geometry, in the source's own language — evidence, not truth. Conflicting "
                        "claims coexist (conflict is knowledge); the adjudicated value lives on the "
                        "PieceType with geometryBasis rationale. about = the PieceType."),
        "fields": {
            "sourceUrl": {"type": "string", "description": "Where the claim was published"},
            "archiveUrl": {"type": "string?", "description": "Durable copy (Wayback etc.) when available"},
            "sourceKind": {"type": "string", "description": "official-product-page | official-pdf | retailer-tech-page | community-cad | community-forum | own-measurement | derived-geometrically"},
            "lengthMm": {"type": "number?", "description": "Claimed centerline length"},
            "radiusCenterlineMm": {"type": "number?", "description": "Claimed centerline radius"},
            "radiusInnerEdgeMm": {"type": "number?", "description": "Claimed inner-edge radius (marketing pages use rounded edge values)"},
            "radiusOuterEdgeMm": {"type": "number?", "description": "Claimed outer-edge radius"},
            "arcDeg": {"type": "number?", "description": "Claimed arc angle"},
            "trackWidthMm": {"type": "number?", "description": "Claimed track profile width (system-wide, recorded on straight/full)"},
            "slotSpacingMm": {"type": "number?", "description": "Claimed slot-to-slot spacing (system-wide, recorded on straight/full)"},
            "valuesNote": {"type": "string?", "description": "Source wording, derivation method, caveats"},
            "observedAt": {"type": "string", "description": "ISO-8601 date we read the source (system time, not source publication time)"},
            "pieceTypeSlug": {"type": "string", "description": "Denormalized piece type path"},
        }}},
]

# ---------------------------------------------------------------- piece types
# (slug, title, kind, lengthMm, radiusMm, arcDeg, solverReady, geometryBasis)

R = {"r1": 297.0, "r2": 495.0, "r3": 693.0, "r4": 891.0}
NEST = ("Exact-nesting model (198 mm track-width steps), confirmed 2026-07-16 by least-squares "
        "over 4 official circuit-plan lengths (fitted spacing ~198 mm; rounded 300/500/700/900 "
        "model refuted). See SpecClaims.")

PIECE_TYPES = [
    ("straight/full", "Standard straight", "straight", 345.0, None, None, True,
     "345 mm; consistent across official pages and all official circuit-plan reconstructions"),
    ("straight/third", "1/3 straight", "straight", 115.0, None, None, True, "115 mm = 345/3, official pages"),
    ("straight/quarter", "1/4 straight", "straight", 86.25, None, None, True,
     "86.25 mm = 345/4 exactly; retail listings round to 86 mm"),
    ("straight/single-lane", "Single-lane straight", "straight", 345.0, None, None, True,
     "345 mm, one slot only (pit-lane extension)"),
    ("curve/r1-60", "Curve 1/60°", "curve", None, R["r1"], 60, True, NEST),
    ("curve/r1-30", "Curve 1/30°", "curve", None, R["r1"], 30, True, NEST),
    ("curve/r2-30", "Curve 2/30°", "curve", None, R["r2"], 30, True, NEST),
    ("curve/r3-30", "Curve 3/30°", "curve", None, R["r3"], 30, True, NEST),
    ("curve/r4-15", "Curve 4/15°", "curve", None, R["r4"], 15, True, NEST),
    ("curve-banked/r1-30", "High banked curve 1/30°", "curve-banked", None, R["r1"], 30, False,
     "Nominal radius as flat R1; banking angle and projected plan-view footprint unverified — distinct type from flat (not interchangeable), excluded from solver v1"),
    ("curve-banked/r2-30", "High banked curve 2/30°", "curve-banked", None, R["r2"], 30, False, "See curve-banked/r1-30"),
    ("curve-banked/r3-30", "High banked curve 3/30°", "curve-banked", None, R["r3"], 30, False, "See curve-banked/r1-30"),
    ("curve-banked/r4-15", "High banked curve 4/15°", "curve-banked", None, R["r4"], 15, False, "See curve-banked/r1-30"),
    ("curve-banked/transition", "Flat-to-banked transition section", "curve-banked", None, None, None, False,
     "Connects flat track to banked curves; geometry unverified"),
    ("special/chicane-piece", "Chicane / narrow section piece", "special", 345.0, None, None, True,
     "Standard-straight footprint; both slots converge toward center (sold as 2-piece set 20516)"),
    ("special/lane-change-analog", "Lane change piece (analog crossover)", "special", 345.0, None, None, True,
     "Standard-straight footprint; slots swap lanes (sold as 2-piece set 20517)"),
    ("special/ramp-convex", "Ramp bridge section, convex", "special", 345.0, None, None, False,
     "345 mm plan footprint; vertical profile (part of 4-piece crossing kit 20587, ~93 mm clearance)"),
    ("special/ramp-concave", "Ramp bridge section, concave", "special", 345.0, None, None, False, "See special/ramp-convex"),
    ("special/connecting-evolution", "Evolution connecting section (analog power base)", "special", 345.0, None, None, True,
     "345 mm; carries analog power feed + controller sockets. Geometrically a standard straight — official plans list it as part 20515"),
    ("special/hairpin-component", "Hairpin kit component", "special", None, None, None, False,
     "Kit 20613 internal geometry unverified (lanes converge to near-single-lane apex); pieces not sold individually"),
    ("digital/lane-change-left", "Lane change section, left (digital)", "digital", 690.0, None, None, True,
     "Two joined 345 mm sections, 690 mm functional unit with flipper"),
    ("digital/lane-change-right", "Lane change section, right (digital)", "digital", 690.0, None, None, True, "See digital/lane-change-left"),
    ("digital/double-lane-change", "Double lane change section (digital)", "digital", 690.0, None, None, True, "Both directions; 690 mm unit"),
    ("digital/narrow-left", "Digital narrow section, left", "digital", 690.0, None, None, False,
     "690 mm total (4 pieces per product); internal piece breakdown unverified"),
    ("digital/narrow-right", "Digital narrow section, right", "digital", 690.0, None, None, False, "See digital/narrow-left"),
    ("digital/lane-change-curve-left-io", "Lane change curve, left, in-to-out", "digital", None, R["r1"], 60, True,
     "R1/60° footprint with lane-change flipper"),
    ("digital/lane-change-curve-left-oi", "Lane change curve, left, out-to-in", "digital", None, R["r1"], 60, True, "R1/60° footprint"),
    ("digital/lane-change-curve-right-io", "Lane change curve, right, in-to-out", "digital", None, R["r1"], 60, True, "R1/60° footprint"),
    ("digital/lane-change-curve-right-oi", "Lane change curve, right, out-to-in", "digital", None, R["r1"], 60, True, "R1/60° footprint"),
    ("digital/control-unit", "Control Unit (digital power base)", "digital", 345.0, None, None, True,
     "Golden case: electronics that is geometrically a 345 mm standard straight"),
    ("digital/black-box", "Black Box (legacy digital power base)", "digital", 345.0, None, None, True, "345 mm straight footprint"),
    ("digital/driver-display", "Driver Display", "digital", 345.0, None, None, True, "345 mm straight footprint"),
    ("digital/lap-counter", "Lap Counter", "digital", 345.0, None, None, True, "345 mm straight footprint"),
    ("digital/multistart", "Multistart / start-finish lane", "digital", 345.0, None, None, True, "345 mm straight footprint"),
    ("digital/pit-adapter", "Pit stop adapter unit", "digital", None, None, None, False, "Part of pit lane kit; footprint unverified"),
    ("digital/turnout-entry", "Pit lane turnout, entry", "digital", None, None, None, False,
     "Diverges pit lane from main track; transform unverified — solver-excluded"),
    ("digital/turnout-exit", "Pit lane turnout, exit", "digital", None, None, None, False, "See digital/turnout-entry"),
]

BORDER_TYPES = [
    ("border/straight-full", "Border for standard straight"),
    ("border/straight-third", "Border for 1/3 straight"),
    ("border/straight-quarter", "Border for 1/4 straight"),
    ("border/crossing", "Border for crossing"),
    ("border/pit-outside", "Outside border for pit lane"),
    ("border/narrow-outside", "Outside border for narrow section"),
    ("border/curve-inside-r1-60", "Inside border, curve 1/60°"),
    ("border/curve-inside-r1-30", "Inside border, curve 1/30°"),
    ("border/curve-inside-r2", "Inside border, curve 2"),
    ("border/curve-inside-r3", "Inside border, curve 3"),
    ("border/curve-inside-r4", "Inside border, curve 4"),
    ("border/curve-outside-r1-60", "Outside border, curve 1/60°"),
    ("border/curve-outside-r1-30", "Outside border, curve 1/30°"),
    ("border/curve-outside-r2", "Outside border, curve 2"),
    ("border/curve-outside-r3", "Outside border, curve 3"),
    ("border/curve-outside-r4", "Outside border, curve 4"),
    ("border/banked-inside-r1", "Inside border, banked curve 1"),
    ("border/banked-inside-r2", "Inside border, banked curve 2"),
    ("border/banked-inside-r3", "Inside border, banked curve 3"),
    ("border/banked-inside-r4", "Inside border, banked curve 4"),
    ("border/banked-outside-r1", "Outside border, banked curve 1"),
    ("border/banked-outside-r2", "Outside border, banked curve 2"),
    ("border/banked-outside-r3", "Outside border, banked curve 3"),
    ("border/banked-outside-r4", "Outside border, banked curve 4"),
    ("border/end-piece", "End piece, outside shoulder"),
    ("border/banked-end-piece", "End section, banked inner edge"),
]

ACCESSORY_TYPES = [
    ("accessory/connection-clip", "Track connection clip/bolt"),
    ("accessory/tire-stack", "Tire stack"),
    ("accessory/power-cable-5m", "Additional power supply cable 5 m"),
    ("accessory/power-cable-10m", "Additional power supply cable 10 m"),
]

# ---------------------------------------------------------------- products
# (part, title, class, contents {slug: qty} | None, verified, notes)

PRODUCTS = [
    ("20509", "Standard straight, 4 pieces", "piece-pack", {"straight/full": 4}, True, None),
    ("20601", "Standard straight, 2 pieces", "piece-pack", {"straight/full": 2}, False,
     "Part number seen only on slottrackpro survey — confirm against official source"),
    ("20611", "1/3 straight, 2 pieces", "piece-pack", {"straight/third": 2}, True, None),
    ("20612", "1/4 straight, 2 pieces", "piece-pack", {"straight/quarter": 2}, True, None),
    ("30341", "Single-lane straight", "piece-pack", {"straight/single-lane": 1}, True, None),
    ("20571", "Curve 1/60°, 3 pieces", "piece-pack", {"curve/r1-60": 3}, True, None),
    ("20577", "Curve 1/30°, 6 pieces", "piece-pack", {"curve/r1-30": 6}, True, None),
    ("20572", "Curve 2/30°, 6 pieces", "piece-pack", {"curve/r2-30": 6}, True, None),
    ("20573", "Curve 3/30°, 6 pieces", "piece-pack", {"curve/r3-30": 6}, True, None),
    ("20578", "Curve 4/15°, 12 pieces", "piece-pack", {"curve/r4-15": 12}, True, None),
    ("20574", "High banked curve 1/30°, 6 pieces", "piece-pack", {"curve-banked/r1-30": 6}, True, None),
    ("20575", "High banked curve 2/30°, 6 pieces", "piece-pack", {"curve-banked/r2-30": 6}, True, None),
    ("20576", "High banked curve 3/30°, 6 pieces", "piece-pack", {"curve-banked/r3-30": 6}, True, None),
    ("20579", "High banked curve 4/15°, 12 pieces", "piece-pack", {"curve-banked/r4-15": 12}, True, None),
    ("20600", "Connecting pieces flat-to-banked, 4 pieces", "piece-pack", {"curve-banked/transition": 4}, True, None),
    ("20599", "End sections banked inner edge, 4 pieces (2 L, 2 R)", "piece-pack", {"border/banked-end-piece": 4}, True, None),
    ("20516", "Chicane / narrow section, 2 pieces", "kit", {"special/chicane-piece": 2}, True, None),
    ("20517", "Lane change section (analog), 2 pieces", "kit", {"special/lane-change-analog": 2}, True, None),
    ("20587", "Ramp bridge crossing, 4 pieces + supports", "kit",
     {"special/ramp-convex": 2, "special/ramp-concave": 2}, True, "~93 mm clearance; supports included"),
    ("20613", "Hairpin curve kit", "kit", None, False,
     "UNRESOLVED CONTENTS: ~3x R1/60-like bends + straights + end pieces; exact internal geometry unverified"),
    ("20515", "Evolution connecting section", "kit",
     {"special/connecting-evolution": 1, "straight/full": 1}, True, "Analog power base; box includes one extra standard straight"),
    ("30343", "Lane change section, left (digital)", "kit", {"digital/lane-change-left": 1}, True, "Unit = 2 joined 345 mm pieces"),
    ("30345", "Lane change section, right (digital)", "kit", {"digital/lane-change-right": 1}, True, "Unit = 2 joined 345 mm pieces"),
    ("30347", "Double lane change section (digital)", "kit", {"digital/double-lane-change": 1}, True, "Unit = 2 joined 345 mm pieces"),
    ("30350", "Digital narrow section, left", "kit", {"digital/narrow-left": 1}, False, "4 pieces / 690 mm; internal breakdown unverified"),
    ("30351", "Digital narrow section, right", "kit", {"digital/narrow-right": 1}, False, "4 pieces / 690 mm; internal breakdown unverified"),
    ("30362", "Lane change curve, left, in-to-out", "piece-pack", {"digital/lane-change-curve-left-io": 1}, True, None),
    ("30363", "Lane change curve, left, out-to-in", "piece-pack", {"digital/lane-change-curve-left-oi": 1}, True, None),
    ("30364", "Lane change curve, right, in-to-out", "piece-pack", {"digital/lane-change-curve-right-io": 1}, True, None),
    ("30365", "Lane change curve, right, out-to-in", "piece-pack", {"digital/lane-change-curve-right-oi": 1}, True, None),
    ("30356", "Pit lane kit (digital)", "kit",
     {"digital/turnout-entry": 1, "digital/turnout-exit": 1, "straight/full": 1,
      "straight/single-lane": 2, "digital/pit-adapter": 1, "border/end-piece": 2}, True,
     "1035 mm parallel to main track"),
    ("30361", "Pit stop adapter unit (spare)", "piece-pack", {"digital/pit-adapter": 1}, True, None),
    ("30352", "Control Unit (Digital 124/132)", "piece-pack", {"digital/control-unit": 1}, True, None),
    ("30344", "Black Box (legacy digital power base)", "piece-pack", {"digital/black-box": 1}, True, "Superseded by Control Unit 30352"),
    ("30353", "Driver Display", "piece-pack", {"digital/driver-display": 1}, True, None),
    ("30355", "Lap Counter", "piece-pack", {"digital/lap-counter": 1}, True, None),
    ("30370", "Multistart lane", "piece-pack", {"digital/multistart": 1}, True, None),
    # borders
    ("20560", "Borders for standard straight, 6 pieces", "piece-pack", {"border/straight-full": 6}, True, None),
    ("20588", "Borders for 1/3 straight, 4 pieces", "piece-pack", {"border/straight-third": 4}, True, None),
    ("20589", "Borders for 1/4 straight, 4 pieces", "piece-pack", {"border/straight-quarter": 4}, True, None),
    ("20597", "Borders for crossing, 4 pieces", "piece-pack", {"border/crossing": 4}, True, None),
    ("20602", "Outside borders for pit lane, 3 pieces", "piece-pack", {"border/pit-outside": 3}, True, None),
    ("20603", "Outside borders for narrow section, 4 pieces", "piece-pack", {"border/narrow-outside": 4}, True, None),
    ("20551", "Inside borders curve 1/60°", "piece-pack", {"border/curve-inside-r1-60": 6}, False, "Pack count unverified"),
    ("20590", "Inside borders curve 1/30°", "piece-pack", {"border/curve-inside-r1-30": 6}, False, "Pack count unverified"),
    ("20591", "Inside borders curve 2", "piece-pack", {"border/curve-inside-r2": 6}, False, "Pack count unverified"),
    ("20592", "Inside borders curve 3", "piece-pack", {"border/curve-inside-r3": 6}, False, "Pack count unverified"),
    ("20593", "Inside borders curve 4", "piece-pack", {"border/curve-inside-r4": 6}, False, "Pack count unverified"),
    ("20561", "Outside borders curve 1/60°", "piece-pack", {"border/curve-outside-r1-60": 6}, False, "Pack count unverified"),
    ("20567", "Outside borders curve 1/30°", "piece-pack", {"border/curve-outside-r1-30": 6}, False, "Pack count unverified"),
    ("20562", "Outside borders curve 2", "piece-pack", {"border/curve-outside-r2": 6}, False, "Pack count unverified"),
    ("20563", "Outside borders curve 3", "piece-pack", {"border/curve-outside-r3": 6}, False, "Pack count unverified"),
    ("20568", "Outside borders curve 4", "piece-pack", {"border/curve-outside-r4": 6}, False, "Pack count unverified"),
    ("20569", "Inside borders banked curve 1", "piece-pack", {"border/banked-inside-r1": 6}, False, "Pack count unverified"),
    ("20594", "Inside borders banked curve 2", "piece-pack", {"border/banked-inside-r2": 6}, False, "Pack count unverified"),
    ("20595", "Inside borders banked curve 3", "piece-pack", {"border/banked-inside-r3": 6}, False, "Pack count unverified"),
    ("20596", "Inside borders banked curve 4", "piece-pack", {"border/banked-inside-r4": 6}, False, "Pack count unverified"),
    ("20564", "Outside borders banked curve 1", "piece-pack", {"border/banked-outside-r1": 6}, False, "Pack count unverified"),
    ("20565", "Outside borders banked curve 2", "piece-pack", {"border/banked-outside-r2": 6}, False, "Pack count unverified"),
    ("20566", "Outside borders banked curve 3", "piece-pack", {"border/banked-outside-r3": 6}, False, "Pack count unverified"),
    ("20580", "Outside borders banked curve 4", "piece-pack", {"border/banked-outside-r4": 6}, False, "Pack count unverified"),
    ("20598", "End pieces outside shoulder, 4 pieces (2 L, 2 R)", "piece-pack", {"border/end-piece": 4}, True, None),
    # accessories
    ("85245", "Track connection clips/bolts, 20 pieces", "accessory", {"accessory/connection-clip": 20}, True, None),
    ("21130", "Tire stacks", "accessory", {"accessory/tire-stack": 1}, False, "Pack count unverified"),
    ("20584", "Additional power supply cable 5 m", "accessory", {"accessory/power-cable-5m": 1}, True, None),
    ("20585", "Additional power supply cable 10 m", "accessory", {"accessory/power-cable-10m": 1}, True, None),
    # extension sets
    ("26953", "Extension set 1 (2 straights + 4x curve 1/60°)", "extension-set",
     {"straight/full": 2, "curve/r1-60": 4}, True, None),
    ("26955", "Extension set 2 (2 straights + 4x curve 1/30°)", "extension-set",
     {"straight/full": 2, "curve/r1-30": 4}, True, None),
    ("26956", "Extension set 3", "extension-set",
     {"straight/full": 4, "special/lane-change-analog": 2, "special/chicane-piece": 2, "curve/r2-30": 4}, False,
     "Contents partially unverified"),
    ("30367", "Digital extension set", "extension-set", None, False,
     "UNRESOLVED CONTENTS — enumerate from official set manual"),
]

# ---------------------------------------------------------------- spec claims
# (pieceTypeSlug, sourceSlug, data-fields)

CS = "https://www.carreraslots.com/slot-car/"
SPEC_CLAIMS = [
    ("straight/full", "carreraslots-20509",
     {"sourceUrl": CS + "20509.html", "sourceKind": "official-product-page", "lengthMm": 345,
      "valuesNote": "13.58 in / 34.5 cm"}),
    ("straight/full", "system-profile-freeslotter",
     {"sourceUrl": "https://www.freeslotter.de/index.php?thread/104908-abmessungen-der-carrera-132-schienen/",
      "sourceKind": "community-cad", "trackWidthMm": 198, "slotSpacingMm": 99,
      "valuesNote": "Slot centers 49.5 mm from each edge (CAD measurement for 3D-printing compatibility). System-wide track profile, recorded on straight/full. Direct fetch 403s; confirmed via search snippet"}),
    ("straight/third", "carreraslots-20611",
     {"sourceUrl": CS + "20611.html", "sourceKind": "official-product-page", "lengthMm": 115}),
    ("straight/quarter", "retail-rounded",
     {"sourceUrl": "https://www.slottrackpro.com/carrera-track/", "sourceKind": "retailer-tech-page", "lengthMm": 86,
      "valuesNote": "Retail listings round to 86 mm / 3.38 in"}),
    ("straight/quarter", "derived-quarter",
     {"sourceUrl": "https://github.com/WJCorey/trackmarshal", "sourceKind": "derived-geometrically", "lengthMm": 86.25,
      "valuesNote": "345/4 = 86.25 exactly; 1/3 straight is exactly 345/3=115, so quarter is presumed exact too"}),
    ("curve/r1-60", "carreraslots-20571",
     {"sourceUrl": CS + "20571.html", "sourceKind": "official-product-page",
      "radiusInnerEdgeMm": 200, "radiusOuterEdgeMm": 400, "arcDeg": 60,
      "valuesNote": "Marketing edge radii 20/40 cm — ROUNDED; true edges 198/396 (see community-cad and derived claims)"}),
    ("curve/r1-60", "freeslotter-cad",
     {"sourceUrl": "https://www.freeslotter.de/index.php?thread/104908-abmessungen-der-carrera-132-schienen/",
      "sourceKind": "community-cad", "radiusCenterlineMm": 297,
      "valuesNote": "Slot radii 247.5 / 346.5 mm => centerline 297.0 exactly (= 198 + 99)"}),
    ("curve/r2-30", "carreraslots-20572",
     {"sourceUrl": CS + "20572.html", "sourceKind": "official-product-page",
      "radiusInnerEdgeMm": 400, "radiusOuterEdgeMm": 600, "arcDeg": 30, "valuesNote": "Marketing edge radii, rounded"}),
    ("curve/r3-30", "carreraslots-20573",
     {"sourceUrl": CS + "20573.html", "sourceKind": "official-product-page",
      "radiusInnerEdgeMm": 600, "radiusOuterEdgeMm": 800, "arcDeg": 30, "valuesNote": "Marketing edge radii, rounded"}),
    ("curve/r4-15", "carreraslots-20578",
     {"sourceUrl": CS + "20578.html", "sourceKind": "official-product-page",
      "radiusInnerEdgeMm": 800, "radiusOuterEdgeMm": 1000, "arcDeg": 15, "valuesNote": "Marketing edge radii, rounded"}),
    ("curve/r4-15", "slotfun-anchor",
     {"sourceUrl": "https://www.slotfun.de/Produkt-Technik-Info:_:22.html", "sourceKind": "retailer-tech-page",
      "radiusOuterEdgeMm": 990,
      "valuesNote": "R4 180-degree outer diameter quoted as exactly 198 cm => outer edge 990 mm => centerline 891 (exact-nesting anchor)"}),
]
# derived-oracle claims for all four radii
for slug, r, fitted in [("curve/r1-60", 297, 298.9), ("curve/r1-30", 297, 298.9),
                        ("curve/r2-30", 495, 496.5), ("curve/r3-30", 693, 695.1),
                        ("curve/r4-15", 891, 893.6)]:
    SPEC_CLAIMS.append((slug, "official-plan-lsq",
        {"sourceUrl": "https://carrera-toys.com/en/pages/landing-page-route-planner",
         "sourceKind": "derived-geometrically", "radiusCenterlineMm": r,
         "valuesNote": (f"Least-squares over 4 official circuit-plan lengths fits ~{fitted} mm effective, "
                        "with spacing ~198 mm confirming exact-nesting; the uniform ~+1.9 mm/radius residual is "
                        "constant per curve-degree (~0.033 mm/deg) across all plans => Carrera planner length "
                        "convention, not physical radius. Adjudicated physical value: exact-nesting. "
                        "See TrackMarshal solver/README.md")}))


def pt_op(slug, title, kind, length, radius, arc, ready, basis):
    data = {"title": title, "kind": kind, "solverReady": ready}
    if length is not None:
        data["lengthMm"] = length
    if radius is not None:
        data["radiusMm"] = radius
    if arc is not None:
        data["arcDeg"] = arc
    if basis:
        data["geometryBasis"] = basis
    return {"operation": "add", "kind": "thing", "name": f"PieceType/{slug}", "data": data}


def main():
    piece_titles = {}
    ops_types = []
    for slug, title, kind, length, radius, arc, ready, basis in PIECE_TYPES:
        piece_titles[slug] = title
        ops_types.append(pt_op(slug, title, kind, length, radius, arc, ready, basis))
    for slug, title in BORDER_TYPES:
        piece_titles[slug] = title
        ops_types.append(pt_op(slug, title, "border", None, None, None, False,
                               "Cosmetic/car-retention apron; no effect on closure; apron width unverified"))
    for slug, title in ACCESSORY_TYPES:
        piece_titles[slug] = title
        ops_types.append(pt_op(slug, title, "accessory", None, None, None, False, None))

    ops_products = []
    for part, title, pclass, contents, verified, notes in PRODUCTS:
        data = {"partNumber": part, "title": title, "productClass": pclass, "status": "current"}
        if part.isdigit() and len(part) == 5 and part[0] in "23":
            data["skuAliases"] = ["200" + part]
        if notes:
            data["notes"] = notes
        ops_products.append({"operation": "add", "kind": "thing", "name": f"Product/{part}", "data": data})
        if contents:
            for slug, qty in contents.items():
                flat = slug.replace("/", "-")
                pair = f"{part}--{flat}"
                ops_products.append({"operation": "add", "kind": "collection", "type": "pair",
                                     "name": pair, "members": [f"Product/{part}", f"PieceType/{slug}"]})
                ops_products.append({"operation": "add", "kind": "assertion",
                                     "name": f"ProductContent/{part}/{flat}", "about": f"Pair/{pair}",
                                     "data": {"quantity": qty, "partNumber": part, "pieceTypeSlug": slug,
                                              "pieceTitle": piece_titles[slug], "verified": verified}})

    ops_claims = []
    for slug, source, fields in SPEC_CLAIMS:
        flat = slug.replace("/", "-")
        data = dict(fields)
        data["observedAt"] = TODAY
        data["pieceTypeSlug"] = slug
        ops_claims.append({"operation": "add", "kind": "assertion",
                           "name": f"SpecClaim/{flat}/{source}", "about": f"PieceType/{slug}", "data": data})

    chunks = [("ops-1-shapes.json", SHAPES), ("ops-2-piecetypes.json", ops_types)]
    half = (len(ops_products) + 1) // 2
    # keep product/pair/content triples together: split at a product boundary
    split = half
    while split < len(ops_products) and ops_products[split]["kind"] != "thing":
        split += 1
    chunks += [("ops-3-products-a.json", ops_products[:split]),
               ("ops-4-products-b.json", ops_products[split:]),
               ("ops-5-specclaims.json", ops_claims)]
    for fname, ops in chunks:
        (OUT / fname).write_text(json.dumps(ops, ensure_ascii=False))
        print(f"{fname}: {len(ops)} ops, {(OUT / fname).stat().st_size} bytes")


if __name__ == "__main__":
    main()
