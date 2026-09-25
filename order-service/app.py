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
        "service": "order-service",
        "status": "healthy"
    })


@app.route("/orders")
def orders():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            status VARCHAR(50) NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) FROM orders")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute(
            """
            INSERT INTO orders (user_id, product_id, status)
            VALUES (%s, %s, %s)
            """,
            (1, 1, "PLACED")
        )
        conn.commit()

    cur.execute("""
        SELECT id, user_id, product_id, status
        FROM orders
        ORDER BY id
    """)

    orders = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": order[0],
            "user_id": order[1],
            "product_id": order[2],
            "status": order[3]
        }
        for order in orders
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
