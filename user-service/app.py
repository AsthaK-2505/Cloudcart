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
        "service": "user-service",
        "status": "healthy"
    })


@app.route("/users")
def users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute(
            "INSERT INTO users (name) VALUES (%s), (%s)",
            ("Astha", "Rahul")
        )
        conn.commit()

    cur.execute("SELECT id, name FROM users ORDER BY id")
    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {"id": user[0], "name": user[1]}
        for user in users
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
