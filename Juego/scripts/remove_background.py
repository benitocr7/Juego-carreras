import cv2
import numpy as np
import os

def remove_background_from_image(input_path, output_path, tolerance=50):
    """
    Remove background from an image and make it transparent
    More aggressive approach to remove all background
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image with transparency
        tolerance: Color tolerance for background detection
    """
    
    print(f"Procesando imagen: {input_path}")
    
    # Read image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: No se pudo cargar {input_path}")
        return
    
    # Get image dimensions
    h, w = img.shape[:2]
    print(f"Dimensiones: {w}x{h}")
    
    # Convert to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Create a copy for processing
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Get the background color from the corner (top-left corner should be background)
    bg_color = img_hsv[0, 0]
    print(f"Color de fondo detectado en esquina: {bg_color}")
    
    # Create mask for background colors (with higher tolerance for HSV)
    # HSV ranges: H(0-180), S(0-255), V(0-255)
    lower = np.array([bg_color[0] - 20, 0, 0])  
    upper = np.array([bg_color[0] + 20, 255, 255])
    
    # Also handle colors similar to the background
    mask1 = cv2.inRange(img_hsv, lower, upper)
    
    # Additional check: pixels that are very close to the original color
    img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    bg_lab = img_lab[0, 0]
    lower_lab = np.array([bg_lab[0] - 40, bg_lab[1] - 20, bg_lab[2] - 20])
    upper_lab = np.array([bg_lab[0] + 40, bg_lab[1] + 20, bg_lab[2] + 20])
    
    mask2 = cv2.inRange(img_lab, lower_lab, upper_lab)
    
    # Combine masks
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Invert mask (we want to keep the object, remove background)
    mask_inv = cv2.bitwise_not(mask)
    
    # Apply morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask_inv = cv2.morphologyEx(mask_inv, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask_inv = cv2.morphologyEx(mask_inv, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Dilate slightly to ensure clean edges
    mask_inv = cv2.dilate(mask_inv, kernel, iterations=1)
    
    # Convert image to BGRA (add alpha channel)
    bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # Set alpha channel based on mask
    bgra[:, :, 3] = mask_inv
    
    # Save result
    cv2.imwrite(output_path, bgra)
    print(f"Imagen guardada en: {output_path}")
    print(f"Píxeles con transparencia: {np.sum(mask_inv == 0)}")

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    # Process moto
    moto_input = os.path.join(assets_dir, "moto.png")
    moto_output = os.path.join(assets_dir, "moto.png")
    
    if os.path.exists(moto_input):
        print("=" * 60)
        print("Procesando MOTO...")
        print("=" * 60)
        remove_background_from_image(moto_input, moto_output, tolerance=50)
    else:
        print(f"No se encontró: {moto_input}")
    
    # Process camion
    camion_input = os.path.join(assets_dir, "camion.png")
    camion_output = os.path.join(assets_dir, "camion.png")
    
    if os.path.exists(camion_input):
        print("\n" + "=" * 60)
        print("Procesando CAMIÓN...")
        print("=" * 60)
        remove_background_from_image(camion_input, camion_output, tolerance=50)
    else:
        print(f"No se encontró: {camion_input}")
    
    print("\n✅ Procesamiento completado!")
    print("Las imágenes ahora solo tienen los vehículos sin fondo.")
    print("Las colisiones usarán máscaras pixel-perfect basadas en la transparencia.")
