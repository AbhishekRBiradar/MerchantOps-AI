from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.commerce.catalog import get_product


# ============================================================
# IN-MEMORY CART STORE
# ============================================================

_CARTS: Dict[str, Dict[str, Any]] = {}


# ============================================================
# HELPERS
# ============================================================

def _new_cart(
    cart_id: Optional[str] = None,
) -> Dict[str, Any]:

    return {
        "cart_id": cart_id or f"cart_{uuid4().hex[:12]}",
        "currency": "INR",
        "items": [],
        "subtotal": 0.0,
        "discount": 0.0,
        "tax": 0.0,
        "total": 0.0,
    }


def _calculate_cart(
    cart: Dict[str, Any],
) -> Dict[str, Any]:

    subtotal = 0.0

    for item in cart["items"]:

        quantity = int(
            item.get(
                "quantity",
                0,
            )
        )

        price = float(
            item.get(
                "unit_price",
                0.0,
            )
        )

        item["line_total"] = round(
            quantity * price,
            2,
        )

        subtotal += item[
            "line_total"
        ]

    subtotal = round(
        subtotal,
        2,
    )

    discount = round(
        float(
            cart.get(
                "discount",
                0.0,
            )
            or 0.0
        ),
        2,
    )

    tax = round(
        float(
            cart.get(
                "tax",
                0.0,
            )
            or 0.0
        ),
        2,
    )

    total = round(
        subtotal
        - discount
        + tax,
        2,
    )

    cart["subtotal"] = subtotal
    cart["discount"] = discount
    cart["tax"] = tax
    cart["total"] = total

    return cart


def _get_cart(
    cart_id: str,
) -> Optional[Dict[str, Any]]:

    return _CARTS.get(
        str(cart_id).strip()
    )


# ============================================================
# CREATE CART
# ============================================================

def create_cart() -> Dict[str, Any]:

    cart = _new_cart()

    _CARTS[
        cart["cart_id"]
    ] = cart

    return _calculate_cart(
        cart
    )


# ============================================================
# GET CART
# ============================================================

def get_cart(
    cart_id: str,
) -> Optional[Dict[str, Any]]:

    cart = _get_cart(
        cart_id
    )

    if cart is None:
        return None

    return _calculate_cart(
        cart
    )


# ============================================================
# ADD ITEM
# ============================================================

def add_item(
    cart_id: str,
    product_id: str,
    quantity: int = 1,
    variant_id: Optional[str] = None,
) -> Dict[str, Any]:

    quantity = int(
        quantity
    )

    if quantity <= 0:
        raise ValueError(
            "quantity must be greater than zero."
        )

    cart = _get_cart(
        cart_id
    )

    if cart is None:
        raise ValueError(
            "Cart not found."
        )

    product = get_product(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found."
        )

    available_stock = int(
        product.get(
            "stock",
            0,
        )
        or 0
    )

    selected_variant = None

    if variant_id:

        variants = (
            product.get(
                "variants",
                [],
            )
            or []
        )

        selected_variant = next(
            (
                variant
                for variant
                in variants
                if str(
                    variant.get(
                        "variant_id",
                        "",
                    )
                )
                .strip()
                .upper()
                ==
                str(
                    variant_id
                )
                .strip()
                .upper()
            ),
            None,
        )

        if selected_variant is None:
            raise ValueError(
                "Variant not found."
            )

        available_stock = int(
            selected_variant.get(
                "stock",
                0,
            )
            or 0
        )

        unit_price = float(
            selected_variant.get(
                "price",
                product.get(
                    "price",
                    0,
                ),
            )
            or 0
        )

        variant_name = selected_variant.get(
            "name"
        )

    else:

        unit_price = float(
            product.get(
                "price",
                0,
            )
            or 0
        )

        variant_name = None

    if available_stock <= 0:

        raise ValueError(
            "Product is out of stock."
        )

    if quantity > available_stock:

        raise ValueError(
            (
                f"Only {available_stock} unit(s) "
                "are currently available."
            )
        )

    existing = next(
        (
            item
            for item
            in cart["items"]
            if item.get(
                "product_id"
            )
            ==
            product.get(
                "product_id"
            )
            and item.get(
                "variant_id"
            )
            ==
            variant_id
        ),
        None,
    )

    if existing:

        new_quantity = (
            int(
                existing.get(
                    "quantity",
                    0,
                )
            )
            +
            quantity
        )

        if new_quantity > available_stock:

            raise ValueError(
                (
                    f"Only {available_stock} unit(s) "
                    "are currently available."
                )
            )

        existing["quantity"] = new_quantity

        existing["line_total"] = round(
            new_quantity * unit_price,
            2,
        )

    else:

        cart["items"].append(
            {
                "product_id":
                    product["product_id"],

                "product_name":
                    product["name"],

                "category":
                    product.get(
                        "category"
                    ),

                "variant_id":
                    variant_id,

                "variant_name":
                    variant_name,

                "quantity":
                    quantity,

                "unit_price":
                    round(
                        unit_price,
                        2,
                    ),

                "currency":
                    product.get(
                        "currency",
                        "INR",
                    ),

                "line_total":
                    round(
                        quantity
                        *
                        unit_price,
                        2,
                    ),
            }
        )

    return _calculate_cart(
        cart
    )


