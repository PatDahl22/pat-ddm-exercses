"""
NovaStore - Del 5: Buggar och flaskhalsar
Kör: python python/del5_buggar.py
Kräver: pip install psycopg2-binary
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import threading
import time

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "student",
    "password": "student",
    "database": "shop",
}


def get_connection(autocommit: bool = True) -> psycopg2.extensions.connection:
    """Returnerar en ny databasanslutning."""
    connection = psycopg2.connect(**DB_CONFIG)
    connection.autocommit = autocommit
    return connection


# ------------------------------------------------------------------
# PROBLEM A: Långsam query med LOWER()
# ------------------------------------------------------------------
def demo_problem_a() -> None:
    """
    Visar varför LOWER() på kolumnen gör queryn långsam,
    och hur ett funktionellt index löser det.
    """
    print("\n--- PROBLEM A: Långsam query ---")

    connection = get_connection()
    db_cursor = connection.cursor(cursor_factory=RealDictCursor)

    # PROBLEMET: LOWER() på kolumnen gör att PostgreSQL inte kan använda
    # det vanliga indexet (idx_customers_email). Den måste scanna HELA
    # tabellen (Seq Scan) för varje rad – långsamt vid stor datamängd.
    print("\n[SLOW] EXPLAIN - query med LOWER() på kolumnen:")
    db_cursor.execute("""
        EXPLAIN
        SELECT * FROM customers
        WHERE LOWER(email) = LOWER('sara@example.com')
    """)
    for row in db_cursor.fetchall():
        print(" ", list(row.values())[0])

    # LÖSNING: Skapa ett funktionellt index på LOWER(email).
    # Nu indexeras de lowercasade värdena direkt – Index Scan används istället.
    print("\n[FIX] Skapar funktionellt index på LOWER(email)...")
    db_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_customers_email_lower
        ON customers(LOWER(email))
    """)

    print("\n[FAST] EXPLAIN - samma query EFTER funktionellt index:")
    db_cursor.execute("""
        EXPLAIN
        SELECT * FROM customers
        WHERE LOWER(email) = LOWER('sara@example.com')
    """)
    for row in db_cursor.fetchall():
        print(" ", list(row.values())[0])

    print("""
FÖRKLARING:
  Utan index : Seq Scan  -> läser varje rad i tabellen = O(n)
  Med index  : Index Scan -> hoppar direkt till rätt rad = O(log n)

  Bättre alternativ långsiktigt: lagra alltid email i lowercase
  redan vid INSERT, så slipper man LOWER() i queries helt.
""")

    db_cursor.close()
    connection.close()


# ------------------------------------------------------------------
# PROBLEM C: Race condition – negativt lager
# ------------------------------------------------------------------
def kop_utan_skydd(anvandare: str) -> None:
    """Simulerar ett köp UTAN transaktionsskydd (visar buggen)."""
    connection = get_connection(autocommit=True)
    db_cursor = connection.cursor(cursor_factory=RealDictCursor)
    time.sleep(0.05)  # simulerar att båda läser stock=1 "samtidigt"
    db_cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = 1")
    db_cursor.execute("SELECT stock FROM products WHERE id = 1")
    result = db_cursor.fetchone()
    if result is None:
        print(f"  {anvandare}: FEL - produkten finns inte")
    else:
        stock = result["stock"]
        print(f"  {anvandare} köpte - lager nu: {stock}")
    db_cursor.close()
    connection.close()


def kop_med_skydd(anvandare: str) -> None:
    """Simulerar ett köp MED SELECT FOR UPDATE (korrekt lösning)."""
    connection = get_connection(autocommit=False)
    db_cursor = connection.cursor(cursor_factory=RealDictCursor)
    try:
        # Lås raden – bara en transaktion åt gången
        db_cursor.execute("SELECT stock FROM products WHERE id = 1 FOR UPDATE")
        result = db_cursor.fetchone()
        if result is None:
            connection.rollback()
            print(f"  {anvandare}: FEL - produkten finns inte")
            return

        stock = result["stock"]

        if stock > 0:
            db_cursor.execute(
                "UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock > 0"
            )
            connection.commit()
            print(f"  {anvandare}: Kop lyckades! (stock var {stock})")
        else:
            connection.rollback()
            print(f"  {anvandare}: Kop misslyckades - produkten slutsald!")
    except psycopg2.Error as db_error:
        connection.rollback()
        print(f"  {anvandare}: FEL - {db_error}")
    finally:
        db_cursor.close()
        connection.close()


def demo_problem_c() -> None:
    """Demonstrerar race condition och hur SELECT FOR UPDATE löser det."""
    print("=" * 60)
    print("--- PROBLEM C: Negativt lager (race condition) ---")

    connection = get_connection()
    db_cursor = connection.cursor(cursor_factory=RealDictCursor)

    # Sätt lagret till 1 så vi kan demonstrera problemet
    db_cursor.execute("UPDATE products SET stock = 1 WHERE id = 1")
    db_cursor.execute("SELECT name, stock FROM products WHERE id = 1")
    row = db_cursor.fetchone()
    if row is None:
        print("\nStartläge: PRODUKTEN FÖRSVANN")
    else:
        print(f"\nStartläge: {dict(row)}")

    # BUGGEN: Två trådar köper "samtidigt" utan skydd
    print("\n[BUGG] Simulerar två köp utan skydd...")
    thread_a = threading.Thread(target=kop_utan_skydd, args=("Användare A",))
    thread_b = threading.Thread(target=kop_utan_skydd, args=("Användare B",))
    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    db_cursor.execute("SELECT stock FROM products WHERE id = 1")
    result = db_cursor.fetchone()
    if result is None:
        print("  Resultat efter bugg: stock = <missing>  <- kan bli negativt!")
    else:
        print(f"  Resultat efter bugg: stock = {result['stock']}  <- kan bli negativt!")

    # FIXET: Återställ och kör med SELECT FOR UPDATE
    db_cursor.execute("UPDATE products SET stock = 1 WHERE id = 1")
    print("\n[FIX] Återställer lager till 1 och kör med SELECT FOR UPDATE...")

    thread_a = threading.Thread(target=kop_med_skydd, args=("Användare A",))
    thread_b = threading.Thread(target=kop_med_skydd, args=("Användare B",))
    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    db_cursor.execute("SELECT stock FROM products WHERE id = 1")
    result = db_cursor.fetchone()
    if result is None:
        print("  Resultat efter fix: stock = <missing>  <- aldrig negativt!")
    else:
        print(f"  Resultat efter fix: stock = {result['stock']}  <- aldrig negativt!")

    print("""
FÖRKLARING:
  Utan skydd : Båda läser stock=1, båda drar ifrån 1 -> stock=-1 (race condition)
  Med skydd  : SELECT FOR UPDATE låser raden - Användare B väntar tills
               A är klar, ser då stock=0 och nekas köpet.
               Lager kan aldrig bli negativt.
""")

    db_cursor.close()
    connection.close()


# ------------------------------------------------------------------
# Kör alla demos
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("DEL 5 - Buggar och flaskhalsar")
    print("=" * 60)

    demo_problem_a()
    demo_problem_c()

    print("Klart!")
