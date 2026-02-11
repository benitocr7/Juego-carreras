import cv2
import numpy as np
import os

def remove_background_floodfill(filename, tolerance=40):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    # Load image with alpha if present, or add it
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to load {path}")
        return

    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Work on a copy for the mask
    # We want to floodfill from (0,0) assuming top-left is background
    h, w = img.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    
    # Extract BGR for floodfill (alpha doesn't matter for the color difference check usually)
    # But often these fake pngs have white/grey squares.
    # FloodFill options:
    # loDiff: max lower brightness/color difference
    # upDiff: max upper brightness/color difference
    # flags: 4 or 8 connectivity + FLOODFILL_MASK_ONLY likely?
    # Actually, let's just modify the image directly or create a mask.
    
    # We will run floodfill on the BGR channels.
    # Seed point: (0,0).
    # We need to handle the case where the background is a pattern (checkerboard).
    # Floodfill might stop at the color change of the checkerboard.
    # If it's a checkerboard, it's usually White (255) and Grey (~204 or similar).
    # The tolerance needs to be high enough to cover both, OR we run it multiple times?
    # Or we assume the car is NOT touching the corners.
    
    # Let's try a simpler approach if it's a checkerboard:
    # 1. Floodfill from (0,0).
    # 2. Floodfill from (0, w-1).
    # 3. Floodfill from (h-1, 0).
    # 4. Floodfill from (h-1, w-1).
    # Using a high tolerance might eat into the car if the car is white/grey.
    
    # Alternative: Magic Wand style.
    # The user image showed a checkerboard.
    # Let's try a standard floodfill with high tolerance (e.g. 50) from the top-left.
    
    flood_flags = 4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255 << 8)
    
    # We use a loose tolerance to catch the grey squares too.
    # If the car is distinct in color (Red/Blue), this should be safe.
    # The car in the screenshot is Red, background is White/Grey.
    # 60 tolerance should bridge the gap between white(255) and light grey(190-200).
    
    # Seed at 0,0
    cv2.floodFill(img, mask, (0,0), (0,0,0,0), (tolerance,)*3, (tolerance,)*3, flood_flags)
    
    # Also seed at other corners just in case
    cv2.floodFill(img, mask, (w-1,0), (0,0,0,0), (tolerance,)*3, (tolerance,)*3, flood_flags)
    cv2.floodFill(img, mask, (0,h-1), (0,0,0,0), (tolerance,)*3, (tolerance,)*3, flood_flags)
    cv2.floodFill(img, mask, (w-1,h-1), (0,0,0,0), (tolerance,)*3, (tolerance,)*3, flood_flags)
    
    # mask now has 255 where the background is.
    # The mask is size (h+2, w+2). We crop it.
    mask_cropped = mask[1:-1, 1:-1]
    
    # Apply to Alpha channel
    # Where mask is 255 (background), Alpha = 0
    # Where mask is 0 (foreground), Alpha remains (or 255)
    
    b, g, r, a = cv2.split(img)
    
    # Set alpha to 0 where mask is 255
    # We use bitwise_not to get foreground as 255, background as 0
    foreground_mask = cv2.bitwise_not(mask_cropped)
    
    # Update alpha: keep original alpha AND the new mask
    # If original was opaque(255) and it's background(mask=0), it becomes 0.
    new_a = cv2.bitwise_and(a, foreground_mask)
    
    out_img = cv2.merge((b, g, r, new_a))
    
    cv2.imwrite(path, out_img)
    print(f"Processed {filename} with FloodFill.")

if __name__ == "__main__":
    # Process both
    remove_background_floodfill("cars1.png", tolerance=60)
    remove_background_floodfill("car_enemy.png", tolerance=60)
