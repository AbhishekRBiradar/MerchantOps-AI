from __future__ import annotations

import os

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import psycopg

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


class PostgresDatabase:
    """
    PostgreSQL persistence layer for MerchantOps AI.

    Production:
        Uses DATABASE_URL.

    Stores:
        - audit_logs
        - webhook_events
        - merchant_orders

    Merchant orders store the complete commercial breakdown:

        product
        quantity
        unit price
        subtotal
        discount
        tax
        final amount
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
    ) -> None:

        self.database_url = (
            database_url
            or os.getenv(
                "DATABASE_URL"
            )
        )

        if not self.database_url:

            raise ValueError(
                "DATABASE_URL is missing."
            )

    # ========================================================
    # CONNECTION
    # ========================================================

    def connect(self):

        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    def initialize(self) -> None:
        """
        Create all MerchantOps tables and migrate the
        merchant_orders table when older installations are used.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                # ====================================================
                # AUDIT LOGS
                # ====================================================

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id BIGSERIAL PRIMARY KEY,

                        timestamp TIMESTAMPTZ NOT NULL,

                        event_type TEXT NOT NULL,

                        payment_id TEXT,

                        decision TEXT,

                        action TEXT,

                        risk_level TEXT,

                        approval_required BOOLEAN,

                        execution_mode TEXT,

                        status TEXT NOT NULL,

                        details JSONB NOT NULL
                            DEFAULT '{}'::jsonb
                    );
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_payment_id
                    ON audit_logs(payment_id);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_event_type
                    ON audit_logs(event_type);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_timestamp
                    ON audit_logs(timestamp DESC);
                    """
                )

                # ====================================================
                # WEBHOOK EVENTS
                # ====================================================

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS webhook_events (
                        event_id TEXT PRIMARY KEY,

                        event_name TEXT NOT NULL,

                        payment_id TEXT,

                        created_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW()
                    );
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_payment_id
                    ON webhook_events(payment_id);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_created_at
                    ON webhook_events(created_at DESC);
                    """
                )

                                # ====================================================
                # PRODUCT CATALOG
                # ====================================================

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS catalog_products (
                        id BIGSERIAL PRIMARY KEY,

                        product_id TEXT UNIQUE NOT NULL,

                        name TEXT NOT NULL,

                        category TEXT NOT NULL,

                        price NUMERIC(12, 2)
                            NOT NULL
                            DEFAULT 0,

                        currency TEXT NOT NULL
                            DEFAULT 'INR',

                        stock INTEGER
                            NOT NULL
                            DEFAULT 0,

                        description TEXT,

                        features JSONB NOT NULL
                            DEFAULT '[]'::jsonb,

                        tags JSONB NOT NULL
                            DEFAULT '[]'::jsonb,

                        variants JSONB NOT NULL
                            DEFAULT '[]'::jsonb,

                        related_products JSONB NOT NULL
                            DEFAULT '[]'::jsonb,

                        created_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW(),

                        updated_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW()
                    );
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_catalog_products_category
                    ON catalog_products(category);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_catalog_products_name
                    ON catalog_products(name);
                    """
                )

                # ====================================================
                # MERCHANT ORDERS
                # ====================================================

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS merchant_orders (
                        id BIGSERIAL PRIMARY KEY,

                        order_id TEXT UNIQUE NOT NULL,

                        customer_name TEXT,

                        customer_email TEXT,

                        customer_phone TEXT,

                        product_name TEXT,

                        quantity INTEGER
                            NOT NULL
                            DEFAULT 1,

                        unit_price NUMERIC(12, 2)
                            NOT NULL
                            DEFAULT 0,

                        subtotal NUMERIC(12, 2)
                            NOT NULL
                            DEFAULT 0,

                        discount NUMERIC(12, 2)
                            NOT NULL
                            DEFAULT 0,

                        tax NUMERIC(12, 2)
                            NOT NULL
                            DEFAULT 0,

                        amount NUMERIC(12, 2)
                            NOT NULL,

                        currency TEXT NOT NULL
                            DEFAULT 'INR',

                        description TEXT,

                        status TEXT NOT NULL
                            DEFAULT 'CREATED',

                        payment_id TEXT,

                        created_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW(),

                        updated_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW()
                    );
                    """
                )

                # ====================================================
                # MIGRATION FOR EXISTING DATABASES
                # ====================================================
                #
                # If merchant_orders already existed before the
                # commercial breakdown fields were introduced,
                # add the missing columns without deleting data.
                #
                # ====================================================

                cursor.execute(
                    """
                    ALTER TABLE merchant_orders
                    ADD COLUMN IF NOT EXISTS
                    product_name TEXT;
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE merchant_orders
                    ADD COLUMN IF NOT EXISTS
                    quantity INTEGER
                    NOT NULL
                    DEFAULT 1;
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE merchant_orders
                    ADD COLUMN IF NOT EXISTS
                    unit_price NUMERIC(12, 2)
                    NOT NULL
                    DEFAULT 0;
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE merchant_orders
                    ADD COLUMN IF NOT EXISTS
                    subtotal NUMERIC(12, 2)
                    NOT NULL
                    DEFAULT 0;
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE merchant_orders
                    ADD COLUMN IF NOT EXISTS
                    discount NUMERIC(12, 2)
                    NOT NULL
                    DEFAULT 0;
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE merchant_orders
                    ADD COLUMN IF NOT EXISTS
                    tax NUMERIC(12, 2)
                    NOT NULL
                    DEFAULT 0;
                    """
                )

                # ====================================================
                # MERCHANT ORDER INDEXES
                # ====================================================

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_merchant_orders_payment_id
                    ON merchant_orders(payment_id);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_merchant_orders_status
                    ON merchant_orders(status);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_merchant_orders_created_at
                    ON merchant_orders(created_at DESC);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_merchant_orders_customer_email
                    ON merchant_orders(customer_email);
                    """
                )

            connection.commit()

    # ========================================================
    # INSERT AUDIT EVENT
    # ========================================================

    def insert_audit_event(
        self,
        event: Dict[str, Any],
    ) -> None:

        details = event.get(
            "details",
            {},
        )

        if details is None:
            details = {}

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO audit_logs (
                        timestamp,
                        event_type,
                        payment_id,
                        decision,
                        action,
                        risk_level,
                        approval_required,
                        execution_mode,
                        status,
                        details
                    )
                    VALUES (
                        %(timestamp)s,
                        %(event_type)s,
                        %(payment_id)s,
                        %(decision)s,
                        %(action)s,
                        %(risk_level)s,
                        %(approval_required)s,
                        %(execution_mode)s,
                        %(status)s,
                        %(details)s
                    )
                    """,
                    {
                        "timestamp":
                            event.get(
                                "timestamp"
                            ),

                        "event_type":
                            event.get(
                                "event_type"
                            ),

                        "payment_id":
                            event.get(
                                "payment_id"
                            ),

                        "decision":
                            event.get(
                                "decision"
                            ),

                        "action":
                            event.get(
                                "action"
                            ),

                        "risk_level":
                            event.get(
                                "risk_level"
                            ),

                        "approval_required":
                            event.get(
                                "approval_required"
                            ),

                        "execution_mode":
                            event.get(
                                "execution_mode"
                            ),

                        "status":
                            event.get(
                                "status",
                                "RECORDED",
                            ),

                        "details":
                            Jsonb(details),
                    },
                )

            connection.commit()

    # ========================================================
    # READ ALL AUDIT EVENTS
    # ========================================================

    def read_audit_events(
        self,
    ) -> List[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        timestamp,
                        event_type,
                        payment_id,
                        decision,
                        action,
                        risk_level,
                        approval_required,
                        execution_mode,
                        status,
                        details
                    FROM audit_logs
                    ORDER BY id ASC
                    """
                )

                rows = cursor.fetchall()

        events: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            event = dict(row)

            timestamp = event.get(
                "timestamp"
            )

            if timestamp is not None:

                event[
                    "timestamp"
                ] = timestamp.isoformat()

            events.append(
                event
            )

        return events

    # ========================================================
    # READ RECENT AUDIT EVENTS
    # ========================================================

    def read_recent_audit_events(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:

        limit = max(
            1,
            min(
                int(limit),
                1000,
            ),
        )

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        timestamp,
                        event_type,
                        payment_id,
                        decision,
                        action,
                        risk_level,
                        approval_required,
                        execution_mode,
                        status,
                        details
                    FROM audit_logs
                    ORDER BY
                        timestamp DESC,
                        id DESC
                    LIMIT %s
                    """,
                    (
                        limit,
                    ),
                )

                rows = cursor.fetchall()

        events: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            event = dict(row)

            timestamp = event.get(
                "timestamp"
            )

            if timestamp is not None:

                event[
                    "timestamp"
                ] = timestamp.isoformat()

            events.append(
                event
            )

        return events

    # ========================================================
    # WEBHOOK EXISTS
    # ========================================================

    def webhook_exists(
        self,
        event_id: str,
    ) -> bool:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1
                        FROM webhook_events
                        WHERE event_id = %s
                    ) AS exists
                    """,
                    (
                        event_id,
                    ),
                )

                row = cursor.fetchone()

        return bool(
            row["exists"]
        )

    # ========================================================
    # RECORD WEBHOOK
    # ========================================================

    def record_webhook(
        self,
        event_id: str,
        event_name: str,
        payment_id: Optional[str] = None,
    ) -> None:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO webhook_events (
                        event_id,
                        event_name,
                        payment_id
                    )
                    VALUES (
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (
                        event_id
                    )
                    DO NOTHING
                    """,
                    (
                        event_id,
                        event_name,
                        payment_id,
                    ),
                )

            connection.commit()

    # ========================================================
    # READ WEBHOOK EVENTS
    # ========================================================

    def read_webhook_events(
        self,
    ) -> List[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        event_id,
                        event_name,
                        payment_id,
                        created_at
                    FROM webhook_events
                    ORDER BY
                        created_at DESC
                    """
                )

                rows = cursor.fetchall()

        events: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            event = dict(row)

            created_at = event.get(
                "created_at"
            )

            if created_at is not None:

                event[
                    "created_at"
                ] = created_at.isoformat()

            events.append(
                event
            )

        return events

    # ========================================================
    # BASIC DATABASE STATS
    # ========================================================

    def get_stats(
        self,
    ) -> Dict[str, int]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS count
                    FROM audit_logs
                    """
                )

                audit_row = (
                    cursor.fetchone()
                )

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS count
                    FROM webhook_events
                    """
                )

                webhook_row = (
                    cursor.fetchone()
                )

        return {

            "audit_logs":
                int(
                    audit_row["count"]
                    or 0
                ),

            "webhook_events":
                int(
                    webhook_row["count"]
                    or 0
                ),
        }

    # ========================================================
    # ACTIVITY STATISTICS
    # ========================================================

    def get_activity_stats(
        self,
    ) -> Dict[str, int]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT

                        COUNT(*) FILTER (
                            WHERE event_type =
                            'PAYMENT_VERIFICATION'
                        ) AS verification_events,

                        COUNT(*) FILTER (
                            WHERE event_type =
                            'PAYMENT_VERIFICATION'
                            AND status =
                            'VERIFIED'
                        ) AS verified_payments,

                        COUNT(*) FILTER (
                            WHERE event_type =
                            'WEBHOOK_PROCESSING'
                        ) AS webhook_processing

                    FROM audit_logs
                    """
                )

                row = (
                    cursor.fetchone()
                )

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS webhook_events
                    FROM webhook_events
                    """
                )

                webhook_row = (
                    cursor.fetchone()
                )

        return {

            "verified_payments":
                int(
                    row[
                        "verified_payments"
                    ]
                    or 0
                ),

            "verification_events":
                int(
                    row[
                        "verification_events"
                    ]
                    or 0
                ),

            "webhook_events":
                int(
                    webhook_row[
                        "webhook_events"
                    ]
                    or 0
                ),

            "webhook_processing":
                int(
                    row[
                        "webhook_processing"
                    ]
                    or 0
                ),
        }

    # ========================================================
    # NORMALIZE MERCHANT ORDER
    # ========================================================

    @staticmethod
    def _normalize_merchant_order(
        row: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:

        if row is None:

            return None

        result = dict(
            row
        )

        # ----------------------------------------------------
        # Numeric fields
        # ----------------------------------------------------

        numeric_fields = [

            "quantity",
            "unit_price",
            "subtotal",
            "discount",
            "tax",
            "amount",

        ]

        for field in numeric_fields:

            value = result.get(
                field
            )

            if value is None:

                continue

            if field == "quantity":

                result[
                    field
                ] = int(
                    value
                )

            else:

                result[
                    field
                ] = float(
                    value
                )

        # ----------------------------------------------------
        # Datetimes
        # ----------------------------------------------------

        for field in [
            "created_at",
            "updated_at",
        ]:

            timestamp = result.get(
                field
            )

            if timestamp is not None:

                result[
                    field
                ] = timestamp.isoformat()

        return result
        # ========================================================
    # CREATE / UPDATE CATALOG PRODUCT
    # ========================================================

    def upsert_catalog_product(
        self,
        product_id: str,
        name: str,
        category: str,
        price: float = 0.0,
        currency: str = "INR",
        stock: int = 0,
        description: Optional[str] = None,
        features: Optional[List[Any]] = None,
        tags: Optional[List[Any]] = None,
        variants: Optional[List[Dict[str, Any]]] = None,
        related_products: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        product_id = str(
            product_id
        ).strip()

        name = str(
            name
        ).strip()

        category = str(
            category
        ).strip()

        if not product_id:
            raise ValueError(
                "product_id is required."
            )

        if not name:
            raise ValueError(
                "name is required."
            )

        if not category:
            raise ValueError(
                "category is required."
            )

        price = float(
            price
        )

        stock = int(
            stock
        )

        if price < 0:
            raise ValueError(
                "price cannot be negative."
            )

        if stock < 0:
            raise ValueError(
                "stock cannot be negative."
            )

        features = (
            features
            if features is not None
            else []
        )

        tags = (
            tags
            if tags is not None
            else []
        )

        variants = (
            variants
            if variants is not None
            else []
        )

        related_products = (
            related_products
            if related_products is not None
            else []
        )

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO catalog_products (
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        features,
                        tags,
                        variants,
                        related_products
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::jsonb,
                        %s::jsonb,
                        %s::jsonb,
                        %s::jsonb,
                        %s::jsonb
                    )
                    ON CONFLICT (product_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        category = EXCLUDED.category,
                        price = EXCLUDED.price,
                        currency = EXCLUDED.currency,
                        stock = EXCLUDED.stock,
                        description = EXCLUDED.description,
                        features = EXCLUDED.features,
                        tags = EXCLUDED.tags,
                        variants = EXCLUDED.variants,
                        related_products =
                            EXCLUDED.related_products,
                        updated_at = NOW()
                    RETURNING
                        id,
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        features,
                        tags,
                        variants,
                        related_products,
                        created_at,
                        updated_at
                    """,
                    (
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        json.dumps(features),
                        json.dumps(tags),
                        json.dumps(variants),
                        json.dumps(related_products),
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        return (
            self._normalize_catalog_product(
                row
            )
            or {}
        )

    # ========================================================
    # GET CATALOG PRODUCT
    # ========================================================

    def get_catalog_product(
        self,
        product_id: str,
    ) -> Optional[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        features,
                        tags,
                        variants,
                        related_products,
                        created_at,
                        updated_at
                    FROM catalog_products
                    WHERE product_id = %s
                    LIMIT 1
                    """,
                    (
                        product_id,
                    ),
                )

                row = cursor.fetchone()

        return (
            self._normalize_catalog_product(
                row
            )
        )

    # ========================================================
    # LIST CATALOG PRODUCTS
    # ========================================================

    def list_catalog_products(
        self,
    ) -> List[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        features,
                        tags,
                        variants,
                        related_products,
                        created_at,
                        updated_at
                    FROM catalog_products
                    ORDER BY created_at DESC
                    """
                )

                rows = cursor.fetchall()

        return [
            self._normalize_catalog_product(
                row
            )
            for row in rows
        ]

    # ========================================================
    # SEARCH CATALOG
    # ========================================================

    def search_catalog_products(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:

        query = (
            str(query or "")
            .strip()
        )

        if not query:
            return self.list_catalog_products()

        pattern = f"%{query}%"

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        features,
                        tags,
                        variants,
                        related_products,
                        created_at,
                        updated_at
                    FROM catalog_products
                    WHERE
                        product_id ILIKE %s
                        OR name ILIKE %s
                        OR category ILIKE %s
                        OR description ILIKE %s
                    ORDER BY created_at DESC
                    """,
                    (
                        pattern,
                        pattern,
                        pattern,
                        pattern,
                    ),
                )

                rows = cursor.fetchall()

        return [
            self._normalize_catalog_product(
                row
            )
            for row in rows
        ]

    # ========================================================
    # CATEGORY PRODUCTS
    # ========================================================

    def list_catalog_category(
        self,
        category: str,
    ) -> List[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        product_id,
                        name,
                        category,
                        price,
                        currency,
                        stock,
                        description,
                        features,
                        tags,
                        variants,
                        related_products,
                        created_at,
                        updated_at
                    FROM catalog_products
                    WHERE LOWER(category) = LOWER(%s)
                    ORDER BY created_at DESC
                    """,
                    (
                        category,
                    ),
                )

                rows = cursor.fetchall()

        return [
            self._normalize_catalog_product(
                row
            )
            for row in rows
        ]

    # ========================================================
    # CATALOG PRODUCT NORMALIZER
    # ========================================================

    def _normalize_catalog_product(
        self,
        row: Any,
    ) -> Optional[Dict[str, Any]]:

        if not row:
            return None

        result = dict(
            row
        )

        for field in [
            "features",
            "tags",
            "variants",
            "related_products",
        ]:

            if result.get(field) is None:
                result[field] = []

        for field in [
            "created_at",
            "updated_at",
        ]:

            timestamp = result.get(
                field
            )

            if timestamp is not None:
                result[field] = (
                    timestamp.isoformat()
                )

        return result

    # ========================================================
    # CREATE MERCHANT ORDER
    # ========================================================

    def create_merchant_order(
        self,
        order_id: str,
        amount: float,
        currency: str = "INR",
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        product_name: Optional[str] = None,
        quantity: int = 1,
        unit_price: float = 0.0,
        subtotal: Optional[float] = None,
        discount: float = 0.0,
        tax: float = 0.0,
        description: Optional[str] = None,
        status: str = "CREATED",
    ) -> Dict[str, Any]:
        """
        Create or update a merchant order.

        Financial structure:

            subtotal = quantity × unit_price

            final amount =
                subtotal - discount + tax

        The caller should pass the same final amount used
        to create the Razorpay order.
        """

        quantity = int(
            quantity
        )

        if quantity <= 0:

            raise ValueError(
                "quantity must be greater than zero."
            )

        unit_price = float(
            unit_price
        )

        discount = float(
            discount
        )

        tax = float(
            tax
        )

        amount = float(
            amount
        )

        if subtotal is None:

            subtotal = (
                quantity
                *
                unit_price
            )

        subtotal = float(
            subtotal
        )

        calculated_amount = (
            subtotal
            -
            discount
            +
            tax
        )

        # ----------------------------------------------------
        # Financial consistency
        # ----------------------------------------------------

        if abs(
            calculated_amount
            -
            amount
        ) > 0.01:

            raise ValueError(
                (
                    "Merchant order amount mismatch. "
                    f"Expected ₹{calculated_amount:.2f}, "
                    f"received ₹{amount:.2f}."
                )
            )

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO merchant_orders (

                        order_id,

                        customer_name,

                        customer_email,

                        customer_phone,

                        product_name,

                        quantity,

                        unit_price,

                        subtotal,

                        discount,

                        tax,

                        amount,

                        currency,

                        description,

                        status

                    )
                    VALUES (

                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s

                    )

                    ON CONFLICT (
                        order_id
                    )
                    DO UPDATE SET

                        customer_name =
                            EXCLUDED.customer_name,

                        customer_email =
                            EXCLUDED.customer_email,

                        customer_phone =
                            EXCLUDED.customer_phone,

                        product_name =
                            EXCLUDED.product_name,

                        quantity =
                            EXCLUDED.quantity,

                        unit_price =
                            EXCLUDED.unit_price,

                        subtotal =
                            EXCLUDED.subtotal,

                        discount =
                            EXCLUDED.discount,

                        tax =
                            EXCLUDED.tax,

                        amount =
                            EXCLUDED.amount,

                        currency =
                            EXCLUDED.currency,

                        description =
                            EXCLUDED.description,

                        status =
                            EXCLUDED.status,

                        updated_at =
                            NOW()

                    RETURNING

                        id,

                        order_id,

                        customer_name,

                        customer_email,

                        customer_phone,

                        product_name,

                        quantity,

                        unit_price,

                        subtotal,

                        discount,

                        tax,

                        amount,

                        currency,

                        description,

                        status,

                        payment_id,

                        created_at,

                        updated_at

                    """,

                    (
                        order_id,
                        customer_name,
                        customer_email,
                        customer_phone,
                        product_name,
                        quantity,
                        unit_price,
                        subtotal,
                        discount,
                        tax,
                        amount,
                        currency,
                        description,
                        status,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        return (
            self._normalize_merchant_order(
                row
            )
            or
            {}
        )

    # ========================================================
    # GET MERCHANT ORDER
    # ========================================================

    def get_merchant_order(
        self,
        order_id: str,
    ) -> Optional[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT

                        id,

                        order_id,

                        customer_name,

                        customer_email,

                        customer_phone,

                        product_name,

                        quantity,

                        unit_price,

                        subtotal,

                        discount,

                        tax,

                        amount,

                        currency,

                        description,

                        status,

                        payment_id,

                        created_at,

                        updated_at

                    FROM merchant_orders

                    WHERE order_id = %s

                    LIMIT 1
                    """,
                    (
                        order_id,
                    ),
                )

                row = cursor.fetchone()

        return (
            self._normalize_merchant_order(
                row
            )
        )

    # ========================================================
    # UPDATE MERCHANT ORDER
    # ========================================================

    def update_merchant_order(
        self,
        order_id: str,
        status: Optional[str] = None,
        payment_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        fields: List[str] = []

        values: List[Any] = []

        if status is not None:

            fields.append(
                "status = %s"
            )

            values.append(
                status
            )

        if payment_id is not None:

            fields.append(
                "payment_id = %s"
            )

            values.append(
                payment_id
            )

        if not fields:

            return (
                self.get_merchant_order(
                    order_id
                )
            )

        fields.append(
            "updated_at = NOW()"
        )

        values.append(
            order_id
        )

        query = f"""
            UPDATE merchant_orders
            SET
                {", ".join(fields)}
            WHERE order_id = %s
            RETURNING

                id,

                order_id,

                customer_name,

                customer_email,

                customer_phone,

                product_name,

                quantity,

                unit_price,

                subtotal,

                discount,

                tax,

                amount,

                currency,

                description,

                status,

                payment_id,

                created_at,

                updated_at
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    tuple(
                        values
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        return (
            self._normalize_merchant_order(
                row
            )
        )

    # ========================================================
    # LIST MERCHANT ORDERS
    # ========================================================

    def list_merchant_orders(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:

        limit = max(
            1,
            min(
                int(limit),
                1000,
            ),
        )

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT

                        id,

                        order_id,

                        customer_name,

                        customer_email,

                        customer_phone,

                        product_name,

                        quantity,

                        unit_price,

                        subtotal,

                        discount,

                        tax,

                        amount,

                        currency,

                        description,

                        status,

                        payment_id,

                        created_at,

                        updated_at

                    FROM merchant_orders

                    ORDER BY
                        created_at DESC,
                        id DESC

                    LIMIT %s
                    """,
                    (
                        limit,
                    ),
                )

                rows = cursor.fetchall()

        orders: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            normalized = (
                self._normalize_merchant_order(
                    row
                )
            )

            if normalized is not None:

                orders.append(
                    normalized
                )

        return orders

    # ========================================================
    # COMPATIBILITY ALIASES
    # ========================================================

    def insert_webhook_event(
        self,
        event_id: str,
        event_name: str,
        payment_id: Optional[str] = None,
    ) -> None:

        self.record_webhook(
            event_id=
                event_id,
            event_name=
                event_name,
            payment_id=
                payment_id,
        )

    def webhook_event_exists(
        self,
        event_id: str,
    ) -> bool:

        return self.webhook_exists(
            event_id
        )