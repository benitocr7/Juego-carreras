import cv2
import numpy as np
import os

def fix_orientation_exotico_leyenda():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    # "Exótico" -> cars3.png
    # "Leyenda" -> cars4.png
    target_cars = ["cars3.png", "cars4.png"]
    
    for filename in target_cars:
        file_path = os.path.join(assets_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"File not found: {filename}")
            continue

        # Read image
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            print(f"Error reading {filename}")
            continue

        # Rotate 180 degrees
        img = cv2.rotate(img, cv2.ROTATE_180)

        # Save
        cv2.imwrite(file_path, img)
        print(f"Rotated {filename} 180 degrees")

if __name__ == "__main__":
    fix_orientation_exotico_leyenda()
