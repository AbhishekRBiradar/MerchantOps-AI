from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.agents.buyer_agent import BuyerAgent
from backend.commerce.cart import create_cart


router = APIRouter(
    prefix="/buyer",
    tags=["Buyer AI"],
)


agent = BuyerAgent()


class BuyerChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=2000,
    )

    session_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    cart_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )


class BuyerSearchRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=2000,
    )


# ============================================================
# CHAT
# ============================================================

@router.post(
    "/chat",
)
def buyer_chat(
    request: BuyerChatRequest,
) -> Dict[str, Any]:

    cart_id = request.cart_id

    # For cart operations, create a cart automatically
    # when the client hasn't supplied one yet.

    if not cart_id:

        preview = agent.detect_intent(
            request.message
        )

        if preview["intent"] in {
            "ADD_TO_CART",
            "VIEW_CART",
            "UPDATE_CART",
            "REMOVE_FROM_CART",
        }:

            cart_id = create_cart()[
                "cart_id"
            ]

    result = agent.respond(
        request.message,
        cart_id=cart_id,
    )

    if cart_id:

        result["cart_id"] = cart_id

    if request.session_id:

        result["session_id"] = (
            request.session_id
        )

    return result


# ============================================================
# SEARCH
# ============================================================

@router.post(
    "/search",
)
def buyer_search(
    request: BuyerSearchRequest,
) -> Dict[str, Any]:

    return agent.search(
        request.message
    )