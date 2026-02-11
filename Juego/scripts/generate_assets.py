import cv2
import numpy as np
import os

def create_road_texture(width=960, height=840): # Width reduced for sidebar
    print("Generating road texture...")
    
    # 1. Base Asphalt (Dark Grey)
    # Create dark grey background
    img = np.full((height, width, 3), 60, dtype=np.uint8)
    
    # Add Monochromatic Gaussian noise for texture (Greyscale noise)
    # We generate one channel of noise and apply it to all 3 channels
    noise = np.random.normal(0, 2, (height, width)).astype(np.uint8)
    noise_rgb = cv2.merge([noise, noise, noise])
    
    img = cv2.add(img, noise_rgb)
    
    # 2. Curbs (Red and White stripes) - patrón repetible
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
        
    # 3. Lane Markers (Dashed Lines) - patrón repetible
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

def create_enemy_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # 1. Motorcycle (Small, thin, fast look)
    # Size: 50x90
    moto = np.zeros((90, 50, 4), dtype=np.uint8)
    
    # Body (Yellow/Black)
    cv2.rectangle(moto, (15, 10), (35, 80), (0, 255, 255, 255), -1) # Yellow body
    cv2.circle(moto, (25, 20), 10, (50, 50, 50, 255), -1) # Helmet/Head
    
    # Wheels
    cv2.rectangle(moto, (10, 10), (15, 30), (0, 0, 0, 255), -1)
    cv2.rectangle(moto, (35, 10), (40, 30), (0, 0, 0, 255), -1)
    cv2.rectangle(moto, (10, 60), (15, 80), (0, 0, 0, 255), -1)
    cv2.rectangle(moto, (35, 60), (40, 80), (0, 0, 0, 255), -1)

    cv2.imwrite(os.path.join(assets_dir, "moto.png"), moto)
    print("Saved moto.png")

    # 2. Truck (Large, long, slow look)
    # Size: 140x250 (Wider than car 130, much longer)
    truck = np.zeros((250, 140, 4), dtype=np.uint8)
    
    # Trailer (Grey/White)
    cv2.rectangle(truck, (10, 10), (130, 200), (200, 200, 200, 255), -1)
    # Cab (Blue or Red)
    cv2.rectangle(truck, (20, 200), (120, 240), (200, 0, 0, 255), -1) # Blue Cab (BGR)
    
    # Details
    cv2.line(truck, (10, 10), (10, 200), (100, 100, 100, 255), 2)
    cv2.line(truck, (130, 10), (130, 200), (100, 100, 100, 255), 2)
    
    cv2.imwrite(os.path.join(assets_dir, "truck.png"), truck)
    print("Saved truck.png")

    # 3. Power-ups Icons
    
    # Heart (Lives) - 40x40
    heart = np.zeros((40, 40, 4), dtype=np.uint8)
    # Draw two circles and a triangle
    cv2.circle(heart, (12, 12), 12, (0, 0, 255, 255), -1) # Left lobe (BGR - Red)
    cv2.circle(heart, (28, 12), 12, (0, 0, 255, 255), -1) # Right lobe
    triangle_cnt = np.array([(0, 15), (40, 15), (20, 40)])
    cv2.drawContours(heart, [triangle_cnt], 0, (0, 0, 255, 255), -1)
    cv2.imwrite(os.path.join(assets_dir, "heart.png"), heart)
    print("Saved heart.png")

    # Shield (Powerup) - 50x50
    shield = np.zeros((50, 50, 4), dtype=np.uint8)
    # Blue shield shape
    cv2.circle(shield, (25, 25), 23, (255, 0, 0, 255), -1) # Blue background
    cv2.circle(shield, (25, 25), 18, (200, 200, 255, 255), 2) # Inner ring
    cv2.putText(shield, "S", (12, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255, 255), 4)
    cv2.imwrite(os.path.join(assets_dir, "shield.png"), shield)
    print("Saved shield.png")

    # Turbo (Powerup) - 50x50
    turbo = np.zeros((50, 50, 4), dtype=np.uint8)
    # Yellow background
    cv2.circle(turbo, (25, 25), 23, (0, 255, 255, 255), -1) # Yellow
    # Red Lightning bolt
    bolt = np.array([(20, 10), (35, 10), (15, 40), (30, 40)]) # Simple shape
    cv2.line(turbo, (28, 10), (15, 25), (0, 0, 255, 255), 3)
    cv2.line(turbo, (15, 25), (35, 25), (0, 0, 255, 255), 3)
    cv2.line(turbo, (35, 25), (22, 45), (0, 0, 255, 255), 3)
    cv2.imwrite(os.path.join(assets_dir, "turbo.png"), turbo)
    cv2.imwrite(os.path.join(assets_dir, "turbo.png"), turbo)
    print("Saved turbo.png")


