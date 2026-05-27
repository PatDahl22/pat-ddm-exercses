import csv
import random
import time
from datetime import datetime

users = ["alice", "bob", "charlie", "diana"]
file_path = "/data/payments.csv"

with open(file_path, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["timestamp", "user", "amount"])
    writer.writeheader()

print("Generator started (FAST MODE - backpressure simulation)", flush=True)

counter = 0

while True:
    payment = {
        "timestamp": datetime.now().isoformat(),
        "user": random.choice(users),
        "amount": random.randint(10, 5000),
    }

    with open(file_path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "user", "amount"])
        writer.writerow(payment)

    counter += 1

    # Print every 100 events so the terminal doesn't flood completely
    if counter % 100 == 0:
        print(f"Generated {counter} events so far...", flush=True)

    # 0.01 seconds = 100 events per second (vs 1 event per second before)
    time.sleep(0.01)
