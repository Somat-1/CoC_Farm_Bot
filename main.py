from utils.adb_helper import take_screenshot, tap, tap_and_hold, ensure_connection
from time import sleep
from pathlib import Path
from datetime import datetime
import cv2
import easyocr
import re
import random
import math
import time


def random_point(center, radius):
    θ = random.random() * 2 * math.pi
    r = radius * math.sqrt(random.random())
    x = int(center[0] + r * math.cos(θ))
    y = int(center[1] + r * math.sin(θ))
    return x, y

# ========== CONFIG ==========

SCREEN_PATH = "screen.png"
DATASET_DIR = "loot_dataset"
POST_ATTACK_WAIT = 60
POST_ATTACK_TAPS = [(800, 850), (97, 900), (1200, 625)]

GOLD_THRESHOLD = 800000
ELIXIR_THRESHOLD = 800000
DARK_THRESHOLD = 0

reader = easyocr.Reader(['en'], gpu=False)

# ========== SAVE SCREENSHOT ==========


def draw_full_debug_overlay(image_path="screen.png", output_path="debug_full_overlay.png"):
    img = cv2.imread(image_path)
    if img is None:
        print("[-] Failed to load screenshot for overlay.")
        return

    # === Crop Boxes ===
    boxes = {
        "Gold":   (65, 113, 205, 142),
        "Elixir": (65, 158, 205, 185),
        "Dark":   (65, 198, 180, 228)
    }

    for label, (x1, y1, x2, y2) in boxes.items():
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # === Troop Tap Locations ===
    troop_coords = [
        (210, 920),  # Troop 1
        (460, 920),  # Troop 2
        (570, 920),  # Troop 3
        (680, 920),  # Troop 4
        (780, 920),  # Troop 5
        (340, 920)   # Troop 6
    ]
    for i, (x, y) in enumerate(troop_coords):
        cv2.circle(img, (x, y), 12, (255, 0, 0), 2)
        cv2.putText(img, f"T{i+1}", (x - 20, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # === Deploy Zones ===
    deploy_1 = (1426, 450)
    deploy_2 = (170, 460)
    cv2.circle(img, deploy_1, 12, (0, 255, 255), 2)
    cv2.putText(img, "D1", (deploy_1[0] - 20, deploy_1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.circle(img, deploy_2, 12, (0, 255, 255), 2)
    cv2.putText(img, "D2", (deploy_2[0] - 20, deploy_2[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # === Return to base taps ===
    return_taps = [(800, 850), (110, 915), (1234, 636)]
    for i, (x, y) in enumerate(return_taps):
        cv2.circle(img, (x, y), 10, (0, 0, 255), 2)
        cv2.putText(img, f"R{i+1}", (x - 20, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # === Next button ===
    next_btn = (1470, 760)
    cv2.circle(img, next_btn, 12, (128, 0, 255), 2)
    cv2.putText(img, "Next", (next_btn[0] - 30, next_btn[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 0, 255), 1)

    cv2.imwrite(output_path, img)
    print(f"[+] Debug overlay saved: {output_path}")



###

def save_loot_crop():
    Path(DATASET_DIR).mkdir(parents=True, exist_ok=True)
    img = cv2.imread(SCREEN_PATH)
    if img is None or img.shape[0] == 0:
        print("[-] Screenshot invalid.")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"{DATASET_DIR}/loot_{timestamp}.png"
    cv2.imwrite(out_path, img)
    print(f"[+] Saved loot panel to: {out_path}")

# ========== READ LOOT VIA EASYOCR ==========

def extract_loot_values(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("[-] Could not load screenshot.")
        return None

    # Crop coordinates (gold, elixir, dark elixir)
    crops = {
        "gold": image[113:142, 65:205],     # was [113:140, 70:190]
        "elixir": image[158:185, 65:205],   # was [160:185, 70:190]
        "dark": image[198:228, 65:180],     # was [200:230, 70:160]
    }


    loot = {}
    for key, crop in crops.items():
        result = reader.readtext(crop, detail=0)
        text = ''.join(result)
        digits = re.sub(r'[^\d]', '', text)
        loot[key] = int(digits) if digits.isdigit() else 0

    print(f"[OCR] Parsed Loot: Gold={loot['gold']}, Elixir={loot['elixir']}, Dark={loot['dark']}")
    return loot['gold'], loot['elixir'], loot['dark']

# ========== TROOP DEPLOYMENT ==========
def deploy_troops():
    print("[*] Deploying troops...")
    troop_icons = [
        (210, 920), (460, 920), (570, 920),
        (680, 920), (780, 920), (340, 920)
    ]
    deploy_1 = (1426, 450)
    deploy_2 = (170, 460)

    # Deploy troop 1
    tap(*troop_icons[0]); sleep(0.1)
    tap_and_hold(*random_point(deploy_1, 5), duration_ms=2700)

    # Deploy troop 6
    tap(*troop_icons[5]); sleep(0.1)
    tap(*random_point(deploy_1, 5)); sleep(0.1)

    # Deploy troop 2 twice
    tap(*troop_icons[1])
    tap(*random_point(deploy_1, 5)); sleep(5)
    tap(*troop_icons[1])
    tap(*random_point(deploy_1, 5))

    # Deploy troops 3–5 in pairs at deploy_2
    for troop in troop_icons[2:5]:
        for _ in range(2):
            tap(*troop); sleep(0.1)
            tap(*random_point(deploy_2, 5)); sleep(0.1)

    print("[+] Troops deployed.")

    # === SPELL DEPLOYMENT ===
    print("[*] Deploying spells...")
    spell_button = (925, 925)
    spell_drops = [
        (800, 350),
        (800, 480),
        (800, 600),
        (930, 480),
        (700, 480)
    ]

    tap(*spell_button)
    for loc in spell_drops:
        tap(*random_point(loc, 15))

    print("[+] Spells deployed.")
# ========== MAIN LOOP ==========

start_time = time.time()
TIMEOUT_SECONDS = 100 * 60  # 100 minutes
zero_loot_count = 0  # Track persistent consecutive zero loot readings

while True:
    # Exit after timeout
    if time.time() - start_time > TIMEOUT_SECONDS:
        print("[!] Timeout reached. Exiting script.")
        break

    ensure_connection()

    print("[*] =========================================================")
    print("[*] Taking screenshot...")
    take_screenshot(SCREEN_PATH)
    draw_full_debug_overlay(SCREEN_PATH)

    sleep(1.5)
    save_loot_crop()

    loot = extract_loot_values(SCREEN_PATH)

    # Retry up to 2 more times if loot is 0,0,0
    if loot == (0, 0, 0):
        for attempt in range(2):
            print(f"[!] Loot 0,0,0 detected. Retrying OCR attempt {attempt+1}...")
            sleep(2)
            take_screenshot(SCREEN_PATH)
            draw_full_debug_overlay(SCREEN_PATH)
            sleep(1.5)
            save_loot_crop()
            loot = extract_loot_values(SCREEN_PATH)
            if loot != (0, 0, 0):
                break

    # Track consecutive 0,0,0 results
    if loot == (0, 0, 0):
        zero_loot_count += 1
        print(f"[!] Consecutive zero loot count: {zero_loot_count}")
    else:
        zero_loot_count = 0

    # Trigger recovery taps if too many 0,0,0
    if zero_loot_count >= 7:
        print("[!] 15 consecutive zero loot results. Performing recovery taps...")
        for coords in [(800, 850), (97, 900), (1200, 625)]:
            tap(*coords)
            sleep(2)
        # Do not reset zero_loot_count
        continue  # Move to next loop iteration

    if loot:
        gold, elixir, dark = loot
        print(f"[+] Loot parsed: Gold={gold}, Elixir={elixir}, Dark={dark}")
        if (
            (gold >= GOLD_THRESHOLD and elixir >= ELIXIR_THRESHOLD and dark >= DARK_THRESHOLD)
            or gold >= 1_200_000
            or elixir >= 1_200_000
        ):
            print("[+] Loot is sufficient. Attacking base...")
            deploy_troops()

            print(f"[*] Waiting {POST_ATTACK_WAIT} seconds...")
            sleep(POST_ATTACK_WAIT)

            # Extra post-attack taps
            EXTRA_ATTACK_TAPS = [(110, 790), (960, 623)]
            print("[*] Performing extra post-attack taps...")
            for coords in EXTRA_ATTACK_TAPS:
                tap(*coords)
                sleep(2)

            print("[*] Returning to base...")
            for coords in POST_ATTACK_TAPS:
                tap(*coords)
                sleep(2)

            continue
        else:
            print("[-] Loot too low. Skipping base.")
    else:
        print("[-] Loot parsing failed.")

    print("[*] Tapping 'Next'...")
    tap(1470, 760)
    sleep(5)  # Wait for next base to appear
