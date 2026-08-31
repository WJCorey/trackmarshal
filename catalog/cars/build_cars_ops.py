"""Generate WarmHub commit operations for the car layer of slotcars/carrera-catalog.

Per docs/CARS-DESIGN.md build order steps 1-2. Emits chunked ops JSON for
`wh commit submit --file` (same conventions as ../build_ops.py: deterministic
names, idempotent re-submission, pairs as explicit named collections with `--`).

Provenance: every datum below carries its source; research 2026-07-27 (see
SpecClaim sourceUrls). Official Carrera pages publish NO tire dimensions
(OQ-C1 resolved: dimensional grounding must come from vendor charts or
measurement) — CarModel tire fields stay null until then.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent
TODAY = "2026-07-27"

EU = "https://www.carrera-toys.com/en/products/"
US = "https://carrera-revell-toys.com/carrera/product/"

# ------------------------------------------------------------- car models

CAR_MODELS = [
    ("d132/ferrari-296-gt3", {
        "title": "Ferrari 296 GT3",
        "system": "d132", "scale": "1:32", "digital": True, "lights": True,
        "oemTireSparePart": "89800",
        "fitmentBasis": ("Digital/lights/scale from official EU+US product pages of the realizing "
                         "SKU 32001 (see SpecClaims). Tire DIMENSIONS ungrounded: official pages "
                         "publish none; OEM spare tire part 89800 associated via the official "
                         "spare-parts tab."),
        "notes": ("Liveries are Products (32001 'AF Corse, No.21'; spare-part cross-references "
                  "suggest 32000 is another livery of this model — not asserted without a source). "
                  "Axle spare 20091294 shared with 20027761/20027762/20032000/20032001 — "
                  "platform-grain evidence, recorded not modeled (CARS-DESIGN promotion trigger). "
                  "Pacecar/Safetycar function; length 14.8 cm (US page '5.81 in')."),
    }),
    ("d132/aston-martin-vantage-gt3", {
        "title": "Aston Martin Vantage GT3",
        "system": "d132", "scale": "1:32", "digital": True, "lights": True,
        "oemTireSparePart": "89800",
        "fitmentBasis": ("Digital/lights/scale from official EU+US product pages of the realizing "
                         "SKU 32022 (see SpecClaims). Tire DIMENSIONS ungrounded: official pages "
                         "publish none; OEM spare tire part 89800 associated via the official "
                         "spare-parts tab."),
        "notes": ("Livery Product 32022 'Northwest, No.98'. Axle spare 20091087 shared with "
                  "20027631/20027969/20027743/20027783/20027784/20032022/20032023 — a DIFFERENT "
                  "axle group than the 296 GT3 (evidence the two cars are not one platform). "
                  "Pacecar/Safetycar function; length 14.7 cm."),
    }),
]

# ------------------------------------------------------------- part types

PART_TYPES = [
    ("brush/double-2007", {
        "kind": "brush", "title": "Double brush (sliding contact), 2007-generation",
        "vendor": "carrera",
        "specBasis": "Official product page of the 10-pack (Product 20365).",
        "notes": ("The universal contact brush: official page states compatibility with "
                  "DIGITAL 124, DIGITAL 132, EVOLUTION (from 2007) and Exclusiv from 2006 — "
                  "the high-fanout fitment case (CARS-DESIGN OQ-C3): system-wide compatibility "
                  "recorded here; per-car Fitments asserted only for cars whose official "
                  "spare-parts tabs list it."),
    }),
    ("guide/keel-2007", {
        "kind": "guide", "title": "Guide keel, 2007-generation",
        "vendor": "carrera",
        "specBasis": "Official product page of spare kit 20366 ('2 guide keels incl. 8 double brushes, from 2007').",
        "notes": None,
    }),
    ("decoder/d132-26732", {
        "kind": "decoder", "title": "Digital 132 decoder (26732)",
        "vendor": "carrera",
        "specBasis": "Official product page 20026732; listed as the decoder spare on both 32001 and 32022 official spare-parts tabs.",
        "notes": ("Current-generation D132 car decoder / Evolution retrofit. Other decoders exist "
                  "for specific cars (20026750 for 20030943; 20026751 for 20031054/55) — not "
                  "modeled until a question needs them."),
    }),
    ("tire/oem-89800", {
        "kind": "tire", "title": "Carrera OEM tire set 89800 (GT3-class D132)",
        "vendor": "carrera",
        # dimensions null — no official source publishes them (OQ-C1)
        "compound": "rubber",
        "specBasis": ("Identity from the spare pack (Product 89800) — the only official handle. "
                      "NO published dimensions anywhere official; compound rubber per Carrera's "
                      "standard OEM tires (US 32001 page: 'Double contact brushes', tires unspecified)."),
        "notes": ("Pack title enumerates cars 27438...30662 but NOT 32001/32022; the official "
                  "association to our two cars is each car's spare-parts tab. Recorded as a "
                  "productive tension, not resolved by guessing."),
    }),
]

# ---------------------------------------------- third-party tires (2026-07-27 research)

SCC = "https://slotcarcorner.com/products/"
QS_CHART_NOTE = ('Quick Slicks Fitment Summary v4.15, dated 07/14/2026, distributed as Google Drive '
                 'PDFs via retail partner Slot Car Corner (quickslicks.com DNS-dead 2026-07-27): '
                 'by-brand https://drive.google.com/file/d/19VP8NpUA56tI9QnPyjCwA3qjhfbhj5EI/view')

VENDOR_TIRES = [
    ("tire/qs-ca02", {
        "kind": "tire", "title": "Quick Slicks CA02 (1:32 Carrera DTM-class wheels)",
        "vendor": "quick-slicks", "compound": "silicone",
        "outerDiaMm": 21.9, "widthMm": 9.65,
        "specBasis": "Retail-partner product page (CA02XF variant); QS publishes OD + contact-patch width only, never ID.",
        "notes": ("Suffix variants (XF = X-Firm etc.) are compound firmness on one size; the fitment "
                  "chart lists base numbers. 'Designed specifically for 1:32 Carrera DTM stock wheels.'"),
    }),
    ("tire/qs-ca03", {
        "kind": "tire", "title": "Quick Slicks CA03 (1:32 Carrera DTM-class wheels)",
        "vendor": "quick-slicks", "compound": "silicone",
        "outerDiaMm": 22.4, "widthMm": 9.65,
        "specBasis": "Retail-partner product page (CA03XF variant).",
        "notes": None,
    }),
    ("tire/qs-ca107", {
        "kind": "tire", "title": "Quick Slicks CA107 (1:32 Carrera Ferrari 296 rear wheels)",
        "vendor": "quick-slicks", "compound": "silicone",
        "outerDiaMm": 22.6, "widthMm": 9.65,
        "specBasis": "Retail-partner product page (CA107XF variant).",
        "notes": ("'Designed specifically for the 1:32 Carrera Ferrari 296 rear wheels' — QS cut a "
                  "dedicated size rather than mapping to the DTM tires (CA02/03), which is evidence "
                  "the 296 and the Vantage GT3 do NOT share rear wheel sizes."),
    }),
    ("tire/pgt-20115lmxd", {
        "kind": "tire", "title": "Paul Gage PGT-20115LMXD (urethane, 20×11, 5mm rib, XD)",
        "vendor": "paul-gage", "compound": "urethane",
        "outerDiaMm": 20.0, "innerDiaMm": 13.0, "widthMm": 11.0,
        "specBasis": ("Dealer Slot Car-Union full dims (OD 20 / ID 13 / W 11 / rib 5 / groove 1.5 mm). "
                      "CONFLICT preserved in SpecClaims: Slot Car Corner filter tags say 12 mm width "
                      "vs the size-code's 11 mm."),
        "notes": ("Size code decode (Home Racing World): OD(2)+width(2)+rib(1); LM = larger center "
                  "opening / low profile, XD = deeper groove for tall center-rib wheels. PGT = Shore 40 "
                  "firm (XPG = Shore 20 soft variant of the same size). PG tuning tires run deliberately "
                  "smaller than stock."),
    }),
    ("tire/pgt-20125lm", {
        "kind": "tire", "title": "Paul Gage PGT-20125LM (urethane, 20×12, 5mm rib)",
        "vendor": "paul-gage", "compound": "urethane",
        "outerDiaMm": 20.0, "widthMm": 12.0,
        "specBasis": "Dimensions from the size code (HRW decode); no dealer publishes full dims incl. ID.",
        "notes": ("Paul Gage's own eBay title pairs this size with the SCALEXTRIC Aston Martin GT3; "
                  "Slot Car Corner tags it for the CARRERA Vantage GT3 — possibly a cross-brand "
                  "artifact. See the conflicting Fitment records."),
    }),
    ("tire/pgt-20126lmxd", {
        "kind": "tire", "title": "Paul Gage PGT-20126LMXD (urethane, 20×12, 6mm rib, XD)",
        "vendor": "paul-gage", "compound": "urethane",
        "outerDiaMm": 20.0, "widthMm": 12.0,
        "specBasis": "Dimensions from the size code; no dealer publishes full dims.",
        "notes": "6 mm rib + XD needs a physically different wheel than 20125LM (5 mm rib) — at most one of the two conflicting Carrera-Vantage claims is right.",
    }),
]

VENDOR_FITMENTS = [
    ("tire/qs-ca107", "d132/ferrari-296-gt3", "rear", "vendor-chart", False,
     'QS chart v4.15 row: "Carrera | Ferrari 296 | CA107" (name match, no SKU; chart says "Ferrari 296" '
     'without GT3 — Carrera\'s only 1:32 296 is the GT3, and the product page says designed for its rear wheels). '
     + QS_CHART_NOTE),
    ("tire/qs-ca02", "d132/aston-martin-vantage-gt3", "rear", "vendor-chart", False,
     'QS chart v4.15 row: "Carrera | Aston Martin Vantage GT3 | CA02, CA03" (exact name match, no SKU). ' + QS_CHART_NOTE),
    ("tire/qs-ca03", "d132/aston-martin-vantage-gt3", "rear", "vendor-chart", False,
     'QS chart v4.15 row: "Carrera | Aston Martin Vantage GT3 | CA02, CA03". ' + QS_CHART_NOTE),
    ("tire/pgt-20115lmxd", "d132/ferrari-296-gt3", "rear", "vendor-chart", False,
     "Paul Gage's OWN eBay listing 157857297473: '…PGT-20115LMXD fits Carrera Ferrari F296' "
     "(via PicClick mirror; the vendor's first-party listing is the strongest vendor-chart-class evidence). "
     "Corroborated by Slot Car Corner's Ferrari 296 tag."),
    ("tire/pgt-20125lm", "d132/aston-martin-vantage-gt3", "rear", "vendor-chart", False,
     "DISPUTED, dealer-level only: Slot Car Corner tags this for the Carrera Vantage GT3, but Paul Gage's "
     "own listing pairs 20125LM with the Scalextric Aston — possible cross-brand artifact. PG's own store "
     "has NO Carrera Aston listing. Conflicts with the 20126LMXD claim (different rib widths — at most one is right). "
     "Owner mounting adjudicates."),
    ("tire/pgt-20126lmxd", "d132/aston-martin-vantage-gt3", "rear", "vendor-chart", False,
     "DISPUTED, dealer-level only: Amerikids listing title 'PGT-20126LMXD For Carrera Aston Martin Vantage' "
     "(page body unfetchable; does not specify GT3 vs older V12 Vantage). Conflicts with the 20125LM claim. "
     "Owner mounting adjudicates."),
]

VENDOR_CLAIMS = [
    ("PartType/tire/qs-ca02", "scc-product-page", {
        "sourceUrl": SCC + "ca02xf-quick-slicks", "sourceKind": "retailer-tech-page",
        "tireOuterDiaMm": 21.9, "tireWidthMm": 9.65, "position": "rear",
        "valuesNote": '"O.D.: .862\\" (21.90mm)"; "Contact Patch Width: .380\\" (9.65mm)"; "designed specifically for 1:32 Carrera DTM stock wheels".',
    }),
    ("PartType/tire/qs-ca03", "scc-product-page", {
        "sourceUrl": SCC + "ca03xf-quick-slicks", "sourceKind": "retailer-tech-page",
        "tireOuterDiaMm": 22.4, "tireWidthMm": 9.65, "position": "rear",
        "valuesNote": '"O.D.: .882\\" (22.40mm)"; width ".380\\" (9.65mm)".',
    }),
    ("PartType/tire/qs-ca107", "scc-product-page", {
        "sourceUrl": SCC + "ca107xf-quick-slicks-silicone-tires-x-firm", "sourceKind": "retailer-tech-page",
        "tireOuterDiaMm": 22.6, "tireWidthMm": 9.65, "position": "rear",
        "valuesNote": '"Outer Diameter (O.D.): .889\\" (22.60mm)"; "Width (Contact Patch): .380\\" (9.65mm)"; "designed specifically for the 1:32 Carrera Ferrari 296 rear wheels".',
    }),
    ("PartType/tire/pgt-20115lmxd", "slotcar-union-page", {
        "sourceUrl": "https://www.slotcar-union.com/en/tires/21402-paul-gage-pgt-20115lmxd-urethane-tires-20x11x5mm-2-pcs.html",
        "sourceKind": "retailer-tech-page",
        "tireOuterDiaMm": 20.0, "tireInnerDiaMm": 13.0, "tireWidthMm": 11.0, "position": "rear",
        "valuesNote": "OD 20 mm, ID 13 mm, width 11 mm, center-rib width 5 mm, rib groove height 1.5 mm — the only source publishing the ID.",
    }),
    ("PartType/tire/pgt-20115lmxd", "scc-filter-tags", {
        "sourceUrl": SCC + "pgt-20115lmxd-paul-gage-urethane-tires-firm",
        "sourceKind": "retailer-tech-page",
        "tireOuterDiaMm": 20.0, "tireWidthMm": 12.0, "position": "rear",
        "valuesNote": "SCC filter tags: 20mm(OD), 12mm(W), 5mm — the 12 mm width CONFLICTS with the size-code/Slot Car-Union 11 mm. Preserved unresolved.",
    }),
]

# --------------------------------------------------------------- products

PRODUCTS = [
    ("32001", {
        "partNumber": "32001", "skuAliases": ["20032001"],
        "title": 'Ferrari 296 GT3 "AF Corse, No.21" — Digital 132 car',
        "productClass": "car", "status": "current",
        "notes": ("Working front/rear/brake lights; pacecar+safetycar function; official Ferrari "
                  "license. Also sold inside starter set 30044. Official spare parts: brushes "
                  "20365, keels+brushes 20366, decoder 26732, tires 89800, motor E200 20089200, "
                  "bits 20091262, axles 20091294."),
    }),
    ("32022", {
        "partNumber": "32022", "skuAliases": ["20032022"],
        "title": 'Aston Martin Vantage GT3 "Northwest, No.98" — Digital 132 car',
        "productClass": "car", "status": "current",
        "notes": ("Working front/rear/brake lights; pacecar+safetycar function; official "
                  "Aston Martin license. Also sold inside starter set 30044. Official spare "
                  "parts: brushes 20365, keels+brushes 20366, decoder 26732, tires 89800, "
                  "motor E200 20089200, bits 20091280, axles 20091087."),
    }),
    ("20365", {
        "partNumber": "20365", "skuAliases": ["20020365"],
        "title": "Double Brushes, 10 pcs, from 2007",
        "productClass": "spare-part", "status": "current",
        "notes": "Fits DIGITAL 124, DIGITAL 132, EVOLUTION (from 2007), Exclusiv from 2006 (official page).",
    }),
    ("20366", {
        "partNumber": "20366", "skuAliases": ["20020366"],
        "title": "2 guide keels incl. 8 double brushes, from 2007",
        "productClass": "spare-part", "status": "current", "notes": None,
    }),
    ("26732", {
        "partNumber": "26732", "skuAliases": ["20026732"],
        "title": "Digital decoder (D132 cars / Evolution retrofit)",
        "productClass": "spare-part", "status": "current", "notes": None,
    }),
    ("89800", {
        "partNumber": "89800", "skuAliases": ["20089800"],
        "title": "Tires for 27438...30662 (GT3-class D132 tire set)",
        "productClass": "spare-part", "status": "current",
        "notes": ("UNRESOLVED CONTENTS: tire count per pack not published. Title enumerates "
                  "specific car numbers; ALSO the official spare-tire part for 32001/32022 via "
                  "their spare-parts tabs. €4.99 (EU, 2026-07)."),
    }),
]

# product -> [(contentKind, slug, title, qty, verified, note)]
PRODUCT_CONTENTS = {
    "32001": [("carModel", "d132/ferrari-296-gt3", "Ferrari 296 GT3", 1, True, None)],
    "32022": [("carModel", "d132/aston-martin-vantage-gt3", "Aston Martin Vantage GT3", 1, True, None)],
    "20365": [("partType", "brush/double-2007", "Double brush (sliding contact), 2007-generation", 10, True, None)],
    "20366": [("partType", "guide/keel-2007", "Guide keel, 2007-generation", 2, True, None),
              ("partType", "brush/double-2007", "Double brush (sliding contact), 2007-generation", 8, True, None)],
    "26732": [("partType", "decoder/d132-26732", "Digital 132 decoder (26732)", 1, True, None)],
    # 89800: contents unresolved (count unknown) — explicitly NO ProductContent
    # 30044 (existing product): gains its two cars — official productContents JSON on the US set page
    "30044": [("carModel", "d132/ferrari-296-gt3", "Ferrari 296 GT3", 1, True, None),
              ("carModel", "d132/aston-martin-vantage-gt3", "Aston Martin Vantage GT3", 1, True, None)],
}

# --------------------------------------------------------------- fitments
# (partTypeSlug, carModelSlug, position, basis, verified, notes)

FITMENTS = [
    ("brush/double-2007", "d132/ferrari-296-gt3", "n/a", "official-listing", False,
     "Listed on the official 32001 spare-parts tab (carrera-toys.com, 2026-07-27)."),
    ("brush/double-2007", "d132/aston-martin-vantage-gt3", "n/a", "official-listing", False,
     "Listed on the official 32022 spare-parts tab."),
    ("guide/keel-2007", "d132/ferrari-296-gt3", "n/a", "official-listing", False,
     "Spare kit 20366 on the official 32001 spare-parts tab."),
    ("guide/keel-2007", "d132/aston-martin-vantage-gt3", "n/a", "official-listing", False,
     "Spare kit 20366 on the official 32022 spare-parts tab."),
    ("decoder/d132-26732", "d132/ferrari-296-gt3", "n/a", "official-listing", False,
     "Decoder 26732 on the official 32001 spare-parts tab."),
    ("decoder/d132-26732", "d132/aston-martin-vantage-gt3", "n/a", "official-listing", False,
     "Decoder 26732 on the official 32022 spare-parts tab."),
    ("tire/oem-89800", "d132/ferrari-296-gt3", "both", "official-listing", False,
     "Tire part 89800 on the official 32001 spare-parts tab. Caveat: the part's own title "
     "enumerates other car numbers, not 32001 — tab association is the official link."),
    ("tire/oem-89800", "d132/aston-martin-vantage-gt3", "both", "official-listing", False,
     "Tire part 89800 on the official 32022 spare-parts tab. Same title-enumeration caveat."),
]

# ------------------------------------------------------------ spec claims
# (subject wref-path, source-slug, data)

SPEC_CLAIMS = [
    ("CarModel/d132/ferrari-296-gt3", "official-eu-page", {
        "sourceUrl": EU + "20032001-ferrari-296-gt3-af-corse-no-21",
        "sourceKind": "official-product-page",
        "valuesNote": ('DIGITAL 132 category; "Front, rear, and brake lights"; scale 1:32; spare-parts '
                       'tab: brushes 20020365, keels 20020366, decoder 20026732, tires 20089800, '
                       'axles 20091294, motor E200 20089200. No tire dimensions published.'),
    }),
    ("CarModel/d132/ferrari-296-gt3", "official-us-page", {
        "sourceUrl": US + "20032001-ferrari-296-gt3-af-corse-no-21",
        "sourceKind": "official-product-page",
        "valuesNote": ('"Carrera Digital 132 1:32 scale digital slot car"; "Working front and rear '
                       'lights"; "Light function 1 = Front and rear/brake light"; "Vehicle function = '
                       'Pacecar and Safetycar function"; length 5.81 in; "Double contact brushes for '
                       'maximum track contact". No tire dimensions published.'),
    }),
    ("CarModel/d132/aston-martin-vantage-gt3", "official-eu-page", {
        "sourceUrl": EU + "20032022-aston-martin-vantage-gt3-northwest-no-98",
        "sourceKind": "official-product-page",
        "valuesNote": ('DIGITAL 132 category; "Front, rear, and brake lights"; scale 1:32; spare-parts '
                       'tab: brushes 20020365, keels 20020366, decoder 20026732, tires 20089800, '
                       'axles 20091087. No tire dimensions published.'),
    }),
    ("CarModel/d132/aston-martin-vantage-gt3", "official-us-page", {
        "sourceUrl": US + "20032022-aston-martin-vantage-gt3-northwest-no-98",
        "sourceKind": "official-product-page",
        "valuesNote": ('"Carrera Digital 132 1:32 scale digital slot car"; "Working front and rear '
                       'lights"; "Vehicle function = Pacecar and Safetycar function"; length 14.7 cm. '
                       'No tire dimensions published.'),
    }),
    ("PartType/brush/double-2007", "official-eu-page", {
        "sourceUrl": EU + "20020365-double-brushes-10-pcs-from-2007",
        "sourceKind": "official-product-page",
        "valuesNote": ('"Double Brushes, 10 pcs, from 2007" — "the contact point between slot car and '
                       'track"; compatible with "DIGITAL 124, DIGITAL 132, EVOLUTION (from 2007)" and '
                       'Exclusiv vehicles from 2006.'),
    }),
    ("Product/30044", "official-us-set-page", {
        "sourceUrl": US + "20030044-24h-speed",
        "sourceKind": "official-product-page",
        "valuesNote": ('Set productContents JSON lists SKU 20032001 (Ferrari 296 GT3 "AF Corse, No.21") '
                       'and SKU 20032022 (Aston-Martin Vantage GT3 "Northwest, No.98") — official '
                       'confirmation the set cars ARE retail 32001/32022. "Car scale: 1:32", '
                       '"Track scale: 1:24", "Track length: 26.25-ft.", "Race up to 6 cars at once".'),
    }),
]


def flat(slug):
    return slug.replace("/", "-")


def build():
    ops_things, ops_rel, ops_claims = [], [], []

    for slug, data in CAR_MODELS:
        d = {k: v for k, v in data.items() if v is not None}
        ops_things.append({"operation": "add", "kind": "thing", "name": f"CarModel/{slug}", "data": d})
    for slug, data in PART_TYPES:
        d = {k: v for k, v in data.items() if v is not None}
        ops_things.append({"operation": "add", "kind": "thing", "name": f"PartType/{slug}", "data": d})
    for part, data in PRODUCTS:
        d = {k: v for k, v in data.items() if v is not None}
        ops_things.append({"operation": "add", "kind": "thing", "name": f"Product/{part}", "data": d})

    kind_prefix = {"carModel": "CarModel", "partType": "PartType", "pieceType": "PieceType"}
    for part, contents in PRODUCT_CONTENTS.items():
        for ckind, slug, title, qty, verified, note in contents:
            pair = f"{part}--{flat(slug)}"
            ops_rel.append({"operation": "add", "kind": "collection", "type": "pair",
                            "name": pair, "members": [f"Product/{part}", f"{kind_prefix[ckind]}/{slug}"]})
            data = {"quantity": qty, "partNumber": part, "verified": verified,
                    "contentKind": ckind, "contentSlug": slug, "contentTitle": title}
            if note:
                data["notes"] = note
            ops_rel.append({"operation": "add", "kind": "assertion",
                            "name": f"ProductContent/{part}/{flat(slug)}", "about": f"Pair/{pair}",
                            "data": data})

    part_titles = {s: d["title"] for s, d in PART_TYPES}
    car_titles = {s: d["title"] for s, d in CAR_MODELS}
    for pslug, cslug, position, basis, verified, notes in FITMENTS:
        pair = f"{flat(pslug)}--{flat(cslug)}"
        ops_rel.append({"operation": "add", "kind": "collection", "type": "pair",
                        "name": pair, "members": [f"PartType/{pslug}", f"CarModel/{cslug}"]})
        ops_rel.append({"operation": "add", "kind": "assertion",
                        "name": f"Fitment/{flat(pslug)}/{flat(cslug)}", "about": f"Pair/{pair}",
                        "data": {"position": position, "basis": basis, "verified": verified,
                                 "partTypeSlug": pslug, "carModelSlug": cslug,
                                 "partTitle": part_titles[pslug], "carTitle": car_titles[cslug],
                                 "notes": notes}})

    for subject, source, fields in SPEC_CLAIMS:
        data = dict(fields)
        data["observedAt"] = TODAY
        data["subjectSlug"] = subject
        ops_claims.append({"operation": "add", "kind": "assertion",
                           "name": f"SpecClaim/{flat(subject.split('/', 1)[1])}/{source}",
                           "about": subject, "data": data})

    ops_vendor = []
    for slug, data in VENDOR_TIRES:
        d = {k: v for k, v in data.items() if v is not None}
        ops_vendor.append({"operation": "add", "kind": "thing", "name": f"PartType/{slug}", "data": d})
    vendor_titles = {s: d["title"] for s, d in VENDOR_TIRES}
    for pslug, cslug, position, basis, verified, notes in VENDOR_FITMENTS:
        pair = f"{flat(pslug)}--{flat(cslug)}"
        ops_vendor.append({"operation": "add", "kind": "collection", "type": "pair",
                           "name": pair, "members": [f"PartType/{pslug}", f"CarModel/{cslug}"]})
        ops_vendor.append({"operation": "add", "kind": "assertion",
                           "name": f"Fitment/{flat(pslug)}/{flat(cslug)}", "about": f"Pair/{pair}",
                           "data": {"position": position, "basis": basis, "verified": verified,
                                    "partTypeSlug": pslug, "carModelSlug": cslug,
                                    "partTitle": vendor_titles[pslug], "carTitle": car_titles[cslug],
                                    "notes": notes}})
    for subject, source, fields in VENDOR_CLAIMS:
        data = dict(fields)
        data["observedAt"] = TODAY
        data["subjectSlug"] = subject
        ops_vendor.append({"operation": "add", "kind": "assertion",
                           "name": f"SpecClaim/{flat(subject.split('/', 1)[1])}/{source}",
                           "about": subject, "data": data})

    chunks = [("cars-ops-1-things.json", ops_things),
              ("cars-ops-2-relations.json", ops_rel),
              ("cars-ops-3-claims.json", ops_claims),
              ("cars-ops-4-vendor-tires.json", ops_vendor)]
    for fname, ops in chunks:
        (OUT / fname).write_text(json.dumps(ops, indent=1))  # wh commit submit --file wants a bare array
        print(fname, len(ops), "ops")


if __name__ == "__main__":
    build()
