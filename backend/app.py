from flask import Flask, render_template, request, jsonify
from upload_handler import *

app = Flask("__main__")

data_list = []

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/api/download")

@app.route("/api/upload", methods=["POST"])
def upload_api():
    data = request.get_json()
    if not data or "machine" not in data or "data" not in data: 
        return jsonify({"error": "Invalid payload"}), 400
    upload(data)
    data_list.append(data)
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True) 