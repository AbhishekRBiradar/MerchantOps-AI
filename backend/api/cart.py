from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import BaseModel, Field

from backend.commerce.cart import (
    add_item,
    create_cart,
    get_cart,
    remove_item,
    set_totals,
    update_item_quantity,
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class AddCartItemRequest(BaseModel):

    product_id: str = Field(
        min_length=1,
        max_length=100,
    )

    quantity: int = Field(
        default=1,
        ge=1,
    )

    variant_id: Optional[str] = None


class UpdateCartItemRequest(BaseModel):

    quantity: int = Field(
        ge=1,
    )

    variant_id: Optional[str] = None


class CartTotalsRequest(BaseModel):

    discount: float = Field(
        default=0.0,
        ge=0,
    )

    tax: float = Field(
        default=0.0,
        ge=0,
    )


# ============================================================
# CREATE CART
# ============================================================

@router.post(
    "",
)
def create_new_cart() -> Dict[str, Any]:

    return {
        "created": True,
        "cart": create_cart(),
    }


# ============================================================
# GET CART
# ============================================================

@router.get(
    "/{cart_id}",
)
def read_cart(
    cart_id: str,
) -> Dict[str, Any]:

    cart = get_cart(
        cart_id
    )

    if cart is None:

        raise HTTPException(
            status_code=404,
            detail="Cart not found.",
        )

    return {
        "cart": cart,
    }


# ============================================================
# ADD ITEM
# ============================================================

@router.post(
    "/{cart_id}/items",
)
def add_cart_item(
    cart_id: str,
    request: AddCartItemRequest,
) -> Dict[str, Any]:

    try:

        cart = add_item(
            cart_id=cart_id,
            product_id=request.product_id,
            quantity=request.quantity,
            variant_id=request.variant_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "updated": True,
        "cart": cart,
    }


# ============================================================
# UPDATE ITEM
# ============================================================

@router.patch(
    "/{cart_id}/items/{product_id}",
)
def update_cart_item(
    cart_id: str,
    product_id: str,
    request: UpdateCartItemRequest,
) -> Dict[str, Any]:

    try:

        cart = update_item_quantity(
            cart_id=cart_id,
            product_id=product_id,
            quantity=request.quantity,
            variant_id=request.variant_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "updated": True,
        "cart": cart,
    }


# ============================================================
# REMOVE ITEM
# ============================================================

@router.delete(
    "/{cart_id}/items/{product_id}",
)
def delete_cart_item(
    cart_id: str,
    product_id: str,
    variant_id: Optional[str] = None,
) -> Dict[str, Any]:

    try:

        cart = remove_item(
            cart_id=cart_id,
            product_id=product_id,
            variant_id=variant_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if cart is None:

        raise HTTPException(
            status_code=404,
            detail="Cart not found.",
        )

    return {
        "deleted": True,
        "cart": cart,
    }


# ============================================================
# CALCULATE TOTALS
# ============================================================

@router.post(
    "/{cart_id}/calculate",
)
def calculate_cart(
    cart_id: str,
    request: CartTotalsRequest,
) -> Dict[str, Any]:

    try:

        cart = set_totals(
            cart_id=cart_id,
            discount=request.discount,
            tax=request.tax,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if cart is None:

        raise HTTPException(
            status_code=404,
            detail="Cart not found.",
        )

    return {
        "calculated": True,
        "cart": cart,
    }