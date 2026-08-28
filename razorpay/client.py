from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv


load_dotenv()


class RazorpayClient:
    """
    Minimal Razorpay REST API client for MerchantOps AI.

    Uses Razorpay Test Mode credentials stored in .env.
    """

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(
        self,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
    ) -> None:

        self.key_id = (
            key_id
            or os.getenv("RAZORPAY_KEY_ID")
        )

        self.key_secret = (
            key_secret
            or os.getenv("RAZORPAY_KEY_SECRET")
        )

        if not self.key_id:
            raise ValueError(
                "RAZORPAY_KEY_ID is missing from .env"
            )

        if not self.key_secret:
            raise ValueError(
                "RAZORPAY_KEY_SECRET is missing from .env"
            )

        self.session = requests.Session()

        self.session.auth = (
            self.key_id,
            self.key_secret,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}{endpoint}"

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def create_order(
        self,
        amount: int,
        currency: str = "INR",
        receipt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order.

        amount must be supplied in the smallest currency unit.
        Example: ₹500 = 50000 paise.
        """

        payload = {
            "amount": amount,
            "currency": currency,
            "receipt": receipt
            or "merchantops_test_receipt",
        }

        return self._request(
            "POST",
            "/orders",
            json=payload,
        )

    def fetch_payments(
        self,
        count: int = 10,
    ) -> Dict[str, Any]:

        return self._request(
            "GET",
            "/payments",
            params={
                "count": count,
            },
        )

    def fetch_orders(
        self,
        count: int = 10,
    ) -> Dict[str, Any]:

        return self._request(
            "GET",
            "/orders",
            params={
                "count": count,
            },
        )

    def fetch_payment(
        self,
        payment_id: str,
    ) -> Dict[str, Any]:

        return self._request(
            "GET",
            f"/payments/{payment_id}",
        )

    def fetch_order(
        self,
        order_id: str,
    ) -> Dict[str, Any]:

        return self._request(
            "GET",
            f"/orders/{order_id}",
        )