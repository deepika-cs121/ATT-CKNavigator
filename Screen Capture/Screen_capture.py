import os
import time
import threading
import queue
import logging
from datetime import datetime
import numpy as np
import cv2
import mss
from tkinter import Tk, scrolledtext, END


SAVE_FOLDER = "captures"      
LOG_FILE = "capture_log.txt"   
INTERVAL = 5                   

os.makedirs(SAVE_FOLDER, exist_ok=True)

log_queue = queue.Queue()


class QueueHandler(logging.Handler):
    def __init__(self, q):
        super().__init__()
        self.q = q
    def emit(self, record):
        self.q.put(self.format(record))


logger = logging.getLogger("ScreenCapture")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)

queue_handler = QueueHandler(log_queue)
queue_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(queue_handler)


def capture_loop():
    logger.info("Screen Capture Session Started")
    sct = mss.mss()

    try:
        while True:
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(SAVE_FOLDER, f"screenshot_{timestamp}.png")

            
            img = sct.grab(sct.monitors[1])
            frame = np.array(img)


            cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR))
            logger.info(f"Captured: {os.path.basename(filename)}")

            
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        logger.info("=== Session stopped ===")


def gui_loop():
    """Show a live updating window of capture logs."""
    root = Tk()
    root.title("Screen Capture Logs")
    root.geometry("600x400")

    text = scrolledtext.ScrolledText(root, state='disabled')
    text.pack(expand=True, fill='both')

   
    def update_logs():
        while not log_queue.empty():
            msg = log_queue.get()
            text.config(state='normal')
            text.insert(END, msg + "\n")
            text.config(state='disabled')
            text.yview(END)
        root.after(500, update_logs)  

    update_logs()
    root.mainloop()


threading.Thread(target=capture_loop, daemon=True).start()
gui_loop()
