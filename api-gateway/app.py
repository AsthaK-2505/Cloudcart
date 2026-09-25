from flask import Flask, jsonify
import requests

app = Flask(__name__)


USER_SERVICE = "http://localhost:5001"
PRODUCT_SERVICE = "http://localhost:5002"
ORDER_SERVICE = "http://localhost:5003"


@app.route("/")
def home():
    return "CloudCart API Gateway is running!"


@app.route("/users")
def users():
    response = requests.get(f"{USER_SERVICE}/users")
    return jsonify(response.json())


@app.route("/products")
def products():
    response = requests.get(f"{PRODUCT_SERVICE}/products")
    return jsonify(response.json())


@app.route("/orders")
def orders():
    response = requests.get(f"{ORDER_SERVICE}/orders")
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
