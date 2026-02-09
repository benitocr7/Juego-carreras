import cv2
import mediapipe as mp
import pygame
import math
import random
import numpy as np
import os
from gestos import detectar_gestos_manos

# ================== CÁMARA & MEDIAPIPE ==================
USE_WEBCAM = False
cap = None
hands = None
mp_draw = None

try:
    import mediapipe as mp
    try:
        if not hasattr(mp, 'solutions'):
            raise AttributeError("mediapipe.solutions missing")
            
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        
        hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        def init_camera():
            global cap, USE_WEBCAM
            # Try indices 0 to 4
            for index in range(5):
                try:
                    print(f"Probando cámara índice {index}...")
                    # Try with DirectShow first (Windows)
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                         cap = cv2.VideoCapture(index)
                    
                    if cap.isOpened():
                        # Read a frame to be sure
                        ret, frame = cap.read()
                        if ret:
                            USE_WEBCAM = True
                            print(f"Cámara encontrada en índice {index}.")
                            return True
                        else:
                            cap.release()
                except:
                    pass
            
            print("Ninguna cámara encontrada después de escanear índices.")
            USE_WEBCAM = False
            return False

        init_camera()

    except Exception as e:
        print(f"Error inicializando MediaPipe/Cámara: {e}")
        USE_WEBCAM = False
except ImportError:
    print("MediaPipe no instalado.")
    USE_WEBCAM = False

# ================== PYGAME ==================
pygame.init()
WIDTH, HEIGHT = 1280, 840
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carreras por Gestos")

# ================== CARGA DE IMÁGENES ==================
# ================== CARGA DE IMÁGENES ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# 1. Load Player
try:
    # Attempt to load player image
    if not os.path.exists(os.path.join(ASSETS_DIR, "cars1.png")):
        raise FileNotFoundError("cars1.png not found")
    PLAYER_IMG_RAW = pygame.image.load(os.path.join(ASSETS_DIR, "cars1.png")).convert_alpha()
except Exception as e:
    print(f"Error loading cars1.png: {e}")
    # Fallback: Green Square
    PLAYER_IMG_RAW = pygame.Surface((130, 130))
    PLAYER_IMG_RAW.fill((0, 255, 0))

# Load Unlockable Cars
UNLOCKABLE_CARS = []
UNLOCK_COSTS = [0, 0, 0, 0]
CAR_NAMES = ["ESTÁNDAR", "DEPORTIVO", "EXÓTICO", "LEYENDA"]

# Car 1 (Default)
UNLOCKABLE_CARS.append(pygame.transform.scale(PLAYER_IMG_RAW, (130, 130)))

# Car 2 (cars2.png)
try:
    c2 = pygame.image.load(os.path.join(ASSETS_DIR, "cars2.png")).convert_alpha()
    UNLOCKABLE_CARS.append(pygame.transform.scale(c2, (130, 130)))
except:
    print("cars2.png not found, using tint")
    c2 = PLAYER_IMG_RAW.copy()
    c2.fill((50, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    UNLOCKABLE_CARS.append(pygame.transform.scale(c2, (130, 130)))

# Car 3 (cars3.png)
try:
    c3 = pygame.image.load(os.path.join(ASSETS_DIR, "cars3.png")).convert_alpha()
    UNLOCKABLE_CARS.append(pygame.transform.scale(c3, (130, 130)))
except:
    print("cars3.png not found, using tint")
    c3 = PLAYER_IMG_RAW.copy()
    c3.fill((0, 50, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    UNLOCKABLE_CARS.append(pygame.transform.scale(c3, (130, 130)))

# Car 4 (cars4.png)
try:
    c4 = pygame.image.load(os.path.join(ASSETS_DIR, "cars4.png")).convert_alpha()
    UNLOCKABLE_CARS.append(pygame.transform.scale(c4, (130, 130)))
except:
    print("cars4.png not found, using tint")
    c4 = PLAYER_IMG_RAW.copy()
    c4.fill((0, 0, 50, 0), special_flags=pygame.BLEND_RGBA_ADD)
    UNLOCKABLE_CARS.append(pygame.transform.scale(c4, (130, 130)))

# 2. Load Enemy
ENEMY_VARIANTS = []
try:
    if not os.path.exists(os.path.join(ASSETS_DIR, "car_enemy.png")):
        raise FileNotFoundError("car_enemy.png not found")
        
    enemy_img = pygame.image.load(os.path.join(ASSETS_DIR, "car_enemy.png")).convert_alpha()
    ENEMY_VARIANTS.append(enemy_img)
except Exception as e:
    print(f"Error loading car_enemy.png: {e}")
    # Fallback: Red Square
    surf = pygame.Surface((130, 130))
    surf.fill((255, 0, 0))
    ENEMY_VARIANTS.append(surf)

try:
    MOTO_IMG_RAW = pygame.image.load(os.path.join(ASSETS_DIR, "moto.png")).convert_alpha()
    TRUCK_IMG_RAW = pygame.image.load(os.path.join(ASSETS_DIR, "camion.png")).convert_alpha()
    HEART_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "heart.png"))
    SHIELD_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "shield.png"))
    TURBO_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "turbo.png"))
    COIN_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "coin.png"))
