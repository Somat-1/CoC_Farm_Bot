import cv2

def draw_full_debug_overlay(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("[-] Failed to load screenshot for overlay.")
        return

    # === Crop Boxes ===
    boxes = {
        "Gold":   (70, 113, 190, 140),
        "Elixir": (70, 160, 190, 185),
        "Dark":   (70, 200, 160, 230)
    }

    for label, (x1, y1, x2, y2) in boxes.items():
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    debug_path = "debug_full_overlay.png"
    cv2.imwrite(debug_path, image)
    print(f"[+] Debug overlay saved: {debug_path}")
