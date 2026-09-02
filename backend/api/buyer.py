from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.agents.buyer_agent import BuyerAgent


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


@router.post(
    "/chat",
)
def buyer_chat(
    request: BuyerChatRequest,
) -> Dict[str, Any]:

    return agent.respond(
        request.message
    )


@router.post(
    "/search",
)
def buyer_search(
    request: BuyerChatRequest,
) -> Dict[str, Any]:

    return agent.search(
        request.message
    )