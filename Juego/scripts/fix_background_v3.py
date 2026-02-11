import cv2
import numpy as np
import os

def remove_background_floodfill(filename, tolerance=60):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    # Load image
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to load {path}")
        return

    # Ensure 4 channels
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Work on BGR for floodfill
    # Create mask (h+2, w+2)
    h, w = img.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    
    # Floodfill uses BGR (first 3 channels)
    # Be careful, floodFill modifies the image in-place unless FLOODFILL_MASK_ONLY is set.
    # We want mask only.
    
    flood_flags = 4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255 << 8)
    
    # Tolerance tuple - must match channel count of the image passed to floodFill
    # If we pass the 4-channel img, we need 4-tuple tolerance.
    # Or just convert to BGR first for analysis.
    
    img_bgr = img[:,:,:3].copy()
    
    # Run floodFill on BGR copy to update the mask
    seeds = [(0,0), (w-1, 0), (0, h-1), (w-1, h-1)]
    
    for seed in seeds:
        # cv2.floodFill(image, mask, seedPoint, newVal, loDiff, upDiff, flags)
        cv2.floodFill(img_bgr, mask, seed, (0,0,0), (tolerance,)*3, (tolerance,)*3, flood_flags)
        
    # Mask has 255 for background. Crop it.
    mask_cropped = mask[1:-1, 1:-1]
    
    # Invert mask to get foreground
    foreground = cv2.bitwise_not(mask_cropped)
    
    # Update alpha channel
    b, g, r, a = cv2.split(img)
    a = cv2.bitwise_and(a, foreground)
    
    out_img = cv2.merge((b, g, r, a))
    
    cv2.imwrite(path, out_img)
    print(f"Processed {filename} with corrected FloodFill.")

if __name__ == "__main__":
    remove_background_floodfill("cars1.png")
    remove_background_floodfill("car_enemy.png")
