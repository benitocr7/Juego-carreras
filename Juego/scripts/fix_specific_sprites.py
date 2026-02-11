import cv2
import numpy as np
import os
import shutil

def remove_white_background(filename):
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    file_path = os.path.join(assets_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Backup
    backup_path = os.path.join(assets_dir, filename.replace(".png", "_backup.png"))
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
    else:
        print(f"Backup already exists: {backup_path}")

    # Read image
    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Error reading {file_path}")
        return

    # Ensure alpha channel exists
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    h, w = img.shape[:2]
    
    # Create mask for floodFill (h+2, w+2)
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Flood fill from corners with tolerance
    # White background is usually (255, 255, 255)
    # Be careful not to remove parts of the object if they touch the border and are white-ish.
    # But usually sprite sheets have a distinct background color or enough tolerance.
    
    # We will set the ALPHA channel to 0 for the background.
    # Approach:
    # 1. Flood fill on a copy of the BGR image to identify the background region.
    # 2. Use that mask to set alpha to 0 on the original image.
    
    bgr = img[:, :, :3].copy()
    
    # Seeds: top-left, top-right, bottom-left, bottom-right
    seeds = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
    
    # Tolerance for compression artifacts (e.g. 10-20)
    loDiff = (20, 20, 20)
    upDiff = (20, 20, 20)
    
    # Flags: 
    # 4 connectivity
    # FLOODFILL_MASK_ONLY: We want to update the mask, not the image (yet)
    # But wait, floodFill with MASK_ONLY doesn't use loDiff/upDiff well with seed color if we don't pass the image?
    # Actually, we can just flood fill the BGR image with a specific color (e.g. magenta) to visualize, 
    # OR just use the mask.
    
    # Let's use FLOODFILL_MASK_ONLY? No, standard floodFill is easier to debug if we see the result.
    # But we want to modify the ALPHA channel.
    
    # Let's floodFill the mask directly.
    # NewVal doesn't matter if we use MASK_ONLY? 
    # "If FLOODFILL_MASK_ONLY is set, the function does not change the image ... but fills the mask"
    
    flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE
    
    for seed in seeds:
        # Check if the seed point is already filled in the mask (to avoid re-work)
        # Mask is (y, x) but seed is (x, y). Mask is shifted by 1.
        if mask[seed[1]+1, seed[0]+1] == 0:
            cv2.floodFill(bgr, mask, seed, (0,0,0), loDiff, upDiff, flags)
            
    # The mask now has 255 where the background is.
    # Mask size is (h+2, w+2). We need to crop it to (h, w).
    mask_trimmed = mask[1:-1, 1:-1]
    
    # Where mask is 255 (background), set alpha to 0.
    img[mask_trimmed == 255, 3] = 0
    
    # Save
    cv2.imwrite(file_path, img)
    print(f"Successfully processed {filename}")

if __name__ == "__main__":
    remove_white_background("charco_aceite.png")
    remove_white_background("charco_agua.png")
