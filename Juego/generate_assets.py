import cv2
import numpy as np
import os

def create_road_texture(width=960, height=720): # Width reduced for sidebar
    print("Generating road texture...")
    
    # 1. Base Asphalt (Dark Grey)
    # Create dark grey background
    img = np.full((height, width, 3), 60, dtype=np.uint8)
    
    # Add Monochromatic Gaussian noise for texture (Greyscale noise)
    # We generate one channel of noise and apply it to all 3 channels
    noise = np.random.normal(0, 3, (height, width)).astype(np.uint8)
    noise_rgb = cv2.merge([noise, noise, noise])
    
    img = cv2.add(img, noise_rgb)
    
    # 2. Curbs (Red and White stripes)
    # Stripe height
    stripe_h = 60
    curb_w = 30
    
    for y in range(0, height, stripe_h):
        # Colors: White (220, 220, 220) and Red (50, 50, 220) in BGR
        is_white = (y // stripe_h) % 2 == 0
        color = (220, 220, 220) if is_white else (50, 50, 220) 
        
        # Left Curb
        cv2.rectangle(img, (0, y), (curb_w, y + stripe_h), color, -1)
        # Right Curb
        cv2.rectangle(img, (width - curb_w, y), (width, y + stripe_h), color, -1)
        
    # 3. Lane Markers (Dashed Lines)
    lane_w = 12
    lane_h = 60
    gap_h = 60
    center_x = width // 2
    
    for y in range(0, height, lane_h + gap_h):
        cv2.rectangle(img, (center_x - lane_w//2, y), (center_x + lane_w//2, y + lane_h), (220, 220, 220), -1)

    # 4. Save
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    output_path = os.path.join(assets_dir, "road_texture.png")
    cv2.imwrite(output_path, img)
    print(f"Saved road texture to {output_path}")

if __name__ == "__main__":
    create_road_texture(width=960, height=720) # 1280 - 320 (sidebar) = 960
