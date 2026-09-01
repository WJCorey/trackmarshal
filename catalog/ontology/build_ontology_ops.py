"""Generate the ontology + grounding seed ops for slotcars/carrera-catalog.

Translates the existing design corpus (docs/DESIGN.md D-decisions, docs/SHAPES.md
naming formulas, docs/ONTOLOGY-REVIEW.md golden objects + CQs, docs/CARS-DESIGN.md)
into the warmhub-data/ontology 2.0 method records, plus the two grounding Sources
for the update pipeline (warmhub-data/grounding 4.0). Every exemplarWref was
verified live on 2026-08-31 before inclusion. Deterministic names; re-submission
is safe (adds on existing names error harmlessly).

Contract assertion names are version-bound to the Shape revision they govern
(e.g. product-shape-v2 governs Product@v2), matching the warmhub-data/us.infrastructure
precedent. Contract assertions are about the bare Shape wref (platform pins it).
"""

import json
from pathlib import Path

OPS = []


def thing(name, data):
    OPS.append({"operation": "add", "kind": "thing", "name": name, "data": data})


def assertion(name, about, data):
    OPS.append({"operation": "add", "kind": "assertion", "name": name,
                "about": about, "data": data})


# ---------------------------------------------------------------- charter

thing("OntologyCharter/ontology/charter", {
    "mission": (
        "Open, source-cited knowledge of the Carrera 1:24/1:32 slot-car system — every "
        "track piece's exact geometry, every retail product's contents and status, every "
        "car's fitment-relevant specs — with per-datum provenance, for the racers, "
        "hobbyist tool-builders, and agents who compose personal inventories, garages, "
        "layouts, and track designs on top of it."),
    "nonGoals": [
        "The 1:43 GO!!! and Hybrid product lines (different track system)",
        "Pricing history or commerce beyond current availability/status",
        "Personal inventories, garages, layouts, and taste — personal repos compose on this catalog via cross-repo assertions",
        "Performance opinions (grip, feel, fun) — DesignBelief-family taste in personal repos, never catalog facts",
        "Republishing protected compilations: vendor fitment charts, proprietary app piece libraries, official PDFs and photos are linked, never copied",
    ],
    "commitments": [
        "Facts in the catalog, opinions in personal repos (D1)",
        "Adjudicated values live on things with an explicit basis rationale; per-source claims are preserved in source language as SpecClaims — conflict is knowledge, adjudication is separate (D1)",
        "Piece type is not product; car model is not livery SKU: geometry and fitment attach to the physical design, commerce to the part number (D8; CARS identity model)",
        "Names are contracts: kind-led trees for geometric/functional identity, source-stable Carrera part numbers for commerce; no state, no relationships in names",
        "Compile facts, never extract compilations (D7): every datum cites its source per-claim; dataset CC-BY-SA-4.0, code MIT",
        "Commerce records are never retracted: disappearance from a source means a reviewed status revision (discontinued), not deletion",
        "Method classes, never confidence floats: basis/sourceKind enums carry the epistemics (guidebook anti-pattern 4)",
        "Shapes with external consumers evolve additively only (D6)",
        "Machine writers operate under narrow write contracts: the update pipeline may never mint PieceType or CarModel identities — new physical designs are human-reviewed",
    ],
})

# ---------------------------------------------------- competency questions
# Domain slugs: track/* from ONTOLOGY-REVIEW CQ-1..12, cars/* from CARS-DESIGN CQ-C*.