except Exception as e:
    print(f"Error loading new enemies/powerups: {e}")
    MOTO_IMG_RAW = pygame.Surface((50, 90))
    MOTO_IMG_RAW.fill((255, 255, 0))
    TRUCK_IMG_RAW = pygame.Surface((140, 250))
    TRUCK_IMG_RAW.fill((0, 0, 255))
    HEART_IMG = pygame.Surface((30, 30))
    HEART_IMG.fill((255, 0, 0))
    SHIELD_IMG = pygame.Surface((40, 40))
    SHIELD_IMG.fill((0, 0, 255))
    TURBO_IMG = pygame.Surface((40, 40))
    TURBO_IMG.fill((255, 255, 0))
    COIN_IMG = pygame.Surface((40, 40))
    pygame.draw.circle(COIN_IMG, (255, 215, 0), (20, 20), 20)

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

# ================== CLASES Y VARIABLES ==================

# ================== AUDIO ==================
pygame.mixer.init()
SOUNDS = {}
try:
    SOUNDS['crash'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "crash.wav"))
    SOUNDS['coin'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "coin.wav"))
    SOUNDS['turbo'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "turbo.wav"))
    SOUNDS['whoosh'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "whoosh.wav"))
    # Reduce volumes
    for s in SOUNDS.values():
        s.set_volume(0.4)
except Exception as e:
    print(f"Error loading sounds: {e}")

# ================== CLASES Y VARIABLES ==================
class SpeedLine:
    def __init__(self):
        self.x = random.randint(SIDEBAR_WIDTH, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.h = random.randint(50, 200)
        self.w = random.randint(2, 5)
        self.speed = random.randint(20, 40)
        self.color = (255, 255, 255, 100) # White transparent

    def update(self, game_speed):
        self.y += self.speed + game_speed
        if self.y > HEIGHT:
            self.y = random.randint(-500, -100)
            self.x = random.randint(SIDEBAR_WIDTH, WIDTH)

    def draw(self, surface):
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s.fill(self.color)
        surface.blit(s, (self.x, self.y))

class Particle:
    def __init__(self, x, y, color, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            s_surface = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s_surface, (*self.color, min(255, self.life * 5)), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s_surface, (self.x - self.size, self.y - self.size))

car_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
car_y = HEIGHT - 120
car_w, car_h = 130, 130 
car_angle = 0
speed = 0
score = 0
level = 1
lives = 3
powerups = [] # List of available powerups on road
active_powerups = {'shield': 0, 'turbo': 0} # Timer for active effects
particles = []
speed_lines = [SpeedLine() for _ in range(10)]
oncoming_cars = []
spawn_timer = 0
game_over = False
road_y = 0
MAX_SPEED = 12

# Progression & Risk
total_coins = 0
multiplier = 1.0
multiplier_timer = 0
shake_timer = 0
near_miss_cooldowns = {} # Track which cars we already got bonus for

# Day/Night Cycle
time_of_day = 0 # 0.0 to 1.0
day_duration = 5000 # Frames for full cycle

# Redimensionar jugador
player_img = pygame.transform.scale(PLAYER_IMG_RAW, (car_w, car_h))
# Sports car unlockable

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# ================== NUBES ==================
clouds = []
for _ in range(5):
    clouds.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT // 2 - 50),
        'speed': random.uniform(0.5, 1.5)
    })

def reset_game():
    global car_x, car_y, car_angle, speed, score, oncoming_cars, spawn_timer, game_over, GAME_STATE, road_y, level, lives, powerups, active_powerups, particles
    global multiplier, multiplier_timer, shake_timer, near_miss_cooldowns, time_of_day, boss_active, boss, boss_level, score_at_level_reset, boss_barrels, bullets, last_shot_time
    
    car_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
    car_y = HEIGHT - 120
    car_angle = 0
    speed = 0
    score = 0
    level = 1
    lives = 3
    oncoming_cars = []
    powerups = []
    active_powerups = {'shield': 0, 'turbo': 0}
    particles = []
    spawn_timer = 0
    game_over = False
    road_y = 0
    multiplier = 1.0
    multiplier_timer = 0
    shake_timer = 0
    near_miss_cooldowns = {}
    time_of_day = 0
    GAME_STATE = "PLAYING"
    boss_active = False
    boss = None
    boss_level = 1
    score_at_level_reset = 0
    boss_barrels = []
    bullets = []
    last_shot_time = 0

    # Auto-equip sports car if unlocked
    # (Checked in drawing loop)

def draw_text_centered(text, font, color, surface, offset_y=0, x_offset=0):
    text_obj = font.render(text, True, color)
    # Centrado respecto al área de juego (desplazado por SIDEBAR_WIDTH)
    center_x = SIDEBAR_WIDTH + GAME_WIDTH // 2 + x_offset
    text_rect = text_obj.get_rect(center=(center_x, HEIGHT // 2 + offset_y))
    surface.blit(text_obj, text_rect)


# ================== LEADERBOARD ==================
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscores.txt")

def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        return [0] * 5
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            scores = [int(line.strip()) for line in f.readlines()]
        scores.sort(reverse=True)
        return scores[:5] # Keep top 5
    except:
        return [0] * 5

def save_highscores(scores):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            for s in scores:
                f.write(f"{s}\n")
    except Exception as e:
        print(f"Error saving highscores: {e}")

high_scores = load_highscores()
new_record = False

def update_highscores(new_score):
    global high_scores, new_record
    new_record = False
    high_scores.append(int(new_score))
    high_scores.sort(reverse=True)
    high_scores = high_scores[:5]
    
    if int(new_score) == high_scores[0] and int(new_score) > 0:
        new_record = True
        
    save_highscores(high_scores)

# ================== GAME LOOP ==================
# Load additional road textures
ROAD_VARIANTS = []
try:
    # Default is already loaded as ROAD_IMG
    ROAD_VARIANTS.append(ROAD_IMG)
    # Load new ones
    for name in ["carreterav1.png", "carreterav2.png", "carreterav3.png", "carreterav4.png"]:
        path = os.path.join(ASSETS_DIR, name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            ROAD_VARIANTS.append(img)
        else:
            print(f"Warning: {name} not found, skipping.")
except Exception as e:
    print(f"Error loading road variants: {e}")

# Create Obstacle Assets
try:
    OIL_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "charco_aceite.png")).convert_alpha()
    OIL_IMG = pygame.transform.scale(OIL_IMG, (80, 60)) # Resize to reasonable size
    
    WATER_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "charco_agua.png")).convert_alpha()
    WATER_IMG = pygame.transform.scale(WATER_IMG, (90, 70)) # Resize to reasonable size
