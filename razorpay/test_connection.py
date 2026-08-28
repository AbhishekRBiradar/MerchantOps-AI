from client import RazorpayClient


def main():
    client = RazorpayClient()

    result = client.fetch_payments(count=5)

    print("Razorpay Test API connection successful.")
    print(
        "Payments returned:",
        len(result.get("items", []))
    )


if __name__ == "__main__":
    main()