thing("CompetencyQuestion/ontology/track/piece-dims-with-basis", {
    "question": "What are the exact dimensions and rigid-body transform of piece type X, and on what basis do we believe them?",
    "personas": ["track designer (agent)", "racer"],
    "requiredConcepts": ["PieceType", "SpecClaim"],
    "provenanceRequirement": "source-level",
})
thing("CompetencyQuestion/ontology/track/product-contents-both-ways", {
    "question": "What is inside product P — and which products contain piece type X?",
    "personas": ["racer", "inventory skill (agent)"],
    "requiredConcepts": ["Product", "ProductContent", "PieceType"],
})
thing("CompetencyQuestion/ontology/track/cheapest-covering-product", {
    "question": "What is the cheapest in-production product that covers my piece shortfall?",
    "personas": ["racer", "track designer (agent)"],
    "requiredConcepts": ["Product", "ProductContent"],
    "temporalSemantics": "Answer as-of current catalog status; discontinued products are excluded from purchase advice but remain valid in layouts",
})
thing("CompetencyQuestion/ontology/track/why-believe-r2-495", {
    "question": "Why do we believe the R2 centerline radius is 495 mm — which sources say what, and how was the conflict adjudicated?",
    "personas": ["catalog maintainer", "skeptical contributor"],
    "requiredConcepts": ["SpecClaim", "PieceType"],
    "provenanceRequirement": "source-level",
})
thing("CompetencyQuestion/ontology/track/what-changed-this-month", {
    "question": "What changed in the catalog this month — new products, discontinuations, spec corrections — and from which source snapshot?",
    "personas": ["catalog maintainer", "update pipeline (agent)"],
    "requiredConcepts": ["Product", "SpecClaim", "Source", "SourceArtifact"],
    "temporalSemantics": "Monthly cadence; answers pin the accepted SourceArtifact versions that established the changes",
    "provenanceRequirement": "artifact-hash-level",
})
thing("CompetencyQuestion/ontology/cars/tire-sizes-with-evidence", {
    "question": "What are the tire sizes (front/rear) for car X, with evidence?",
    "personas": ["racer", "garage skill (agent)"],
    "requiredConcepts": ["CarModel", "SpecClaim", "PartType", "Fitment"],
    "provenanceRequirement": "source-level",
})
thing("CompetencyQuestion/ontology/cars/cars-for-part-reverse-query", {
    "question": "Which cars does tire/part Y fit? (vendor charts answer per-car; this reverse query is the one nobody publishes)",
    "personas": ["racer", "vendor"],
    "requiredConcepts": ["PartType", "Fitment", "CarModel"],
})
thing("CompetencyQuestion/ontology/cars/single-source-fitments", {
    "question": "Which fitment claims rest on a single non-official source, and which are disputed between sources?",
    "personas": ["catalog maintainer"],
    "requiredConcepts": ["Fitment", "SpecClaim"],
    "provenanceRequirement": "source-level",
})

# ------------------------------------------------------- semantic contracts

assertion("SemanticContract/ontology/piece-type-shape-v1", "PieceType", {
    "definition": "One geometric/functional Carrera 124/132 track piece type — the unit solvers, inventories, and layouts reason in.",
    "identityTest": "Two pieces are the same PieceType iff geometrically and functionally interchangeable in a layout. Banked and flat curves of the same nominal radius are different types; digital lane-changers are not plain curves.",
    "examples": ["PieceType/straight/full", "PieceType/curve/r2-30", "PieceType/curve-banked/r2-30"],
    "counterexamples": ["A retail SKU (20509 and 20601 are Products containing this same type)", "A specific physical piece someone owns (Holding, personal repos)"],
    "lifecycleNotes": "Piece types are never retracted; product-line changes never touch them. New geometry is human-reviewed — the update pipeline may not mint PieceTypes.",
    "lifecycleStatus": "approved",
})
assertion("SemanticContract/ontology/product-shape-v2", "Product", {
    "definition": "One purchasable Carrera retail SKU: piece pack, kit, extension set, starter set, car, spare part, or accessory. The unit of commerce, keyed by Carrera's own part number.",
    "identityTest": "Same canonical 5-digit Carrera part number. Full 8-digit SKUs (200-prefixed) and legacy Exclusiv-era numbers are skuAliases on the same Product, never a second identity.",
    "examples": ["Product/20509", "Product/30044", "Product/32001"],
    "counterexamples": ["A piece type (the geometric unit sold inside SKUs)", "The 8-digit alias 20020509 (same Product as 20509)"],
    "lifecycleNotes": "Pack size, price, availability, and status changes are revisions; discontinuation is a reviewed status revision. Products are never retracted — holdings and garages reference them forever.",
    "lifecycleStatus": "approved",
})
assertion("SemanticContract/ontology/car-model-shape-v1", "CarModel", {
    "definition": "One physical Carrera slot-car design — the unit tire fitment, garage inventories, and lap records reason about.",
    "identityTest": "Same chassis, electronics, and body physical design. The d132 and evolution versions of 'the same car' are different CarModels; liveries never create identity (a livery is a Product).",
    "examples": ["CarModel/d132/ferrari-296-gt3", "CarModel/d132/aston-martin-vantage-gt3"],
    "counterexamples": ["A livery SKU (Product/32001)", "A chassis platform (deferred grain — see OntologyDecision/ontology/od-platform-grain)"],
    "lifecycleNotes": "Human-reviewed identities; the update pipeline may not mint CarModels. Discontinued cars keep their CarModel and Fitments forever.",
    "lifecycleStatus": "approved",
})

