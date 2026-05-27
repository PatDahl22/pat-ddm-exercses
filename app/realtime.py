import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

file_path = "/data/payments.csv"
last_position = 0

# Tracks recent payment timestamps per user (for frequency detection)
recent_payments = defaultdict(deque)

# Tracks last known amounts per user (for repeated amount detection)
last_amounts = defaultdict(list)

print("Realtime monitor started", flush=True)

while not os.path.exists(file_path):
    time.sleep(1)

while True:
    with open(file_path, "r") as file:
        file.seek(last_position)
        lines = file.readlines()
        last_position = file.tell()

    for line in lines:
        if line.startswith("timestamp") or not line.strip():
            continue

        timestamp, user, amount = line.strip().split(",")
        amount = int(amount)
        now = datetime.fromisoformat(timestamp)

        print(f"Realtime received: {user} {amount}", flush=True)

        # ---------------------------------------------------
        # FRAUD CHECK 1: Belopp över 3000
        # ---------------------------------------------------
        if amount > 3000:
            print(f"🚨 ALERT: High amount payment! {user} paid {amount}", flush=True)

        # ---------------------------------------------------
        # FRAUD CHECK 2: Många betalningar inom 10 sekunder
        # ---------------------------------------------------
        # Ta bort gamla timestamps utanför 10-sekunders fönstret
        while recent_payments[user] and recent_payments[user][0] < now - timedelta(seconds=10):
            recent_payments[user].popleft()

        # Lägg till nuvarande timestamp 
        recent_payments[user].append(now)

        if len(recent_payments[user]) >= 3:
            print(f"🚨 ALERT: Many payments in short time! {user} made {len(recent_payments[user])} payments in 10 seconds", flush=True)

        # ---------------------------------------------------
        # FRAUD CHECK 3: Upprepade belopp
        # ---------------------------------------------------
        last_amounts[user].append(amount)

        # Behåll bara de 3 senaste beloppen per användare
        if len(last_amounts[user]) > 3:
            last_amounts[user].pop(0)

        # Om de 3 senaste beloppen är identiska → misstänkt
        if len(last_amounts[user]) == 3 and len(set(last_amounts[user])) == 1:
            print(f"🚨 ALERT: Repeated amount detected! {user} sent {amount} three times in a row", flush=True)

    time.sleep(1)
