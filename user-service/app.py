from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "service": "user-service",
        "status": "healthy"
    })


@app.route("/users")
def users():
    return jsonify([
        {"id": 1, "name": "Astha"},
        {"id": 2, "name": "Rahul"}
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
