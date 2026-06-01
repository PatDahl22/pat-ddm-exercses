import json

from flask import Flask, jsonify, request

from db import (
    get_all_products_from_db,
    get_product_by_id_from_db,
    insert_product_into_db,
)
from cache import (
    get_cached_products,
    set_cached_products,
    clear_products_cache,
)

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/products")
def get_products():
    """
    Del 2:
    Den här endpointen hämtar redan produkter från PostgreSQL.

    Del 4:
    Studenterna ska senare bygga ut endpointen med Redis-cache.
    """
    # TODO Del 4 (Uppgift 12-15):
    # 1. Kontrollera Redis först med get_cached_products()
    # 2. Om cache finns: skriv ut "CACHE HIT" och returnera cachead JSON
    # 3. Om cache saknas: skriv ut "CACHE MISS" och läs från PostgreSQL
    # 4. Spara resultatet i Redis med set_cached_products()

    products = get_all_products_from_db()
    return jsonify(products), 200


@app.get("/products/<int:product_id>")
def get_product(product_id):
    """
    Del 2:
    TODO (Uppgift 5 och 6).

    Förväntat beteende:
    - Om produkten finns: returnera produkten som JSON med 200 OK
    - Om produkten inte finns: returnera {"error": "Product not found"} med 404
    """
    product = get_product_by_id_from_db(product_id)

    # TODO: Implementera 404 Not Found om produkten inte existerar (Uppgift 6).
    return jsonify({
        "message": "TODO: Implementera GET /products/{id} (Uppgift 5)",
        "product_id": product_id,
        "hint": "Använd get_product_by_id_from_db(product_id) i db.py"
    }), 501


@app.post("/products")
def create_product():
    """
    Del 3:
    TODO (Uppgift 7-10).

    Förväntat beteende:
    - Läs JSON från requesten
    - Validera name och price
    - Avvisa saknat name, saknat price eller negativt price med 400 Bad Request
    - Spara produkten i PostgreSQL
    - Returnera skapad produkt med 201 Created
    - Del 5: Töm produktcachen efter lyckad insert (Uppgift 17)
    """
    data = request.get_json(silent=True)

    # TODO: Validera inkommande data och stoppa ogiltiga requests (Uppgift 10).
    # Exempel som ska ge 400:
    # {}
    # {"price": 999}
    # {"name": "Webcam"}
    # {"name": "Webcam", "price": -10}

    # TODO: Spara ny produkt i PostgreSQL med insert_product_into_db(data) (Uppgift 8).
    # TODO Del 5: Töm produktcachen med clear_products_cache() efter POST (Uppgift 17).

    return jsonify({
        "message": "TODO: Implementera POST /products (Uppgift 7-9)",
        "received": data
    }), 501


@app.get("/crash")
def crash():
    """
    Optional endpoint for discussing 500 Internal Server Error.
    """
    raise Exception("Simulated server error")


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
