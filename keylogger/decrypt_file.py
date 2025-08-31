from cryptography.fernet import Fernet
import json
import os


def decrypt_file(encrypted_file_path: str, key_file_path: str = "key.key", output_file_path: str = "decrypted.json"):
    # Check if key file exists
    if not os.path.exists(key_file_path):
        print(f"Error: Key file '{key_file_path}' not found. Cannot decrypt without the key.")
        return

    # Check if encrypted file exists
    if not os.path.exists(encrypted_file_path):
        print(f"Error: Encrypted file '{encrypted_file_path}' not found. Please provide the correct file path.")
        return

    # Load the encryption key
    try:
        with open(key_file_path, "rb") as key_file:
            key = key_file.read()
    except Exception as e:
        print(f"Error reading key file '{key_file_path}': {e}")
        return

    # Load the encrypted file
    try:
        with open(encrypted_file_path, "rb") as enc_file:
            encrypted_data = enc_file.read()
    except Exception as e:
        print(f"Error reading encrypted file '{encrypted_file_path}': {e}")
        return

    # Decrypt the data
    try:
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"Error decrypting data: {e}. The key may not match the encrypted file.")
        return

    # Save decrypted data to file
    try:
        with open(output_file_path, "wb") as out_file:
            out_file.write(decrypted_data)
        print(f"Decrypted data saved to '{output_file_path}'")
    except Exception as e:
        print(f"Error saving decrypted file '{output_file_path}': {e}")
        return

    # Try to display as JSON
    try:
        decrypted_json = json.loads(decrypted_data.decode("utf-8"))
        print("Decrypted content:")
        print(json.dumps(decrypted_json, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Decrypted content is not valid JSON: {e}")
        print(f"Raw decrypted content: {decrypted_data.decode('utf-8', errors='ignore')}")


if __name__ == "__main__":
    # Example usage
    encrypted_file = "encrypted_file.bin"
    decrypt_file(encrypted_file)