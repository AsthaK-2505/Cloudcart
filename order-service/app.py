from flask import Flask, jsonify, request
import psycopg
import pika
import json

app = Flask(__name__)

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "cloudcart",
    "user": "cloudcart",
    "password": "cloudcart"
}


def get_db_connection():
    return psycopg.connect(**DB_CONFIG)


def publish_order_event(order):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )

    channel = connection.channel()

    channel.queue_declare(queue="order_events", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="order_events",
        body=json.dumps(order)
    )

    connection.close()


@app.route("/health")
def health():
    return jsonify({
        "service": "order-service",
        "status": "healthy"
    })


@app.route("/orders", methods=["GET"])
def get_orders():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, user_id, product_id, status
        FROM orders
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    orders = []

    for row in rows:
        orders.append({
            "id": row[0],
            "user_id": row[1],
            "product_id": row[2],
            "status": row[3]
        })

    return jsonify(orders)


@app.route("/orders", methods=["POST"])
def create_order():

    data = request.get_json()

    user_id = data.get("user_id")
    product_id = data.get("product_id")

    if not user_id or not product_id:
        return jsonify({
            "error": "user_id and product_id are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO orders (user_id, product_id, status)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (user_id, product_id, "PLACED"))

    order_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    order = {
        "id": order_id,
        "user_id": user_id,
        "product_id": product_id,
        "status": "PLACED"
    }

    try:
        publish_order_event(order)
    except Exception as e:
        print("RabbitMQ error:", e)

    return jsonify(order), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
