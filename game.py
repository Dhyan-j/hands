import pygame
import mediapipe as mp
import cv2
import sys
import random

pygame.init()

# ------------------ GAME WINDOW ------------------
GAME_WIDTH = 800
CAMERA_WIDTH = 320
WIDTH = GAME_WIDTH + CAMERA_WIDTH
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Hand Gesture Dino Game")

# ------------------ COLORS ------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
NIGHT_SKY = (25, 25, 50)
GROUND_COLOR = (200, 200, 200)
MOON_COLOR = (240, 240, 200)
STAR_COLOR = (255, 255, 200)

# ------------------ FONTS ------------------
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# ------------------ DINO SETTINGS ------------------
dino_x = 80
ground_y = 300
dino_w = 50
dino_h = 50
dino_y = ground_y
velocity_y = 0
gravity = 0.8
jump_power = -16
is_jumping = False

# ------------------ OBSTACLE ------------------
obstacles = []
obstacle_timer = 0
obstacle_spawn_interval = 90  # frames between spawns
min_spawn_interval = 40

# ------------------ DAY/NIGHT CYCLE ------------------
is_night = False
cycle_timer = 0
cycle_duration = 500  # Switch every 500 score points
stars = [(random.randint(0, GAME_WIDTH), random.randint(20, 150)) for _ in range(30)]

# ------------------ GAME STATE ------------------
score = 0
high_score = 0
game_over = False
base_speed = 6
current_speed = base_speed

# ------------------ MEDIAPIPE HAND ------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1,
                        min_detection_confidence=0.7,
                        min_tracking_confidence=0.7)

