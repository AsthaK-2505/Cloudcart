from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "service": "product-service",
        "status": "healthy"
    })


@app.route("/products")
def products():
    return jsonify([
        {
            "id": 1,
            "name": "Laptop",
            "price": 65000
        },
        {
            "id": 2,
            "name": "Keyboard",
            "price": 2000
        }
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
