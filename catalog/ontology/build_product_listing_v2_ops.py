"""ProductListing v2: widen for the carreraslots.com sitemap stream (m2).

Approved direction 2026-09-01 (Corey: proceed with the remaining roadmap).
The carreraslots.com stream publishes only page presence + part number (its
sitemap), so stream-specific fields become optional: only `sku` and `url` are
required across streams. Loosening required->optional is legacy-safe for the
1,463 existing toys-shop records. Contracts re-issued version-bound (v2);
Set/ontology/release revised to v3.
"""

import json
from pathlib import Path

DESCRIPTION = (
    "Grounding-layer projection of one storefront listing for the Carrera 1:24/1:32 track "
    "system, keyed by the storefront's own article key (name segment lowercased; sku field "
    "verbatim). One stream per Source under ProductListing/grounding/{authority}/{system}/: "
    "carrera/toys-shop (official Shopify shop: full listing fields) and carreraslots/store "
    "(US importer: sitemap presence only — sku and url; absent fields mean 'not published in "
    "this stream', never zero). Written exclusively by the carrera-catalog-pipeline "
    "(github.com/WJCorey/carrera-catalog-pipeline) under managed scope "
    "ProductListing/grounding/** with absence policy preserve. partNumber5 is identity "
    "EVIDENCE for the curated Product/{p5} layer, never an identity claim here. A listing's "
    "disappearance is review evidence for a human discontinuation decision, never a deletion "
    "(OntologyDecision/ontology/od-discontinuation-semantics). Prices are verbatim source "
    "strings — no normalization."
)

FIELDS = {
    "sku": {"type": "string", "description": "The storefront's article key, verbatim (mirrors the name segment, which lowercases it). carrera-toys: 8-digit SKU; carreraslots: the /slot-car/{part}.html part number"},
    "url": {"type": "string", "description": "Product page URL (derived for carrera-toys; verbatim sitemap loc for carreraslots)"},
    "productId": {"type": "number?", "description": "Shopify product id, verbatim (carrera-toys stream)"},
    "handle": {"type": "string?", "description": "Storefront product handle (carrera-toys stream)"},
    "title": {"type": "string?", "description": "Storefront title, verbatim (carrera-toys stream)"},
    "tags": {"type": "array?", "items": {"type": "string"}, "description": "Storefront tags, sorted (order is presentation, not semantics)"},
    "collections": {"type": "array?", "items": {"type": "string"}, "description": "Scoped collection handles this product appeared in, sorted (carrera-toys stream)"},
    "priceEur": {"type": "string?", "description": "Verbatim sale price, EUR string (carrera-toys stream)"},
    "compareAtPriceEur": {"type": "string?", "description": "Verbatim list price when the storefront publishes one"},
    "available": {"type": "boolean?", "description": "Storefront availability flag as published (carrera-toys stream)"},
    "publishedAt": {"type": "string?", "description": "Storefront published_at when present"},
    "partNumber5": {"type": "string?", "description": "Derived: 200 prefix stripped from an 8-digit SKU — join evidence to the curated Product/{p5}, not an identity"},
}

RELEASE_MEMBERS = [
    "SemanticContract/ontology/piece-type-shape-v1",
    "SemanticContract/ontology/product-shape-v2",
    "SemanticContract/ontology/car-model-shape-v1",
    "SemanticContract/ontology/product-listing-shape-v2",
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
    "NamingContract/ontology/product-listing-shape-v2",
]

OPS = [
    {"operation": "revise", "kind": "shape", "name": "ProductListing",
     "data": {"description": DESCRIPTION, "fields": FIELDS}},
    {"operation": "add", "kind": "assertion",
     "name": "NamingContract/ontology/product-listing-shape-v2", "about": "ProductListing",
     "data": {
        "nameTemplate": "ProductListing/grounding/{authority}/{system}/{key-lowercased}",
        "segmentSemantics": [
            "grounding — the epistemic layer segment; scopes the pipeline's write token and managed scope (ProductListing/grounding/**)",
            "{authority}/{system} — the owning Source (Source/grounding/{authority}/{system}): carrera/toys-shop, carreraslots/store",
            "key-lowercased — the storefront's own article key, lowercased for the name (verbatim in data.sku)",
        ],
        "exampleNames": [
            "ProductListing/grounding/carrera/toys-shop/20020509",
            "ProductListing/grounding/carrera/toys-shop/29920402b",
            "ProductListing/grounding/carreraslots/store/20509",
        ],
        "globs": ["ProductListing/grounding/**", "ProductListing/grounding/carrera/toys-shop/**", "ProductListing/grounding/carreraslots/store/**"],
        "identityStabilityTest": "Price, availability, title, and page-content changes revise the record; each storefront's article key survives them. A delisted product keeps its name forever (preserve). The same physical product in two storefronts is two listings — cross-store identity belongs to the curated Product layer.",
    }},
    {"operation": "add", "kind": "assertion",
     "name": "SemanticContract/ontology/product-listing-shape-v2", "about": "ProductListing",
     "data": {
        "definition": "The source-faithful projection of one storefront listing for a Carrera track-system article — what that storefront currently publishes about it, in its own vocabulary. Streams differ in richness: the official shop publishes full listing fields; the US importer stream records sitemap presence only.",
        "identityTest": "Same storefront (Source) and same storefront article key, case-insensitive. One listing per store — never merged across stores (that resolution belongs to the curated Product layer via partNumber5 evidence).",
        "examples": [
            "ProductListing/grounding/carrera/toys-shop/20020509 (full listing)",
            "ProductListing/grounding/carreraslots/store/20509 (sitemap presence)",
        ],
        "counterexamples": [
            "The curated Product/20509 (adjudicated commerce identity — listings are evidence about it)",
            "A single merged cross-store record (identity failure: two sources, two claims)",
        ],
        "lifecycleNotes": "Revisions track each storefront. Disappearance never retracts (absence policy preserve); it becomes review evidence for a curated-layer status change. Absent optional fields mean the stream does not publish them — never zero, never unknown-to-the-world.",
        "lifecycleStatus": "approved",
    }},
    {"operation": "revise", "kind": "collection", "type": "set", "name": "Set/ontology/release",
     "members": RELEASE_MEMBERS},
]

if __name__ == "__main__":
    out = Path(__file__).parent / "ops-product-listing-v2.json"
    out.write_text(json.dumps(OPS, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(OPS)} ops -> {out.name}")
