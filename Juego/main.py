import cv2
import mediapipe as mp
import pygame
import math
import random
import numpy as np
import os
from gestos import detectar_gestos_manos

# ================== CÁMARA ==================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error cámara")
    exit()

# ================== MEDIAPIPE ==================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

# ================== PYGAME ==================
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carreras por Gestos")

# ================== CARGA DE IMÁGENES ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

try:
    PLAYER_IMG_RAW = pygame.image.load(os.path.join(ASSETS_DIR, "player_car.png"))
    ENEMY_IMG_RAW = pygame.image.load(os.path.join(ASSETS_DIR, "enemy_car.png"))
except Exception as e:
    print(f"Error cargando imágenes: {e}")
    PLAYER_IMG_RAW.fill((0, 255, 0))
    ENEMY_IMG_RAW = pygame.Surface((50, 80))
    ENEMY_IMG_RAW.fill((255, 0, 0))

try:
    ROAD_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "road_texture.png"))
except Exception as e:
    print(f"Error cargando carretera: {e}")
    ROAD_IMG = pygame.Surface((960, HEIGHT))
    ROAD_IMG.fill((60, 60, 60))

# ================== ESTADOS DEL JUEGO ==================
GAME_STATE = "START"  # START, PLAYING, GAME_OVER

# Layout
SIDEBAR_WIDTH = 320
GAME_WIDTH = WIDTH - SIDEBAR_WIDTH

# Variables globales del juego (se reinician en reset_game)
car_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
car_y = HEIGHT - 120
car_w, car_h = 130, 130 # Hecho AUN MÁS grande y ancho
car_angle = 0
speed = 0
score = 0
oncoming_cars = []
spawn_timer = 0
game_over = False
road_y = 0
MAX_SPEED = 12

# Redimensionar jugador
player_img = pygame.transform.scale(PLAYER_IMG_RAW, (car_w, car_h))

font = pygame.font.SysFont(None, 36)


# ================== NUBES ==================
clouds = []
for _ in range(5):
    clouds.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT // 2 - 50),
        'speed': random.uniform(0.5, 1.5)
    })

def reset_game():
    global car_x, car_y, car_angle, speed, score, oncoming_cars, spawn_timer, game_over, GAME_STATE, road_y
    car_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
    car_y = HEIGHT - 120
    car_angle = 0
    speed = 0
    score = 0
    oncoming_cars = []
    spawn_timer = 0
    game_over = False
    road_y = 0
    GAME_STATE = "PLAYING"