# ----------------------------------------------------- predicate declarations

assertion("PredicateDeclaration/ontology/fitment-shape-v1", "Fitment", {
    "subjectPattern": "PartType/**",
    "objectPattern": "CarModel/**",
    "forwardLabel": "fits",
    "inverseLabel": "is fitted by",
    "subjectForm": "arc",
    "subjectNameRecipe": "Pair/{partTypeSlug flattened with -}--{carModelSlug flattened with -}, e.g. Pair/tire-oem-89800--d132-ferrari-296-gt3; the assertion is Fitment/{partTypeSlug-flattened}/{carModelSlug-flattened}. Members never rename (both endpoint namespaces are identity-stable).",
    "structuralCardinality": "many:many",
    "epistemicClass": "source-claim",
    "prohibitedSemantics": ["car-to-track-system compatibility", "performance or grip preference (DesignBelief territory, personal repos)"],
    "antiInferences": [
        "verified:false is a lead, not a fact — always surface the basis",
        "dimensional match does not imply fitment: basis=dimensional is the weakest explicit claim class, minted precisely to mark that inference",
        "a discontinued car's Fitments remain valid (people race discontinued cars forever)",
        "conflicting vendor charts are preserved as parallel Fitments — owner mounting adjudicates via verified:true, never by deleting the loser",
    ],
})
assertion("PredicateDeclaration/ontology/product-content-shape-v2", "ProductContent", {
    "subjectPattern": "Product/**",
    "objectPattern": "PieceType/**, CarModel/**, PartType/** (contentKind discriminates; pre-widening rows are implicitly pieceType)",
    "forwardLabel": "contains",
    "inverseLabel": "is contained in",
    "subjectForm": "arc",
    "subjectNameRecipe": "Pair/{partNumber}--{contentSlug flattened with -}; the assertion is ProductContent/{partNumber}/{contentSlug-flattened}. Members never rename.",
    "structuralCardinality": "many:many",
    "epistemicClass": "normalized-state",
    "antiInferences": [
        "box art and set photos are not authoritative contents; only rows with verified:true are",
        "quantity is in individual content units (pieces/cars), never packs",
        "a piece type appearing inside a kit does not imply it is purchasable individually",
    ],
})

# --------------------------------------------------------- naming contracts

