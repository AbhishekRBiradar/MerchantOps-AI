from __future__ import annotations

import re
from typing import Any, Dict, List

from backend.commerce.buyer_tools import (
    get_catalog_product,
    get_product_recommendations,
    search_catalog,
)


class BuyerAgent:
    """
    Commerce-focused buyer agent.

    This first implementation is deliberately deterministic
    and catalog-grounded. It does not invent product data.
    An LLM can be added later on top of these tools.
    """

    def detect_intent(
        self,
        message: str,
    ) -> Dict[str, Any]:

        text = (
            str(message or "")
            .strip()
            .lower()
        )

        if not text:

            return {
                "intent": "UNKNOWN",
                "filters": {},
            }

        if (
            "related" in text
            or "similar" in text
            or "accessor" in text
            or "goes with" in text
        ):

            return {
                "intent": "RELATED_PRODUCTS",
                "filters": {},
            }

        if (
            "details" in text
            or "tell me about" in text
            or "more about" in text
            or "features" in text
        ):

            return {
                "intent": "PRODUCT_DETAILS",
                "filters": {},
            }

        return {
            "intent": "PRODUCT_SEARCH",
            "filters": self.extract_filters(
                text
            ),
        }


    def extract_filters(
        self,
        message: str,
    ) -> Dict[str, Any]:

        text = str(
            message or ""
        ).lower()

        filters: Dict[str, Any] = {}

        price_patterns = [
            r"under\s*[₹rs\.\s]*([\d,]+)",
            r"below\s*[₹rs\.\s]*([\d,]+)",
            r"less than\s*[₹rs\.\s]*([\d,]+)",
            r"within\s*[₹rs\.\s]*([\d,]+)",
            r"budget\s*(?:of)?\s*[₹rs\.\s]*([\d,]+)",
        ]

        for pattern in price_patterns:

            match = re.search(
                pattern,
                text,
            )

            if match:

                filters[
                    "max_price"
                ] = float(
                    match.group(
                        1
                    ).replace(
                        ",",
                        "",
                    )
                )

                break

        categories = [
            "backpack",
            "backpacks",
            "laptop",
            "mouse",
            "keyboard",
            "accessory",
            "accessories",
            "travel",
        ]

        for category in categories:

            if category in text:

                filters[
                    "keyword"
                ] = category

                break

        context_tags = []

        for tag in [
            "office",
            "travel",
            "college",
            "laptop",
            "gaming",
        ]:

            if tag in text:
                context_tags.append(
                    tag
                )

        if context_tags:

            filters[
                "tags"
            ] = context_tags

        return filters


    def _rank_products(
        self,
        products: List[
            Dict[str, Any]
        ],
        filters: Dict[str, Any],
    ) -> List[
        Dict[str, Any]
    ]:

        requested_tags = set(
            filters.get(
                "tags",
                [],
            )
        )

        keyword = str(
            filters.get(
                "keyword",
                "",
            )
        ).lower()

        scored = []

        for product in products:

            score = 0.0

            name = str(
                product.get(
                    "name",
                    "",
                )
            ).lower()

            category = str(
                product.get(
                    "category",
                    "",
                )
            ).lower()

            tags = {
                str(tag).lower()
                for tag
                in (
                    product.get(
                        "tags",
                        [],
                    )
                    or []
                )
            }

            if keyword:

                if keyword in name:
                    score += 5

                if keyword in category:
                    score += 4

                if keyword in tags:
                    score += 3

            score += (
                2 * len(
                    requested_tags
                    &
                    tags
                )
            )

            stock = int(
                product.get(
                    "stock",
                    0,
                )
                or 0
            )

            if stock > 0:
                score += 1

            scored.append(
                (
                    score,
                    product,
                )
            )

        scored.sort(
            key=lambda item: (
                item[0],
                float(
                    item[1].get(
                        "stock",
                        0,
                    )
                    or 0
                ),
            ),
            reverse=True,
        )

        return [
            product
            for _, product
            in scored
        ]


    def search(
        self,
        message: str,
    ) -> Dict[str, Any]:

        intent_data = self.detect_intent(
            message
        )

        filters = intent_data[
            "filters"
        ]

        keyword = filters.get(
            "keyword"
        ) or message

        result = search_catalog(
            query=str(
                keyword
            ),
            max_price=filters.get(
                "max_price"
            ),
            in_stock_only=True,
        )

        products = self._rank_products(
            result.get(
                "products",
                [],
            ),
            filters,
        )

        return {
            "intent":
                "PRODUCT_SEARCH",

            "filters":
                filters,

            "count":
                len(products),

            "products":
                products,
        }


    def respond(
        self,
        message: str,
    ) -> Dict[str, Any]:

        intent_data = self.detect_intent(
            message
        )

        intent = intent_data[
            "intent"
        ]

        if intent == "PRODUCT_SEARCH":

            result = self.search(
                message
            )

            return {
                "intent": intent,
                "message": self._search_response(
                    result[
                        "products"
                    ],
                    result[
                        "filters"
                    ],
                ),
                "products":
                    result[
                        "products"
                    ],
                "filters":
                    result[
                        "filters"
                    ],
            }

        return {
            "intent": intent,
            "message": (
                "I can help you find products. "
                "Tell me what you are looking for, "
                "your budget, or your use case."
            ),
            "products": [],
            "filters": {},
        }


    def _search_response(
        self,
        products: List[
            Dict[str, Any]
        ],
        filters: Dict[str, Any],
    ) -> str:

        if not products:

            return (
                "I couldn't find an in-stock product "
                "matching those requirements."
            )

        product = products[0]

        name = product.get(
            "name",
            "this product",
        )

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

        features = product.get(
            "features",
            [],
        ) or []

        feature_text = ""

        if features:

            feature_text = (
                " Key features: "
                +
                ", ".join(
                    map(
                        str,
                        features[:3],
                    )
                )
                +
                "."
            )

        return (
            f"I recommend {name} at "
            f"₹{price:,.2f}. "
            f"It has {stock} unit(s) in stock."
            f"{feature_text}"
        )