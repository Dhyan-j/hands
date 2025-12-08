import cv2
import mediapipe as mp
import pygame
import random
import time

# ---------------------- SETUP ------------------------
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pygame.init()
pygame.mixer.init()

# Load background music
pygame.mixer.music.load("music.mp3")   # place music.mp3 in same folder
pygame.mixer.music.play(-1)

# Game window
WIDTH, HEIGHT = 900, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Game")

font = pygame.font.SysFont("Arial", 40)
small_font = pygame.font.SysFont("Arial", 25)

# Webcam
cap = cv2.VideoCapture(0)

# Game variables
score = 0
game_over = False
current_action = None
action_start_time = time.time()
ACTION_DURATION = 5

# Simple actions suitable for sitting
ACTIONS = [
    "Raise Right Hand",
    "Raise Left Hand",
    "Raise Both Hands"
]

# -------------------------------------------------------------
# ---------------------- FUNCTIONS ----------------------------
# -------------------------------------------------------------

def flip_lr(x):
    """Fix mirror effect by flipping x-axis."""
    return 1 - x

def check_action(landmarks, action):
    """Check if user completed the current action."""
    if not landmarks:
        return False

    # Get landmarks
    lh = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rh = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    # Fix left-right visually
    lh_x = flip_lr(lh.x)
    rh_x = flip_lr(rh.x)

    # Hand raised logic
    left_up = lh.y < ls.y
    right_up = rh.y < rs.y

    if action == "Raise Right Hand":
        return right_up and not left_up

    if action == "Raise Left Hand":
        return left_up and not right_up

    if action == "Raise Both Hands":
        return left_up and right_up

    return False


def new_action():
    return random.choice(ACTIONS)


# -------------------------------------------------------------
# ----------------------- GAME LOOP ----------------------------
# -------------------------------------------------------------
with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:

    current_action = new_action()

    while True:

        ret, frame = cap.read()
        if not ret:
            continue

        # Fix camera mirror
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(rgb)

        # Draw pose skeleton
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Convert camera frame to pygame
        cam_surface = pygame.surfarray.make_surface(cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE))
        cam_surface = pygame.transform.scale(cam_surface, (320, 240))

        # ---------------- GAME LOGIC -----------------
        if not game_over:

            time_left = ACTION_DURATION - (time.time() - action_start_time)

            # If completed
            if results.pose_landmarks:
                if check_action(results.pose_landmarks.landmark, current_action):
                    score += 1
                    current_action = new_action()
                    action_start_time = time.time()

            # Failed
            if time_left <= 0:
                game_over = True

        # ------------------- UI ----------------------
        win.fill((30, 30, 70))  # dark blue background

        # Webcam on screen
        win.blit(cam_surface, (20, 20))

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(score_text, (20, 280))

        # If playing
        if not game_over:
            action_text = font.render(f"Do: {current_action}", True, (255, 215, 0))
            timer_text = font.render(f"Time Left: {int(time_left)}", True, (255, 80, 80))
            win.blit(action_text, (20, 340))
            win.blit(timer_text, (20, 400))

        # If lost
        else:
            over_text = font.render("GAME OVER!", True, (255, 0, 0))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            win.blit(over_text, (350, 260))
            win.blit(restart_text, (300, 320))

        pygame.display.update()

        # ---------------- EVENT HANDLING --------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Reset everything
                    score = 0
                    game_over = False
                    current_action = new_action()
                    action_start_time = time.time()