assertion("NamingContract/ontology/piece-type-shape-v1", "PieceType", {
    "nameTemplate": "PieceType/{kind}/{geometry-slug}",
    "segmentSemantics": [
        "kind — the dimension agents narrow by first (straight | curve | curve-banked | special | digital | border | accessory); scopes globs like PieceType/curve/**",
        "geometry-slug — intrinsic geometric identity (e.g. r1-60 = radius index 1, 60 degrees)",
    ],
    "exampleNames": ["PieceType/straight/full", "PieceType/straight/quarter", "PieceType/curve/r1-60", "PieceType/curve-banked/r2-30", "PieceType/digital/lane-change-left"],
    "globs": ["PieceType/curve/**", "PieceType/digital/**", "PieceType/**"],
    "identityStabilityTest": "Product-line changes, discontinuation, and new SKUs must never falsify the name: kind and geometry are intrinsic to the piece.",
})
assertion("NamingContract/ontology/product-shape-v2", "Product", {
    "nameTemplate": "Product/{part-number}",
    "segmentSemantics": [
        "part-number — Carrera's own stable commerce key, canonical 5-digit form; 8-digit 200-prefixed full SKUs and legacy numbers live in skuAliases, never in names",
    ],
    "exampleNames": ["Product/20509", "Product/30044", "Product/32001", "Product/89800"],
    "globs": ["Product/**"],
    "identityStabilityTest": "Pack size, price, availability, and status changes never touch the name. An alias discovered later joins skuAliases on the existing Product — it never mints a second name.",
})
assertion("NamingContract/ontology/product-content-shape-v2", "ProductContent", {
    "nameTemplate": "ProductContent/{partNumber}/{contentSlug-flattened}",
    "segmentSemantics": [
        "partNumber — the containing Product's key (subject side)",
        "contentSlug-flattened — the contained thing's slug with '/' flattened to '-' (object side); deterministic name = idempotent pipeline writes",
    ],
    "exampleNames": ["ProductContent/30044/d132-ferrari-296-gt3", "ProductContent/26732/decoder-d132-26732"],
    "globs": ["ProductContent/**"],
    "identityStabilityTest": "Quantity and verification changes are revisions; endpoints are identity-stable so the name never goes false.",
})
assertion("NamingContract/ontology/spec-claim-shape-v2", "SpecClaim", {
    "nameTemplate": "SpecClaim/{subjectSlug-flattened}/{source-slug}",
    "segmentSemantics": [
        "subjectSlug-flattened — the subject thing's slug below its shape, '/' flattened to '-' (e.g. curve-r2-30)",
        "source-slug — identifies the publishing source and locator (e.g. carreraslots-20572, official-plan-lsq); a method identity, never a trust ranking",
    ],
    "exampleNames": ["SpecClaim/curve-r2-30/official-plan-lsq", "SpecClaim/curve-r2-30/carreraslots-20572"],
    "globs": ["SpecClaim/**"],
    "identityStabilityTest": "A source correcting its published value revises the claim; a different source is a different claim name. Adjudication changes never touch claim names.",
})
assertion("NamingContract/ontology/car-model-shape-v1", "CarModel", {
    "nameTemplate": "CarModel/{system}/{slug}",
    "segmentSemantics": [
        "system — d132 | d124 | evolution; leads because the d132 and evolution versions of 'the same car' are physically different designs",
        "slug — the car design (no livery, no year, no state)",
    ],
    "exampleNames": ["CarModel/d132/ferrari-296-gt3", "CarModel/d132/aston-martin-vantage-gt3"],
    "globs": ["CarModel/d132/**", "CarModel/**"],
    "identityStabilityTest": "New liveries, discontinuation, and price changes never touch the name; livery identity lives on Product.",
})
assertion("NamingContract/ontology/part-type-shape-v1", "PartType", {
    "nameTemplate": "PartType/{kind}/{slug}",
    "segmentSemantics": [
        "kind — tire | brush | guide | magnet | decoder | axle | gear | motor; the dimension fitment queries narrow by",
        "slug — vendor-prefixed for third-party parts (pgt-*, qs-*), oem-* or generation slugs for Carrera parts",
    ],
    "exampleNames": ["PartType/tire/oem-89800", "PartType/tire/pgt-20115lmxd", "PartType/brush/double-2007", "PartType/decoder/d132-26732"],
    "globs": ["PartType/tire/**", "PartType/**"],
    "identityStabilityTest": "Vendor catalog reshuffles and availability changes never touch the name; the part's physical identity is intrinsic.",
})
assertion("NamingContract/ontology/fitment-shape-v1", "Fitment", {
    "nameTemplate": "Fitment/{partTypeSlug-flattened}/{carModelSlug-flattened}",
    "segmentSemantics": [
        "partTypeSlug-flattened — subject part, '/' flattened to '-'",
        "carModelSlug-flattened — object car, '/' flattened to '-'; deterministic name = independent writers mint one claim per (part, car), and idempotent pipeline writes",
    ],
    "exampleNames": ["Fitment/tire-oem-89800/d132-ferrari-296-gt3", "Fitment/tire-pgt-20125lm/d132-aston-martin-vantage-gt3"],
    "globs": ["Fitment/**"],
    "identityStabilityTest": "basis upgrades (vendor-chart to owner-verified) and verification are revisions of the same name — the claim's identity is the (part, car) pair, not its evidence state.",
})
assertion("NamingContract/ontology/source-shape-v1", "Source", {
    "nameTemplate": "Source/grounding/{authority}/{system}",
    "segmentSemantics": [
        "grounding — the epistemic layer segment (co-located repo convention from the grounding 4.0 component docs)",
        "authority — the publishing organization (carrera, carreraslots)",
        "system — the specific publishing system or surface (toys-shop, store)",
    ],
    "exampleNames": ["Source/grounding/carrera/toys-shop", "Source/grounding/carreraslots/store"],
    "globs": ["Source/grounding/**"],
    "identityStabilityTest": "Storefront redesigns, URL changes, and platform migrations revise fields; the logical publisher-system identity survives them.",
})
assertion("NamingContract/ontology/source-artifact-shape-v1", "SourceArtifact", {
    "nameTemplate": "SourceArtifact/grounding/{authority}/{system}/{stream-slug}",
    "segmentSemantics": [
        "grounding/{authority}/{system} — mirrors the owning Source",
        "stream-slug — one logical dataset stream whose versions are accepted canonical snapshots (never a date, run id, or hash); streams are minted by the update pipeline under its managed scope",
    ],
    "exampleNames": ["SourceArtifact/grounding/carrera/toys-shop/products", "SourceArtifact/grounding/carreraslots/store/product-pages"],
    "globs": ["SourceArtifact/grounding/**"],
    "identityStabilityTest": "A new snapshot revises the stream thing (new version); only a genuinely different logical stream mints a new name.",
})