def draw_text_centered(text, font, color, surface, offset_y=0, x_offset=0):
    text_obj = font.render(text, True, color)
    # Centrado respecto al área de juego (desplazado por SIDEBAR_WIDTH)
    center_x = SIDEBAR_WIDTH + GAME_WIDTH // 2 + x_offset
    text_rect = text_obj.get_rect(center=(center_x, HEIGHT // 2 + offset_y))
    surface.blit(text_obj, text_rect)

# ================== LOOP ==================
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(30)
    screen.fill((25, 25, 25))
    
    # 0. LEER CÁMARA (Una vez por frame)
    ret, frame = cap.read()
    gesto = "NONE"
    
    if ret:
        frame = cv2.flip(frame, 1)
        # Convertir a RGB una vez para procesar y mostrar
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar mano
        result = hands.process(frame_rgb)
        
        # Dibujar landmarks en el frame original (BGR) para mostrar en Sidebar
        if result.multi_hand_landmarks and result.multi_handedness:
             gesto = detectar_gestos_manos(result.multi_hand_landmarks, result.multi_handedness)
             for hand in result.multi_hand_landmarks:
                 mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    # 1. DIBUJAR SIDEBAR (Izquierda)
    pygame.draw.rect(screen, (20, 20, 40), (0, 0, SIDEBAR_WIDTH, HEIGHT))
    
    # Mostrar Cámara en el Sidebar
    if ret:
        # Redimensionar frame (ya tiene landmarks dibujados) para el sidebar (320x240)
        # Convertimos a RGB para pygame
        frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_display = cv2.resize(frame_display, (SIDEBAR_WIDTH, 240))
        frame_surface = pygame.surfarray.make_surface(np.transpose(frame_display, (1, 0, 2)))
        screen.blit(frame_surface, (0, 0))

    # Mostrar Estadísticas en el Sidebar
    if GAME_STATE == "PLAYING" or GAME_STATE == "GAME_OVER":
        screen.blit(font.render("PUNTUACIÓN", True, (200, 200, 200)), (20, 300))
        screen.blit(font.render(f"{int(score)}", True, (255, 215, 0)), (20, 340))
        
        screen.blit(font.render("VELOCIDAD", True, (200, 200, 200)), (20, 400))
        screen.blit(font.render(f"{int(speed * 10)} km/h", True, (0, 255, 255)), (20, 440))
    
    # Separador
    pygame.draw.line(screen, (255, 255, 255), (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if GAME_STATE == "START":
                if event.key == pygame.K_SPACE:
                    reset_game()
            elif GAME_STATE == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()

    # 1.5 FONDO (Nubes)
    # Dibujar cielo y nubes detras del juego (pero ya limpiamos screen)
    # Solo necesitamos dibujar el fondo en la zona de juego
    sky_rect = (SIDEBAR_WIDTH, 0, GAME_WIDTH, HEIGHT // 2)
    pygame.draw.rect(screen, (135, 206, 235), sky_rect)
    
    for cloud in clouds:
        # Ajustar X de nubes para el area de juego si queremos, o dejarlas globales
        # Las nubes son globales, las dibujamos si caen en la zona de juego
        # Simple: dibujar y que el sidebar tape si es necesario (pero ya dibujamos sidebar)
        # Mejor dibujamos clouds solo en la zona derecha
        if cloud['x'] > SIDEBAR_WIDTH: 
             pygame.draw.circle(screen, (255, 255, 255), (cloud['x'], cloud['y']), 20)
             pygame.draw.circle(screen, (255, 255, 255), (cloud['x'] + 15, cloud['y']), 25)
             pygame.draw.circle(screen, (255, 255, 255), (cloud['x'] + 30, cloud['y']), 20)
        
        cloud['x'] += cloud['speed']
        if cloud['x'] > WIDTH + 50:
            cloud['x'] = SIDEBAR_WIDTH - 50

    # Decoración lateral (Césped)
    for y in range(0, HEIGHT, 100):
        pygame.draw.rect(screen, (0, 100, 0), (SIDEBAR_WIDTH, y, 50, 80)) # Izquierda del juego
        pygame.draw.rect(screen, (0, 100, 0), (WIDTH - 100, y, 50, 80)) # Derecha total

    if GAME_STATE == "START":
        # Pantalla de Inicio (En el área de juego)
        pygame.draw.rect(screen, (30, 30, 50), (SIDEBAR_WIDTH, 0, GAME_WIDTH, HEIGHT))
        
        draw_text_centered("CARRERAS POR GESTOS", font, (255, 215, 0), screen, -100)
        
        inst_font = pygame.font.SysFont(None, 28)
        draw_text_centered("Instrucciones:", inst_font, (200, 200, 200), screen, -40)
        draw_text_centered("- Usa tus manos para girar", inst_font, (255, 255, 255), screen, 0)
        draw_text_centered("- Puño: FRENAR | Mano abierta: ACELERAR", inst_font, (255, 255, 255), screen, 30)

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_text_centered("Presiona ESPACIO para Iniciar", font, (0, 255, 0), screen, 120)


    elif GAME_STATE == "PLAYING" or GAME_STATE == "GAME_OVER":
        # CARRETERA SCROLLING
        if GAME_STATE == "PLAYING":
            road_y = (road_y + speed) % HEIGHT
        
        # Dibujar dos copias para el efecto infinito
        # La carretera se mueve hacia ABAJO (speed > 0)
        # Dibujamos una en road_y y otra justo arriba (road_y - HEIGHT)
        screen.blit(ROAD_IMG, (SIDEBAR_WIDTH, road_y))
        screen.blit(ROAD_IMG, (SIDEBAR_WIDTH, road_y - HEIGHT))

        # LOGICA DEL JUEGO
        if GAME_STATE == "PLAYING":
            # YA NO LEEMOS CÁMARA AQUÍ, USAMOS 'gesto' calculado arriba
            
            speed = max(0, speed - 0.1)
            if "STOP" in gesto:
                speed = 0
            elif "ACCEL" in gesto:
                speed = min(MAX_SPEED, speed + 0.3)

            car_angle = 0
            if "LEFT" in gesto:
                car_angle -= 1.0
            if "RIGHT" in gesto:
                car_angle += 1.0

            car_angle = max(-math.pi / 2, min(math.pi / 2, car_angle))

            car_x += speed * math.sin(car_angle)
            car_y -= speed * math.cos(car_angle)

            if car_y < -car_h:
                car_y = HEIGHT
                car_angle = 0

            # Limites del coche (Respetando Sidebar y nuevas dimensiones)
            # Road start: SIDEBAR_WIDTH (320)
            # Game Width: 960. Road width approx same. 
            # Curbs approx 30px on each side.
            # Safe zone: 320 + 30 to 1280 - 30
            
            min_x = SIDEBAR_WIDTH + 40
            max_x = WIDTH - 40 - car_w
            car_x = max(min_x, min(car_x, max_x))

            spawn_timer += 1
            if spawn_timer > 60:
                spawn_timer = 0
                car_type = random.choice([
                    {'w': 130, 'h': 130},
                    {'w': 125, 'h': 125},
                    {'w': 135, 'h': 135},
                    {'w': 120, 'h': 120}
                ])
                enemy_surf = pygame.transform.scale(ENEMY_IMG_RAW, (car_type['w'], car_type['h']))
                
                # Spawn Enemy
                # Ensure they spawn strictly within the lanes
                spawn_min = SIDEBAR_WIDTH + 50
                spawn_max = WIDTH - 50 - car_type['w']
                
                oncoming_cars.append({
                    'x': random.randint(spawn_min, spawn_max),
                    'y': -car_type['h'],
                    'speed': random.randint(7, 12),
                    'surface': enemy_surf,
                    'mask': pygame.mask.from_surface(enemy_surf), 
                    'w': car_type['w'],
                    'h': car_type['h']
                })

            for car in oncoming_cars[:]:
                car['y'] += car['speed']
                if car['y'] > HEIGHT:
                    oncoming_cars.remove(car)
                    score += 10

            # Pre-calcular jugador rotado para colisiones
            rotated_player = pygame.transform.rotate(player_img, math.degrees(-car_angle))
            player_rect = rotated_player.get_rect(center=(car_x + car_w // 2, car_y + car_h // 2))
            player_mask = pygame.mask.from_surface(rotated_player)

            for car in oncoming_cars:
                # Colision por Mascara (Pixel Perfect)
                # Offset es la distancia relativa entre las top-left corners de las mascaras
                offset_x = int(car['x'] - player_rect.left)
                offset_y = int(car['y'] - player_rect.top)
                
                if player_mask.overlap(car['mask'], (offset_x, offset_y)):
                     GAME_STATE = "GAME_OVER"

            if speed > 0:
                score += speed / 10

        # DIBUJAR JUEGO
        # Usamos el player_rect y rotated_player que ya calculamos arriba
        if GAME_STATE == "PLAYING" or GAME_STATE == "GAME_OVER":
            # Si estamos en GAME_OVER, quiza no se calculo player_rect en este frame si salta la logica
            # Pero como esto esta dentro del bucle de "PLAYING" o "GAME_OVER" logic...
            # Espera, la logica de movimiento esta dentro de "if GAME_STATE == 'PLAYING':"
            # Si es GAME_OVER, no entra ahi, asi que necesitamos recalcular para dibujar o guardar el ultimo estado.
            # Para simplificar, recalculamos al dibujar si es necesario, o movemos el dibujo fuera.
            
            # Mejor recalculamos aqui para asegurar que siempre se dibuja bien
            rotated = pygame.transform.rotate(player_img, math.degrees(-car_angle))
            rect = rotated.get_rect(center=(car_x + car_w // 2, car_y + car_h // 2))
            screen.blit(rotated, rect)

            for car in oncoming_cars:
                screen.blit(car['surface'], (car['x'], car['y']))



        if GAME_STATE == "GAME_OVER":
             draw_text_centered("¡Juego Terminado!", font, (255, 0, 0), screen, -20)
             draw_text_centered("Presiona R para Reiniciar", font, (255, 255, 255), screen, 20)



    pygame.display.flip()

cap.release()
pygame.quit()
