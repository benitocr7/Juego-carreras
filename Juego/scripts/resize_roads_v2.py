import cv2
import os

def crop_and_resize_road(filename, width=960, height=840):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    img = cv2.imread(path)
    if img is None:
        print(f"Failed to load {path}")
        return

    # User wants ONLY the road, no background (trees/snow/grass).
    # Assuming vertical road in the middle.
    # We should crop the center part of the image where the road usually is.
    # Let's crop the middle 50% width? And scale that to fill the screen.
    
    h, w, _ = img.shape
    
    # Crop settings (adjustable)
    # Keeping mostly the center. 
    # Let's keep center 60% of the width
    crop_w = int(w * 0.5) 
    start_x = (w - crop_w) // 2
    
    # We want to stretch this crop to 960 width.
    # And keep height full or crop too? Usually height is fine.
    
    cropped = img[0:h, start_x:start_x+crop_w]
    
    # Now resize to Target game dimension
    final_img = cv2.resize(cropped, (width, height))
    
    cv2.imwrite(path, final_img)
    print(f"Processed {filename}: Cropped center and stretched to {width}x{height}")

if __name__ == "__main__":
    # Also process the original road variants
    for name in ["carreterav1.png", "carreterav2.png", "carreterav3.png", "carreterav4.png"]:
        crop_and_resize_road(name)