# ------------------------------------------------------------- golden cases

thing("GoldenCase/ontology/20509-vs-20601", {
    "title": "Two Products, one PieceType — the case that forced the identity split",
    "narrative": (
        "Carrera sells the same standard straight as a 4-pack (20509) and a 2-pack (20601). "
        "Attacks the temptation to key geometry by part number (the v1 TrackPiece design). "
        "Passing: both Products resolve to PieceType/straight/full via ProductContent, quantities "
        "in piece units, and the solver never sees a SKU. Is the ontology lying? It would be if "
        "either pack minted its own geometric identity."),
    "exemplarWrefs": ["Product/20509", "Product/20601", "PieceType/straight/full"],
})
thing("GoldenCase/ontology/flat-r2-vs-banked-r2", {
    "title": "Same nominal radius, distinct PieceTypes",
    "narrative": (
        "The flat and banked R2/30-degree curves share a nominal radius but have different projected "
        "geometry — they are not layout-interchangeable. Attacks banking-as-a-flag designs. Passing: "
        "two PieceTypes under different kind segments, each with its own adjudicated transform."),
    "exemplarWrefs": ["PieceType/curve/r2-30", "PieceType/curve-banked/r2-30"],
})
thing("GoldenCase/ontology/one-set-two-cars-30044", {
    "title": "One starter set, two CarModels — the 20509/20601 of cars (G-C1)",
    "narrative": (
        "Starter set 30044 contains a Ferrari 296 GT3 and an Aston Martin Vantage GT3 — retail "
        "products 32001/32022 — plus track pieces. Attacks fitment-per-SKU designs: the two cars "
        "possibly share tire values but are distinct physical designs. Passing: ProductContent rows "
        "with contentKind carModel alongside piece rows; same-tire-fits-both stays queryable via "
        "Fitment without merging car identities."),
    "exemplarWrefs": ["Product/30044", "ProductContent/30044/d132-ferrari-296-gt3",
                       "ProductContent/30044/d132-aston-martin-vantage-gt3",
                       "CarModel/d132/ferrari-296-gt3", "CarModel/d132/aston-martin-vantage-gt3"],
})
thing("GoldenCase/ontology/vantage-tire-dispute", {
    "title": "Two dealers, two incompatible tires, zero first-party evidence (G-C2)",
    "narrative": (
        "For the Aston Martin Vantage GT3, one dealer maps Paul Gage 20125LM and another maps "
        "20126LMXD — physically incompatible rib widths, and Paul Gage's own store lists neither "
        "for this car. Attacks any design that must pick a winner to store a fact. Passing: both "
        "Fitments preserved as parallel vendor-chart claims with the dispute in notes, adjudication "
        "reserved for owner mounting (basis owner-verified). The graph refuses to claim what it "
        "cannot prove."),
    "exemplarWrefs": ["Fitment/tire-pgt-20125lm/d132-aston-martin-vantage-gt3",
                       "Fitment/tire-pgt-20126lmxd/d132-aston-martin-vantage-gt3",
                       "CarModel/d132/aston-martin-vantage-gt3"],
})

