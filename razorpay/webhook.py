from __future__ import annotations

import hashlib
import hmac
import os
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


class RazorpayWebhookVerifier:
    """
    Verifies Razorpay webhook signatures.

    The webhook secret must remain server-side in .env.
    """

    def __init__(
        self,
        webhook_secret: Optional[str] = None,
    ) -> None:

        self.webhook_secret = (
            webhook_secret
            or os.getenv(
                "RAZORPAY_WEBHOOK_SECRET"
            )
        )

        if not self.webhook_secret:
            raise ValueError(
                "RAZORPAY_WEBHOOK_SECRET "
                "is missing from .env"
            )

    def verify(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify the Razorpay webhook signature.

        payload:
            Exact raw HTTP request body.

        signature:
            Value of the X-Razorpay-Signature header.
        """

        expected_signature = hmac.new(
            self.webhook_secret.encode(
                "utf-8"
            ),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            expected_signature,
            signature,
        )


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    webhook_secret: Optional[str] = None,
) -> bool:
    """
    Convenience function for webhook verification.
    """

    verifier = RazorpayWebhookVerifier(
        webhook_secret=webhook_secret
    )

    return verifier.verify(
        payload,
        signature,
    )