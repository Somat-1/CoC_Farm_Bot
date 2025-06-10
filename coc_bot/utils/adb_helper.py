import os
import time
import cv2
import subprocess
import shutil
import sys

# Automatically locate adb
ADB_PATH = shutil.which("adb")

# Verify ADB is available
try:
    output = subprocess.check_output([ADB_PATH, "devices"]).decode()
    lines = output.strip().split("\n")[1:]  # Skip "List of devices attached"
    connected = [line.split()[0] for line in lines if "device" in line]
    if not connected:
        print("[-] No ADB device found. Please connect or start an emulator.")
        sys.exit(1)
    ADB_DEVICE = connected[0]  # Pick the first connected device
    print(f"[+] Using ADB device: {ADB_DEVICE}")
except Exception as e:
    print(f"[-] Failed to detect ADB device: {e}")
    sys.exit(1)

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
