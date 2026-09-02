from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.database.postgres import PostgresDatabase


# ============================================================
# LOCAL STORAGE
# ============================================================

CATALOG_FILE = Path(
    "data/catalog.json"
)


# ============================================================
# INITIAL SEED CATALOG
# ============================================================

SEED_PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "BP001",
        "name": "Laptop Backpack Pro",
        "category": "Backpacks",
        "price": 1499.0,
        "currency": "INR",
        "stock": 32,
        "description": (
            "Premium water-resistant backpack for office, "
            "college and travel."
        ),
        "features": [
            "15.6-inch laptop compartment",
            "Water resistant",
            "USB charging port",
            "Padded shoulder straps",
        ],
        "tags": [
            "office",
            "college",
            "travel",
            "laptop",
        ],
        "variants": [
            {
                "variant_id": "BP001-BLK",
                "name": "Black",
                "price": 1499.0,
                "stock": 20,
            },
            {
                "variant_id": "BP001-BLU",
                "name": "Blue",
                "price": 1549.0,
                "stock": 12,
            },
        ],
        "related_products": [
            "LS001",
            "ORG001",
        ],
    },
    {
        "product_id": "LS001",
        "name": "15.6-inch Laptop Sleeve",
        "category": "Laptop Accessories",
        "price": 499.0,
        "currency": "INR",
        "stock": 45,
        "description": (
            "Protective padded sleeve for laptops up to 15.6 inches."
        ),
        "features": [
            "Water resistant",
            "Padded protection",
            "Lightweight",
        ],
        "tags": [
            "laptop",
            "office",
            "travel",
            "accessory",
        ],
        "variants": [
            {
                "variant_id": "LS001-BLK",
                "name": "Black",
                "price": 499.0,
                "stock": 30,
            },
            {
                "variant_id": "LS001-GRY",
                "name": "Grey",
                "price": 549.0,
                "stock": 15,
            },
        ],
        "related_products": [
            "BP001",
        ],
    },
    {
        "product_id": "ORG001",
        "name": "Travel Organizer",
        "category": "Travel Accessories",
        "price": 299.0,
        "currency": "INR",
        "stock": 60,
        "description": (
            "Compact organizer for chargers, cables and travel essentials."
        ),
        "features": [
            "Multiple compartments",
            "Cable storage",
            "Travel friendly",
        ],
        "tags": [
            "travel",
            "office",
            "organizer",
            "accessory",
        ],
        "variants": [
            {
                "variant_id": "ORG001-BLK",
                "name": "Black",
                "price": 299.0,
                "stock": 60,
            },
        ],
        "related_products": [
            "BP001",
            "LS001",
        ],
    },
]


# ============================================================
# STORAGE MODE
# ============================================================

def _use_postgres() -> bool:
    return bool(
        os.getenv(
            "DATABASE_URL"
        )
    )


def _db() -> PostgresDatabase:
    return PostgresDatabase()


# ============================================================
# LOCAL FILE HELPERS
# ============================================================

