import pygame
import mediapipe as mp
import cv2
import sys
import random
import math

pygame.init()

# ------------------ GAME WINDOW ------------------
GAME_WIDTH = 800
CAMERA_WIDTH = 400
WIDTH = GAME_WIDTH + CAMERA_WIDTH
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("One-Hand Exercise Game")

# ------------------ COLORS ------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 220, 50)
PURPLE = (200, 50, 255)
ORANGE = (255, 150, 50)
PINK = (255, 100, 180)
BG_COLOR = (240, 248, 255)

# ------------------ FONTS ------------------
font_huge = pygame.font.Font(None, 72)
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# ------------------ GAME STATE ------------------
current_exercise = 0
exercises = ["Fruit Slicer", "Dodge Obstacles", "Circle Trace", "Speed Tapper"]
score = 0
timer = 45  # seconds per exercise
frame_count = 0
game_state = "menu"  # menu, playing, complete

# ------------------ MEDIAPIPE HAND ------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1,
                        min_detection_confidence=0.7,
                        min_tracking_confidence=0.7)

# ------------------ SMOOTHING ------------------
hand_smoothing_buffer = []
smoothing_window = 5  # Number of frames to average

# ------------------ EXERCISE 1: FRUIT SLICER ------------------
fruits = []
fruit_spawn_timer = 0
slices = 0

def spawn_fruit():
    """Spawn a fruit to slice."""
    side = random.choice(['left', 'right', 'top'])
    if side == 'left':
        x, y = 0, random.randint(100, HEIGHT - 100)
        vx, vy = random.randint(5, 10), random.randint(-3, 3)
    elif side == 'right':
        x, y = GAME_WIDTH, random.randint(100, HEIGHT - 100)
        vx, vy = random.randint(-10, -5), random.randint(-3, 3)
    else:
        x, y = random.randint(100, GAME_WIDTH - 100), HEIGHT
        vx, vy = random.randint(-3, 3), random.randint(-15, -10)
    
    fruits.append({
        'x': x, 'y': y, 'vx': vx, 'vy': vy,
        'size': 40,
        'type': random.choice(['apple', 'orange', 'watermelon']),
        'sliced': False
    })

def check_slice(hand_x, hand_y, hand_trail):
    """Check if hand slices any fruit."""
    global fruits, score, slices
    for fruit in fruits:
        if not fruit['sliced']:
            dist = math.sqrt((hand_x - fruit['x'])**2 + (hand_y - fruit['y'])**2)
            if dist < fruit['size'] + 20:
                fruit['sliced'] = True
                score += 10
                slices += 1
                return True
    return False

# ------------------ EXERCISE 2: DODGE OBSTACLES ------------------
obstacles = []
obstacle_spawn_timer = 0
dodges = 0
player_x = GAME_WIDTH // 2
player_y = HEIGHT // 2
hits = 0

def spawn_obstacle():
    """Spawn an obstacle to dodge."""
    side = random.choice(['left', 'right', 'top', 'bottom'])
    speed = random.randint(6, 10)
    
    if side == 'left':
        x, y = 0, random.randint(50, HEIGHT - 50)
        vx, vy = speed, 0
    elif side == 'right':
        x, y = GAME_WIDTH, random.randint(50, HEIGHT - 50)
        vx, vy = -speed, 0
    elif side == 'top':
        x, y = random.randint(50, GAME_WIDTH - 50), 0
        vx, vy = 0, speed
    else:
        x, y = random.randint(50, GAME_WIDTH - 50), HEIGHT
        vx, vy = 0, -speed
    
    obstacles.append({
        'x': x, 'y': y, 'vx': vx, 'vy': vy,
        'size': 40
    })

# ------------------ EXERCISE 3: CIRCLE TRACE ------------------
circles = []
circle_index = 0
traces = 0
trace_progress = 0
current_shape = "circle"
shape_patterns = {
    "circle": {"name": "Circle", "color": PURPLE},
    "square": {"name": "Square", "color": BLUE},
    "triangle": {"name": "Triangle", "color": GREEN},
    "star": {"name": "Star", "color": YELLOW},
    "heart": {"name": "Heart", "color": RED},
    "zigzag": {"name": "Lightning", "color": ORANGE}
}