# ------------------ DRAW FUNCTIONS ------------------
def draw_dino(x, y):
    """Draw a simple but better looking dino."""
    color = (50, 150, 50) if not is_night else (100, 200, 100)
    # Body
    pygame.draw.rect(screen, color, (x, y, dino_w, dino_h))
    # Head
    pygame.draw.rect(screen, color, (x + dino_w - 15, y - 15, 25, 25))
    # Eye
    eye_color = BLACK if not is_night else WHITE
    pygame.draw.circle(screen, eye_color, (x + dino_w - 5, y - 8), 3)
    # Legs
    leg_offset = 0 if is_jumping else (score // 5) % 2 * 5
    pygame.draw.rect(screen, color, (x + 5, y + dino_h, 8, 10 + leg_offset))
    pygame.draw.rect(screen, color, (x + dino_w - 13, y + dino_h, 8, 10 - leg_offset))

def draw_cactus(x, y, width, height):
    """Draw a cactus obstacle."""
    color = (34, 139, 34) if not is_night else (50, 100, 50)
    detail_color = (50, 200, 50) if not is_night else (70, 130, 70)
    # Main body
    pygame.draw.rect(screen, color, (x, y, width, height))
    # Arms
    pygame.draw.rect(screen, color, (x - 8, y + 10, 8, 15))
    pygame.draw.rect(screen, color, (x + width, y + 15, 8, 12))
    # Details
    for i in range(3):
        pygame.draw.line(screen, detail_color, 
                        (x + width//2 - 2, y + 10 + i * 15),
                        (x + width//2 + 2, y + 10 + i * 15), 2)

def draw_ground():
    """Draw animated ground."""
    line_color = BLACK if not is_night else (200, 200, 200)
    ground_line_color = (150, 150, 150) if not is_night else (100, 100, 100)
    
    pygame.draw.line(screen, line_color, (0, ground_y + dino_h + 10), 
                    (GAME_WIDTH, ground_y + dino_h + 10), 3)
    # Moving ground lines
    offset = (score * 2) % 40
    for i in range(-1, GAME_WIDTH // 40 + 1):
        x = i * 40 - offset
        pygame.draw.line(screen, ground_line_color, (x, ground_y + dino_h + 12),
                        (x + 20, ground_y + dino_h + 12), 2)

def draw_clouds():
    """Draw background clouds."""
    cloud_positions = [(100, 80), (400, 50), (650, 90)]
    offset = (score // 2) % GAME_WIDTH
    cloud_color = WHITE if not is_night else (70, 70, 90)
    
    for cx, cy in cloud_positions:
        x = (cx - offset) % GAME_WIDTH
        # Simple cloud shape
        pygame.draw.circle(screen, cloud_color, (x, cy), 20)
        pygame.draw.circle(screen, cloud_color, (x + 25, cy), 25)
        pygame.draw.circle(screen, cloud_color, (x + 50, cy), 20)
        pygame.draw.ellipse(screen, cloud_color, (x - 10, cy + 10, 70, 30))

def draw_stars():
    """Draw stars for night mode."""
    for star_x, star_y in stars:
        brightness = (score % 30) / 30.0
        if random.random() > 0.98:  # Twinkling effect
            size = 2
        else:
            size = 1
        pygame.draw.circle(screen, STAR_COLOR, (star_x, star_y), size)

def draw_moon():
    """Draw moon for night mode."""
    moon_x = GAME_WIDTH - 100
    moon_y = 80
    pygame.draw.circle(screen, MOON_COLOR, (moon_x, moon_y), 30)
    # Moon craters
    pygame.draw.circle(screen, (200, 200, 180), (moon_x - 8, moon_y - 5), 6)
    pygame.draw.circle(screen, (200, 200, 180), (moon_x + 10, moon_y + 8), 4)

def jump():
    """Makes Dino jump."""
    global is_jumping, velocity_y
    if not is_jumping:
        velocity_y = jump_power
        is_jumping = True

def reset_game():
    """Reset game state."""
    global dino_y, velocity_y, is_jumping, obstacles, score, game_over
    global obstacle_timer, current_speed, obstacle_spawn_interval, is_night, cycle_timer
    dino_y = ground_y
    velocity_y = 0
    is_jumping = False
    obstacles = []
    score = 0
    game_over = False
    obstacle_timer = 0
    current_speed = base_speed
    obstacle_spawn_interval = 90
    is_night = False
    cycle_timer = 0

def show_game_over():
    """Display game over screen."""
    overlay = pygame.Surface((GAME_WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(WHITE if not is_night else (40, 40, 60))
    screen.blit(overlay, (0, 0))
    
    text_color = BLACK if not is_night else WHITE
    game_over_text = font_large.render("GAME OVER!", True, text_color)
    score_text = font_medium.render(f"Score: {score}", True, text_color)
    high_score_text = font_medium.render(f"High Score: {high_score}", True, text_color)
    restart_text = font_small.render("Raise your hand to restart", True, text_color)
    
    screen.blit(game_over_text, (GAME_WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
    screen.blit(score_text, (GAME_WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
    screen.blit(high_score_text, (GAME_WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 20))
    screen.blit(restart_text, (GAME_WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 70))

# ------------------ GAME LOOP ------------------
hand_up_frames = 0  # Debounce counter
last_hand_up = False

while True:
    # ---------- PROCESS CAMERA ----------
    ret, frame = cap.read()
    if not ret:
        continue
        
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    
    # Draw hand landmarks on frame
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
            )
    
    hand_up = False
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        wrist = hand.landmark[mp_hands.HandLandmark.WRIST]
        
        # Simplified: Hand is raised if wrist is in upper half of frame
        if wrist.y < 0.5:
            hand_up = True
    
    # Trigger jump/reset on hand raise (with debounce)
    if hand_up and not last_hand_up:
        if game_over:
            reset_game()
        else:
            jump()
    
    last_hand_up = hand_up
    
    # ---------- GAME EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                else:
                    jump()
    
    if not game_over:
        # ---------- DAY/NIGHT CYCLE ----------
        if score > 0 and score % cycle_duration == 0 and score != cycle_timer:
            is_night = not is_night
            cycle_timer = score
        
        # ---------- GRAVITY & JUMP ----------
        if is_jumping or dino_y < ground_y:
            dino_y += velocity_y
            velocity_y += gravity
            
            if dino_y >= ground_y:
                dino_y = ground_y
                is_jumping = False
                velocity_y = 0
        
        # ---------- SPEED INCREASE ----------
        score += 1
        if score % 100 == 0:
            current_speed = min(base_speed + score // 100, 15)
            obstacle_spawn_interval = max(min_spawn_interval, 90 - score // 200)
        
        # ---------- SPAWN OBSTACLES ----------
        obstacle_timer += 1
        if obstacle_timer >= obstacle_spawn_interval:
            obstacle_height = random.choice([40, 50, 60])
            obstacles.append({
                'x': GAME_WIDTH,
                'y': ground_y + dino_h - obstacle_height + 10,
                'width': random.choice([30, 40]),
                'height': obstacle_height
            })
            obstacle_timer = 0
        
        # ---------- MOVE OBSTACLES ----------
        for obs in obstacles:
            obs['x'] -= current_speed
        
        # Remove off-screen obstacles
        obstacles = [obs for obs in obstacles if obs['x'] > -obs['width']]
        
        # ---------- COLLISION ----------
        dino_rect = pygame.Rect(dino_x + 5, dino_y + 5, dino_w - 10, dino_h - 5)
        for obs in obstacles:
            obs_rect = pygame.Rect(obs['x'] + 5, obs['y'], obs['width'] - 10, obs['height'])
            if dino_rect.colliderect(obs_rect):
                game_over = True
                high_score = max(high_score, score)
    
    # ---------- DRAW EVERYTHING ----------
    # Draw game area background
    bg_color = SKY_BLUE if not is_night else NIGHT_SKY
    pygame.draw.rect(screen, bg_color, (0, 0, GAME_WIDTH, HEIGHT))
    
    # Draw stars and moon if night
    if is_night:
        draw_stars()
        draw_moon()
    
    draw_clouds()
    draw_ground()
    
    # Draw obstacles
    for obs in obstacles:
        draw_cactus(obs['x'], obs['y'], obs['width'], obs['height'])
    
    # Draw dino
    draw_dino(dino_x, dino_y)
    
    # Draw scores
    text_color = BLACK if not is_night else WHITE
    score_text = font_small.render(f"Score: {score}", True, text_color)
    high_score_text = font_small.render(f"High Score: {high_score}", True, text_color)
    speed_text = font_small.render(f"Speed: {current_speed}", True, text_color)
    cycle_text = font_small.render(f"Mode: {'Night' if is_night else 'Day'}", True, text_color)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 35))
    screen.blit(speed_text, (10, 60))
    screen.blit(cycle_text, (10, 85))
    
    # Show game over screen
    if game_over:
        show_game_over()
    
    # ---------- DRAW CAMERA FEED ----------
    # Resize camera frame to fit sidebar
    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    camera_display = cv2.resize(frame, (CAMERA_WIDTH, HEIGHT))
    camera_surface = pygame.surfarray.make_surface(camera_display.swapaxes(0, 1))
    screen.blit(camera_surface, (GAME_WIDTH, 0))
    
    # Draw border around camera
    pygame.draw.rect(screen, BLACK if not is_night else WHITE, 
                    (GAME_WIDTH, 0, CAMERA_WIDTH, HEIGHT), 3)
    
    # Hand status on camera feed
    hand_status = "HAND UP!" if hand_up else "Raise Hand"
    hand_color = (0, 255, 0) if hand_up else (255, 255, 255)
    hand_bg = pygame.Surface((CAMERA_WIDTH - 20, 40))
    hand_bg.set_alpha(180)
    hand_bg.fill((0, 0, 0))
    screen.blit(hand_bg, (GAME_WIDTH + 10, HEIGHT - 50))
    
    hand_text = font_small.render(hand_status, True, hand_color)
    screen.blit(hand_text, (GAME_WIDTH + CAMERA_WIDTH//2 - hand_text.get_width()//2, HEIGHT - 40))
    
    pygame.display.update()
    clock.tick(60)  # Increased to 60 FPS for smoother gameplay