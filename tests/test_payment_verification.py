import hashlib
import hmac

from razorpay.client import RazorpayClient


def make_signature(
    order_id: str,
    payment_id: str,
    secret: str,
) -> str:

    message = (
        f"{order_id}|{payment_id}"
    ).encode("utf-8")

    return hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def test_valid_payment_signature():

    secret = "test_secret"

    client = RazorpayClient(
        key_id="test_key",
        key_secret=secret,
    )

    order_id = "order_test_001"
    payment_id = "pay_test_001"

    signature = make_signature(
        order_id,
        payment_id,
        secret,
    )

    assert client.verify_payment_signature(
        order_id=order_id,
        payment_id=payment_id,
        signature=signature,
    ) is True


def test_invalid_payment_signature():

    client = RazorpayClient(
        key_id="test_key",
        key_secret="test_secret",
    )

    assert client.verify_payment_signature(
        order_id="order_test_001",
        payment_id="pay_test_001",
        signature="invalid_signature",
    ) is False


def test_modified_order_id_fails():

    secret = "test_secret"

    client = RazorpayClient(
        key_id="test_key",
        key_secret=secret,
    )

    signature = make_signature(
        "order_test_001",
        "pay_test_001",
        secret,
    )

    assert client.verify_payment_signature(
        order_id="order_modified",
        payment_id="pay_test_001",
        signature=signature,
    ) is False