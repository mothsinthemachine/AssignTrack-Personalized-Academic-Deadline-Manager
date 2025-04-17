from save_reminder import constant_save_reminder
from send_reminder import constant_send_reminder
import threading
import time
import random

def run_save_reminder():  # You were missing the colon here
    while True:
        constant_save_reminder()

def run_send_reminder():
    while True:
        time.sleep(60)
        constant_send_reminder()

# Create thread objects
save_thread = threading.Thread(target=run_save_reminder, daemon=True)
send_thread = threading.Thread(target=run_send_reminder, daemon=True)

save_thread.start()
send_thread.start()

# Add this to keep the main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user")