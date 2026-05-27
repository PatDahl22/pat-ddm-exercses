import csv
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

file_path = "/data/payments.csv"
reports_dir = "/data/reports"
BATCH_INTERVAL_SECONDS = 30

os.makedirs(reports_dir, exist_ok=True)

print("Batch job started", flush=True)

while not os.path.exists(file_path):
    time.sleep(1)


def export_json(report, filename):
    """Export report as JSON file."""
    path = os.path.join(reports_dir, filename)
    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"📁 Exported JSON: {path}", flush=True)


def export_csv(rows, fieldnames, filename):
    """Export report rows as CSV file."""
    path = os.path.join(reports_dir, filename)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"📁 Exported CSV: {path}", flush=True)


while True:
    time.sleep(BATCH_INTERVAL_SECONDS)
    window_end = datetime.now()
    window_start = window_end - timedelta(seconds=BATCH_INTERVAL_SECONDS)
    timestamp_label = window_end.strftime("%Y%m%d_%H%M%S")

    payments = []

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                event_time = datetime.fromisoformat(row["timestamp"])
                amount = int(row["amount"])
            except (KeyError, ValueError):
                continue

            if window_start <= event_time <= window_end:
                row["amount"] = amount
                row["hour"] = event_time.strftime("%Y-%m-%d %H:00")
                payments.append(row)

    print("\n📊 BATCH REPORT", flush=True)
    print(f"Window: {window_start.isoformat()} -> {window_end.isoformat()}", flush=True)

    if not payments:
        print("No transactions in this window", flush=True)
        print("-" * 40, flush=True)
        continue

    # ---------------------------------------------------
    # 1. Grundläggande statistik
    # ---------------------------------------------------
    total = sum(p["amount"] for p in payments)
    count = len(payments)
    average = round(total / count, 2)

    # ---------------------------------------------------
    # 2. Revenue per user
    # ---------------------------------------------------
    revenue_per_user = defaultdict(int)
    count_per_user = defaultdict(int)
    for p in payments:
        revenue_per_user[p["user"]] += p["amount"]
        count_per_user[p["user"]] += 1

    # ---------------------------------------------------
    # 3. Average transaction per user
    # ---------------------------------------------------
    avg_per_user = {
        user: round(revenue_per_user[user] / count_per_user[user], 2)
        for user in revenue_per_user
    }

    # ---------------------------------------------------
    # 4. Top spender (högst total revenue)
    # ---------------------------------------------------
    top_spender = max(revenue_per_user, key=revenue_per_user.get)
    top_spender_amount = revenue_per_user[top_spender]

    # ---------------------------------------------------
    # 5. Hourly transaction volume
    # ---------------------------------------------------
    hourly_volume = defaultdict(lambda: {"count": 0, "total": 0})
    for p in payments:
        hourly_volume[p["hour"]]["count"] += 1
        hourly_volume[p["hour"]]["total"] += p["amount"]

    # ---------------------------------------------------
    # PRINT REPORT
    # ---------------------------------------------------
    print(f"Transactions:        {count}", flush=True)
    print(f"Total amount:        {total}", flush=True)
    print(f"Average transaction: {average}", flush=True)
    print(f"🏆 Top spender:      {top_spender} ({top_spender_amount} kr)", flush=True)

    print("\nRevenue per user:", flush=True)
    for user, rev in sorted(revenue_per_user.items(), key=lambda x: x[1], reverse=True):
        print(f"  {user}: {rev} kr (avg {avg_per_user[user]} kr, {count_per_user[user]} transactions)", flush=True)

    print("\nHourly transaction volume:", flush=True)
    for hour, stats in sorted(hourly_volume.items()):
        print(f"  {hour}: {stats['count']} transactions, {stats['total']} kr", flush=True)

    print("-" * 40, flush=True)

    # ---------------------------------------------------
    # EXPORT TO JSON
    # ---------------------------------------------------
    report = {
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "total_transactions": count,
        "total_amount": total,
        "average_transaction": average,
        "top_spender": {"user": top_spender, "amount": top_spender_amount},
        "revenue_per_user": dict(revenue_per_user),
        "avg_per_user": avg_per_user,
        "hourly_volume": {h: v for h, v in hourly_volume.items()},
    }
    export_json(report, f"report_{timestamp_label}.json")

    # ---------------------------------------------------
    # EXPORT TO CSV
    # ---------------------------------------------------
    csv_rows = [
        {
            "user": user,
            "total_revenue": revenue_per_user[user],
            "transaction_count": count_per_user[user],
            "average_transaction": avg_per_user[user],
        }
        for user in sorted(revenue_per_user)
    ]
    export_csv(
        csv_rows,
        fieldnames=["user", "total_revenue", "transaction_count", "average_transaction"],
        filename=f"report_{timestamp_label}.csv",
    )
