import cv2
import numpy as np
import os

def create_road_variant(variant_num=1, width=960, height=840):
    """Create different road variations with different styling"""
    
    print(f"Generating road variant {variant_num}...")
    
    # Base Asphalt (Dark Grey)
    img = np.full((height, width, 3), 60, dtype=np.uint8)
    
    # Add Monochromatic Gaussian noise for texture
    noise = np.random.normal(0, 2, (height, width)).astype(np.uint8)
    noise_rgb = cv2.merge([noise, noise, noise])
    img = cv2.add(img, noise_rgb)
    
    # Variant-specific styling - todos con patrones que se repiten perfectamente
    
    if variant_num == 1:
        # Variant 1: Red and White curbs with dashed center lines
        curb_w = 30
        stripe_pattern = 60  # Patrón que se repite cada 60 píxeles
        
        for y in range(0, height, stripe_pattern):
            is_white = (y // stripe_pattern) % 2 == 0
            color = (220, 220, 220) if is_white else (50, 50, 220)
            
            # Curbs left and right
            cv2.rectangle(img, (0, y), (curb_w, y + stripe_pattern), color, -1)
            cv2.rectangle(img, (width - curb_w, y), (width, y + stripe_pattern), color, -1)
        
        # Center dashed lines - patrón repetible
        lane_w = 12
        lane_segment = 60
        gap_segment = 60
        center_x = width // 2
        pattern_height = lane_segment + gap_segment
        
        for y in range(0, height, pattern_height):
            cv2.rectangle(img, (center_x - lane_w//2, y), (center_x + lane_w//2, y + lane_segment), (220, 220, 220), -1)
    
    elif variant_num == 2:
        # Variant 2: Yellow curbs with double lines
        curb_w = 35
        stripe_pattern = 80
        
        for y in range(0, height, stripe_pattern):
            color = (0, 255, 255)  # Cyan/Yellow
            cv2.rectangle(img, (0, y), (curb_w, y + stripe_pattern), color, -1)
            cv2.rectangle(img, (width - curb_w, y), (width, y + stripe_pattern), color, -1)
        
        # Double center lines con patrón repetible
        center_x = width // 2
        line_spacing = 8
        line_w = 6
        pattern_height = 100
        
        for y in range(0, height, pattern_height):
            # Left line
            cv2.rectangle(img, (center_x - line_spacing - line_w, y), (center_x - line_spacing, y + 80), (0, 255, 255), -1)
            # Right line
            cv2.rectangle(img, (center_x + line_spacing, y), (center_x + line_spacing + line_w, y + 80), (0, 255, 255), -1)
    
    elif variant_num == 3:
        # Variant 3: Green curbs with alternating segments
        curb_w = 32
        stripe_pattern = 70
        
        for y in range(0, height, stripe_pattern * 2):  # Patrón cada 2 segmentos
            is_visible = (y // stripe_pattern) % 2 == 0
            if is_visible:
                color = (0, 200, 0)  # Green
                cv2.rectangle(img, (0, y), (curb_w, y + stripe_pattern), color, -1)
                cv2.rectangle(img, (width - curb_w, y), (width, y + stripe_pattern), color, -1)
        
        # Center lane con patrón repetible
        center_x = width // 2
        lane_w = 15
        pattern_height = 90
        
        for y in range(0, height, pattern_height):
            if (y // pattern_height) % 2 == 0:
                cv2.rectangle(img, (center_x - lane_w//2, y), (center_x + lane_w//2, y + 70), (0, 200, 0), -1)
    
    elif variant_num == 4:
        # Variant 4: Orange curbs with triple lines
        curb_w = 28
        stripe_pattern = 90
        
        for y in range(0, height, stripe_pattern):
            color = (255, 100, 0)  # Orange/Blue in BGR
            cv2.rectangle(img, (0, y), (curb_w, y + stripe_pattern), color, -1)
            cv2.rectangle(img, (width - curb_w, y), (width, y + stripe_pattern), color, -1)
        
        # Triple center lines con patrón repetible
        center_x = width // 2
        line_w = 6
        spacing = 12
        pattern_height = 110
        
        for y in range(0, height, pattern_height):
            # Left line
            cv2.rectangle(img, (center_x - spacing - line_w, y), (center_x - spacing, y + 90), (255, 100, 0), -1)
            # Center line
            cv2.rectangle(img, (center_x - line_w//2, y), (center_x + line_w//2, y + 90), (255, 100, 0), -1)
            # Right line
            cv2.rectangle(img, (center_x + spacing, y), (center_x + spacing + line_w, y + 90), (255, 100, 0), -1)
    
    # Save
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    output_path = os.path.join(assets_dir, f"carreterav{variant_num}.png")
    cv2.imwrite(output_path, img)
    print(f"Saved road variant {variant_num} to {output_path}")

if __name__ == "__main__":
    for v in range(1, 5):
        create_road_variant(v)
    print("All road variants generated!")
