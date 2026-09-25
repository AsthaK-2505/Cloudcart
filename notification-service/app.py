from flask import Flask, jsonify
import pika
import json
import threading
import time

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "service": "notification-service",
        "status": "healthy"
    })


@app.route("/notifications")
def notifications():
    return jsonify({
        "message": "Notification service is ready"
    })


def consume_messages():

    while True:
        try:
            print("Connecting to RabbitMQ...", flush=True)

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq",
                    port=5672,
                    connection_attempts=3,
                    retry_delay=2,
                    socket_timeout=5,
                    blocked_connection_timeout=5
                )
            )

            channel = connection.channel()

            channel.queue_declare(
                queue="order_events",
                durable=True
            )

            def callback(ch, method, properties, body):

                try:
                    event = json.loads(body)

                    print(
                        "Notification received:",
                        event,
                        flush=True
                    )

                except Exception as e:
                    print(
                        "Error processing message:",
                        e,
                        flush=True
                    )

            channel.basic_consume(
                queue="order_events",
                on_message_callback=callback,
                auto_ack=True
            )

            print(
                "Notification service listening for events...",
                flush=True
            )

            channel.start_consuming()

        except Exception as e:

            print(
                "RabbitMQ connection failed:",
                repr(e),
                flush=True
            )

            print(
                "Retrying in 5 seconds...",
                flush=True
            )

            time.sleep(5)


if __name__ == "__main__":

    thread = threading.Thread(
        target=consume_messages,
        daemon=True
    )

    thread.start()

    app.run(
        host="0.0.0.0",
        port=5005
    )
