from __future__ import annotations

from typing import Any, Dict, List

from backend.commerce.offer_tools import (
    build_offer_candidates,
)


class OfferAgent:
    """
    Generates grounded, cart-aware upsell and cross-sell
    recommendations.

    Rules:

        - Only recommend catalog products that exist.
        - Only recommend products with stock.
        - Do not recommend products already in the cart.
        - Keep upsell and cross-sell separate.
        - Prefer the most relevant offers first.
    """

    # ========================================================
    # RECOMMEND
    # ========================================================

    def recommend(
        self,
        product_id: str,
        cart_id: str | None = None,
        max_offers: int = 3,
    ) -> Dict[str, Any]:

        result = build_offer_candidates(
            product_id=product_id,
            cart_id=cart_id,
        )

        # ----------------------------------------------------
        # Product not found
        # ----------------------------------------------------

        if not result.get(
            "found",
            False,
        ):

            return {
                "success": False,
                "product": None,
                "offers": [],
                "message": (
                    "The selected product "
                    "could not be found."
                ),
            }

        # ----------------------------------------------------
        # Cart requested but not found
        # ----------------------------------------------------

        if (
            cart_id
            and
            result.get(
                "cart_found"
            )
            is False
        ):

            return {
                "success": False,
                "product":
                    result.get(
                        "product"
                    ),
                "offers": [],
                "message": (
                    "The buyer cart could not be found."
                ),
            }

        product = result[
            "product"
        ]

        offers = (
            result.get(
                "offers",
                [],
            )
            or []
        )

        if not offers:

            return {
                "success": True,
                "product": product,
                "offers": [],
                "message": (
                    "There are no additional "
                    "in-stock offers for this product."
                ),
            }

        # ----------------------------------------------------
        # Separate offer types
        # ----------------------------------------------------

        cross_sells = [

            offer

            for offer
            in offers

            if offer.get(
                "type"
            )
            ==
            "CROSS_SELL"

        ]

        upsells = [

            offer

            for offer
            in offers

            if offer.get(
                "type"
            )
            ==
            "UPSELL"

        ]

        # ----------------------------------------------------
        # Prioritize cross-sells first, then upsells.
        # This creates a better "complete your purchase"
        # experience.
        # ----------------------------------------------------

        ordered_offers = (
            cross_sells
            +
            upsells
        )

        max_offers = max(
            int(max_offers),
            1,
        )

        selected_offers = ordered_offers[
            :max_offers
        ]

        # ----------------------------------------------------
        # Build conversational message
        # ----------------------------------------------------

        message_parts: List[
            str
        ] = []

        selected_cross_sells = [

            offer

            for offer
            in selected_offers

            if offer.get(
                "type"
            )
            ==
            "CROSS_SELL"

        ]

        selected_upsells = [

            offer

            for offer
            in selected_offers

            if offer.get(
                "type"
            )
            ==
            "UPSELL"

        ]

        if selected_cross_sells:

            names = ", ".join(

                str(
                    offer.get(
                        "name",
                        "Product",
                    )
                )

                for offer
                in selected_cross_sells
            )

            message_parts.append(
                f"You may also like {names}."
            )

        if selected_upsells:

            names = ", ".join(

                str(
                    offer.get(
                        "name",
                        "Variant",
                    )
                )

                for offer
                in selected_upsells
            )

            message_parts.append(
                f"There is also an upgraded option: {names}."
            )

        message = " ".join(
            message_parts
        )

        return {
            "success": True,
            "product": product,
            "offers": selected_offers,
            "message": message,
            "cart_id": cart_id,
        }


    # ========================================================
    # BEST OFFER
    # ========================================================

    def best_offer(
        self,
        product_id: str,
        cart_id: str | None = None,
    ) -> Dict[str, Any]:

        result = self.recommend(
            product_id=product_id,
            cart_id=cart_id,
            max_offers=3,
        )

        offers = (
            result.get(
                "offers",
                [],
            )
            or []
        )

        if not offers:

            return {
                **result,
                "best_offer": None,
            }

        # Prefer cross-sell because it adds a distinct
        # product instead of asking the buyer to switch
        # variants.
        best = next(
            (
                offer
                for offer
                in offers
                if offer.get(
                    "type"
                )
                ==
                "CROSS_SELL"
            ),
            offers[0],
        )

        return {
            **result,
            "best_offer": best,
        }