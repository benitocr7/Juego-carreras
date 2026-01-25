import cv2
import mediapipe as mp
import pygame
import math
import random
import numpy as np
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

car_x = WIDTH // 2
car_y = HEIGHT - 120
car_w, car_h = 50, 80
car_angle = 0

car_surface = pygame.Surface((car_w, car_h))
car_surface.fill((0, 255, 0))
pygame.draw.circle(car_surface, (0, 0, 0), (10, car_h - 10), 8)
pygame.draw.circle(car_surface, (0, 0, 0), (car_w - 10, car_h - 10), 8)
pygame.draw.circle(car_surface, (255, 255, 0), (5, 10), 5)
pygame.draw.circle(car_surface, (255, 255, 0), (car_w - 5, 10), 5)
pygame.draw.polygon(
    car_surface,
    (173, 216, 230),
    [(10, 15), (car_w - 10, 15), (car_w - 15, 30), (15, 30)]
)

font = pygame.font.SysFont(None, 36)

oncoming_cars = []
spawn_timer = 0

def create_oncoming_car_surface(w, h, color):
    surface = pygame.Surface((w, h))
    surface.fill(color)
    pygame.draw.circle(surface, (0, 0, 0), (10, h - 10), 6)
    pygame.draw.circle(surface, (0, 0, 0), (w - 10, h - 10), 6)
    pygame.draw.circle(surface, (255, 255, 0), (5, h - 15), 4)
    pygame.draw.circle(surface, (255, 255, 0), (w - 5, h - 15), 4)
    pygame.draw.rect(surface, (173, 216, 230), (5, 10, w - 10, h // 2 - 10))
    pygame.draw.polygon(
        surface,
        (173, 216, 230),
        [(10, h - 25), (w - 10, h - 25), (w - 15, h - 35), (15, h - 35)]
    )
    return surface

# ================== NUBES ==================
clouds = []
for _ in range(5):
    clouds.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT // 2 - 50),
        'speed': random.uniform(0.5, 1.5)
    })

score = 0
game_over = False
BASE_SPEED = 4
speed = 0
MAX_SPEED = 12

clock = pygame.time.Clock()
running = True

# ================== LOOP ==================
while running:
    clock.tick(30)
    screen.fill((25, 25, 25))

    pygame.draw.rect(screen, (135, 206, 235), (0, 0, WIDTH, HEIGHT // 2))

    for cloud in clouds:
        pygame.draw.circle(screen, (255, 255, 255), (cloud['x'], cloud['y']), 20)
        pygame.draw.circle(screen, (255, 255, 255), (cloud['x'] + 15, cloud['y']), 25)
        pygame.draw.circle(screen, (255, 255, 255), (cloud['x'] + 30, cloud['y']), 20)
        cloud['x'] += cloud['speed']
        if cloud['x'] > WIDTH + 50:
            cloud['x'] = -50

    for y in range(0, HEIGHT, 100):
        pygame.draw.rect(screen, (0, 100, 0), (50, y, 50, 80))
        pygame.draw.rect(screen, (0, 100, 0), (WIDTH - 100, y, 50, 80))

    # CARRETERA (NO SE TOCA)
    pygame.draw.rect(screen, (50, 50, 50), (250, 0, 1100, HEIGHT))
    for y in range(0, HEIGHT, 60):
        pygame.draw.rect(screen, (255, 255, 255), (795, y, 10, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                car_x = WIDTH // 2
                car_y = HEIGHT - 120
                car_angle = 0
                speed = 0
                score = 0
                oncoming_cars = []
                spawn_timer = 0
                game_over = False

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesto = "NONE"
    if result.multi_hand_landmarks and result.multi_handedness:
        gesto = detectar_gestos_manos(
            result.multi_hand_landmarks,
            result.multi_handedness
        )
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

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

    car_x = max(250, min(car_x, 1350 - car_w))

    spawn_timer += 1
    if spawn_timer > 60 and not game_over:
        spawn_timer = 0
        car_type = random.choice([
            {'w': 45, 'h': 75, 'color': (255, 0, 0)},
            {'w': 50, 'h': 80, 'color': (0, 0, 255)},
            {'w': 40, 'h': 70, 'color': (255, 255, 0)},
            {'w': 55, 'h': 85, 'color': (128, 128, 128)}
        ])
        surface = create_oncoming_car_surface(
            car_type['w'], car_type['h'], car_type['color']
        )
        oncoming_cars.append({
            'x': random.randint(270, 1330 - car_type['w']),
            'y': -car_type['h'],
            'speed': random.randint(7, 12),
            'surface': surface,
            'w': car_type['w'],
            'h': car_type['h']
        })

    for car in oncoming_cars[:]:
        car['y'] += car['speed']
        if car['y'] > HEIGHT:
            oncoming_cars.remove(car)
            score += 10

    for car in oncoming_cars:
        if (
            abs((car_x + car_w // 2) - (car['x'] + car['w'] // 2)) < min(car_w, car['w']) and
            abs((car_y + car_h // 2) - (car['y'] + car['h'] // 2)) < min(car_h, car['h'])
        ):
            game_over = True

    if speed > 0 and not game_over:
        score += speed / 10

    if not game_over:
        rotated = pygame.transform.rotate(car_surface, math.degrees(-car_angle))
        rect = rotated.get_rect(center=(car_x + car_w // 2, car_y + car_h // 2))
        screen.blit(rotated, rect)

        for car in oncoming_cars:
            screen.blit(car['surface'], (car['x'], car['y']))

        screen.blit(font.render(f"Puntuación: {int(score)}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Velocidad: {int(speed * 10)} km/h", True, (255, 255, 255)), (10, 50))
    else:
        screen.blit(
            font.render("¡Juego Terminado! Presiona R", True, (255, 0, 0)),
            (WIDTH // 2 - 200, HEIGHT // 2)
        )

    # ================== CÁMARA ==================
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))
    frame_surface = pygame.transform.scale(frame_surface, (400, 300))
    screen.blit(frame_surface, (10, HEIGHT // 2 + 20))

    pygame.display.flip()

cap.release()
pygame.quit()
