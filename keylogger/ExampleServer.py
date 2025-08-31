from flask import Flask, request, jsonify
from cryptography.fernet import Fernet

app = Flask(__name__)

def decrypt_file(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data

@app.route('/upload', methods=['POST'])
def upload():
    try:
        encrypted_file = request.files['file'].read()
        key = request.files['key'].read()

        decrypted_data = decrypt_file(encrypted_file, key)

        with open("decrypted_output.txt", "wb") as f:
            f.write(decrypted_data)

        return jsonify({"status": "success", "message": "File decrypted and saved!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)