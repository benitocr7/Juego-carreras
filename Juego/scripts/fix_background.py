import cv2
import numpy as np
import os

def remove_background(filename):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    
    # Check if image has alpha channel
    if img.shape[2] == 3:
        # Add alpha channel
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Convert to grayscale for thresholding
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Assuming white/light background (common in downloaded assets)
    # Threshold to identify background (pixels > 240 almost white)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Invert mask: Background becomes black (0), Object white (255)
    mask_inv = cv2.bitwise_not(mask)

    # Apply mask to alpha channel
    # Where mask is 255 (Background), make alpha 0
    # But wait, we want to KEEP the object.
    # The mask 'mask' has White(255) for background.
    # So we want Alpha to be 0 where mask is 255.
    
    # Normalize alpha based on the mask
    # Logic: If pixel is 'white' (background), Alpha = 0. Else Alpha = 255.
    
    # Isolate the alpha channel
    b, g, r, a = cv2.split(img)
    
    # Set alpha: valid pixels (mask_inv) keep alpha, background (mask) become transparent
    # Ensure we don't accidentally remove white parts of the car.
    # Better approach: FloodFill from corners if it's a solid box?
    # Let's try simple threshold first, assuming the car isn't pure white #F0F0F0+
    
    # Update alpha channel: 
    # If mask (background) is 255, set alpha to 0
    a = cv2.bitwise_and(a, mask_inv) 
    
    out_img = cv2.merge((b, g, r, a))
    
    cv2.imwrite(path, out_img)
    print(f"Processed {filename}: Background removed.")

if __name__ == "__main__":
    remove_background("cars1.png")
    # Also process car_enemy.png just in case, since user mentioned it earlier
    remove_background("car_enemy.png") 
