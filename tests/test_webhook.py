import hashlib
import hmac

from razorpay.webhook import (
    RazorpayWebhookVerifier,
)


def test_valid_webhook_signature():

    secret = "test_webhook_secret"

    payload = (
        b'{"event":"payment.failed"}'
    )

    signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    verifier = RazorpayWebhookVerifier(
        webhook_secret=secret
    )

    assert verifier.verify(
        payload,
        signature,
    ) is True


def test_invalid_webhook_signature():

    secret = "test_webhook_secret"

    payload = (
        b'{"event":"payment.failed"}'
    )

    verifier = RazorpayWebhookVerifier(
        webhook_secret=secret
    )

    assert verifier.verify(
        payload,
        "invalid_signature",
    ) is False


def test_modified_payload_fails():

    secret = "test_webhook_secret"

    original_payload = (
        b'{"event":"payment.failed"}'
    )

    modified_payload = (
        b'{"event":"payment.captured"}'
    )

    signature = hmac.new(
        secret.encode("utf-8"),
        original_payload,
        hashlib.sha256,
    ).hexdigest()

    verifier = RazorpayWebhookVerifier(
        webhook_secret=secret
    )

    assert verifier.verify(
        modified_payload,
        signature,
    ) is False