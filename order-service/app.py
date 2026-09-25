from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "service": "order-service",
        "status": "healthy"
    })


@app.route("/orders")
def orders():
    return jsonify([
        {
            "id": 101,
            "user_id": 1,
            "product_id": 1,
            "status": "PLACED"
        }
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