# ============================================================
# UPDATE ITEM QUANTITY
# ============================================================

def update_item_quantity(
    cart_id: str,
    product_id: str,
    quantity: int,
    variant_id: Optional[str] = None,
) -> Dict[str, Any]:

    quantity = int(
        quantity
    )

    if quantity <= 0:
        raise ValueError(
            "quantity must be greater than zero."
        )

    cart = _get_cart(
        cart_id
    )

    if cart is None:
        raise ValueError(
            "Cart not found."
        )

    product = get_product(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found."
        )

    selected_variant = None

    if variant_id:

        selected_variant = next(
            (
                variant
                for variant
                in (
                    product.get(
                        "variants",
                        [],
                    )
                    or []
                )
                if str(
                    variant.get(
                        "variant_id",
                        "",
                    )
                )
                .strip()
                .upper()
                ==
                str(
                    variant_id
                )
                .strip()
                .upper()
            ),
            None,
        )

        if selected_variant is None:
            raise ValueError(
                "Variant not found."
            )

        available_stock = int(
            selected_variant.get(
                "stock",
                0,
            )
            or 0
        )

        unit_price = float(
            selected_variant.get(
                "price",
                product.get(
                    "price",
                    0,
                ),
            )
            or 0
        )

    else:

        available_stock = int(
            product.get(
                "stock",
                0,
            )
            or 0
        )

        unit_price = float(
            product.get(
                "price",
                0,
            )
            or 0
        )

    if quantity > available_stock:

        raise ValueError(
            (
                f"Only {available_stock} unit(s) "
                "are currently available."
            )
        )

    item = next(
        (
            item
            for item
            in cart["items"]
            if item.get(
                "product_id"
            )
            ==
            product_id
            and item.get(
                "variant_id"
            )
            ==
            variant_id
        ),
        None,
    )

    if item is None:

        raise ValueError(
            "Cart item not found."
        )

    item["quantity"] = quantity

    item["unit_price"] = round(
        unit_price,
        2,
    )

    item["line_total"] = round(
        quantity * unit_price,
        2,
    )

    return _calculate_cart(
        cart
    )


# ============================================================
# REMOVE ITEM
# ============================================================

def remove_item(
    cart_id: str,
    product_id: str,
    variant_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:

    cart = _get_cart(
        cart_id
    )

    if cart is None:
        return None

    original_count = len(
        cart["items"]
    )

    cart["items"] = [

        item

        for item
        in cart["items"]

        if not (
            item.get(
                "product_id"
            )
            ==
            product_id
            and item.get(
                "variant_id"
            )
            ==
            variant_id
        )

    ]

    if len(
        cart["items"]
    ) == original_count:

        raise ValueError(
            "Cart item not found."
        )

    return _calculate_cart(
        cart
    )


# ============================================================
# APPLY DISCOUNT / TAX
# ============================================================

def set_totals(
    cart_id: str,
    discount: float = 0.0,
    tax: float = 0.0,
) -> Optional[Dict[str, Any]]:

    cart = _get_cart(
        cart_id
    )

    if cart is None:
        return None

    discount = float(
        discount
    )

    tax = float(
        tax
    )

    if discount < 0:
        raise ValueError(
            "discount cannot be negative."
        )

    if tax < 0:
        raise ValueError(
            "tax cannot be negative."
        )

    cart["discount"] = round(
        discount,
        2,
    )

    cart["tax"] = round(
        tax,
        2,
    )

    return _calculate_cart(
        cart
    )