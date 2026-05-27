import csv
import random
import time
from datetime import datetime

users = ["alice", "bob", "charlie", "diana"]
file_path = "/data/payments.csv"

with open(file_path, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["timestamp", "user", "amount"])
    writer.writeheader()

print("Generator started", flush=True)

while True:
    # Inject a broken event roughly 1 in 5 times
    if random.random() < 0.2:
        broken_type = random.choice(["null_user", "invalid_amount", "missing_field"])

        if broken_type == "null_user":
            payment = {
                "timestamp": datetime.now().isoformat(),
                "user": "",
                "amount": random.randint(10, 5000),
            }
        elif broken_type == "invalid_amount":
            payment = {
                "timestamp": datetime.now().isoformat(),
                "user": random.choice(users),
                "amount": "INVALID",
            }
        else:
            # Missing field — write raw broken line directly
            with open(file_path, "a") as f:
                f.write(f"{datetime.now().isoformat()},\n")
            print("Generated broken event: missing field", flush=True)
            time.sleep(1)
            continue

        with open(file_path, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "user", "amount"])
            writer.writerow(payment)

        print(f"Generated broken event: {broken_type} → {payment}", flush=True)

    else:
        payment = {
            "timestamp": datetime.now().isoformat(),
            "user": random.choice(users),
            "amount": random.randint(10, 5000),
        }

        with open(file_path, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "user", "amount"])
            writer.writerow(payment)

        print("Generated:", payment, flush=True)

    time.sleep(1)
