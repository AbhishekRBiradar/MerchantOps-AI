from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.agents.offer_agent import OfferAgent


router = APIRouter(
    prefix="/offers",
    tags=["Offers"],
)


agent = OfferAgent()


# ============================================================
# OFFER RECOMMENDATIONS
# ============================================================

@router.post(
    "/recommend",
)
def recommend_offers(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    product_id = str(
        payload.get(
            "product_id",
            "",
        )
    ).strip()

    cart_id = payload.get(
        "cart_id"
    )

    if cart_id is not None:

        cart_id = str(
            cart_id
        ).strip()

        if not cart_id:

            cart_id = None

    max_offers = payload.get(
        "max_offers",
        3,
    )

    try:

        max_offers = int(
            max_offers
        )

    except (
        TypeError,
        ValueError,
    ):

        max_offers = 3

    if not product_id:

        raise HTTPException(
            status_code=400,
            detail="product_id is required.",
        )

    return agent.recommend(
        product_id=product_id,
        cart_id=cart_id,
        max_offers=max_offers,
    )


# ============================================================
# BEST OFFER
# ============================================================

@router.post(
    "/best",
)
def best_offer(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    product_id = str(
        payload.get(
            "product_id",
            "",
        )
    ).strip()

    cart_id = payload.get(
        "cart_id"
    )

    if cart_id is not None:

        cart_id = str(
            cart_id
        ).strip()

        if not cart_id:

            cart_id = None

    if not product_id:

        raise HTTPException(
            status_code=400,
            detail="product_id is required.",
        )

    return agent.best_offer(
        product_id=product_id,
        cart_id=cart_id,
    )