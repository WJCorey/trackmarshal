"""Provision the ProductListing shape + its ontology contracts on the catalog.

Post-approval step for the carrera-catalog-pipeline SPEC (approved by Corey,
2026-09-01). Adds the grounding-layer ProductListing shape, its NamingContract
and SemanticContract, and revises Set/ontology/release to include them (16
members). Mushroom never creates shapes — this manual, reviewed commit is the
SPEC's "Target Shape prerequisite".
"""

import json
from pathlib import Path

DESCRIPTION = (
    "Grounding-layer projection of one carrera-toys.com storefront listing, keyed by the "
    "storefront's article SKU (name segment lowercased; sku field verbatim). Source-faithful "
    "claims from Source/grounding/carrera/toys-shop; written exclusively by the "
    "carrera-catalog-pipeline (github.com/WJCorey/carrera-catalog-pipeline) under managed scope "
    "ProductListing/grounding/carrera/toys-shop/** with absence policy preserve. partNumber5 is "
    "identity EVIDENCE for the curated Product/{p5} layer, never an identity claim here. A "
    "listing's disappearance is review evidence for a human discontinuation decision, never a "
    "deletion (OntologyDecision/ontology/od-discontinuation-semantics). Prices are verbatim EUR "
    "strings — no normalization."
)

OPS = [
    {"operation": "add", "kind": "shape", "name": "ProductListing", "data": {
        "description": DESCRIPTION,
        "fields": {
            "sku": {"type": "string", "description": "Storefront article SKU, verbatim (mirrors the name segment, which lowercases it)"},
            "productId": {"type": "number", "description": "Shopify product id, verbatim"},
            "handle": {"type": "string", "description": "Storefront product handle"},
            "title": {"type": "string", "description": "Storefront title, verbatim"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Storefront tags, sorted (order is presentation, not semantics)"},
            "collections": {"type": "array", "items": {"type": "string"}, "description": "Scoped collection handles this product appeared in, sorted"},
            "priceEur": {"type": "string", "description": "Verbatim sale price, EUR string (e.g. 18.99)"},
            "compareAtPriceEur": {"type": "string?", "description": "Verbatim list price when the storefront publishes one"},
            "available": {"type": "boolean", "description": "Storefront availability flag as published"},
            "publishedAt": {"type": "string?", "description": "Storefront published_at when present"},
            "partNumber5": {"type": "string?", "description": "Derived: 200 prefix stripped from an 8-digit SKU — join evidence to the curated Product/{p5}, not an identity"},
            "url": {"type": "string", "description": "Derived product page URL"},
        },
    }},
    {"operation": "add", "kind": "assertion",
     "name": "NamingContract/ontology/product-listing-shape-v1", "about": "ProductListing",
     "data": {
        "nameTemplate": "ProductListing/grounding/carrera/toys-shop/{sku-lowercased}",
        "segmentSemantics": [
            "grounding — the epistemic layer segment; scopes the pipeline's write token and managed scope",
            "carrera/toys-shop — the owning Source (Source/grounding/carrera/toys-shop)",
            "sku-lowercased — the storefront's article SKU, lowercased for the name (verbatim in data.sku); alphabet ^[0-9]{5,10}[A-Z]?$ observed live 2026-08-31",
        ],
        "exampleNames": [
            "ProductListing/grounding/carrera/toys-shop/20020509",
            "ProductListing/grounding/carrera/toys-shop/29920402b",
        ],
        "globs": ["ProductListing/grounding/carrera/toys-shop/**", "*/grounding/**"],
        "identityStabilityTest": "Price, availability, title, tag, and collection changes revise the record; the SKU is the storefront's stable article key and survives them. A delisted product keeps its name forever (preserve).",
    }},
    {"operation": "add", "kind": "assertion",
     "name": "SemanticContract/ontology/product-listing-shape-v1", "about": "ProductListing",
     "data": {
        "definition": "The source-faithful projection of one carrera-toys.com storefront product listing — what the official storefront currently publishes about one article, in its own vocabulary.",
        "identityTest": "Same storefront article SKU (case-insensitive). One Shopify product = one listing; multi-variant products are outside the reviewed grain and stop the pipeline.",
        "examples": ["ProductListing/grounding/carrera/toys-shop/20020509 (Standard Straight 4-pack listing)"],
        "counterexamples": [
            "The curated Product/20509 (adjudicated commerce identity — a listing is evidence about it, not it)",
            "A carreraslots.com listing (different Source, different stream — milestone 2)",
        ],
        "lifecycleNotes": "Revisions track the storefront. Disappearance from the storefront never retracts the record (absence policy preserve); it becomes review evidence for a curated-layer status change.",
        "lifecycleStatus": "approved",
    }},
    {"operation": "revise", "kind": "collection", "type": "set", "name": "Set/ontology/release",
     "members": [
        "SemanticContract/ontology/piece-type-shape-v1",
        "SemanticContract/ontology/product-shape-v2",
        "SemanticContract/ontology/car-model-shape-v1",
        "SemanticContract/ontology/product-listing-shape-v1",
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
        "NamingContract/ontology/product-listing-shape-v1",
     ]},
]

if __name__ == "__main__":
    out = Path(__file__).parent / "ops-product-listing.json"
    out.write_text(json.dumps(OPS, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(OPS)} ops -> {out.name}")
