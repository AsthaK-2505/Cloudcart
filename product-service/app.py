from flask import Flask, jsonify
import psycopg
import redis
import json
import os

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "cloudcart"),
    "user": os.getenv("DB_USER", "cloudcart"),
    "password": os.getenv("DB_PASSWORD", "cloudcart")
}

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


def get_db_connection():
    return psycopg.connect(**DB_CONFIG)


@app.route("/health")
def health():
    return jsonify({
        "service": "product-service",
        "status": "healthy"
    })


@app.route("/products")
def get_products():

    # 1. Check Redis
    cached_products = redis_client.get("products")

    if cached_products:
        print("CACHE HIT", flush=True)
        return jsonify(json.loads(cached_products))

    # 2. Cache miss → query PostgreSQL
    print("CACHE MISS", flush=True)

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, price
        FROM products
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2]
        })

    # 3. Store result in Redis
    redis_client.set(
        "products",
        json.dumps(products),
        ex=60
    )

    return jsonify(products)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5002
    )
