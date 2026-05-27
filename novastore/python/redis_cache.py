"""
NovaStore - Del 8: Redis caching + pagination
Kör: python python/redis_cache.py
Kräver: pip install psycopg2-binary redis
"""

import json
import time
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
import redis


class DecimalEncoder(json.JSONEncoder):
    """Gör att json.dumps() klarar PostgreSQL DECIMAL-värden."""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "student",
    "password": "student",
    "database": "shop",
}

# Redis-anslutning
cache = redis.Redis(host="localhost", port=6379, decode_responses=True)
print("Redis pingad:", cache.ping())  # True = ansluten


# ------------------------------------------------------------------
# PAGINATION – hämta produkter sida för sida
# ------------------------------------------------------------------
def get_products_page(page: int = 1, page_size: int = 2) -> list:
    """
    Returnerar en sida produkter från PostgreSQL.
    OFFSET = (page - 1) * page_size
    LIMIT  = page_size
    """
    offset = (page - 1) * page_size
    connection = psycopg2.connect(**DB_CONFIG)
    db_cursor = connection.cursor(cursor_factory=RealDictCursor)
    db_cursor.execute(
        "SELECT id, name, price, stock FROM products ORDER BY id LIMIT %s OFFSET %s",
        (page_size, offset)
    )
    rows = [dict(row) for row in db_cursor.fetchall()]
    db_cursor.close()
    connection.close()
    return rows


def demo_pagination() -> None:
    """Visar hur pagination fungerar i PostgreSQL."""
    print("\n--- PAGINATION ---")
    print("Hämtar produkter sida för sida (2 per sida):\n")
    for page_num in range(1, 4):
        products = get_products_page(page=page_num, page_size=2)
        if not products:
            print(f"  Sida {page_num}: (inga fler produkter)")
            break
        print(f"  Sida {page_num}:")
        for product in products:
            print(f"    id={product['id']}  {product['name']}  {product['price']} kr")


# ------------------------------------------------------------------
# REDIS CACHING – cacha produktsida i Redis
# ------------------------------------------------------------------
CACHE_TTL = 30  # sekunder tills cachen går ut


def get_products_page_cached(page: int = 1, page_size: int = 2) -> list:
    """
    Hämtar produktsida - från Redis-cache om möjligt,
    annars från PostgreSQL (och sparar i cache).
    """
    cache_key = f"products:page:{page}:size:{page_size}"

    # 1. Kolla cache
    cached = cache.get(cache_key)
    if cached is not None:
        print(f"  [CACHE HIT]  nyckel={cache_key}")
        if isinstance(cached, (str, bytes, bytearray)):
            return json.loads(cached)
        return json.loads(str(cached))

    # 2. Cache miss – hämta från databasen
    print(f"  [CACHE MISS] nyckel={cache_key} -> hämtar från PostgreSQL...")
    products = get_products_page(page=page, page_size=page_size)

    # 3. Spara i cache med TTL
    cache.setex(cache_key, CACHE_TTL, json.dumps(products, cls=DecimalEncoder))
    return products


def demo_caching() -> None:
    """Visar skillnaden i hastighet mellan cache hit och miss."""
    print("\n--- REDIS CACHING ---")
    print(f"TTL (livslängd i cache): {CACHE_TTL} sekunder\n")

    # Rensa eventuell gammal cache
    cache.flushdb()

    # Första anropet – cache miss, hämtar från DB
    start = time.perf_counter()
    products = get_products_page_cached(page=1, page_size=2)
    db_time = (time.perf_counter() - start) * 1000
    print(f"  Första anropet:  {db_time:.2f} ms  ({len(products)} produkter)")

    # Andra anropet – cache hit, hämtar från Redis
    start = time.perf_counter()
    products = get_products_page_cached(page=1, page_size=2)
    cache_time = (time.perf_counter() - start) * 1000
    print(f"  Andra anropet:   {cache_time:.2f} ms  ({len(products)} produkter)")

    print(f"""
FÖRKLARING:
  Cache miss : Hämtar från PostgreSQL (långsammare, nätverksanrop + query)
  Cache hit  : Hämtar från Redis i minnet (snabbare, inget SQL-anrop)

  Cachar man t.ex. produktlistor slipper databasen läsa samma data
  om och om igen vid hög trafik - kritiskt för e-handel som NovaStore.

  Nackdel: Cachen kan bli inaktuell (stale data).
  Lösning: Sätt ett rimligt TTL eller invalidera cachen vid UPDATE.
""")


# ------------------------------------------------------------------
# TRANSACTIONS i PostgreSQL – ACID-garanti
# ------------------------------------------------------------------
def demo_transaction() -> None:
    """
    Visar en komplett transaktion: skapa order + dra från lager atomärt.
    Antingen lyckas ALLT eller rullas ALLT tillbaka.
    """
    print("--- TRANSACTION: Skapa order + uppdatera lager ---\n")

    connection = psycopg2.connect(**DB_CONFIG)
    connection.autocommit = False
    db_cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        # Steg 1: Kontrollera lagret
        db_cursor.execute(
            "SELECT stock FROM products WHERE id = 1 FOR UPDATE"
        )
        result = db_cursor.fetchone()
        if result is None or result["stock"] < 1:
            raise ValueError("Produkten är slutsåld")

        # Steg 2: Skapa order
        db_cursor.execute(
            "INSERT INTO orders (customer_id, status) VALUES (%s, %s) RETURNING id",
            (1, "created")
        )
        order_id = db_cursor.fetchone()["id"]

        # Steg 3: Lägg till orderrad
        db_cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
            (order_id, 1, 1)
        )

        # Steg 4: Dra från lager
        db_cursor.execute(
            "UPDATE products SET stock = stock - 1 WHERE id = 1"
        )

        # Allt lyckades – commita
        connection.commit()
        print(f"  Transaktion lyckades! Order {order_id} skapad, lager uppdaterat.")

    except (psycopg2.Error, ValueError) as error:
        # Något gick fel – rulla tillbaka ALLT
        connection.rollback()
        print(f"  Transaktion misslyckades, allt rullade tillbaka: {error}")

    finally:
        db_cursor.close()
        connection.close()


# ------------------------------------------------------------------
# Kör allt
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("DEL 8 - Redis caching + Pagination + Transactions")
    print("=" * 60)

    demo_pagination()
    demo_caching()
    demo_transaction()

    print("Klart!")
