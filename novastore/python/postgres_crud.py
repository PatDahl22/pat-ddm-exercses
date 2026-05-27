"""
NovaStore – PostgreSQL CRUD (Del 3 & Del 6)
Kör: python postgres_crud.py
Kräver: pip install psycopg2-binary
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# ------------------------------------------------------------------
# Anslutning
# ------------------------------------------------------------------
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="student",
    password="student",
    database="shop"
)
conn.autocommit = False          # vi hanterar transaktioner manuellt
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("✅ Ansluten till PostgreSQL!\n")


# ------------------------------------------------------------------
# CREATE – lägg till en kund och en produkt
# ------------------------------------------------------------------
def create_examples():
    cursor.execute(
        "INSERT INTO customers (name, email) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        ("Pat", "pat@example.com")
    )
    cursor.execute(
        "INSERT INTO products (name, price, category, stock) VALUES (%s, %s, %s, %s)",
        ("Mus", 299.00, "Elektronik", 50)
    )
    conn.commit()
    print("CREATE: Kund och produkt skapade.")


# ------------------------------------------------------------------
# READ – hämta alla kunder
# ------------------------------------------------------------------
def read_customers():
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    print("\nREAD – Kunder:")
    for row in rows:
        print(f"  id={row['id']}  namn={row['name']}  email={row['email']}")


# ------------------------------------------------------------------
# READ – orders med JOIN (vem beställde vad)
# ------------------------------------------------------------------
def read_orders_with_join():
    cursor.execute("""
        SELECT
            customers.name  AS kund,
            orders.id       AS order_id,
            orders.status,
            orders.created_at
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        ORDER BY orders.id
    """)
    rows = cursor.fetchall()
    print("\nREAD – Orders (JOIN med customers):")
    for row in rows:
        print(f"  order={row['order_id']}  kund={row['kund']}  status={row['status']}")


# ------------------------------------------------------------------
# UPDATE – ändra orderstatus
# ------------------------------------------------------------------
def update_order_status(order_id: int, new_status: str):
    cursor.execute(
        "UPDATE orders SET status = %s WHERE id = %s",
        (new_status, order_id)
    )
    conn.commit()
    print(f"\nUPDATE: Order {order_id} → status = '{new_status}'")


# ------------------------------------------------------------------
# DELETE – ta bort en produkt (med säkerhetskontroll)
# ------------------------------------------------------------------
def delete_product(product_id: int):
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    print(f"\nDELETE: Produkt {product_id} borttagen.")


# ------------------------------------------------------------------
# Kör alla operationer
# ------------------------------------------------------------------
if __name__ == "__main__":
    create_examples()
    read_customers()
    read_orders_with_join()
    update_order_status(order_id=1, new_status="shipped")
    read_orders_with_join()   # visa förändringen

    cursor.close()
    conn.close()
    print("\n🔒 Anslutning stängd.")