except Exception as e:
    print(f"Error loading obstacle images: {e}")
    # Fallback to procedural
    OIL_IMG = pygame.Surface((70, 50), pygame.SRCALPHA)
    pygame.draw.ellipse(OIL_IMG, (20, 20, 20), (0, 0, 70, 50)) 
    pygame.draw.ellipse(OIL_IMG, (40, 40, 40), (10, 10, 50, 30)) 

    WATER_IMG = pygame.Surface((80, 60), pygame.SRCALPHA)
    pygame.draw.ellipse(WATER_IMG, (0, 100, 255, 180), (0, 0, 80, 60))
    pygame.draw.ellipse(WATER_IMG, (100, 200, 255, 200), (10, 10, 60, 40))

slip_timer = 0 # For Oil Effect

# ================== ASSETS FOR BOSS ==================
BARREL_IMG = pygame.Surface((30, 40))
BARREL_IMG.fill((139, 69, 19)) # Brown
pygame.draw.rect(BARREL_IMG, (100, 50, 10), (0, 0, 30, 40), 2)
pygame.draw.line(BARREL_IMG, (0, 0, 0), (0, 10), (30, 10), 2)
pygame.draw.line(BARREL_IMG, (0, 0, 0), (0, 30), (30, 30), 2)

# ================== GAME VARIABLES UPDATE ==================
menu_selected_car = 0 # 0: Normal, 1: Sports (if unlocked)
boss_active = False
boss = None
boss_level = 1
score_at_level_reset = 0
boss_barrels = []
bullets = []
last_shot_time = 0

def draw_text_button(text, font, color, surface, x, y, w, h, hover_color=(200, 200, 200)):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    is_hover = rect.collidepoint(mouse_pos)
    
    current_color = hover_color if is_hover else color
    pygame.draw.rect(surface, current_color, rect, border_radius=10)
    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=10) # White border
    
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return is_hover

clock = pygame.time.Clock()
running = True
GAME_STATE = "MENU" # Start in Menu

