from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from backend.commerce.catalog import get_product
from backend.commerce.cart import get_cart


# ============================================================
# OFFER TOOLS
# ============================================================

def _cart_product_keys(
    cart: Optional[Dict[str, Any]],
) -> Set[str]:
    """
    Return product/variant keys already present in the cart.
    """

    keys: Set[str] = set()

    if not cart:
        return keys

    items = (
        cart.get(
            "items",
            [],
        )
        or []
    )

    for item in items:

        product_id = str(
            item.get(
                "product_id",
                "",
            )
        ).strip()

        variant_id = str(
            item.get(
                "variant_id",
                "",
            )
            or ""
        ).strip()

        if product_id:
            keys.add(
                product_id
            )

        if (
            product_id
            and variant_id
        ):
            keys.add(
                f"{product_id}:{variant_id}"
            )

    return keys


def get_cross_sell_products(
    product_id: str,
    cart: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Return relevant in-stock products linked to the selected
    product, excluding products already in the cart.
    """

    product = get_product(
        product_id
    )

    if not product:
        return []

    cart_keys = _cart_product_keys(
        cart
    )

    related_ids = (
        product.get(
            "related_products",
            [],
        )
        or []
    )

    results: List[
        Dict[str, Any]
    ] = []

    for related_id in related_ids:

        related = get_product(
            str(related_id)
        )

        if not related:
            continue

        related_product_id = str(
            related.get(
                "product_id",
                "",
            )
        ).strip()

        stock = int(
            related.get(
                "stock",
                0,
            )
            or 0
        )

        if stock <= 0:
            continue

        if related_product_id in cart_keys:
            continue

        results.append(
            related
        )

    return results


def get_upsell_products(
    product_id: str,
    cart: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Return higher-priced in-stock variants for the selected
    product, excluding variants already in the cart.
    """

    product = get_product(
        product_id
    )

    if not product:
        return []

    cart_keys = _cart_product_keys(
        cart
    )

    base_price = float(
        product.get(
            "price",
            0,
        )
        or 0
    )

    variants = (
        product.get(
            "variants",
            [],
        )
        or []
    )

    results: List[
        Dict[str, Any]
    ] = []

    product_id_value = str(
        product.get(
            "product_id",
            "",
        )
    ).strip()

    for variant in variants:

        variant_id = str(
            variant.get(
                "variant_id",
                "",
            )
        ).strip()

        variant_price = float(
            variant.get(
                "price",
                base_price,
            )
            or base_price
        )

        variant_stock = int(
            variant.get(
                "stock",
                0,
            )
            or 0
        )

        key = (
            f"{product_id_value}:{variant_id}"
            if variant_id
            else product_id_value
        )

        if key in cart_keys:
            continue

        if (
            variant_stock > 0
            and variant_price > base_price
        ):

            results.append(
                {
                    "product_id":
                        product_id_value,

                    "product_name":
                        product.get(
                            "name"
                        ),

                    "variant_id":
                        variant_id,

                    "variant_name":
                        variant.get(
                            "name"
                        ),

                    "price":
                        variant_price,

                    "stock":
                        variant_stock,

                    "currency":
                        product.get(
                            "currency",
                            "INR",
                        ),

                    "type":
                        "UPSELL",
                }
            )

    results.sort(
        key=lambda item: float(
            item.get(
                "price",
                0,
            )
            or 0
        )
    )

    return results


def build_offer_candidates(
    product_id: str,
    cart_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate cart-aware, grounded upsell and cross-sell
    candidates.
    """

    product = get_product(
        product_id
    )

    if not product:

        return {
            "found": False,
            "product": None,
            "offers": [],
            "cart": None,
        }

    cart = None

    if cart_id:

        cart = get_cart(
            cart_id
        )

        if cart is None:

            return {
                "found": True,
                "product": product,
                "offers": [],
                "cart": None,
                "cart_found": False,
            }

    cross_sell_products = (
        get_cross_sell_products(
            product_id,
            cart=cart,
        )
    )

    upsell_products = (
        get_upsell_products(
            product_id,
            cart=cart,
        )
    )

    offers: List[
        Dict[str, Any]
    ] = []

    # --------------------------------------------------------
    # CROSS-SELL
    # --------------------------------------------------------

    for related in cross_sell_products:

        offers.append(
            {
                "type":
                    "CROSS_SELL",

                "product_id":
                    related.get(
                        "product_id"
                    ),

                "name":
                    related.get(
                        "name"
                    ),

                "price":
                    float(
                        related.get(
                            "price",
                            0,
                        )
                        or 0
                    ),

                "currency":
                    related.get(
                        "currency",
                        "INR",
                    ),

                "stock":
                    int(
                        related.get(
                            "stock",
                            0,
                        )
                        or 0
                    ),

                "reason":
                    (
                        f"Complements "
                        f"{product.get('name', 'your product')}."
                    ),
            }
        )

    # --------------------------------------------------------
    # UPSELL
    # --------------------------------------------------------

    for upsell in upsell_products:

        offers.append(
            {
                "type":
                    "UPSELL",

                "product_id":
                    upsell.get(
                        "product_id"
                    ),

                "variant_id":
                    upsell.get(
                        "variant_id"
                    ),

                "name":
                    (
                        f"{upsell.get('product_name', 'Product')} "
                        f"({upsell.get('variant_name', 'Variant')})"
                    ),

                "price":
                    float(
                        upsell.get(
                            "price",
                            0,
                        )
                        or 0
                    ),

                "currency":
                    upsell.get(
                        "currency",
                        "INR",
                    ),

                "stock":
                    int(
                        upsell.get(
                            "stock",
                            0,
                        )
                        or 0
                    ),

                "reason":
                    (
                        "A higher-priced available "
                        "variant of the selected product."
                    ),
            }
        )

    return {
        "found": True,
        "product": product,
        "offers": offers,
        "cart": cart,
        "cart_found": (
            True
            if cart_id
            else None
        ),
    }