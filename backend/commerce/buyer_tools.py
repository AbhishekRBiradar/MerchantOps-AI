from __future__ import annotations

from typing import Any, Dict, List

from backend.commerce.catalog import (
    get_product,
    get_related_products,
    list_products,
    search_products,
)


# ============================================================
# BUYER CATALOG TOOLS
# ============================================================

def search_catalog(
    query: str,
    max_price: float | None = None,
    category: str | None = None,
    in_stock_only: bool = True,
) -> Dict[str, Any]:

    products = search_products(
        query
    )

    results: List[
        Dict[str, Any]
    ] = []

    for product in products:

        price = float(
            product.get(
                "price",
                0,
            )
            or 0
        )

        stock = int(
            product.get(
                "stock",
                0,
            )
            or 0
        )

        if (
            max_price is not None
            and price > float(max_price)
        ):
            continue

        if category:

            if (
                str(
                    product.get(
                        "category",
                        "",
                    )
                )
                .strip()
                .lower()
                !=
                str(category)
                .strip()
                .lower()
            ):
                continue

        if (
            in_stock_only
            and stock <= 0
        ):
            continue

        results.append(
            product
        )

    return {
        "query": query,
        "count": len(results),
        "products": results,
    }


def get_catalog_product(
    product_id: str,
) -> Dict[str, Any]:

    product = get_product(
        product_id
    )

    if not product:

        return {
            "found": False,
            "product": None,
        }

    return {
        "found": True,
        "product": product,
    }


def get_product_recommendations(
    product_id: str,
) -> Dict[str, Any]:

    product = get_product(
        product_id
    )

    if not product:

        return {
            "found": False,
            "product": None,
            "recommendations": [],
        }

    related = get_related_products(
        product_id
    )

    return {
        "found": True,
        "product": product,
        "recommendations": related,
    }


def get_available_products() -> Dict[str, Any]:

    products = list_products()

    available = [
        product
        for product
        in products
        if int(
            product.get(
                "stock",
                0,
            )
            or 0
        ) > 0
    ]

    return {
        "count": len(available),
        "products": available,
    }