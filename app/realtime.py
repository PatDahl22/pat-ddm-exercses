import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

file_path = "/data/payments.csv"
error_log_path = "/data/errors.log"
lag_log_path = "/data/lag.log"
last_position = 0

# Tracks recent payment timestamps per user (for frequency detection)
recent_payments = defaultdict(deque)

# Tracks last known amounts per user (for repeated amount detection)
last_amounts = defaultdict(list)

# Backpressure metrics
processed_count = 0
total_lag_seconds = 0.0
max_lag_seconds = 0.0

print("Realtime monitor started", flush=True)

while not os.path.exists(file_path):
    time.sleep(1)


def log_error(reason, raw_line):
    """Write invalid events to error log with timestamp and reason."""
    with open(error_log_path, "a") as log:
        log.write(f"[{datetime.now().isoformat()}] ERROR: {reason} | raw: {raw_line.strip()}\n")
    print(f"❌ REJECTED: {reason} | {raw_line.strip()}", flush=True)


def log_lag(lag_seconds, queue_size):
    """Write lag metrics to lag log."""
    with open(lag_log_path, "a") as log:
        log.write(f"[{datetime.now().isoformat()}] LAG: {lag_seconds:.2f}s | queue: {queue_size} unread lines\n")


def validate_event(timestamp, user, amount_str):
    """Validate event fields. Returns (is_valid, reason)."""
    if not timestamp or not timestamp.strip():
        return False, "Missing timestamp"

    try:
        datetime.fromisoformat(timestamp.strip())
    except ValueError:
        return False, f"Invalid timestamp format: {timestamp}"

    if not user or not user.strip():
        return False, "Missing or null user"

    try:
        amount = int(amount_str.strip())
    except ValueError:
        return False, f"Invalid amount (not a number): {amount_str}"

    if amount <= 0:
        return False, f"Invalid amount (must be positive): {amount}"

    return True, None


while True:
    with open(file_path, "r") as file:
        file.seek(last_position)
        lines = file.readlines()
        last_position = file.tell()

    queue_size = len(lines)

    # ---------------------------------------------------
    # BACKPRESSURE WARNING: Show how many unread lines
    # ---------------------------------------------------
    if queue_size > 50:
        print(f"⚠️  BACKPRESSURE: {queue_size} unprocessed lines in queue!", flush=True)
        log_lag(0, queue_size)

    for line in lines:
        if line.startswith("timestamp") or not line.strip():
            continue

        # ---------------------------------------------------
        # SCHEMA VALIDATION: Check correct number of fields
        # ---------------------------------------------------
        parts = line.strip().split(",")
        if len(parts) != 3:
            log_error("Wrong number of fields", line)
            continue

        timestamp, user, amount_str = parts

        # ---------------------------------------------------
        # FIELD VALIDATION
        # ---------------------------------------------------
        is_valid, reason = validate_event(timestamp, user, amount_str)
        if not is_valid:
            log_error(reason, line)
            continue

        # All checks passed — process the event
        amount = int(amount_str.strip())
        now = datetime.fromisoformat(timestamp.strip())

        # ---------------------------------------------------
        # LAG MEASUREMENT: How old is this event?
        # ---------------------------------------------------
        lag = (datetime.now() - now).total_seconds()
        if lag > 0:
            total_lag_seconds += lag
            processed_count += 1
            if lag > max_lag_seconds:
                max_lag_seconds = lag

            if lag > 2.0:
                print(f"🐢 HIGH LAG: {user} event is {lag:.1f}s old", flush=True)
                log_lag(lag, queue_size)

        # ---------------------------------------------------
        # FRAUD CHECK 1: Belopp över 3000
        # ---------------------------------------------------
        if amount > 3000:
            print(f"🚨 ALERT: High amount payment! {user} paid {amount}", flush=True)

        # ---------------------------------------------------
        # FRAUD CHECK 2: Många betalningar inom 10 sekunder
        # ---------------------------------------------------
        while recent_payments[user] and recent_payments[user][0] < now - timedelta(seconds=10):
            recent_payments[user].popleft()

        recent_payments[user].append(now)

        if len(recent_payments[user]) >= 3:
            print(f"🚨 ALERT: Many payments in short time! {user} made {len(recent_payments[user])} payments in 10 seconds", flush=True)

        # ---------------------------------------------------
        # FRAUD CHECK 3: Upprepade belopp
        # ---------------------------------------------------
        last_amounts[user].append(amount)

        if len(last_amounts[user]) > 3:
            last_amounts[user].pop(0)

        if len(last_amounts[user]) == 3 and len(set(last_amounts[user])) == 1:
            print(f"🚨 ALERT: Repeated amount detected! {user} sent {amount} three times in a row", flush=True)

    # ---------------------------------------------------
    # SUMMARY every 100 processed events
    # ---------------------------------------------------
    if processed_count > 0 and processed_count % 100 == 0:
        avg_lag = round(total_lag_seconds / processed_count, 2)
        print(f"\n📈 BACKPRESSURE SUMMARY: processed={processed_count} | avg_lag={avg_lag}s | max_lag={max_lag_seconds:.2f}s\n", flush=True)

    time.sleep(1)
