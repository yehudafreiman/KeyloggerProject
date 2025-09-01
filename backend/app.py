from flask import Flask, render_template, request, jsonify
from upload_handler import *
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project/
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, template_folder=FRONTEND_DIR)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
data_list = []


@app.route("/")
def home():
    return render_template("WebsiteView.html")


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
        with open(file_path, "r") as file:
            try:
                data_objects[f"{file_name.strip('.json')}"] = json.load(file) # actual JSON object
            except json.JSONDecodeError:
                data_objects[f"{file_name.strip('.json')}"] = {"error": f"{file_name} is not valid JSON"}

    return jsonify(data_objects), 200


@app.route("/api/upload", methods=["POST"])
def upload_api():
    data = request.get_json()
    if not data or "machine" not in data or "data" not in data: 
        return jsonify({"error": "Invalid payload"}), 400
    upload(data)
    data_list.append(data)
    print("Current data list:", data_list)
    # return toggle_api()
    return jsonify({"status": "success"}), 200

# @app.route("/api/toggle", methods=["POST"])
# def toggle_api():
#     data = jsonify(request.get_json())

#     return data, 200

if __name__ == "__main__":
    app.run(debug=True) 