while running:
    clock.tick(30)
    screen.fill((25, 25, 25))
    
    # 0. LEER CÁMARA (Una vez por frame) - Update camera regardless of state
    if USE_WEBCAM and cap:
        ret, frame = cap.read()
    else:
        ret = False
        frame = None

    gesto = "NONE"
    
    if ret:
        try:
            frame = cv2.flip(frame, 1)
            # Convertir a RGB una vez para procesar y mostrar
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Procesar mano
            if hands:
                result = hands.process(frame_rgb)
                
                # Dibujar landmarks en el frame original (BGR) para mostrar en Sidebar
                if result.multi_hand_landmarks and result.multi_handedness:
                     gesto = detectar_gestos_manos(result.multi_hand_landmarks, result.multi_handedness)
                     if mp_draw:
                        for hand in result.multi_hand_landmarks:
                             mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        except Exception as e:
            # print(f"Error procesando frame: {e}")
            USE_WEBCAM = False # Disable if runtime error

    # 1. DIBUJAR SIDEBAR (Izquierda) - Persistent Sidebar
    pygame.draw.rect(screen, (20, 20, 40), (0, 0, SIDEBAR_WIDTH, HEIGHT))
    
    # Mostrar Cámara en el Sidebar
    if ret:
        try:
            # Redimensionar frame (ya tiene landmarks dibujados) para el sidebar (320x240)
            # Convertimos a RGB para pygame
            frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_display = cv2.resize(frame_display, (SIDEBAR_WIDTH, 240))
            frame_surface = pygame.surfarray.make_surface(np.transpose(frame_display, (1, 0, 2)))
            screen.blit(frame_surface, (0, 0))
        except:
            pass
    elif not USE_WEBCAM:
        # Show specific message for Keyboard Mode
        # User requested to remove keyboard mode. We will show a "Connect Camera" message instead if failed.
        pygame.draw.rect(screen, (50, 0, 0), (10, 10, SIDEBAR_WIDTH-20, 240))
        draw_text_centered("CÁMARA NO DETECTADA", font, (255, 100, 100), screen, -250, x_offset=-(GAME_WIDTH//2 + SIDEBAR_WIDTH//2) + SIDEBAR_WIDTH//2)
        draw_text_centered("Conecta tu webcam", font, (255, 255, 255), screen, -210, x_offset=-(GAME_WIDTH//2))

    # Sidebar Info (Only in Play/GameOver)
    if GAME_STATE == "PLAYING" or GAME_STATE == "GAME_OVER":
        # VIDAS
        screen.blit(font.render("VIDAS", True, (200, 200, 200)), (20, 260))
        for i in range(lives):
            screen.blit(HEART_IMG, (20 + i * 40, 300))

        # PUNTUACIÓN
        screen.blit(font.render("PUNTUACIÓN", True, (200, 200, 200)), (20, 350))
        score_color = (255, 215, 0) if active_powerups['turbo'] == 0 else (255, 100, 0) # Naranja si Turbo
        screen.blit(font.render(f"{int(score)}", True, score_color), (20, 390))
        
        # Multiplier
        if multiplier > 1.0:
            screen.blit(font.render(f"x{multiplier:.1f}", True, (0, 255, 0)), (150, 390))

        # VELOCIDAD
        screen.blit(font.render("VELOCIDAD", True, (200, 200, 200)), (20, 440))
        screen.blit(font.render(f"{int(speed * 10)} km/h", True, (0, 255, 255)), (20, 480))
        
        # NIVEL & COINS
        screen.blit(font.render(f"NIVEL: {level}", True, (255, 0, 255)), (20, 530))
        
        if boss_active:
             screen.blit(font.render("¡JEFE FINAL!", True, (255, 0, 0)), (20, 560))
        else:
             screen.blit(font.render(f"COINS: {total_coins}", True, (255, 215, 0)), (20, 560))

        # STATUS PODERES
        if active_powerups['shield'] > 0:
             screen.blit(font.render("ESCUDO ACTIVO!", True, (0, 100, 255)), (20, 600))
        if active_powerups['turbo'] > 0:
             screen.blit(font.render("TURBO!", True, (255, 165, 0)), (20, 640))
        if slip_timer > 0:
             screen.blit(font.render("¡PATINANDO!", True, (255, 50, 50)), (20, 680))
    
    # Separador
    pygame.draw.line(screen, (255, 255, 255), (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)

    # EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            center_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
            center_y = HEIGHT // 2

            if GAME_STATE == "MENU":
                # Start Button
                if center_x - 100 < mx < center_x + 100 and center_y + 200 < my < center_y + 250:
                    reset_game()
                
                # Retry Camera Button
                if not USE_WEBCAM:
                    if center_x - 125 < mx < center_x + 125 and center_y + 270 < my < center_y + 320:
                        if 'init_camera' in globals():
                            init_camera()
                        elif 'init_camera' in locals():
                            init_camera()
                


                # Car Select Left Arrow
                if center_x - 150 < mx < center_x - 110 and center_y - 50 < my < center_y + 50:
                    menu_selected_car = (menu_selected_car - 1) % len(UNLOCKABLE_CARS)
                
                # Car Select Right Arrow
                if center_x + 110 < mx < center_x + 150 and center_y - 50 < my < center_y + 50:
                    menu_selected_car = (menu_selected_car + 1) % len(UNLOCKABLE_CARS)

            elif GAME_STATE == "GAME_OVER":
                # Restart Button
                if center_x - 100 < mx < center_x + 100 and center_y + 200 < my < center_y + 250:
                    reset_game()
                # Menu Button
                if center_x - 100 < mx < center_x + 100 and center_y + 270 < my < center_y + 320:
                    GAME_STATE = "MENU"

        elif event.type == pygame.KEYDOWN:
            if GAME_STATE == "MENU":
                if event.key == pygame.K_SPACE:
                    reset_game()
            elif GAME_STATE == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_m:
                    GAME_STATE = "MENU"

    # RENDER GAME AREA
    if GAME_STATE == "MENU":
        # Menu Background
        pygame.draw.rect(screen, (30, 30, 50), (SIDEBAR_WIDTH, 0, GAME_WIDTH, HEIGHT))
        
        # Title
        draw_text_centered("TURBO RACING", get_font(80) if 'get_font' in locals() else font, (255, 215, 0), screen, -250)
        draw_text_centered("GARAJE & MENÚ", font, (200, 200, 200), screen, -180)

        # Show Selected Car
        center_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
        center_y = HEIGHT // 2
        
        if menu_selected_car < len(UNLOCKABLE_CARS):
            car_preview = UNLOCKABLE_CARS[menu_selected_car]
        else:
            car_preview = UNLOCKABLE_CARS[0]

        car_preview = pygame.transform.scale(car_preview, (100, 200))
        
        # Lock visual
        is_locked = total_coins < UNLOCK_COSTS[menu_selected_car]
        if is_locked:
            car_preview.set_alpha(100) # Dim if locked
        else:
            car_preview.set_alpha(255)

        car_rect = car_preview.get_rect(center=(center_x, center_y))
        screen.blit(car_preview, car_rect)

        # Draw Arrows
        pygame.draw.polygon(screen, (255, 255, 255), [(car_rect.left - 20, center_y), (car_rect.left - 40, center_y - 20), (car_rect.left - 40, center_y + 20)])
        pygame.draw.polygon(screen, (255, 255, 255), [(car_rect.right + 20, center_y), (car_rect.right + 40, center_y - 20), (car_rect.right + 40, center_y + 20)])
        
        # Name and Lock Status
        car_name = CAR_NAMES[menu_selected_car]
        if is_locked:
            draw_text_centered(f"BLOQUEADO: {car_name}", font, (255, 100, 100), screen, 120)
            draw_text_centered(f"Necesitas {UNLOCK_COSTS[menu_selected_car]} Monedas", pygame.font.SysFont(None, 24), (200, 200, 200), screen, 150)
        else:
            draw_text_centered(car_name, font, (100, 255, 100), screen, 120)

        # Buttons
        hover_start = draw_text_button("JUGAR", font, (0, 200, 0), screen, center_x - 100, center_y + 200, 200, 50, (50, 255, 50))
        
        if not USE_WEBCAM:
             draw_text_button("REINTENTAR CÁMARA", font, (200, 50, 50), screen, center_x - 125, center_y + 270, 250, 50, (255, 100, 100))
        



    elif GAME_STATE == "PLAYING" or GAME_STATE == "GAME_OVER":
        
        # 1.5 FONDO (Sky Color Logic)
        if GAME_STATE == "PLAYING":
             time_of_day = (pygame.time.get_ticks() % day_duration) / day_duration
        
        # Interpolate Sky Color
        if time_of_day < 0.5: # Day to Sunset
            r = 135 + (255 - 135) * (time_of_day * 2)
            g = 206 + (100 - 206) * (time_of_day * 2)
            b = 235 + (0 - 235) * (time_of_day * 2)
        else: # Sunset to Night
            r = 255 - (255) * ((time_of_day - 0.5) * 2)
            g = 100 - (100) * ((time_of_day - 0.5) * 2)
            b = 0
        sky_color = (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))

        # Solo necesitamos dibujar el fondo en la zona de juego
        sky_rect = (SIDEBAR_WIDTH, 0, GAME_WIDTH, HEIGHT // 2)
        pygame.draw.rect(screen, sky_color, sky_rect)
        
        for cloud in clouds:
            if time_of_day < 0.7:
                 if cloud['x'] > SIDEBAR_WIDTH: 
                      pygame.draw.circle(screen, (255, 255, 255), (cloud['x'], cloud['y']), 20)
                      pygame.draw.circle(screen, (255, 255, 255), (cloud['x'] + 15, cloud['y']), 25)
                      pygame.draw.circle(screen, (255, 255, 255), (cloud['x'] + 30, cloud['y']), 20)
            cloud['x'] += cloud['speed']
            if cloud['x'] > WIDTH + 50:
                cloud['x'] = SIDEBAR_WIDTH - 50

        # Decoración lateral (Césped) - Darken at night
        grass_g = 100 * (1.0 - max(0, (time_of_day - 0.5) * 2))
        grass_color = (0, max(20, int(grass_g)), 0)
        
        for y in range(0, HEIGHT, 100):
            pygame.draw.rect(screen, grass_color, (SIDEBAR_WIDTH, y, 50, 80)) # Izquierda del juego
            pygame.draw.rect(screen, grass_color, (WIDTH - 100, y, 50, 80)) # Derecha total

        # SHAKE OFFSET
        shake_x, shake_y = 0, 0
        if shake_timer > 0:
            shake_timer -= 1
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
            
        # CARRETERA SCROLLING
        if GAME_STATE == "PLAYING":
            road_y = (road_y + speed) % HEIGHT
        
        # Select Road Texture
        if ROAD_VARIANTS:
            r_index = (int(score) // 200) % len(ROAD_VARIANTS)
            current_road = ROAD_VARIANTS[r_index]
        else:
            current_road = ROAD_IMG

        # Dibujar dos copias para el efecto infinito (convertir a int para evitar gaps)
        road_y_int = int(road_y)
        screen.blit(current_road, (SIDEBAR_WIDTH + shake_x, road_y_int + shake_y))
        screen.blit(current_road, (SIDEBAR_WIDTH + shake_x, road_y_int - HEIGHT + shake_y))

        # LOGICA DEL JUEGO
        if GAME_STATE == "PLAYING":
            # Calcular Nivel (Reset progress after boss)
            level = 1 + int((score - score_at_level_reset) // 500)
            
            current_max_speed = 12 + (level - 1)
            
            # === BOSS LOGIC ===
            # Boss appears every 5000 points
            if score >= boss_level * 5000 and not boss_active:
                boss_active = True
                # Spawn Boss at top center
                boss = {
                    'x': SIDEBAR_WIDTH + GAME_WIDTH//2 - 90, 
                    'y': -300,
                    'w': 180,
                    'h': 300, 
                    'hp': 100 + (boss_level - 1) * 50, # Scale HP: 100, 150, 200...
                    'max_hp': 100 + (boss_level - 1) * 50,
                    'dir': 1
                }
                if 'whoosh' in SOUNDS: SOUNDS['whoosh'].play() 

            if boss_active:
                # 1. Boss Movement
                if boss['y'] < 100:
                    boss['y'] += 2 # Enter screen slowly
                else:
                    # ZigZag
                    boss['x'] += boss['dir'] * 2
                    if boss['x'] < SIDEBAR_WIDTH + 40 or boss['x'] > WIDTH - 40 - boss['w']:
                        boss['dir'] *= -1
                
                # 2. Boss Attack: Barrels
                if random.random() < 0.05: 
                    boss_barrels.append({
                        'x': boss['x'] + boss['w']//2 - 15,
                        'y': boss['y'] + boss['h'],
                        'rect': pygame.Rect(boss['x'] + boss['w']//2 - 15, boss['y'] + boss['h'], 30, 40)
                    })

            # Normal Powerups Logic
            if active_powerups['turbo'] > 0:
                current_max_speed += 10
                active_powerups['turbo'] -= 1
                particles.append(Particle(car_x + car_w//2, car_y + car_h, (255, 100, 0), random.randint(5, 10), 20))
                if active_powerups['turbo'] % 5 == 0:
                    shake_timer = 2

            if active_powerups['shield'] > 0:
                active_powerups['shield'] -= 1
            
            if slip_timer > 0:
                slip_timer -= 1

            # INPUT HANDLING
            keys = pygame.key.get_pressed()
            target_speed = 0
            if USE_WEBCAM:
                if "STOP" in gesto: target_speed = 0
                elif "ACCEL" in gesto: target_speed = current_max_speed
            else:
                if keys[pygame.K_SPACE] or keys[pygame.K_UP]: target_speed = current_max_speed
            
            if speed < target_speed: speed = min(current_max_speed, speed + 0.2)
            else: speed = max(0, speed - 0.5)

            # Multiplyer
            if speed > current_max_speed * 0.9:
                multiplier_timer += 1
                if multiplier_timer > 60: multiplier = min(5.0, multiplier + 0.5); multiplier_timer = 0
            else:
                multiplier_timer = 0; multiplier = max(1.0, multiplier - 0.01)

            # Steering
            car_angle = 0
            if slip_timer > 0:
                car_angle = math.sin(pygame.time.get_ticks() * 0.05) * 1.5; speed *= 0.95
            else:
                if USE_WEBCAM:
                    if "LEFT" in gesto: car_angle -= 1.0
                    if "RIGHT" in gesto: car_angle += 1.0
                else:
                    if keys[pygame.K_LEFT]: car_angle -= 1.0
                    if keys[pygame.K_RIGHT]: car_angle += 1.0
                car_angle = max(-math.pi / 2, min(math.pi / 2, car_angle))

            car_x += speed * math.sin(car_angle)
            
            if boss_active:
                # Lock Y to bottom
                car_y = HEIGHT - 150
                # Speed is constant or controlled differently? 
                # Let's keep lateral movement but remove forward speed factor from updates?
                # Actually user said "solo pueda menar de un lado al otro"
                # So we override Y.
            else:
                car_y -= speed * math.cos(car_angle)
                if car_y < -car_h: car_y = HEIGHT; car_angle = 0
            
            car_x = max(SIDEBAR_WIDTH + 40, min(car_x, WIDTH - 40 - car_w))

            # SPAWN ENEMIGOS (Less frequent during Boss)
            spawn_timer += 1
            spawn_threshold = max(20, 50 - (level * 2)) 
            
            if not boss_active and spawn_timer > spawn_threshold:
                spawn_timer = 0
                if random.random() < 0.4: # Increased chance for powerups (40%)
                     rnd = random.random()
                     if rnd < 0.1: ptype = 'shield'; img = SHIELD_IMG
                     elif rnd < 0.2: ptype = 'turbo'; img = TURBO_IMG
                     elif rnd < 0.7: ptype = 'coin'; img = pygame.transform.scale(COIN_IMG, (50, 50)) # 50% chance for coins (0.2 to 0.7)
                     elif rnd < 0.85: ptype = 'oil'; img = OIL_IMG
                     else: ptype = 'water'; img = WATER_IMG
                     powerups.append({'type': ptype, 'x': random.randint(SIDEBAR_WIDTH + 50, WIDTH - 50 - 50), 'y': -50, 'img': img, 'rect': img.get_rect()})
                else:
                    enemy_options = []
                    for variant_img in ENEMY_VARIANTS:
                        enemy_options.extend([
                            {'type': 'car', 'w': 130, 'h': 130, 'img': variant_img},
                            {'type': 'car', 'w': 125, 'h': 125, 'img': variant_img},
                        ])
                    if True:
                        enemy_options.append({'type': 'moto', 'w': 80, 'h': 90, 'img': MOTO_IMG_RAW})
                        enemy_options.append({'type': 'truck', 'w': 180, 'h': 160, 'img': TRUCK_IMG_RAW})

                    choice = random.choice(enemy_options)
                    enemy_surf = pygame.transform.scale(choice['img'], (choice['w'], choice['h']))
                    oncoming_cars.append({
                        'x': random.randint(SIDEBAR_WIDTH + 50, WIDTH - 50 - choice['w']),
                        'startX': 0, 
                        'y': -choice['h'],
                        'speed': random.randint(7+level, 12+level),
                        'surface': enemy_surf,
                        'mask': pygame.mask.from_surface(enemy_surf), 
                        'w': choice['w'], 'h': choice['h'],
                        'sway_phase': random.uniform(0, 6.28), 'sway_speed': random.uniform(0.05, 0.1) + (level * 0.02),
                        'sway_amp': random.randint(0, 20) + (level * 10),
                        'id': random.randint(0, 10000)
                    })
                    oncoming_cars[-1]['startX'] = oncoming_cars[-1]['x']

            # Actualizar Objetos
            for car in oncoming_cars[:]:
                speed_var = math.sin(pygame.time.get_ticks() * 0.005 + car['sway_phase']) * 2
                car['y'] += car['speed'] + speed_var
                if level > 1:
                    sway_offset = math.sin(pygame.time.get_ticks() * 0.005 * car['sway_speed'] + car['sway_phase']) * car['sway_amp']
                    car['x'] = car['startX'] + sway_offset
                    car['x'] = max(SIDEBAR_WIDTH + 20, min(WIDTH - 20 - car['w'], car['x']))
                if car['y'] > HEIGHT:
                    oncoming_cars.remove(car); score += 10 * multiplier
            
            for p in powerups[:]:
                p['y'] += 10; 
                if p['y'] > HEIGHT: powerups.remove(p)
            
            for b in boss_barrels[:]:
                b['y'] += 15 # Fast barrels
                b['rect'].y = int(b['y'])
                if b['y'] > HEIGHT: boss_barrels.remove(b)

            for p in particles[:]: 
                p.update()
                if p.life <= 0: particles.remove(p)
            
            if speed > 8 or active_powerups['turbo'] > 0:
                 for line in speed_lines: line.update(speed + 20)

            # Player Img Update based on selection
            # Player Img Update
            # Auto-revert to car 0 if selected is locked (safety check)
            if total_coins < UNLOCK_COSTS[menu_selected_car]:
                current_player_img = UNLOCKABLE_CARS[0]
            else:
                current_player_img = UNLOCKABLE_CARS[menu_selected_car]
            rotated_player = pygame.transform.rotate(current_player_img, math.degrees(-car_angle))
            player_rect = rotated_player.get_rect(center=(car_x + car_w // 2, car_y + car_h // 2))
            player_mask = pygame.mask.from_surface(rotated_player)

            # COLISIONES
            for p in powerups[:]:
                p_rect = p['img'].get_rect(topleft=(p['x'], p['y']))
                if player_rect.colliderect(p_rect):
                    if p['type'] == 'shield':
                        active_powerups['shield'] = 150
                    elif p['type'] == 'turbo':
                        active_powerups['turbo'] = 150
                        if 'turbo' in SOUNDS: SOUNDS['turbo'].play()
                    elif p['type'] == 'coin':
                        total_coins += 1
                        score += 50
                        if 'coin' in SOUNDS: SOUNDS['coin'].play()
                        # Extra life every 7 coins
                        if total_coins > 0 and total_coins % 7 == 0:
                            lives += 1
                            if 'turbo' in SOUNDS: SOUNDS['turbo'].play() # Feedback sound for extra life
                    elif p['type'] == 'oil':
                        slip_timer = 60
                    elif p['type'] == 'water':
                        speed = max(2, speed - 8)
                    
                    if p in powerups:
                        powerups.remove(p)
            
            # Boss Barrels Check
            for b in boss_barrels[:]:
                if player_rect.colliderect(b['rect']):
                    if active_powerups['shield'] > 0:
                        boss_barrels.remove(b)
                    else:
                        lives -= 1
                        shake_timer = 10
                        if 'crash' in SOUNDS: SOUNDS['crash'].play()
                        boss_barrels.remove(b)
                        multiplier = 1.0
                        if lives <= 0: GAME_STATE = "GAME_OVER"; update_highscores(score)

            # --- BULLET LOGIC (NEW) ---
            if boss_active:
                # 1. Auto-Shoot
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > 100: # Shoot every 100ms (Faster!)
                    # Dual Shot
                    bullets.append(pygame.Rect(car_x + car_w//2 - 20, car_y, 10, 20)) # Left bullet
                    bullets.append(pygame.Rect(car_x + car_w//2 + 10, car_y, 10, 20)) # Right bullet
                    last_shot_time = current_time
                    # SOUNDS['shoot'].play() # If we had one

                # 2. Update Bullets
                for bullet in bullets[:]:
                    bullet.y -= 15 # Bullet speed
                    if bullet.y < 0:
                        bullets.remove(bullet)
                    else:
                        # Collision: Bullet vs Boss
                        boss_rect = pygame.Rect(boss['x'], boss['y'], boss['w'], boss['h'])
                        if boss_rect.colliderect(bullet):
                            boss['hp'] -= 2 # Damage
                            if bullet in bullets: bullets.remove(bullet)
                            
                            if boss['hp'] <= 0:
                                # BOSS DEFEATED
                                score += 1000 # Bonus
                                boss_active = False
                                boss_level += 1 # Next boss is harder
                                bullets = []
                                boss_barrels = []
                                
                                # Reset Speed to "Normal" to start ramping up again
                                speed = 10 
                                spawn_timer = 0
                                score_at_level_reset = score # RESET PROGRESSION
                                
                                if 'crash' in SOUNDS: SOUNDS['crash'].play()
                        
                        # Collision: Bullet vs Barrels
                        for b in boss_barrels[:]:
                            if b['rect'].colliderect(bullet):
                                boss_barrels.remove(b)
                                if bullet in bullets: bullets.remove(bullet)
                                score += 50
                                # Explosion effect?
                                particles.append(Particle(b['x']+15, b['y']+20, (200, 100, 0), 10, 20))


            for car in oncoming_cars[:]:
                offset_x = int(car['x'] - player_rect.left)
                offset_y = int(car['y'] - player_rect.top)
                if player_mask.overlap(car['mask'], (offset_x, offset_y)):
                     if active_powerups['shield'] > 0:
                         oncoming_cars.remove(car); shake_timer = 5
                     else:
                         lives -= 1; shake_timer = 10; oncoming_cars.remove(car)
                         if 'crash' in SOUNDS: SOUNDS['crash'].play()
                         multiplier = 1.0
                         if lives <= 0: GAME_STATE = "GAME_OVER"; update_highscores(score)
                else:
                     # Near Miss
                     if abs((car_x+car_w/2)-(car['x']+car['w']/2)) < car_w+20 and abs((car_y+car_h/2)-(car['y']+car['h']/2)) < car_h+20:
                         if car['id'] not in near_miss_cooldowns:
                             near_miss_cooldowns[car['id']] = True; score += 100 * multiplier; multiplier = min(5.0, multiplier + 0.2)
            
            if speed > 0: score += speed / 10 * multiplier

        # DIBUJAR JUEGO
        if GAME_STATE == "PLAYING" or GAME_STATE == "GAME_OVER":
            if speed > 8 or active_powerups['turbo'] > 0: [line.draw(screen) for line in speed_lines]
            for p in particles: p.draw(screen)
            for p in powerups: screen.blit(p['img'], (p['x'] + shake_x, p['y'] + shake_y))
            for car in oncoming_cars: screen.blit(car['surface'], (car['x'] + shake_x, car['y'] + shake_y))
            for b in boss_barrels: screen.blit(BARREL_IMG, (b['x'] + shake_x, b['y'] + shake_y))
            
            if boss_active:
                boss_surf = pygame.transform.scale(TRUCK_IMG_RAW, (boss['w'], boss['h']))
                screen.blit(boss_surf, (boss['x'] + shake_x, boss['y'] + shake_y))
                
                # Draw Boss Health Bar
                pygame.draw.rect(screen, (100, 100, 100), (boss['x'], boss['y'] - 20, boss['w'], 10))
                if boss['hp'] > 0:
                    pct = boss['hp'] / boss['max_hp']
                    pygame.draw.rect(screen, (255, 0, 0), (boss['x'], boss['y'] - 20, boss['w'] * pct, 10))
                    
                    # Optional: Draw Text
                    # draw_text_centered(f"{int(boss['hp'])}/{boss['max_hp']}", pygame.font.SysFont(None, 20), (255,255,255), screen, boss['y'] - 30 - HEIGHT//2)

            # Draw Bullets
            for bullet in bullets:
                pygame.draw.rect(screen, (255, 255, 0), (bullet.x + shake_x, bullet.y + shake_y, bullet.w, bullet.h))

            # Select Player Image (Consistent with Logic)
            if total_coins < UNLOCK_COSTS[menu_selected_car]:
                current_player_img = UNLOCKABLE_CARS[0]
            else:
                current_player_img = UNLOCKABLE_CARS[menu_selected_car]
            rotated = pygame.transform.rotate(current_player_img, math.degrees(-car_angle))
            rect = rotated.get_rect(center=(car_x + car_w // 2, car_y + car_h // 2))
            screen.blit(rotated, (rect.x + shake_x, rect.y + shake_y))
            
            if active_powerups.get('shield', 0) > 0:
                 pygame.draw.circle(screen, (0, 100, 255), (int(car_x + car_w//2 + shake_x), int(car_y + car_h//2 + shake_y)), 80, 5)

        if GAME_STATE == "GAME_OVER":
            s = pygame.Surface((GAME_WIDTH, HEIGHT)); s.set_alpha(128); s.fill((0,0,0)); screen.blit(s, (SIDEBAR_WIDTH,0))
            draw_text_centered("¡Juego Terminado!", font, (255, 0, 0), screen, -200)
            draw_text_centered(f"Puntuación Final: {int(score)}", font, (255, 255, 255), screen, -160)
            if new_record: draw_text_centered("¡NUEVO RÉCORD!", font, (255, 215, 0), screen, -120)
            draw_text_centered("- MEJORES PUNTUACIONES -", font, (100, 200, 255), screen, -60)
            for i, hs in enumerate(high_scores): draw_text_centered(f"{i+1}. {hs}", font, (255, 215, 0) if i==0 else (200, 200, 200), screen, -20 + (i * 30))
            
            # New code for displaying car info and unlock cost
            # Name and Lock Status
            center_x = SIDEBAR_WIDTH + GAME_WIDTH // 2
            center_y = HEIGHT // 2
            car_name = CAR_NAMES[menu_selected_car]
            is_locked = total_coins < UNLOCK_COSTS[menu_selected_car]
            
            if is_locked:
                draw_text_centered(f"BLOQUEADO: {car_name}", font, (255, 100, 100), screen, 120)
                draw_text_centered(f"Necesitas {UNLOCK_COSTS[menu_selected_car]} Monedas", pygame.font.SysFont(None, 24), (200, 200, 200), screen, 150)
            else:
                draw_text_centered(car_name, font, (100, 255, 100), screen, 120)
                
            draw_text_centered(f"Total Coins: {total_coins}", font, (255, 215, 0), screen, 180 if is_locked else 150) # Adjust Y position if unlock message is shown
            
            # Buttons
            draw_text_button("REINICIAR", font, (0, 200, 0), screen, center_x - 100, center_y + 200, 200, 50, (50, 255, 50))
            draw_text_button("MENÚ", font, (0, 100, 200), screen, center_x - 100, center_y + 270, 200, 50, (50, 150, 255))
            
            # Keyboard hints (smaller)
            draw_text_centered("[R] Reiniciar   [M] Menú", pygame.font.SysFont(None, 24), (150, 150, 150), screen, 340)

    pygame.display.flip()
