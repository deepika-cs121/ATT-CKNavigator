import sounddevice as sd
from scipy.io.wavfile import write
import os, time, datetime

os.makedirs("audio_clips", exist_ok=True)
log_file = "audio_log.txt"

def log(msg):
    """Save log message to file and print it on screen."""
    with open(log_file, "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)

duration = 5  
fs = 44100     
clip = 1

log("=== Audio Capture Started ===")

while True:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"audio_{clip}_{ts}.wav"
    path = os.path.join("audio_clips", filename)

    log(f"Recording #{clip} for {duration}s...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  
    write(path, fs, audio)

    size = os.path.getsize(path)
    log(f"Saved: {filename} | Size: {size} bytes\n")

    clip += 1
    time.sleep(1)  
