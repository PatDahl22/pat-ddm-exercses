import os
import redis


def get_redis_client():
    """
    Creates a Redis client.

    Redis is used in this lab to cache the product list for GET /products.
    """
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


redis_client = get_redis_client()


def get_cached_products():
    """
    TODO:
    Används i Del 4 (Uppgift 12 och 15).

    Den ska:
    - Försöka läsa nyckeln "products" från Redis
    - Returnera cachead data om den finns
    - Returnera None om cachen är tom
    """
    # TODO: Implementera läsning från cache.
    return None


def set_cached_products(json_data):
    """
    TODO:
    Används i Del 4 (Uppgift 14).

    Den ska spara JSON-strängen i Redis med nyckeln "products".
    """
    # TODO: Implementera skrivning till cache.
    pass


def clear_products_cache():
    """
    TODO:
    Används i Del 5 (Uppgift 17).

    Den ska ta bort nyckeln "products" från Redis efter POST /products.
    """
    # TODO: Implementera cache invalidation.
    pass
