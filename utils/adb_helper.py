import os
import time
import cv2

# Configuration
ADB_DEVICE = "emulator-5554"
ADB_PATH = "/Users/tomasvalentinas/Downloads/platform-tools/adb"

def take_screenshot(output_path="screen.png", retries=3, delay=0.5):
    for attempt in range(retries):
        os.system(f'"{ADB_PATH}" -s {ADB_DEVICE} exec-out screencap -p > {output_path}')
        time.sleep(delay)
        img = cv2.imread(output_path)
        if img is not None and img.shape[0] > 0 and img.mean() not in [0, 255]:
            return
        print(f"[-] Screenshot retry {attempt+1}/{retries} (blank result)")
    print("[-] Final screenshot attempt failed or was blank.")

def tap(x, y):
    os.system(f'"{ADB_PATH}" -s {ADB_DEVICE} shell input tap {x} {y}')

def tap_and_hold(x, y, duration_ms=2500):
    os.system(f'"{ADB_PATH}" -s {ADB_DEVICE} shell input swipe {x} {y} {x} {y} {duration_ms}')

def ensure_connection():
    pass  # No-op on Mac with emulator; connection already managed by ADB server
