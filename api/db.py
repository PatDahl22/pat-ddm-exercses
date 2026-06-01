import os
from decimal import Decimal

import psycopg2
import psycopg2.extras


def get_connection():
    """
    Creates a new PostgreSQL connection.

    In a real production API you would usually use connection pooling.
    For this beginner lab, a simple connection per request is easier to understand.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "novastore"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student"),
    )


def _convert_product(row):
    """
    Converts a database row into a JSON-friendly dictionary.

    PostgreSQL NUMERIC values become Decimal in Python, so we convert price to float.
    """
    if row is None:
        return None

    product = dict(row)

    if isinstance(product.get("price"), Decimal):
        product["price"] = float(product["price"])

    if product.get("created_at") is not None:
        product["created_at"] = product["created_at"].isoformat()

    return product


def get_all_products_from_db():
    """
    TODO:
    Den här funktionen fungerar redan som referensimplementation.

    Läs SQL-frågan och förstå hur API:et hämtar data från PostgreSQL.
    """
    query = """
        SELECT id, name, price, category, stock, created_at
        FROM products
        ORDER BY id;
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()

    return [_convert_product(row) for row in rows]


def get_product_by_id_from_db(product_id):
    """
    TODO:
    Implementera den här funktionen i Del 2 (Uppgift 5).

    Den ska:
    - Fråga PostgreSQL efter en produkt baserat på id
    - Returnera produkten som en dictionary om den finns
    - Returnera None om produkten inte finns

    Föreslagen SQL:
        SELECT id, name, price, category, stock, created_at
        FROM products
        WHERE id = %s;
    """
    # TODO: Ersätt detta med en riktig SQL-fråga.
    return None


def insert_product_into_db(product):
    """
    TODO:
    Implementera den här funktionen i Del 3 (Uppgift 8).

    Den ska spara en ny produkt i PostgreSQL och returnera den skapade produkten.

    Föreslagen SQL:
        INSERT INTO products (name, price, category, stock)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, price, category, stock, created_at;
    """
    # TODO: Ersätt detta med en riktig INSERT-fråga.
    return None