# --------------------------------------------------------- ontology decisions

thing("OntologyDecision/ontology/od-platform-grain", {
    "title": "Chassis-platform grain between CarModel and Product?",
    "question": "Do chassis platforms (several CarModels sharing rim/axle/guide hardware) earn their own identity grain, with fitments re-hung on the platform?",
    "options": [
        "Mint Platform things now — risks a guessed taxonomy: no public source enumerates platforms",
        "Two grains (CarModel + Product), duplicating identical SpecClaim-grounded values per CarModel — chosen; duplication with provenance beats guessed taxonomy",
    ],
    "currentLean": "Two grains; platform deferred",
    "settlingEvidence": "At least 3 CarModels demonstrably share identical rim/axle/guide specs AND a fitment source addresses the family as a unit. First datum: both 30044 cars share tire part 89800 but have different axle spares, and Quick Slicks cut a dedicated 296 size — so shared tire-part does not imply shared wheels (OQ-C2).",
    "status": "open",
})
thing("OntologyDecision/ontology/od-fitment-fanout", {
    "title": "High-fanout parts: per-car Fitments or a fitsSystem shortcut?",
    "question": "For parts that fit effectively every car in a system (e.g. the 20365 double-slider brush), do we mint hundreds of per-car Fitments or a system-scoped compatibility field?",
    "options": [
        "Per-car Fitments only for cars whose official spare tabs list the part — chosen; keeps every claim source-backed",
        "A fitsSystem field on PartType — compact but converts an inference into a stored fact",
    ],
    "currentLean": "Per-car, official-tab-backed; system-wide notes in PartType.notes",
    "settlingEvidence": "Brush/guide Fitment volume becoming unmanageable as the car catalog grows past ~50 CarModels (OQ-C3).",
    "status": "open",
})
thing("OntologyDecision/ontology/od-discontinuation-semantics", {
    "title": "What does disappearance from a source listing mean?",
    "question": "When a product vanishes from carrera-toys.com/carreraslots.com listings, is that a retraction, a status change, or nothing?",
    "options": [
        "Retract the Product — destroys holdings/garage references and overclaims (a source dropping a page is not the product ceasing to exist)",
        "Reviewed status revision to discontinued; never delete — chosen",
    ],
    "status": "resolved",
    "resolution": (
        "Absence from a listing is evidence for review, never an automated write: the update pipeline "
        "runs absence-policy preserve permanently, surfaces vanished listings for human review, and a "
        "maintainer applies status discontinued citing the evidence. Products are never retracted — "
        "personal repos reference them forever (ONTOLOGY-REVIEW anti-inference 5; write contracts)."),
})
thing("OntologyDecision/ontology/od-provenance-depth", {
    "title": "Provenance rung: sourceUrl citations or hash-verified artifacts?",
    "question": "Do catalog claims ground at source-level (sourceUrl + quotedText + observedAt on SpecClaim) or artifact-hash-level (pinned SourceArtifact versions)?",
    "options": [
        "Source-level only — proportional for ~4 stable hand-read web sources (the v1 deliberate deviation)",
        "Artifact-hash-level everywhere — regulatory-scale ceremony for hand-curated claims",
        "Split by writer: hand-curated claims stay source-level; machine-written pipeline claims pin SourceArtifact versions",
    ],
    "status": "resolved",
    "resolution": (
        "Split by writer, adopted 2026-08-31 with the grounding 4.0 component install: the update "
        "pipeline grounds its writes in hash-verified SourceArtifact stream versions (canonical JSONL, "
        "JCS serialization); existing hand-curated SpecClaims keep the source-level rung, which remains "
        "valid historical evidence. Supersedes the v1 'no SourceArtifact ladder' deviation for machine "
        "writers only."),
})

