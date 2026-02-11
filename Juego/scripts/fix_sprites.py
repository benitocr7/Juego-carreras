import cv2
import numpy as np
import os

def remove_background(image_path):
    print(f"Processing {image_path}...")
    
    # Read image with alpha channel if exists, otherwise assume RGB
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Error: Could not read {image_path}")
        return

    # Convert to BGRA if it's BGR
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    h, w = img.shape[:2]

    # Create a mask for floodFill (needs to be 2 pixels larger than image)
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Flood fill from all 4 corners
    # We assume the background touches at least one corner.
    # We replace the background color with a specific internal marker color first, 
    # to identify it, then set alpha to 0 for those pixels.
    # Actually, simpler: We can just use floodFill to find the connected components 
    # starting from corners and set their alpha to 0.

    # LoDist and UpDist define the tolerance. 
    # A tolerance of (10, 10, 10) should handle slight compression or noise.
    # 20 might be safer for checkerboards that aren't perfectly uniform.
    tolerance = (50, 50, 50) 
    
    # We will assume corner (0,0) is background
    seed_points = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1)]
    
    for seed in seed_points:
        # Check if this pixel is already transparent (alpha=0), if so, skip/continue
        # or if it's already processed.
        # But floodFill modifies the image inplace.
        
        # NewVAL: We want to set it to transparent. 
        # But floodFill normally sets color. 
        # We can't directly set alpha with floodFill easily if we want to preserve color but set alpha=0.
        # So instead we create a binary mask of what IS background.
        
        # Workaround:
        # 1. Create a simpler BGR version to calculate the mask? No, alpha matters.
        # 2. Use floodFill on a copy to determine the mask of pixels to be removed.
        
        temp_img = img.copy()
        
        # Allow a broad range for background (handling checkerboard white/grey)
        # 255, 255, 255 (White) and 200, 200, 200 (Grey) are quite different.
        # Flood fill might stop at boundaries.
        
        # Let's try a different heuristic:
        # Just manually check corners. If it's a checkerboard, it might be white or gray.
        # We run floodFill with a very high tolerance? No.
        
        # Better approach for simpler sprites:
        # Execute floodFill with NEW_VAL=(0,0,0,0) on the image itself.
        # This effectively makes it transparent black.
        
        # Note: floodFill works on 1 or 3 channel images best, 4 channel support varies or requires careful flags.
        # Let's try 3 channels first to get the mask, then apply to alpha.
        
        # Ensure contiguous array for OpenCV
        bgr = np.ascontiguousarray(img[:, :, :3])
        mask_flood = np.zeros((h + 2, w + 2), np.uint8)
        
        # Flood fill on BGR to find connected background component
        # usage: cv2.floodFill(image, mask, seedPoint, newVal, loDiff, upDiff, flags)
        # newVal doesn't matter for the mask, but changes image.
        
        # We use simple loDiff/upDiff.
        # For checkerboard (white/grey), the diff is large (55).
        # Let's try 60 tolerance.
        
        flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE
        
        # Only process if pixel is part of background
        # We repeatedly apply flood fill.
        
        cv2.floodFill(bgr, mask_flood, seed, (0,0,0), (60,60,60), (60,60,60), flags)
        
        # Extract the actual mask (remove expected 1px border from mask initialization... wait, mask is h+2, w+2)
        # The mask returned has 255 where filled. 
        actual_mask = mask_flood[1:-1, 1:-1]
        
        # Set alpha to 0 where mask is 255
        img[actual_mask == 255, 3] = 0

    print(f"Saving fixed {image_path}")
    cv2.imwrite(image_path, img)

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    cars = ["player_car.png", "enemy_car.png"]
    
    for car in cars:
        path = os.path.join(assets_dir, car)
        if os.path.exists(path):
            remove_background(path)
        else:
            print(f"Not found: {path}")
