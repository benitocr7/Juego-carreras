import cv2
import os

target_w = 960
target_h = 840

files = [
    "road_texture.png",
    "carreterav1.png",
    "carreterav2.png",
    "carreterav3.png",
    "carreterav4.png"
]

print(f"Fixing road assets to {target_w}x{target_h}...")

for f in files:
    path = os.path.join("assets", f)
    if not os.path.exists(path):
        print(f"Skipping {f} (not found)")
        continue
        
    img = cv2.imread(path)
    if img is None:
        print(f"Failed to load {f}")
        continue
        
    # Check current size
    h, w, _ = img.shape
    
    # Force Resize
    if w != target_w or h != target_h:
        # If it's the original road_texture, maybe we mistakenly made it just black?
        # If it's a 'carretera', we might want to crop center again if it's too wide
        
        # Simple resize to force fit
        resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(path, resized)
        print(f"Fixed {f}: {w}x{h} -> {target_w}x{target_h}")
    else:
        print(f"{f} is already correct.")

print("Road assets fixed.")
