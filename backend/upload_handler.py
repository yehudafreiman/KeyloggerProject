import time
from flask import request, jsonify, json
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

def generate_log_filename():
    return "log_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

def upload (data):
    
    # data = request.get_json()
    
    # if not data or "machine" not in data or "data" not in data: 
        # return jsonify({"error": "Invalid payload"}), 400

    machine = data["machine"]
    log_data = data["data"]
    machine_folder = os.path.join(DATA_FOLDER, machine)
    
    if not os.path.exists(machine_folder):
        os.makedirs(machine_folder)
    
    filename = generate_log_filename()
    file_path = os.path.join(machine_folder, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(log_data, indent=4))  # pretty printed JSON

    return jsonify({"status": "success", "file": file_path}), 200