def _ensure_local_catalog() -> List[Dict[str, Any]]:

    if not CATALOG_FILE.exists():

        CATALOG_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        CATALOG_FILE.write_text(
            json.dumps(
                SEED_PRODUCTS,
                indent=2,
            ),
            encoding="utf-8",
        )

    try:

        data = json.loads(
            CATALOG_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(
            data,
            list,
        ):

            return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        pass

    CATALOG_FILE.write_text(
        json.dumps(
            SEED_PRODUCTS,
            indent=2,
        ),
        encoding="utf-8",
    )

    return deepcopy(
        SEED_PRODUCTS
    )


def _write_local_catalog(
    products: List[Dict[str, Any]],
) -> None:

    CATALOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CATALOG_FILE.write_text(
        json.dumps(
            products,
            indent=2,
        ),
        encoding="utf-8",
    )


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_product(
    product: Dict[str, Any],
) -> Dict[str, Any]:

    normalized = dict(
        product
    )

    normalized["product_id"] = str(
        normalized.get(
            "product_id",
            "",
        )
    )

    normalized["name"] = str(
        normalized.get(
            "name",
            "",
        )
    )

    normalized["category"] = str(
        normalized.get(
            "category",
            "",
        )
    )

    normalized["price"] = float(
        normalized.get(
            "price",
            0,
        )
        or 0
    )

    normalized["stock"] = int(
        normalized.get(
            "stock",
            0,
        )
        or 0
    )

    normalized["currency"] = (
        normalized.get(
            "currency",
            "INR",
        )
        or "INR"
    )

    normalized["description"] = (
        normalized.get(
            "description"
        )
        or ""
    )

    normalized["features"] = (
        normalized.get(
            "features",
            [],
        )
        or []
    )

    normalized["tags"] = (
        normalized.get(
            "tags",
            [],
        )
        or []
    )

    normalized["variants"] = (
        normalized.get(
            "variants",
            [],
        )
        or []
    )

    normalized["related_products"] = (
        normalized.get(
            "related_products",
            [],
        )
        or []
    )

    return normalized


# ============================================================
# SEED POSTGRESQL
# ============================================================

def seed_catalog() -> int:

    if not _use_postgres():
        return 0

    db = _db()

    # Make sure the catalog table exists before querying it.
    db.initialize()

    inserted = 0

    for product in SEED_PRODUCTS:

        existing = db.get_catalog_product(
            product["product_id"]
        )

        if existing:
            continue

        db.upsert_catalog_product(
            product_id=product["product_id"],
            name=product["name"],
            category=product["category"],
            price=product["price"],
            currency=product["currency"],
            stock=product["stock"],
            description=product["description"],
            features=product["features"],
            tags=product["tags"],
            variants=product["variants"],
            related_products=product[
                "related_products"
            ],
        )

        inserted += 1

    return inserted


# ============================================================
# LIST PRODUCTS
# ============================================================

def list_products() -> List[Dict[str, Any]]:

    if not _use_postgres():

        products = _ensure_local_catalog()

        return [
            _normalize_product(
                product
            )
            for product in products
        ]

    db = _db()

    db.initialize()

    products = db.list_catalog_products()

    if not products:

        seed_catalog()

        products = db.list_catalog_products()

    return [
        _normalize_product(
            product
        )
        for product in products
    ]


# ============================================================
# GET PRODUCT
# ============================================================

def get_product(
    product_id: str,
) -> Optional[Dict[str, Any]]:

    product_id = (
        str(product_id)
        .strip()
        .upper()
    )

    if not _use_postgres():

        products = _ensure_local_catalog()

        for product in products:

            if (
                str(
                    product.get(
                        "product_id",
                        "",
                    )
                )
                .strip()
                .upper()
                ==
                product_id
            ):

                return _normalize_product(
                    product
                )

        return None

    db = _db()

    db.initialize()

    product = db.get_catalog_product(
        product_id
    )

    if product:

        return _normalize_product(
            product
        )

    seed_catalog()

    product = db.get_catalog_product(
        product_id
    )

    if not product:
        return None

    return _normalize_product(
        product
    )


# ============================================================
# SEARCH PRODUCTS
# ============================================================

def search_products(
    query: str,
) -> List[Dict[str, Any]]:

    query = (
        str(query or "")
        .strip()
        .lower()
    )

    if not _use_postgres():

        products = _ensure_local_catalog()

        if not query:

            return [
                _normalize_product(
                    product
                )
                for product in products
            ]

        results = []

        for product in products:

            searchable = " ".join(
                [
                    str(
                        product.get(
                            "product_id",
                            "",
                        )
                    ),
                    str(
                        product.get(
                            "name",
                            "",
                        )
                    ),
                    str(
                        product.get(
                            "category",
                            "",
                        )
                    ),
                    str(
                        product.get(
                            "description",
                            "",
                        )
                    ),
                    " ".join(
                        map(
                            str,
                            product.get(
                                "tags",
                                [],
                            ),
                        )
                    ),
                    " ".join(
                        map(
                            str,
                            product.get(
                                "features",
                                [],
                            ),
                        )
                    ),
                ]
            ).lower()

            if query in searchable:

                results.append(
                    _normalize_product(
                        product
                    )
                )

        return results

    db = _db()

    db.initialize()

    products = db.search_catalog_products(
        query
    )

    if (
        not products
        and not db.list_catalog_products()
    ):

        seed_catalog()

        products = db.search_catalog_products(
            query
        )

    return [
        _normalize_product(
            product
        )
        for product in products
    ]


# ============================================================
# CATEGORY
# ============================================================

def list_category(
    category: str,
) -> List[Dict[str, Any]]:

    category = (
        str(category or "")
        .strip()
        .lower()
    )

    if not _use_postgres():

        products = _ensure_local_catalog()

        return [
            _normalize_product(
                product
            )
            for product in products
            if str(
                product.get(
                    "category",
                    "",
                )
            )
            .strip()
            .lower()
            ==
            category
        ]

    db = _db()

    db.initialize()

    products = db.list_catalog_category(
        category
    )

    if (
        not products
        and not db.list_catalog_products()
    ):

        seed_catalog()

        products = db.list_catalog_category(
            category
        )

    return [
        _normalize_product(
            product
        )
        for product in products
    ]


# ============================================================
# RELATED PRODUCTS
# ============================================================

def get_related_products(
    product_id: str,
) -> List[Dict[str, Any]]:

    product = get_product(
        product_id
    )

    if not product:
        return []

    related_ids = (
        product.get(
            "related_products",
            [],
        )
        or []
    )

    related_products = []

    for related_id in related_ids:

        related = get_product(
            related_id
        )

        if related:

            related_products.append(
                related
            )

    return related_products


# ============================================================
# CATALOG SUMMARY
# ============================================================

def catalog_summary() -> Dict[str, Any]:

    products = list_products()

    categories = sorted(
        {
            str(
                product.get(
                    "category",
                    "",
                )
            )
            for product in products
            if product.get(
                "category"
            )
        }
    )

    storage = (
        "postgresql"
        if _use_postgres()
        else "local"
    )

    return {
        "product_count": len(
            products
        ),
        "categories": categories,
        "total_stock": sum(
            int(
                product.get(
                    "stock",
                    0,
                )
                or 0
            )
            for product in products
        ),
        "currency": "INR",
        "storage": storage,
    }

# ============================================================
# CREATE / UPDATE PRODUCT
# ============================================================

def upsert_product(
    product: Dict[str, Any],
) -> Dict[str, Any]:

    normalized = _normalize_product(
        product
    )

    product_id = normalized["product_id"]

    if not product_id:
        raise ValueError(
            "product_id is required."
        )

    if not normalized["name"]:
        raise ValueError(
            "name is required."
        )

    if not normalized["category"]:
        raise ValueError(
            "category is required."
        )

    if normalized["price"] < 0:
        raise ValueError(
            "price cannot be negative."
        )

    if normalized["stock"] < 0:
        raise ValueError(
            "stock cannot be negative."
        )

    if not _use_postgres():

        products = _ensure_local_catalog()

        replaced = False

        updated_products = []

        for existing in products:

            if (
                str(
                    existing.get(
                        "product_id",
                        "",
                    )
                ).strip().upper()
                ==
                product_id.upper()
            ):

                updated_products.append(
                    normalized
                )

                replaced = True

            else:

                updated_products.append(
                    existing
                )

        if not replaced:

            updated_products.append(
                normalized
            )

        _write_local_catalog(
            updated_products
        )

        return _normalize_product(
            normalized
        )

    db = _db()

    db.initialize()

    return _normalize_product(
        db.upsert_catalog_product(
            product_id=product_id,
            name=normalized["name"],
            category=normalized["category"],
            price=normalized["price"],
            currency=normalized["currency"],
            stock=normalized["stock"],
            description=normalized["description"],
            features=normalized["features"],
            tags=normalized["tags"],
            variants=normalized["variants"],
            related_products=normalized[
                "related_products"
            ],
        )
    )


# ============================================================
# UPDATE STOCK
# ============================================================

def update_stock(
    product_id: str,
    stock: int,
) -> Optional[Dict[str, Any]]:

    product = get_product(
        product_id
    )

    if not product:
        return None

    stock = int(stock)

    if stock < 0:
        raise ValueError(
            "stock cannot be negative."
        )

    product["stock"] = stock

    return upsert_product(
        product
    )


# ============================================================
# DELETE PRODUCT
# ============================================================

def delete_product(
    product_id: str,
) -> bool:

    product_id = (
        str(product_id)
        .strip()
        .upper()
    )

    if not product_id:
        return False

    if not _use_postgres():

        products = _ensure_local_catalog()

        updated_products = [
            product
            for product in products
            if str(
                product.get(
                    "product_id",
                    "",
                )
            ).strip().upper()
            != product_id
        ]

        if len(updated_products) == len(products):
            return False

        _write_local_catalog(
            updated_products
        )

        return True

    db = _db()

    db.initialize()

    with db.connect() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM catalog_products
                WHERE product_id = %s
                """,
                (
                    product_id,
                ),
            )

            deleted = (
                cursor.rowcount > 0
            )

        connection.commit()

    return deleted