def create_car_variations():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    colors = [
        (0, 0, 255, 255),    # Red
        (255, 0, 0, 255),    # Blue
        (0, 255, 0, 255),    # Green
        (255, 0, 255, 255),  # Magenta
        (255, 255, 0, 255),  # Cyan
        (50, 50, 50, 255)    # Grey
    ]
    
    for i, color in enumerate(colors):
        # Base Car Shape (130x130)
        car = np.zeros((130, 130, 4), dtype=np.uint8)
        
        # Body
        cv2.rectangle(car, (30, 10), (100, 120), color, -1)
        
        # Windows (Black)
        cv2.rectangle(car, (40, 30), (90, 50), (20, 20, 20, 255), -1) # Front
        cv2.rectangle(car, (40, 80), (90, 95), (20, 20, 20, 255), -1) # Back
        
        # Stripes (White or Black depending on brightness)
        stripe_color = (255, 255, 255, 255) if color != (255, 255, 255, 255) else (0, 0, 0, 255)
        
        if i % 2 == 0:
            # Dual Stripe
            cv2.rectangle(car, (50, 10), (55, 120), stripe_color, -1)
            cv2.rectangle(car, (75, 10), (80, 120), stripe_color, -1)
        else:
            # Single Center Stripe
            cv2.rectangle(car, (60, 10), (70, 120), stripe_color, -1)

        # Wheels
        wheel_color = (0, 0, 0, 255)
        cv2.rectangle(car, (15, 20), (30, 45), wheel_color, -1)
        cv2.rectangle(car, (100, 20), (115, 45), wheel_color, -1)
        cv2.rectangle(car, (15, 85), (30, 110), wheel_color, -1)
        cv2.rectangle(car, (100, 85), (115, 110), wheel_color, -1)

        if i == 1: # Save Blue car as the default 'enemy_car.png'
             cv2.imwrite(os.path.join(assets_dir, "enemy_car.png"), car)
             
        filename = f"car_v{i}.png"
        cv2.imwrite(os.path.join(assets_dir, filename), car)
        print(f"Saved {filename}")

    # Player Car (Realistic Red Sports Car - Ferrari Style)
    player = np.zeros((130, 130, 4), dtype=np.uint8)
    
    # 1. Shadow/Glow (Soft black rect underneath)
    cv2.rectangle(player, (25, 10), (105, 125), (0, 0, 0, 100), -1) 
    
    # 2. Body Shape (Sculpted)
    # Main hull - Red (BGR)
    red_paint = (10, 10, 220, 255)
    
    # Rear Section (Wide)
    pts_rear = np.array([[30, 80], [100, 80], [100, 120], [30, 120]], np.int32)
    cv2.fillPoly(player, [pts_rear], red_paint)
    
    # Cabin/Front Section (Tapering)
    pts_front = np.array([[30, 80], [100, 80], [90, 20], [40, 20]], np.int32)
    cv2.fillPoly(player, [pts_front], red_paint)
    
    # Front Wing/Bumper
    cv2.rectangle(player, (35, 10), (95, 20), red_paint, -1)

    # 3. Cockpit / Glass
    # Dark Tinted Glass
    glass_color = (40, 40, 40, 255)
    # Windshield
    pts_shield = np.array([[45, 50], [85, 50], [82, 35], [48, 35]], np.int32)
    cv2.fillPoly(player, [pts_shield], glass_color)
    # Roof
    cv2.rectangle(player, (46, 50), (84, 75), red_paint, -1)
    # Rear Window
    pts_rear_glass = np.array([[46, 75], [84, 75], [88, 85], [42, 85]], np.int32)
    cv2.fillPoly(player, [pts_rear_glass], glass_color)

    # 4. Details
    # Side Intakes (Black)
    cv2.fillPoly(player, [np.array([[30, 60], [40, 65], [30, 80]], np.int32)], (0,0,0,255))
    cv2.fillPoly(player, [np.array([[100, 60], [90, 65], [100, 80]], np.int32)], (0,0,0,255))
    
    # Spoiler (Black Carbon Fiber)
    cv2.rectangle(player, (25, 115), (105, 122), (20, 20, 20, 255), -1)
    
    # Headlights (Bright White/Blue)
    cv2.fillPoly(player, [np.array([[38, 12], [45, 12], [42, 25]], np.int32)], (255, 255, 200, 255))
    cv2.fillPoly(player, [np.array([[92, 12], [85, 12], [88, 25]], np.int32)], (255, 255, 200, 255))
    
    # Taillights (Round Red)
    cv2.circle(player, (40, 120), 4, (0, 0, 255, 255), -1)
    cv2.circle(player, (90, 120), 4, (0, 0, 255, 255), -1)
    
    # Racing Stripes (White - Double center)
    cv2.rectangle(player, (60, 10), (62, 125), (255, 255, 255, 255), -1)
    cv2.rectangle(player, (68, 10), (70, 125), (255, 255, 255, 255), -1)

    # 5. Wheels (Slicks)
    wheel_color = (20, 20, 20, 255)
    cv2.rectangle(player, (18, 25), (30, 45), wheel_color, -1)
    cv2.rectangle(player, (100, 25), (112, 45), wheel_color, -1)
    cv2.rectangle(player, (18, 90), (30, 110), wheel_color, -1)
    cv2.rectangle(player, (100, 90), (112, 110), wheel_color, -1)

    cv2.imwrite(os.path.join(assets_dir, "player_car.png"), player)
    print("Saved player_car.png (Detailed)")

def create_realistic_others():
    # Moto y Truck: Usar las imágenes del usuario si existen, no generar
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    moto_path = os.path.join(assets_dir, "moto.png")
    truck_path = os.path.join(assets_dir, "camion.png")
    
    # Solo generar si no existen (fallback)
    if not os.path.exists(moto_path):
        print("moto.png no encontrado, saltando generación (coloca la imagen en assets/)")
    
    if not os.path.exists(truck_path):
        print("camion.png no encontrado, saltando generación (coloca la imagen en assets/)")

if __name__ == "__main__":
    create_road_texture()
    create_car_variations()
    create_realistic_others()
    create_enemy_assets()
