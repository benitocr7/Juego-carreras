import cv2
import os

def resize_road(filename, width=960, height=720):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    img = cv2.imread(path)
    if img is None:
        print(f"Failed to load {path}")
        return

    resized = cv2.resize(img, (width, height))
    cv2.imwrite(path, resized)
    print(f"Resized {filename} to {width}x{height}")

if __name__ == "__main__":
    resize_road("carreterav1.png")
    resize_road("carreterav2.png")
    resize_road("carreterav3.png")
    resize_road("carreterav4.png")
