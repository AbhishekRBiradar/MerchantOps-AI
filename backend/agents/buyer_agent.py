from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from backend.commerce.buyer_tools import (
    add_product_to_cart,
    get_buyer_cart,
    get_catalog_product,
    get_product_recommendations,
    remove_product_from_cart,
    search_catalog,
    update_product_in_cart,
)


class BuyerAgent:
    """
    Commerce-focused buyer agent.

    Responsibilities:

        Product discovery
        Product details
        Related-product discovery
        Cart operations

    Product facts always come from the live catalog.

    Cart operations use a caller-provided cart_id.
    """

    # ========================================================
    # INTENT DETECTION
    # ========================================================

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

        # ----------------------------------------------------
        # CART: ADD
        # ----------------------------------------------------

        if (
            "add to cart" in text
            or "add it" in text
            or "add this" in text
            or "put it in my cart" in text
            or text.startswith("add ")
        ):

            return {
                "intent": "ADD_TO_CART",
                "filters": self.extract_filters(
                    text
                ),
            }

        # ----------------------------------------------------
        # CART: VIEW
        # ----------------------------------------------------

        if (
            "show my cart" in text
            or "view my cart" in text
            or "what is in my cart" in text
            or "what's in my cart" in text
            or "cart total" in text
            or "my cart total" in text
            or "my total" in text
            or "show cart" in text
            or text == "cart"
        ):

            return {
                "intent": "VIEW_CART",
                "filters": {},
            }

        # ----------------------------------------------------
        # CART: UPDATE
        # ----------------------------------------------------

        if (
            "make it" in text
            or "change quantity" in text
            or "increase quantity" in text
            or "decrease quantity" in text
            or "set quantity" in text
            or "change it to" in text
            or "change to" in text
        ):

            return {
                "intent": "UPDATE_CART",
                "filters": {},
            }

        # ----------------------------------------------------
        # CART: REMOVE
        # ----------------------------------------------------

        if (
            "remove from cart" in text
            or "remove it" in text
            or "remove this" in text
            or "delete from cart" in text
            or "take it out of my cart" in text
            or text.startswith("remove ")
        ):

            return {
                "intent": "REMOVE_FROM_CART",
                "filters": {},
            }

        # ----------------------------------------------------
        # PRODUCT: RELATED
        # ----------------------------------------------------

        if (
            "related" in text
            or "similar" in text
            or "accessor" in text
            or "goes with" in text
            or "what else goes" in text
        ):

            return {
                "intent": "RELATED_PRODUCTS",
                "filters": {},
            }

        # ----------------------------------------------------
        # PRODUCT: DETAILS
        # ----------------------------------------------------

        if (
            "details" in text
            or "tell me about" in text
            or "more about" in text
            or "features" in text
            or "specifications" in text
            or "specs" in text
        ):

            return {
                "intent": "PRODUCT_DETAILS",
                "filters": {},
            }

        # ----------------------------------------------------
        # DEFAULT
        # ----------------------------------------------------

        return {
            "intent": "PRODUCT_SEARCH",
            "filters": self.extract_filters(
                text
            ),
        }

    # ========================================================
    # FILTER EXTRACTION
    # ========================================================

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
            "sleeve",
            "organizer",
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

    # ========================================================
    # PRODUCT RANKING
    # ========================================================

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
                for tag in (
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
                2
                * len(
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

    # ========================================================
    # PRODUCT SEARCH
    # ========================================================

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

        keyword = (
            filters.get(
                "keyword"
            )
            or message
        )

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

    # ========================================================
    # PRODUCT RESOLUTION
    # ========================================================

    def _resolve_product(
        self,
        message: str,
    ) -> Optional[
        Dict[str, Any]
    ]:

        text = (
            str(message or "")
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # Exact catalog IDs
        # ----------------------------------------------------

        for product_id in [
            "BP001",
            "LS001",
            "ORG001",
        ]:

            if product_id.lower() in text:

                result = get_catalog_product(
                    product_id
                )

                if result.get(
                    "found",
                    False,
                ):

                    return result.get(
                        "product"
                    )

        # ----------------------------------------------------
        # Search against all catalog products.
        #
        # This is important for phrases such as:
        #
        # "Add the black backpack"
        #
        # because the full sentence is not itself a
        # product name.
        # ----------------------------------------------------

        from backend.commerce.catalog import (
            list_products,
        )

        products = list_products()

        stop_words = {
            "add",
            "the",
            "a",
            "an",
            "to",
            "my",
            "cart",
            "please",
            "put",
            "it",
            "this",
            "product",
            "item",
            "want",
            "take",
            "get",
            "buy",
            "for",
            "me",
            "into",
            "of",
            "in",
        }

        words = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                text,
            )
            if word not in stop_words
        }

        best_product = None
        best_score = 0

        for product in products:

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

            description = str(
                product.get(
                    "description",
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

            features = {
                str(feature).lower()
                for feature
                in (
                    product.get(
                        "features",
                        [],
                    )
                    or []
                )
            }

            for searchable_word in words:

                # Exact word in name = strongest.
                if (
                    searchable_word
                    in name
                ):

                    best_score_candidate = 10

                # Category match.
                elif (
                    searchable_word
                    in category
                ):

                    best_score_candidate = 7

                # Tag match.
                elif (
                    searchable_word
                    in tags
                ):

                    best_score_candidate = 5

                # Feature match.
                elif (
                    searchable_word
                    in features
                ):

                    best_score_candidate = 3

                elif (
                    searchable_word
                    in description
                ):

                    best_score_candidate = 1

                else:

                    best_score_candidate = 0

                if (
                    best_score_candidate > 0
                ):

                    # Accumulate score on the product.
                    current_score = 0

                    if (
                        searchable_word
                        in name
                    ):
                        current_score += 10

                    if (
                        searchable_word
                        in category
                    ):
                        current_score += 7

                    if (
                        searchable_word
                        in tags
                    ):
                        current_score += 5

                    if (
                        searchable_word
                        in features
                    ):
                        current_score += 3

                    if (
                        searchable_word
                        in description
                    ):
                        current_score += 1

                    if (
                        current_score
                        > best_score
                    ):

                        best_score = (
                            current_score
                        )

                        best_product = (
                            product
                        )

        return best_product

    # ========================================================
    # VARIANT RESOLUTION
    # ========================================================

    def _resolve_variant(
        self,
        product: Optional[
            Dict[str, Any]
        ],
        message: str,
    ) -> Optional[str]:

        if not product:

            return None

        text = (
            str(message or "")
            .strip()
            .lower()
        )

        variants = (
            product.get(
                "variants",
                [],
            )
            or []
        )

        for variant in variants:

            variant_id = str(
                variant.get(
                    "variant_id",
                    "",
                )
            )

            variant_name = str(
                variant.get(
                    "name",
                    "",
                )
            ).lower()

            if (
                variant_id
                and
                variant_id.lower()
                in text
            ):

                return variant_id

            if (
                variant_name
                and
                re.search(
                    rf"\b{re.escape(variant_name)}\b",
                    text,
                )
            ):

                return variant_id

        return None

    # ========================================================
    # QUANTITY EXTRACTION
    # ========================================================

        # ========================================================
    # QUANTITY EXTRACTION
    # ========================================================

    def _extract_quantity(
        self,
        message: str,
        default: int = 1,
    ) -> int:

        text = (
            str(message or "")
            .strip()
            .lower()
        )

        number_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        patterns = [
            r"quantity\s*(?:to|=)?\s*(\d+)",
            r"qty\s*(?:to|=)?\s*(\d+)",
            r"make it\s+(\d+)",
            r"change(?:\s+it)?\s+to\s+(\d+)",
            r"set\s+(?:it\s+)?to\s+(\d+)",
            r"add\s+(\d+)",
            r"(\d+)\s*(?:units|unit|items|item)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
            )

            if match:

                quantity = int(
                    match.group(1)
                )

                if quantity > 0:
                    return quantity

        word_patterns = [
            r"make it\s+(one|two|three|four|five|six|seven|eight|nine|ten)",
            r"change(?:\s+it)?\s+to\s+(one|two|three|four|five|six|seven|eight|nine|ten)",
            r"set\s+(?:it\s+)?to\s+(one|two|three|four|five|six|seven|eight|nine|ten)",
        ]

        for pattern in word_patterns:

            match = re.search(
                pattern,
                text,
            )

            if match:

                return number_words[
                    match.group(1)
                ]

        return default

    # ========================================================
    # FIND SINGLE CART ITEM
    # ========================================================

    def _single_cart_item(
        self,
        cart: Optional[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:

        if not cart:

            return None

        items = (
            cart.get(
                "items",
                [],
            )
            or []
        )

        if len(items) == 1:

            return items[0]

        return None

    # ========================================================
    # ADD TO CART
    # ========================================================

    def add_to_cart(
        self,
        message: str,
        cart_id: str,
    ) -> Dict[str, Any]:

        product = self._resolve_product(
            message
        )

        if not product:

            return {
                "success": False,
                "intent": "ADD_TO_CART",
                "message": (
                    "I couldn't identify the product "
                    "you want to add."
                ),
                "cart": None,
            }

        variant_id = (
            self._resolve_variant(
                product,
                message,
            )
        )

        quantity = self._extract_quantity(
            message,
            default=1,
        )

        try:

            result = add_product_to_cart(
                cart_id=cart_id,
                product_id=product[
                    "product_id"
                ],
                quantity=quantity,
                variant_id=variant_id,
            )

        except ValueError as exc:

            return {
                "success": False,
                "intent": "ADD_TO_CART",
                "message": str(exc),
                "cart": None,
            }

        item_text = product.get(
            "name",
            "Product",
        )

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
                    if variant.get(
                        "variant_id"
                    )
                    ==
                    variant_id
                ),
                None,
            )

            if selected_variant:

                item_text += (
                    " ("
                    +
                    str(
                        selected_variant.get(
                            "name",
                            "",
                        )
                    )
                    +
                    ")"
                )

        total = float(
            result[
                "cart"
            ].get(
                "total",
                0,
            )
            or 0
        )

        return {
            "success": True,
            "intent": "ADD_TO_CART",
            "message": (
                f"Added {quantity} × "
                f"{item_text} to your cart. "
                f"Your current total is "
                f"₹{total:,.2f}."
            ),
            "cart": result[
                "cart"
            ],
        }

    # ========================================================
    # VIEW CART
    # ========================================================

    def view_cart(
        self,
        cart_id: str,
    ) -> Dict[str, Any]:

        result = get_buyer_cart(
            cart_id
        )

        if not result.get(
            "success",
            False,
        ):

            return {
                "success": False,
                "intent": "VIEW_CART",
                "message": (
                    "Your cart could not be found."
                ),
                "cart": None,
            }

        cart = result[
            "cart"
        ]

        items = (
            cart.get(
                "items",
                [],
            )
            or []
        )

        if not items:

            message = (
                "Your cart is currently empty."
            )

        else:

            item_lines = []

            for item in items:

                product_name = item.get(
                    "product_name",
                    "Product",
                )

                variant_name = item.get(
                    "variant_name"
                )

                quantity = int(
                    item.get(
                        "quantity",
                        0,
                    )
                    or 0
                )

                line = (
                    f"{quantity} × "
                    f"{product_name}"
                )

                if variant_name:

                    line += (
                        f" ({variant_name})"
                    )

                item_lines.append(
                    line
                )

            message = (
                "Your cart contains: "
                +
                ", ".join(
                    item_lines
                )
                +
                ". Your total is "
                +
                f"₹{float(cart.get('total', 0) or 0):,.2f}."
            )

        return {
            "success": True,
            "intent": "VIEW_CART",
            "message": message,
            "cart": cart,
        }

    # ========================================================
    # UPDATE CART
    # ========================================================

    def update_cart(
        self,
        message: str,
        cart_id: str,
    ) -> Dict[str, Any]:

        cart_result = get_buyer_cart(
            cart_id
        )

        if not cart_result.get(
            "success",
            False,
        ):

            return {
                "success": False,
                "intent": "UPDATE_CART",
                "message": (
                    "Your cart could not be found."
                ),
                "cart": None,
            }

        cart = cart_result[
            "cart"
        ]

        items = (
            cart.get(
                "items",
                [],
            )
            or []
        )

        if not items:

            return {
                "success": False,
                "intent": "UPDATE_CART",
                "message": (
                    "Your cart is empty."
                ),
                "cart": cart,
            }

        # ----------------------------------------------------
        # Resolve product explicitly first.
        # ----------------------------------------------------

        product = self._resolve_product(
            message
        )

        # ----------------------------------------------------
        # If this is a simple "make it two" request and
        # there is exactly one item, use that item.
        # ----------------------------------------------------

        single_item = (
            self._single_cart_item(
                cart
            )
        )

        if product:

            product_id = product[
                "product_id"
            ]

        elif single_item:

            product_id = single_item.get(
                "product_id"
            )

        else:

            return {
                "success": False,
                "intent": "UPDATE_CART",
                "message": (
                    "Please specify which cart item "
                    "you want to update."
                ),
                "cart": cart,
            }

        # ----------------------------------------------------
        # Resolve variant.
        # ----------------------------------------------------

        variant_id = self._resolve_variant(
            product,
            message,
        )

        if (
            variant_id is None
            and single_item
            and single_item.get(
                "product_id"
            )
            ==
            product_id
        ):

            variant_id = single_item.get(
                "variant_id"
            )

        # ----------------------------------------------------
        # Quantity.
        # ----------------------------------------------------

        current_quantity = 1

        if single_item:

            current_quantity = int(
                single_item.get(
                    "quantity",
                    1,
                )
                or 1
            )

        quantity = self._extract_quantity(
            message,
            default=current_quantity,
        )

        try:

            updated_cart = (
                update_product_in_cart(
                    cart_id=cart_id,
                    product_id=product_id,
                    quantity=quantity,
                    variant_id=variant_id,
                )
            )["cart"]

        except ValueError as exc:

            return {
                "success": False,
                "intent": "UPDATE_CART",
                "message": str(exc),
                "cart": cart,
            }

        return {
            "success": True,
            "intent": "UPDATE_CART",
            "message": (
                f"Cart updated. "
                f"Your total is "
                f"₹{float(updated_cart.get('total', 0) or 0):,.2f}."
            ),
            "cart": updated_cart,
        }

    # ========================================================
    # REMOVE FROM CART
    # ========================================================

    def remove_from_cart(
        self,
        message: str,
        cart_id: str,
    ) -> Dict[str, Any]:

        cart_result = get_buyer_cart(
            cart_id
        )

        if not cart_result.get(
            "success",
            False,
        ):

            return {
                "success": False,
                "intent": "REMOVE_FROM_CART",
                "message": (
                    "Your cart could not be found."
                ),
                "cart": None,
            }

        cart = cart_result[
            "cart"
        ]

        items = (
            cart.get(
                "items",
                [],
            )
            or []
        )

        if not items:

            return {
                "success": False,
                "intent": "REMOVE_FROM_CART",
                "message": (
                    "Your cart is already empty."
                ),
                "cart": cart,
            }

        product = self._resolve_product(
            message
        )

        single_item = (
            self._single_cart_item(
                cart
            )
        )

        if product:

            product_id = product[
                "product_id"
            ]

        elif single_item:

            product_id = single_item.get(
                "product_id"
            )

        else:

            return {
                "success": False,
                "intent": "REMOVE_FROM_CART",
                "message": (
                    "Please specify which cart item "
                    "you want to remove."
                ),
                "cart": cart,
            }

        variant_id = self._resolve_variant(
            product,
            message,
        )

        if (
            variant_id is None
            and single_item
            and single_item.get(
                "product_id"
            )
            ==
            product_id
        ):

            variant_id = single_item.get(
                "variant_id"
            )

        try:

            updated_cart = (
                remove_product_from_cart(
                    cart_id=cart_id,
                    product_id=product_id,
                    variant_id=variant_id,
                )
            )["cart"]

        except ValueError as exc:

            return {
                "success": False,
                "intent": "REMOVE_FROM_CART",
                "message": str(exc),
                "cart": cart,
            }

        return {
            "success": True,
            "intent": "REMOVE_FROM_CART",
            "message": (
                "The product was removed from your cart. "
                f"Your new total is "
                f"₹{float(updated_cart.get('total', 0) or 0):,.2f}."
            ),
            "cart": updated_cart,
        }

    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    def product_details(
        self,
        message: str,
    ) -> Dict[str, Any]:

        product = self._resolve_product(
            message
        )

        if not product:

            return {
                "success": False,
                "intent": "PRODUCT_DETAILS",
                "message": (
                    "I couldn't identify the product "
                    "you want details about."
                ),
                "products": [],
            }

        features = (
            product.get(
                "features",
                [],
            )
            or []
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

        feature_text = ""

        if features:

            feature_text = (
                " Key features: "
                +
                ", ".join(
                    map(
                        str,
                        features,
                    )
                )
                +
                "."
            )

        message_text = (
            f"{product.get('name', 'Product')} "
            f"costs ₹{price:,.2f} and has "
            f"{stock} unit(s) in stock."
            f"{feature_text}"
        )

        return {
            "success": True,
            "intent": "PRODUCT_DETAILS",
            "message": message_text,
            "products": [
                product
            ],
        }

    # ========================================================
    # RELATED PRODUCTS
    # ========================================================

    def related_products(
        self,
        message: str,
    ) -> Dict[str, Any]:

        product = self._resolve_product(
            message
        )

        if not product:

            return {
                "success": False,
                "intent": "RELATED_PRODUCTS",
                "message": (
                    "I couldn't identify the product "
                    "you want related items for."
                ),
                "products": [],
            }

        result = get_product_recommendations(
            product[
                "product_id"
            ]
        )

        related = result.get(
            "recommendations",
            [],
        ) or []

        if related:

            related_names = [
                str(
                    item.get(
                        "name",
                        "Product",
                    )
                )
                for item
                in related
            ]

            message_text = (
                f"Products related to "
                f"{product.get('name', 'this product')}: "
                +
                ", ".join(
                    related_names
                )
                +
                "."
            )

        else:

            message_text = (
                "I couldn't find related products "
                "for this item."
            )

        return {
            "success": True,
            "intent": "RELATED_PRODUCTS",
            "message": message_text,
            "products": related,
        }

    # ========================================================
    # MAIN RESPONSE
    # ========================================================

    def respond(
        self,
        message: str,
        cart_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        intent_data = self.detect_intent(
            message
        )

        intent = intent_data[
            "intent"
        ]

        # ----------------------------------------------------
        # CART OPERATIONS
        # ----------------------------------------------------

        if intent in {
            "ADD_TO_CART",
            "VIEW_CART",
            "UPDATE_CART",
            "REMOVE_FROM_CART",
        }:

            if not cart_id:

                return {
                    "success": False,
                    "intent": intent,
                    "message": (
                        "I need a buyer cart session "
                        "before I can manage your cart."
                    ),
                    "products": [],
                    "filters": {},
                    "cart": None,
                }

            if intent == "ADD_TO_CART":

                result = self.add_to_cart(
                    message,
                    cart_id,
                )

                return {
                    **result,
                    "products": [],
                    "filters": {},
                }

            if intent == "VIEW_CART":

                result = self.view_cart(
                    cart_id
                )

                return {
                    **result,
                    "products": [],
                    "filters": {},
                }

            if intent == "UPDATE_CART":

                result = self.update_cart(
                    message,
                    cart_id,
                )

                return {
                    **result,
                    "products": [],
                    "filters": {},
                }

            result = self.remove_from_cart(
                message,
                cart_id,
            )

            return {
                **result,
                "products": [],
                "filters": {},
            }

        # ----------------------------------------------------
        # PRODUCT DETAILS
        # ----------------------------------------------------

        if intent == "PRODUCT_DETAILS":

            result = self.product_details(
                message
            )

            return {
                **result,
                "filters": {},
            }

        # ----------------------------------------------------
        # RELATED PRODUCTS
        # ----------------------------------------------------

        if intent == "RELATED_PRODUCTS":

            result = self.related_products(
                message
            )

            return {
                **result,
                "filters": {},
            }

        # ----------------------------------------------------
        # PRODUCT SEARCH
        # ----------------------------------------------------

        if intent == "PRODUCT_SEARCH":

            result = self.search(
                message
            )

            return {
                "success": True,
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
                "cart": None,
            }

        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        return {
            "success": True,
            "intent": intent,
            "message": (
                "I can help you find products, "
                "compare options, discover related items, "
                "and manage your cart."
            ),
            "products": [],
            "filters": {},
            "cart": None,
        }

    # ========================================================
    # SEARCH RESPONSE
    # ========================================================

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

        features = (
            product.get(
                "features",
                [],
            )
            or []
        )

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