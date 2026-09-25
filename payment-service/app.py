from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "service": "payment-service",
        "status": "healthy"
    })


@app.route("/payments", methods=["POST"])
def payment():
    data = request.get_json()

    return jsonify({
        "order_id": data.get("order_id"),
        "amount": data.get("amount"),
        "status": "PAYMENT_SUCCESS"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
