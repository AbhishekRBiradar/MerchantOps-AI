import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


OUTPUT = Path("data/payments.csv")

random.seed(42)

payment_methods = [
    "UPI",
    "CARD",
    "NETBANKING",
    "WALLET",
]

statuses = [
    "captured",
    "failed",
]

failure_reasons = [
    "bank_error",
    "insufficient_funds",
    "network_error",
    "authentication_failed",
    "limit_exceeded",
]


def main() -> None:
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    start = datetime(2026, 8, 1)

    rows = []

    for i in range(1, 1001):

        payment_id = f"PAY{i:04d}"
        order_id = f"ORD{i:04d}"
        customer_id = f"CUST{random.randint(1, 250):04d}"

        amount = random.randint(
            499,
            9999,
        )

        method = random.choice(
            payment_methods
        )

        # Create realistic failure patterns.
        if method == "UPI":
            failed_probability = 0.18
        elif method == "CARD":
            failed_probability = 0.10
        else:
            failed_probability = 0.08

        status = (
            "failed"
            if random.random() < failed_probability
            else "captured"
        )

        if status == "failed":

            reason = random.choice(
                failure_reasons
            )

            retry_count = random.randint(
                0,
                3,
            )

        else:

            reason = ""

            retry_count = 0

        created_at = (
            start
            + timedelta(
                minutes=random.randint(
                    0,
                    30 * 24 * 31,
                )
            )
        )

        rows.append(
            {
                "payment_id": payment_id,
                "order_id": order_id,
                "customer_id": customer_id,
                "amount": amount,
                "payment_method": method,
                "status": status,
                "failure_reason": reason,
                "created_at": created_at.isoformat(),
                "retry_count": retry_count,
            }
        )

    with OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Created {len(rows)} payments."
    )

    print(
        f"Saved to: {OUTPUT}"
    )


if __name__ == "__main__":
    main()