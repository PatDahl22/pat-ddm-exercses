"""
NovaStore - MongoDB CRUD (Del 4 & Del 6)
Kör: python mongo_crud.py
Kräver: pip install pymongo
"""

from pymongo import MongoClient, ASCENDING
from datetime import datetime, timezone

# ------------------------------------------------------------------
# Anslutning
# ------------------------------------------------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["shop"]

print("✅ Ansluten till MongoDB!")
print("   Befintliga collections:", db.list_collection_names(), "\n")


# ------------------------------------------------------------------
# Säkerhet: unikt index på email så dubbletter blockeras (Del 5 B)
# ------------------------------------------------------------------
db.customers.create_index([("email", ASCENDING)], unique=True)


# ------------------------------------------------------------------
# CREATE – skapa order-dokument (denormaliserat, allt i ett)
# ------------------------------------------------------------------
def create_orders():
    orders = [
        {
            "order_id": "order_1",
            "customer": {
                "id": "customer_1",
                "name": "Sara",
                "email": "sara@example.com"
            },
            "items": [
                {"product_id": "product_1", "name": "Laptop",   "price": 12990, "quantity": 1},
                {"product_id": "product_2", "name": "Hörlurar", "price":   899, "quantity": 2},
            ],
            "status": "created",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "order_id": "order_2",
            "customer": {
                "id": "customer_2",
                "name": "Ahmed",
                "email": "ahmed@example.com"
            },
            "items": [
                {"product_id": "product_3", "name": "Skrivbord", "price": 3499, "quantity": 1},
            ],
            "status": "shipped",
            "created_at": datetime.now(timezone.utc)
        },
    ]
    # insert_many ignorerar om dokumenten redan finns (idempotent via order_id)
    for order in orders:
        db.orders.update_one(
            {"order_id": order["order_id"]},
            {"$setOnInsert": order},
            upsert=True
        )
    print("CREATE: Orders insatta i MongoDB.")


# ------------------------------------------------------------------
# READ – hämta alla orders
# ------------------------------------------------------------------
def read_orders():
    print("\nREAD - Orders:")
    for order in db.orders.find({}, {"_id": 0}):
        print(f"  order_id={order['order_id']}  kund={order['customer']['name']}  status={order['status']}")


# ------------------------------------------------------------------
# UPDATE – ändra status på en order
# ------------------------------------------------------------------
def update_order_status(order_id: str, new_status: str):
    result = db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"status": new_status}}
    )
    print(f"\nUPDATE: {order_id} → status = '{new_status}'  (matchade: {result.matched_count})")


# ------------------------------------------------------------------
# SOFT DELETE – markera som deleted utan att radera (Del 4)
# ------------------------------------------------------------------
def soft_delete_order(order_id: str):
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"deleted": True, "deleted_at": datetime.now(timezone.utc)}}
    )
    print(f"\nSOFT DELETE: {order_id} markerad som deleted.")


# ------------------------------------------------------------------
# DELETE – hård borttagning
# ------------------------------------------------------------------
def hard_delete_order(order_id: str):
    result = db.orders.delete_one({"order_id": order_id})
    print(f"\nHARD DELETE: {order_id} borttagen (antal borttagna: {result.deleted_count})")


# ------------------------------------------------------------------
# Visa dubbletter-problemet (Del 5 B) – försök sätta in samma email
# ------------------------------------------------------------------
def demo_duplicate_block():
    print("\nDEMO - dubblettskydd:")
    try:
        db.customers.insert_many([
            {"name": "Sara",        "email": "sara@example.com"},
            {"name": "Sara Backup", "email": "sara@example.com"},   # samma email!
        ])
    except Exception as e:
        print(f"  ✅ Dublett blockerad av unikt index: {type(e).__name__}")


# ------------------------------------------------------------------
# Kör alla operationer
# ------------------------------------------------------------------
if __name__ == "__main__":
    create_orders()
    read_orders()
    update_order_status("order_1", "shipped")
    read_orders()
    soft_delete_order("order_2")
    demo_duplicate_block()

    client.close()
    print("\n🔒 Anslutning stängd.")
