import cv2
import mediapipe as mp
import pygame
from gestos import detectar_gesto

# --- MediaPipe ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)

# --- Pygame ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carreras con la Mano")

car_x = WIDTH // 2
car_y = HEIGHT - 100
speed = 7

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    screen.fill((20, 20, 20))

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Cámara ---
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesto = "NONE"

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        gesto = detectar_gesto(hand)

        # Dibujar esqueleto de la mano
        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

    # --- Texto instrucciones ---
    cv2.putText(frame, "LEFT  : Mano a la izquierda", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "RIGHT : Mano a la derecha", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "UP    : Mano arriba (acelera)", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "DOWN  : Mano abajo (frena)", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, f"Gesto: {gesto}", (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # --- Movimiento del carro ---
    if gesto == "LEFT":
        car_x -= speed
    elif gesto == "RIGHT":
        car_x += speed
    elif gesto == "UP":
        car_y -= speed
    elif gesto == "DOWN":
        car_y += speed

    # --- Limites ---
    car_x = max(0, min(car_x, WIDTH - 50))
    car_y = max(0, min(car_y, HEIGHT - 80))

    # --- Dibujar carro ---
    pygame.draw.rect(screen, (0, 255, 0), (car_x, car_y, 50, 80))
    pygame.display.update()

    # --- Mostrar cámara ---
    cv2.imshow("Camara - Control por Gestos", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        running = False

cap.release()
cv2.destroyAllWindows()
pygame.quit()
