import cv2
import os

def rotate_image(filename):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    # Load with alpha
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to load {path}")
        return

    # Rotate 180 degrees
    # cv2.ROTATE_180
    rotated = cv2.rotate(img, cv2.ROTATE_180)
    
    cv2.imwrite(path, rotated)
    print(f"Rotated {filename} 180 degrees.")

if __name__ == "__main__":
    rotate_image("cars1.png")
