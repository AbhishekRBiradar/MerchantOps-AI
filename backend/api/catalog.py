from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from pydantic import BaseModel, Field

from backend.commerce.catalog import (
    catalog_summary,
    delete_product,
    get_product,
    get_related_products,
    list_category,
    list_products,
    search_products,
    update_stock,
    upsert_product,
)


router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class CatalogVariant(BaseModel):

    variant_id: str

    name: str

    price: float = Field(
        ge=0
    )

    stock: int = Field(
        default=0,
        ge=0,
    )


class CatalogProductRequest(BaseModel):

    product_id: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    category: str = Field(
        min_length=1,
        max_length=255,
    )

    price: float = Field(
        default=0.0,
        ge=0,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    stock: int = Field(
        default=0,
        ge=0,
    )

    description: Optional[str] = None

    features: List[str] = Field(
        default_factory=list
    )

    tags: List[str] = Field(
        default_factory=list
    )

    variants: List[
        CatalogVariant
    ] = Field(
        default_factory=list
    )

    related_products: List[str] = Field(
        default_factory=list
    )


class CatalogStockRequest(BaseModel):

    stock: int = Field(
        ge=0
    )


# ============================================================
# CATALOG SUMMARY / LIST
# ============================================================

@router.get(
    "",
)
def catalog(
    q: str | None = Query(
        default=None,
        description="Optional product search query.",
    ),
) -> Dict[str, Any]:

    if q:

        products = search_products(
            q
        )

    else:

        products = list_products()

    return {
        "count": len(
            products
        ),
        "products": products,
        "summary": catalog_summary(),
    }


# ============================================================
# SEARCH
# ============================================================

@router.get(
    "/search/query",
)
def catalog_search(
    q: str = Query(
        min_length=1,
        description="Product search query.",
    ),
) -> Dict[str, Any]:

    products = search_products(
        q
    )

    return {
        "query": q,
        "count": len(
            products
        ),
        "products": products,
    }


# ============================================================
# CATEGORY
# ============================================================

@router.get(
    "/category/{category}",
)
def catalog_category(
    category: str,
) -> Dict[str, Any]:

    products = list_category(
        category
    )

    return {
        "category": category,
        "count": len(
            products
        ),
        "products": products,
    }


# ============================================================
# RELATED PRODUCTS
# ============================================================

@router.get(
    "/{product_id}/related",
)
def catalog_related(
    product_id: str,
) -> Dict[str, Any]:

    product = get_product(
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    related = get_related_products(
        product_id
    )

    return {
        "product_id": product_id,
        "count": len(
            related
        ),
        "products": related,
    }


# ============================================================
# CREATE PRODUCT
# ============================================================

@router.post(
    "",
)
def create_catalog_product(
    payload: CatalogProductRequest,
) -> Dict[str, Any]:

    try:

        product = payload.model_dump()

        product["variants"] = [
            variant.model_dump()
            for variant
            in payload.variants
        ]

        saved_product = upsert_product(
            product
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "created": True,
        "product": saved_product,
    }


# ============================================================
# UPDATE PRODUCT
# ============================================================

@router.put(
    "/{product_id}",
)
def update_catalog_product(
    product_id: str,
    payload: CatalogProductRequest,
) -> Dict[str, Any]:

    requested_id = (
        str(product_id)
        .strip()
        .upper()
    )

    body_product_id = (
        str(payload.product_id)
        .strip()
        .upper()
    )

    if requested_id != body_product_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Path product_id and body "
                "product_id must match."
            ),
        )

    existing = get_product(
        requested_id
    )

    if not existing:

        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    try:

        product = payload.model_dump()

        product["product_id"] = (
            requested_id
        )

        product["variants"] = [
            variant.model_dump()
            for variant
            in payload.variants
        ]

        saved_product = upsert_product(
            product
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "updated": True,
        "product": saved_product,
    }


# ============================================================
# UPDATE STOCK
# ============================================================

@router.patch(
    "/{product_id}/stock",
)
def update_catalog_stock(
    product_id: str,
    payload: CatalogStockRequest,
) -> Dict[str, Any]:

    try:

        product = update_stock(
            product_id,
            payload.stock,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    return {
        "updated": True,
        "product": product,
    }


# ============================================================
# DELETE PRODUCT
# ============================================================

@router.delete(
    "/{product_id}",
)
def delete_catalog_product(
    product_id: str,
) -> Dict[str, Any]:

    deleted = delete_product(
        product_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    return {
        "deleted": True,
        "product_id": product_id,
    }


# ============================================================
# PRODUCT DETAILS
# ============================================================

@router.get(
    "/{product_id}",
)
def catalog_product(
    product_id: str,
) -> Dict[str, Any]:

    product = get_product(
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    return {
        "product": product,
    }