# ------------------------------------------------------------ grounding sources

thing("Source/grounding/carrera/toys-shop", {
    "publisherName": "Carrera Toys GmbH",
    "systemName": "carrera-toys.com storefront (Shopify collections/products JSON; read-only agent access sanctioned by the site's /agents.md)",
    "authorityClass": "manufacturer",
    "canonicalUrl": "https://carrera-toys.com/",
})
thing("Source/grounding/carreraslots/store", {
    "publisherName": "Carrera slot-car US importer storefront (carreraslots.com)",
    "systemName": "carreraslots.com Miva Merchant storefront: sitemap-enumerated product pages at /slot-car/{part}.html (robots.txt allows all; honor the requested 20-second crawl delay)",
    "authorityClass": "commercial-aggregator",
    "canonicalUrl": "https://www.carreraslots.com/",
})

# ------------------------------------------------------------- release set

OPS.append({"operation": "add", "kind": "collection", "type": "set",
            "name": "ontology/release",
            "members": [
                "SemanticContract/ontology/piece-type-shape-v1",
                "SemanticContract/ontology/product-shape-v2",
                "SemanticContract/ontology/car-model-shape-v1",
                "PredicateDeclaration/ontology/fitment-shape-v1",
                "PredicateDeclaration/ontology/product-content-shape-v2",
                "NamingContract/ontology/piece-type-shape-v1",
                "NamingContract/ontology/product-shape-v2",
                "NamingContract/ontology/product-content-shape-v2",
                "NamingContract/ontology/spec-claim-shape-v2",
                "NamingContract/ontology/car-model-shape-v1",
                "NamingContract/ontology/part-type-shape-v1",
                "NamingContract/ontology/fitment-shape-v1",
                "NamingContract/ontology/source-shape-v1",
                "NamingContract/ontology/source-artifact-shape-v1",
            ]})


if __name__ == "__main__":
    out = Path(__file__).parent / "ops-ontology-seed.json"
    out.write_text(json.dumps(OPS, indent=2, ensure_ascii=False) + "\n")
    kinds = {}
    for op in OPS:
        key = op.get("name", "").split("/")[0] if op["kind"] != "collection" else "Set"
        kinds[key] = kinds.get(key, 0) + 1
    print(f"{len(OPS)} ops -> {out.name}")
    for k, v in sorted(kinds.items()):
        print(f"  {k}: {v}")
