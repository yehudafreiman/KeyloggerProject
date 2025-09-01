import time
from flask import request, jsonify, json
import os
from cryptography.fernet import Fernet

key = b'9YxKn3m3G5qXz2o9xYxKn3m3G5qXz2o9xYxKn3m3G5q='
fernet = Fernet(key)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

def generate_log_filename():
    return "log_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".json"

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

    with open(file_path, "wb") as f:
        f.write(fernet.encrypt(json.dumps(log_data, indent=4).encode()))  # pretty printed JSON

    return jsonify({"status": "success", "file": file_path}), 200