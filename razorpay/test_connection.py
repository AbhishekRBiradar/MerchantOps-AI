from client import RazorpayClient


def main() -> None:
    client = RazorpayClient()

    result = client.fetch_payments(count=10)

    items = result.get("items", [])

    print("Razorpay Test API connection successful.")
    print(f"Payments returned: {len(items)}")

    for payment in items[:3]:
        print(
            payment.get("id"),
            payment.get("status"),
            payment.get("amount"),
            payment.get("method"),
        )


if __name__ == "__main__":
    main()