def generate_circles():
    """Generate circle path to trace."""
    global circles, current_shape
    circles = []
    
    # Rotate through different shapes
    shapes = list(shape_patterns.keys())
    current_shape = shapes[traces % len(shapes)]
    
    center_x = GAME_WIDTH // 2
    center_y = HEIGHT // 2
    
    if current_shape == "circle":
        num_points = 12
        radius = 180
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            circles.append({'x': int(x), 'y': int(y), 'size': 45, 'hit': False})
    
    elif current_shape == "square":
        size = 300
        points_per_side = 4
        # Top side
        for i in range(points_per_side):
            x = center_x - size//2 + (size * i) // (points_per_side - 1)
            circles.append({'x': x, 'y': center_y - size//2, 'size': 45, 'hit': False})
        # Right side
        for i in range(1, points_per_side):
            y = center_y - size//2 + (size * i) // (points_per_side - 1)
            circles.append({'x': center_x + size//2, 'y': y, 'size': 45, 'hit': False})
        # Bottom side
        for i in range(1, points_per_side):
            x = center_x + size//2 - (size * i) // (points_per_side - 1)
            circles.append({'x': x, 'y': center_y + size//2, 'size': 45, 'hit': False})
        # Left side
        for i in range(1, points_per_side - 1):
            y = center_y + size//2 - (size * i) // (points_per_side - 1)
            circles.append({'x': center_x - size//2, 'y': y, 'size': 45, 'hit': False})
    
    elif current_shape == "triangle":
        radius = 200
        for i in range(3):
            angle = (2 * math.pi * i) / 3 - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            # Add points along each edge
            next_i = (i + 1) % 3
            next_angle = (2 * math.pi * next_i) / 3 - math.pi / 2
            next_x = center_x + radius * math.cos(next_angle)
            next_y = center_y + radius * math.sin(next_angle)
            
            for j in range(4):
                t = j / 4
                px = int(x + (next_x - x) * t)
                py = int(y + (next_y - y) * t)
                circles.append({'x': px, 'y': py, 'size': 45, 'hit': False})
    
    elif current_shape == "star":
        num_points = 10
        outer_radius = 200
        inner_radius = 80
        for i in range(num_points):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = (2 * math.pi * i) / num_points - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            circles.append({'x': int(x), 'y': int(y), 'size': 40, 'hit': False})
    
    elif current_shape == "heart":
        # Heart shape using parametric equations
        num_points = 16
        for i in range(num_points):
            t = (2 * math.pi * i) / num_points
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            scale = 12
            circles.append({
                'x': int(center_x + x * scale),
                'y': int(center_y + y * scale - 30),
                'size': 45,
                'hit': False
            })
    
    elif current_shape == "zigzag":
        num_zigs = 5
        width = 400
        height = 200
        start_x = center_x - width // 2
        start_y = center_y - height // 2
        
        for i in range(num_zigs * 2 + 1):
            x = start_x + (width * i) // (num_zigs * 2)
            y = start_y if i % 2 == 0 else start_y + height
            circles.append({'x': int(x), 'y': int(y), 'size': 45, 'hit': False})

# ------------------ EXERCISE 4: SPEED TAPPER ------------------
tap_targets = []
tap_timer = 0
taps = 0

def spawn_tap_target():
    """Spawn a target to tap quickly."""
    x = random.randint(100, GAME_WIDTH - 100)
    y = random.randint(100, HEIGHT - 100)
    tap_targets.append({
        'x': x, 'y': y, 'size': 60,
        'lifetime': 90  # 1.5 seconds to tap
    })

# ------------------ DRAWING FUNCTIONS ------------------
def draw_menu():
    """Draw main menu."""
    title = font_huge.render("Exercise Game!", True, BLUE)
    screen.blit(title, (GAME_WIDTH//2 - title.get_width()//2, 100))
    
    instruction = font_medium.render("Raise your hand to start!", True, BLACK)
    screen.blit(instruction, (GAME_WIDTH//2 - instruction.get_width()//2, 200))
    
    # Exercise list
    y_offset = 280
    for i, ex in enumerate(exercises):
        color = GREEN if i == current_exercise else BLACK
        ex_text = font_small.render(f"{i+1}. {ex}", True, color)
        screen.blit(ex_text, (GAME_WIDTH//2 - ex_text.get_width()//2, y_offset))
        y_offset += 35

def draw_hud():
    """Draw heads-up display."""
    # Exercise name
    ex_name = font_large.render(exercises[current_exercise], True, BLUE)
    screen.blit(ex_name, (20, 20))
    
    # Score
    score_text = font_medium.render(f"Score: {score}", True, GREEN)
    screen.blit(score_text, (20, 80))
    
    # Timer
    time_remaining = max(0, timer - frame_count // 60)
    timer_text = font_medium.render(f"Time: {time_remaining}s", True, RED if time_remaining < 10 else BLACK)
    screen.blit(timer_text, (20, 120))
    
    # Exercise-specific stats
    if current_exercise == 0:
        stat_text = font_small.render(f"Slices: {slices}", True, ORANGE)
    elif current_exercise == 1:
        stat_text = font_small.render(f"Hits: {hits} | Survived: {dodges}", True, RED)
    elif current_exercise == 2:
        shape_info = shape_patterns[current_shape]
        stat_text = font_small.render(f"Shape: {shape_info['name']} | Progress: {traces}", True, shape_info['color'])
        screen.blit(stat_text, (20, 160))
        completion_text = font_small.render(f"{circle_index}/{len(circles)} points", True, PURPLE)
        stat_text = completion_text
    else:
        stat_text = font_small.render(f"Taps: {taps}", True, PINK)
    screen.blit(stat_text, (20, 190))

def draw_fruits():
    """Draw fruits to slice."""
    for fruit in fruits:
        if fruit['sliced']:
            # Draw sliced fruit pieces
            offset = (frame_count - fruit.get('slice_frame', frame_count)) * 3
            color = {'apple': RED, 'orange': ORANGE, 'watermelon': GREEN}[fruit['type']]
            pygame.draw.circle(screen, color, (int(fruit['x'] - offset), int(fruit['y'] - offset)), 20)
            pygame.draw.circle(screen, color, (int(fruit['x'] + offset), int(fruit['y'] + offset)), 20)
        else:
            # Draw whole fruit
            color = {'apple': RED, 'orange': ORANGE, 'watermelon': GREEN}[fruit['type']]
            pygame.draw.circle(screen, color, (int(fruit['x']), int(fruit['y'])), fruit['size'])
            pygame.draw.circle(screen, WHITE, (int(fruit['x']), int(fruit['y'])), fruit['size'], 3)

def draw_obstacles():
    """Draw obstacles to dodge."""
    for obs in obstacles:
        # Draw danger zone
        pygame.draw.circle(screen, (255, 200, 200), (int(obs['x']), int(obs['y'])), obs['size'] + 10)
        pygame.draw.circle(screen, RED, (int(obs['x']), int(obs['y'])), obs['size'])
        pygame.draw.circle(screen, (150, 0, 0), (int(obs['x']), int(obs['y'])), obs['size'] // 2)

def draw_player(x, y):
    """Draw player."""
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), 25)
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), 25, 3)
    pygame.draw.circle(screen, BLACK, (int(x), int(y)), 5)

def draw_circles():
    """Draw circle trace path."""
    shape_info = shape_patterns[current_shape]
    
    # Draw lines connecting circles
    for i in range(len(circles)):
        next_i = (i + 1) % len(circles)
        if circles[i]['hit']:
            color = shape_info['color']
            width = 4
        else:
            color = (200, 200, 200)
            width = 2
        pygame.draw.line(screen, color, 
                        (circles[i]['x'], circles[i]['y']),
                        (circles[next_i]['x'], circles[next_i]['y']), width)
    
    # Draw circles
    for i, circle in enumerate(circles):
        if circle['hit']:
            # Completed point - filled with shape color
            pygame.draw.circle(screen, shape_info['color'], (circle['x'], circle['y']), circle['size'])
            pygame.draw.circle(screen, WHITE, (circle['x'], circle['y']), circle['size'], 3)
            # Check mark
            pygame.draw.line(screen, WHITE, 
                           (circle['x'] - 10, circle['y']),
                           (circle['x'] - 3, circle['y'] + 10), 3)
            pygame.draw.line(screen, WHITE,
                           (circle['x'] - 3, circle['y'] + 10),
                           (circle['x'] + 10, circle['y'] - 10), 3)
        elif i == circle_index:
            # Current target - pulsing with number
            pulse = 1 + 0.3 * math.sin(frame_count * 0.15)
            size = int(circle['size'] * pulse)
            pygame.draw.circle(screen, YELLOW, (circle['x'], circle['y']), size)
            pygame.draw.circle(screen, shape_info['color'], (circle['x'], circle['y']), size, 5)
            # Draw arrow pointing to it
            arrow_offset = 80
            arrow_angle = frame_count * 0.1
            arrow_x = circle['x'] + arrow_offset * math.cos(arrow_angle)
            arrow_y = circle['y'] + arrow_offset * math.sin(arrow_angle)
            pygame.draw.circle(screen, YELLOW, (int(arrow_x), int(arrow_y)), 8)
        else:
            # Future point - gray
            pygame.draw.circle(screen, (200, 200, 200), (circle['x'], circle['y']), circle['size'])
            pygame.draw.circle(screen, BLACK, (circle['x'], circle['y']), circle['size'], 2)
            # Draw number
            num_text = font_small.render(str(i + 1), True, BLACK)
            screen.blit(num_text, (circle['x'] - num_text.get_width()//2, 
                                  circle['y'] - num_text.get_height()//2))
    
    # Draw shape name at top
    shape_title = font_large.render(f"Trace: {shape_info['name']}", True, shape_info['color'])
    screen.blit(shape_title, (GAME_WIDTH//2 - shape_title.get_width()//2, 30))

def draw_tap_targets():
    """Draw tap targets."""
    for target in tap_targets:
        life_ratio = target['lifetime'] / 90
        
        # Shrinking circle
        current_size = int(target['size'] * life_ratio)
        
        # Draw target
        pygame.draw.circle(screen, PINK, (target['x'], target['y']), target['size'])
        pygame.draw.circle(screen, WHITE, (target['x'], target['y']), current_size, 5)
        
        # Timer bar
        pygame.draw.arc(screen, RED, 
                       (target['x'] - target['size'], target['y'] - target['size'],
                        target['size'] * 2, target['size'] * 2),
                       0, 2 * math.pi * life_ratio, 6)

def draw_complete():
    """Draw completion screen."""
    overlay = pygame.Surface((GAME_WIDTH, HEIGHT))
    overlay.set_alpha(230)
    overlay.fill(WHITE)
    screen.blit(overlay, (0, 0))
    
    complete_text = font_huge.render("Complete!", True, GREEN)
    screen.blit(complete_text, (GAME_WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 150))
    
    score_text = font_large.render(f"Score: {score}", True, BLUE)
    screen.blit(score_text, (GAME_WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 50))
    
    instruction = font_small.render("Raise hand to continue", True, BLACK)
    screen.blit(instruction, (GAME_WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 100))

def reset_exercise():
    """Reset current exercise."""
    global fruits, obstacles, circles, tap_targets, frame_count
    global slices, dodges, traces, taps, hits, circle_index, trace_progress
    global fruit_spawn_timer, obstacle_spawn_timer, tap_timer
    global player_x, player_y
    
    fruits = []
    obstacles = []
    tap_targets = []
    slices = 0
    dodges = 0
    traces = 0
    taps = 0
    hits = 0
    circle_index = 0
    trace_progress = 0
    frame_count = 0
    fruit_spawn_timer = 0
    obstacle_spawn_timer = 0
    tap_timer = 0
    player_x = GAME_WIDTH // 2
    player_y = HEIGHT // 2
    
    if current_exercise == 2:
        generate_circles()

# ------------------ GAME LOOP ------------------
hand_up_timer = 0
hand_trail = []
smoothed_hand_x = GAME_WIDTH // 2
smoothed_hand_y = HEIGHT // 2

while True:
    # ---------- PROCESS CAMERA ----------
    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    # Draw hand landmarks on frame
    hand_detected = False
    hand_x, hand_y = smoothed_hand_x, smoothed_hand_y  # Use smoothed values as default
    hand_raised = False
    
    if results.multi_hand_landmarks:
        hand_detected = True
        hand_landmarks = results.multi_hand_landmarks[0]
        
        mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
        )
        
        # Get hand position
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        
        # Convert to game coordinates (NO FLIP - direct mapping)
        raw_x = int(wrist.x * GAME_WIDTH)
        raw_y = int(wrist.y * HEIGHT)
        
        # Add to smoothing buffer
        hand_smoothing_buffer.append((raw_x, raw_y))
        if len(hand_smoothing_buffer) > smoothing_window:
            hand_smoothing_buffer.pop(0)
        
        # Calculate smoothed position
        if len(hand_smoothing_buffer) > 0:
            avg_x = sum(pos[0] for pos in hand_smoothing_buffer) / len(hand_smoothing_buffer)
            avg_y = sum(pos[1] for pos in hand_smoothing_buffer) / len(hand_smoothing_buffer)
            
            # Apply exponential smoothing for even smoother movement
            alpha = 0.3  # Smoothing factor (0 = no change, 1 = instant change)
            smoothed_hand_x = int(alpha * avg_x + (1 - alpha) * smoothed_hand_x)
            smoothed_hand_y = int(alpha * avg_y + (1 - alpha) * smoothed_hand_y)
        
        hand_x = smoothed_hand_x
        hand_y = smoothed_hand_y
        
        # Check if hand is raised
        hand_raised = wrist.y < 0.5 and middle_tip.y < wrist.y
        
        # Track hand trail for slicing (use smoothed positions)
        hand_trail.append((hand_x, hand_y))
        if len(hand_trail) > 15:
            hand_trail.pop(0)
    else:
        hand_trail = []
        # Clear smoothing buffer when hand not detected
        if len(hand_smoothing_buffer) > 0:
            hand_smoothing_buffer = []
    
    if hand_raised:
        hand_up_timer += 1
    else:
        hand_up_timer = 0
    
    # ---------- GAME EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
    
    # ---------- GAME STATE MACHINE ----------
    if game_state == "menu":
        screen.fill(BG_COLOR)
        draw_menu()
        
        if hand_up_timer > 30:  # ~0.5 seconds
            game_state = "playing"
            reset_exercise()
            hand_up_timer = 0
    
    elif game_state == "playing":
        frame_count += 1
        
        # Check timer
        if frame_count >= timer * 60:
            game_state = "complete"
        
        screen.fill(BG_COLOR)
        
        # ---------- EXERCISE-SPECIFIC LOGIC ----------
        if current_exercise == 0:  # Fruit Slicer
            # Spawn fruits
            fruit_spawn_timer += 1
            if fruit_spawn_timer > 50:
                spawn_fruit()
                fruit_spawn_timer = 0
            
            # Update fruits
            for fruit in fruits[:]:
                fruit['x'] += fruit['vx']
                fruit['y'] += fruit['vy']
                fruit['vy'] += 0.5  # gravity
                
                # Remove off-screen fruits
                if (fruit['x'] < -100 or fruit['x'] > GAME_WIDTH + 100 or
                    fruit['y'] > HEIGHT + 100):
                    fruits.remove(fruit)
                
                # Mark slice frame
                if fruit['sliced'] and 'slice_frame' not in fruit:
                    fruit['slice_frame'] = frame_count
            
            # Check slices
            if hand_detected:
                check_slice(hand_x, hand_y, hand_trail)
            
            draw_fruits()
            
            # Draw hand trail
            if len(hand_trail) > 1:
                pygame.draw.lines(screen, YELLOW, False, hand_trail, 5)
            
            # Draw hand cursor
            if hand_detected:
                pygame.draw.circle(screen, ORANGE, (hand_x, hand_y), 15, 3)
        
        elif current_exercise == 1:  # Dodge Obstacles
            # Spawn obstacles
            obstacle_spawn_timer += 1
            spawn_rate = max(30, 60 - frame_count // 100)
            if obstacle_spawn_timer > spawn_rate:
                spawn_obstacle()
                obstacle_spawn_timer = 0
            
            # Update player position
            if hand_detected:
                player_x = hand_x
                player_y = hand_y
            
            # Update obstacles
            for obs in obstacles[:]:
                obs['x'] += obs['vx']
                obs['y'] += obs['vy']
                
                # Check collision
                dist = math.sqrt((player_x - obs['x'])**2 + (player_y - obs['y'])**2)
                if dist < 25 + obs['size']:
                    hits += 1
                    obstacles.remove(obs)
                    score = max(0, score - 5)
                    continue
                
                # Remove off-screen
                if (obs['x'] < -100 or obs['x'] > GAME_WIDTH + 100 or
                    obs['y'] < -100 or obs['y'] > HEIGHT + 100):
                    obstacles.remove(obs)
                    dodges += 1
                    score += 5
            
            draw_obstacles()
            draw_player(player_x, player_y)
        
        elif current_exercise == 2:  # Circle Trace
            if hand_detected and circle_index < len(circles):
                current_circle = circles[circle_index]
                dist = math.sqrt((hand_x - current_circle['x'])**2 + 
                               (hand_y - current_circle['y'])**2)
                
                if dist < current_circle['size']:
                    if not current_circle['hit']:
                        current_circle['hit'] = True
                        score += 15
                    
                    # Automatically advance to next circle
                    circle_index += 1
                    
                    # Check if shape is complete
                    if circle_index >= len(circles):
                        score += 50  # Bonus for completing shape
                        traces += 1
                        # Generate new shape
                        generate_circles()
                        circle_index = 0
            
            draw_circles()
            
            # Draw hand cursor with trail
            if len(hand_trail) > 1:
                # Draw fading trail
                for i in range(len(hand_trail) - 1):
                    alpha = int(255 * (i + 1) / len(hand_trail))
                    color = (*shape_patterns[current_shape]['color'][:3], alpha) if i > len(hand_trail) - 5 else (150, 150, 150)
                    start = hand_trail[i]
                    end = hand_trail[i + 1]
                    pygame.draw.line(screen, shape_patterns[current_shape]['color'], start, end, 3)
            
            # Draw hand cursor
            if hand_detected:
                pygame.draw.circle(screen, shape_patterns[current_shape]['color'], (hand_x, hand_y), 20, 4)
                pygame.draw.circle(screen, WHITE, (hand_x, hand_y), 12)
                pygame.draw.circle(screen, shape_patterns[current_shape]['color'], (hand_x, hand_y), 5)
        
        elif current_exercise == 3:  # Speed Tapper
            # Spawn targets
            tap_timer += 1
            if tap_timer > 60 and len(tap_targets) < 3:
                spawn_tap_target()
                tap_timer = 0
            
            # Update targets
            for target in tap_targets[:]:
                target['lifetime'] -= 1
                
                # Check tap
                if hand_detected:
                    dist = math.sqrt((hand_x - target['x'])**2 + 
                                   (hand_y - target['y'])**2)
                    if dist < target['size']:
                        tap_targets.remove(target)
                        score += 10
                        taps += 1
                        continue
                
                # Remove expired
                if target['lifetime'] <= 0:
                    tap_targets.remove(target)
            
            draw_tap_targets()
            
            # Draw hand cursor
            if hand_detected:
                pygame.draw.circle(screen, PINK, (hand_x, hand_y), 20, 3)
                pygame.draw.circle(screen, WHITE, (hand_x, hand_y), 15)
        
        draw_hud()
    
    elif game_state == "complete":
        screen.fill(BG_COLOR)
        draw_complete()
        
        if hand_up_timer > 30:
            current_exercise = (current_exercise + 1) % len(exercises)
            game_state = "menu"
            score = 0
            hand_up_timer = 0
    
    # ---------- DRAW CAMERA FEED ----------
    camera_display = cv2.resize(frame, (CAMERA_WIDTH, HEIGHT))
    camera_surface = pygame.surfarray.make_surface(camera_display.swapaxes(0, 1))
    screen.blit(camera_surface, (GAME_WIDTH, 0))
    
    # Draw border
    pygame.draw.rect(screen, BLACK, (GAME_WIDTH, 0, CAMERA_WIDTH, HEIGHT), 3)
    
    # Hand detection status
    status_bg = pygame.Surface((CAMERA_WIDTH - 20, 60))
    status_bg.set_alpha(200)
    status_bg.fill((0, 0, 0))
    screen.blit(status_bg, (GAME_WIDTH + 10, HEIGHT - 70))
    
    if hand_detected:
        status_text = "Hand Detected!"
        color = (0, 255, 0) if hand_raised else (255, 255, 255)
    else:
        status_text = "Show your hand"
        color = (255, 100, 100)
    
    status = font_small.render(status_text, True, color)
    screen.blit(status, (GAME_WIDTH + CAMERA_WIDTH//2 - status.get_width()//2, HEIGHT - 55))
    
    if hand_raised:
        raised_text = font_small.render("RAISED!", True, (0, 255, 0))
        screen.blit(raised_text, (GAME_WIDTH + CAMERA_WIDTH//2 - raised_text.get_width()//2, HEIGHT - 30))
    
    pygame.display.update()
    clock.tick(60)