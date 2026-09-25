from flask import Flask, jsonify
import os
import psycopg

app = Flask(__name__)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "cloudcart"),
        user=os.getenv("DB_USER", "cloudcart"),
        password=os.getenv("DB_PASSWORD", "cloudcart")
    )


@app.route("/health")
def health():
    return jsonify({
        "service": "product-service",
        "status": "healthy"
    })


@app.route("/products")
def products():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price INTEGER NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute(
            """
            INSERT INTO products (name, price)
            VALUES (%s, %s), (%s, %s)
            """,
            ("Laptop", 65000, "Keyboard", 2000)
        )
        conn.commit()

    cur.execute("SELECT id, name, price FROM products ORDER BY id")
    products = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": product[0],
            "name": product[1],
            "price": product[2]
        }
        for product in products
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
