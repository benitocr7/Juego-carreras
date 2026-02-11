import cv2
import numpy as np
import os
import shutil

def process_car_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    car_files = ["cars1.png", "cars2.png", "cars3.png", "cars4.png"]
    
    for filename in car_files:
        file_path = os.path.join(assets_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"File not found: {filename}")
            continue

        # Read image
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            print(f"Error reading {filename}")
            continue

        # 2. ROTATE 90 DEGREES COUNTER-CLOCKWISE (Right -> Up)
        # Previous run rotated (Down/original -> Right).
        # This run rotates (Right -> Up).
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Save
        cv2.imwrite(file_path, img)
        print(f"Rotated {filename} 90 degrees CCW")

if __name__ == "__main__":
    process_car_assets()
