import pygame
import mediapipe as mp
import cv2
import sys
import random

# Initialize Pygame
pygame.init()

# ==================== CONFIGURATION ====================
class Config:
    """Game configuration constants."""
    # Display settings
    GAME_WIDTH = 800
    CAMERA_WIDTH = 320
    TOTAL_WIDTH = GAME_WIDTH + CAMERA_WIDTH
    HEIGHT = 400
    FPS = 60
    
    # Colors - Day mode
    SKY_BLUE = (135, 206, 235)
    GROUND_COLOR = (200, 200, 200)
    GROUND_LINE_COLOR = (150, 150, 150)
    GROUND_ACCENT = (100, 100, 100)
    DINO_COLOR = (50, 150, 50)
    CACTUS_COLOR = (34, 139, 34)
    CACTUS_DETAIL = (50, 200, 50)
    CLOUD_COLOR = (255, 255, 255)
    
    # Colors - Night mode
    NIGHT_SKY = (25, 25, 50)
    NIGHT_GROUND_LINE = (100, 100, 100)
    NIGHT_DINO = (100, 200, 100)
    NIGHT_CACTUS = (50, 100, 50)
    NIGHT_CACTUS_DETAIL = (70, 130, 70)
    NIGHT_CLOUD = (70, 70, 90)
    MOON_COLOR = (240, 240, 200)
    STAR_COLOR = (255, 255, 200)
    
    # Universal colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Dino settings
    DINO_X = 80
    DINO_WIDTH = 50
    DINO_HEIGHT = 50
    GROUND_Y = 300
    
    # Physics
    GRAVITY = 0.8
    JUMP_POWER = -16
    
    # Game mechanics
    BASE_SPEED = 6
    MAX_SPEED = 15
    INITIAL_SPAWN_INTERVAL = 90
    MIN_SPAWN_INTERVAL = 40
    SPEED_INCREASE_INTERVAL = 100
    SPAWN_DECREASE_RATE = 200
    
    # Day/Night cycle
    CYCLE_DURATION = 500
    NUM_STARS = 30
    
    # Hand detection
    HAND_DETECTION_CONFIDENCE = 0.7
    HAND_TRACKING_CONFIDENCE = 0.7
    HAND_RAISE_THRESHOLD = 0.5

# ==================== GAME STATE ====================
class GameState:
    """Manages the game state."""
    def __init__(self):
        self.reset()
        self.high_score = 0
        
    def reset(self):
        """Reset game to initial state."""
        self.dino_y = Config.GROUND_Y
        self.velocity_y = 0
        self.is_jumping = False
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.obstacle_timer = 0
        self.current_speed = Config.BASE_SPEED
        self.obstacle_spawn_interval = Config.INITIAL_SPAWN_INTERVAL
        self.is_night = False
        self.cycle_timer = 0
        
    def update_high_score(self):
        """Update high score if current score is higher."""
        self.high_score = max(self.high_score, self.score)

# ==================== HAND DETECTOR ====================
class HandDetector:
    """Handles hand detection using MediaPipe."""
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=Config.HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.HAND_TRACKING_CONFIDENCE
        )
        self.cap = cv2.VideoCapture(0)
        self.last_hand_up = False
        
    def process_frame(self):
        """Process camera frame and detect hand position."""
        ret, frame = self.cap.read()
        if not ret:
            return None, False
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
                )
        
        # Detect if hand is raised
        hand_up = False
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            wrist = hand.landmark[self.mp_hands.HandLandmark.WRIST]
            if wrist.y < Config.HAND_RAISE_THRESHOLD:
                hand_up = True
        
        # Detect hand raise edge (transition from down to up)
        hand_raised = hand_up and not self.last_hand_up
        self.last_hand_up = hand_up
        
        return frame, hand_raised, hand_up
        
    def release(self):
        """Release camera resources."""
        self.cap.release()

# ==================== RENDERER ====================
class Renderer:
    """Handles all drawing operations."""
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.stars = [(random.randint(0, Config.GAME_WIDTH), 
                      random.randint(20, 150)) for _ in range(Config.NUM_STARS)]
        
    def draw_background(self, is_night, score):
        """Draw background with sky and clouds."""
        bg_color = Config.NIGHT_SKY if is_night else Config.SKY_BLUE
        pygame.draw.rect(self.screen, bg_color, (0, 0, Config.GAME_WIDTH, Config.HEIGHT))
        
        if is_night:
            self._draw_stars(score)
            self._draw_moon()
        
        self._draw_clouds(is_night, score)
        
    def _draw_stars(self, score):
        """Draw twinkling stars."""
        for star_x, star_y in self.stars:
            size = 2 if random.random() > 0.98 else 1
            pygame.draw.circle(self.screen, Config.STAR_COLOR, (star_x, star_y), size)
            
    def _draw_moon(self):
        """Draw moon with craters."""
        moon_x, moon_y = Config.GAME_WIDTH - 100, 80
        pygame.draw.circle(self.screen, Config.MOON_COLOR, (moon_x, moon_y), 30)
        pygame.draw.circle(self.screen, (200, 200, 180), (moon_x - 8, moon_y - 5), 6)
        pygame.draw.circle(self.screen, (200, 200, 180), (moon_x + 10, moon_y + 8), 4)
        
    def _draw_clouds(self, is_night, score):
        """Draw moving clouds."""
        cloud_positions = [(100, 80), (400, 50), (650, 90)]
        offset = (score // 2) % Config.GAME_WIDTH
        cloud_color = Config.NIGHT_CLOUD if is_night else Config.CLOUD_COLOR
        
        for cx, cy in cloud_positions:
            x = (cx - offset) % Config.GAME_WIDTH
            pygame.draw.circle(self.screen, cloud_color, (x, cy), 20)
            pygame.draw.circle(self.screen, cloud_color, (x + 25, cy), 25)
            pygame.draw.circle(self.screen, cloud_color, (x + 50, cy), 20)
            pygame.draw.ellipse(self.screen, cloud_color, (x - 10, cy + 10, 70, 30))
            
    def draw_ground(self, is_night, score):
        """Draw animated ground."""
        line_color = Config.GROUND_LINE_COLOR if not is_night else Config.WHITE
        ground_accent = Config.GROUND_ACCENT if not is_night else Config.NIGHT_GROUND_LINE
        
        ground_line_y = Config.GROUND_Y + Config.DINO_HEIGHT + 10
        pygame.draw.line(self.screen, line_color, (0, ground_line_y), 
                        (Config.GAME_WIDTH, ground_line_y), 3)
        
        # Moving ground pattern
        offset = (score * 2) % 40
        for i in range(-1, Config.GAME_WIDTH // 40 + 1):
            x = i * 40 - offset
            pygame.draw.line(self.screen, ground_accent, (x, ground_line_y + 2),
                           (x + 20, ground_line_y + 2), 2)
                           
    def draw_dino(self, x, y, is_night, is_jumping, score):
        """Draw animated dinosaur."""
        color = Config.NIGHT_DINO if is_night else Config.DINO_COLOR
        
        # Body
        pygame.draw.rect(self.screen, color, (x, y, Config.DINO_WIDTH, Config.DINO_HEIGHT))
        
        # Head
        pygame.draw.rect(self.screen, color, 
                        (x + Config.DINO_WIDTH - 15, y - 15, 25, 25))
        
        # Eye
        eye_color = Config.WHITE if is_night else Config.BLACK
        pygame.draw.circle(self.screen, eye_color, 
                          (x + Config.DINO_WIDTH - 5, y - 8), 3)
        
        # Animated legs
        leg_offset = 0 if is_jumping else (score // 5) % 2 * 5
        pygame.draw.rect(self.screen, color, 
                        (x + 5, y + Config.DINO_HEIGHT, 8, 10 + leg_offset))
        pygame.draw.rect(self.screen, color, 
                        (x + Config.DINO_WIDTH - 13, y + Config.DINO_HEIGHT, 8, 10 - leg_offset))
                        
    def draw_obstacle(self, x, y, width, height, is_night):
        """Draw cactus obstacle."""
        color = Config.NIGHT_CACTUS if is_night else Config.CACTUS_COLOR
        detail_color = Config.NIGHT_CACTUS_DETAIL if is_night else Config.CACTUS_DETAIL
        
        # Main body
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        # Arms
        pygame.draw.rect(self.screen, color, (x - 8, y + 10, 8, 15))
        pygame.draw.rect(self.screen, color, (x + width, y + 15, 8, 12))
        
        # Details
        for i in range(3):
            pygame.draw.line(self.screen, detail_color,
                           (x + width // 2 - 2, y + 10 + i * 15),
                           (x + width // 2 + 2, y + 10 + i * 15), 2)
                           
    def draw_hud(self, score, high_score, speed, is_night):
        """Draw heads-up display with game stats."""
        text_color = Config.WHITE if is_night else Config.BLACK
        
        texts = [
            (f"Score: {score}", 10),
            (f"High Score: {high_score}", 35),
            (f"Speed: {speed}", 60),
            (f"Mode: {'Night' if is_night else 'Day'}", 85)
        ]
        
        for text, y_pos in texts:
            rendered = self.font_small.render(text, True, text_color)
            self.screen.blit(rendered, (10, y_pos))
            
    def draw_game_over(self, score, high_score, is_night):
        """Draw game over overlay."""
        overlay = pygame.Surface((Config.GAME_WIDTH, Config.HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Config.WHITE if not is_night else (40, 40, 60))
        self.screen.blit(overlay, (0, 0))
        
        text_color = Config.BLACK if not is_night else Config.WHITE
        
        texts = [
            (self.font_large, "GAME OVER!", -80),
            (self.font_medium, f"Score: {score}", -20),
            (self.font_medium, f"High Score: {high_score}", 20),
            (self.font_small, "Raise your hand to restart", 70)
        ]
        
        for font, text, y_offset in texts:
            rendered = font.render(text, True, text_color)
            x = Config.GAME_WIDTH // 2 - rendered.get_width() // 2
            y = Config.HEIGHT // 2 + y_offset
            self.screen.blit(rendered, (x, y))
            
    def draw_camera_feed(self, frame, hand_up):
        """Draw camera feed with hand detection status."""
        # Resize and convert frame (BGR to RGB for correct colors)
        camera_display = cv2.resize(frame, (Config.CAMERA_WIDTH, Config.HEIGHT))
        # Convert BGR to RGB to fix purple face issue
        camera_display = cv2.cvtColor(camera_display, cv2.COLOR_BGR2RGB)
        camera_surface = pygame.surfarray.make_surface(camera_display.swapaxes(0, 1))
        self.screen.blit(camera_surface, (Config.GAME_WIDTH, 0))
        
        # Draw border
        pygame.draw.rect(self.screen, Config.BLACK,
                        (Config.GAME_WIDTH, 0, Config.CAMERA_WIDTH, Config.HEIGHT), 3)
        
        # Hand status indicator
        status_text = "HAND UP!" if hand_up else "Raise Hand"
        status_color = (0, 255, 0) if hand_up else Config.WHITE
        
        # Background for text
        bg_surface = pygame.Surface((Config.CAMERA_WIDTH - 20, 40))
        bg_surface.set_alpha(180)
        bg_surface.fill(Config.BLACK)
        self.screen.blit(bg_surface, (Config.GAME_WIDTH + 10, Config.HEIGHT - 50))
        
        # Status text
        text = self.font_small.render(status_text, True, status_color)
        text_x = Config.GAME_WIDTH + Config.CAMERA_WIDTH // 2 - text.get_width() // 2
        self.screen.blit(text, (text_x, Config.HEIGHT - 40))

# ==================== GAME ENGINE ====================
class DinoGame:
    """Main game engine."""
    def __init__(self):
        self.screen = pygame.display.set_mode((Config.TOTAL_WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Hand Gesture Dino Game")
        self.clock = pygame.time.Clock()
        
        self.state = GameState()
        self.detector = HandDetector()
        self.renderer = Renderer(self.screen)
        
    def handle_jump(self):
        """Make dino jump."""
        if not self.state.is_jumping:
            self.state.velocity_y = Config.JUMP_POWER
            self.state.is_jumping = True
            
    def update_physics(self):
        """Update dino physics."""
        if self.state.is_jumping or self.state.dino_y < Config.GROUND_Y:
            self.state.dino_y += self.state.velocity_y
            self.state.velocity_y += Config.GRAVITY
            
            if self.state.dino_y >= Config.GROUND_Y:
                self.state.dino_y = Config.GROUND_Y
                self.state.is_jumping = False
                self.state.velocity_y = 0
                
    def update_day_night_cycle(self):
        """Update day/night cycle."""
        if (self.state.score > 0 and 
            self.state.score % Config.CYCLE_DURATION == 0 and 
            self.state.score != self.state.cycle_timer):
            self.state.is_night = not self.state.is_night
            self.state.cycle_timer = self.state.score
            
    def update_difficulty(self):
        """Increase game difficulty over time."""
        if self.state.score % Config.SPEED_INCREASE_INTERVAL == 0:
            self.state.current_speed = min(
                Config.BASE_SPEED + self.state.score // Config.SPEED_INCREASE_INTERVAL,
                Config.MAX_SPEED
            )
            self.state.obstacle_spawn_interval = max(
                Config.MIN_SPAWN_INTERVAL,
                Config.INITIAL_SPAWN_INTERVAL - self.state.score // Config.SPAWN_DECREASE_RATE
            )
            
    def spawn_obstacle(self):
        """Spawn a new obstacle."""
        self.state.obstacle_timer += 1
        if self.state.obstacle_timer >= self.state.obstacle_spawn_interval:
            height = random.choice([40, 50, 60])
            self.state.obstacles.append({
                'x': Config.GAME_WIDTH,
                'y': Config.GROUND_Y + Config.DINO_HEIGHT - height + 10,
                'width': random.choice([30, 40]),
                'height': height
            })
            self.state.obstacle_timer = 0
            
    def update_obstacles(self):
        """Move and clean up obstacles."""
        for obs in self.state.obstacles:
            obs['x'] -= self.state.current_speed
        
        self.state.obstacles = [
            obs for obs in self.state.obstacles 
            if obs['x'] > -obs['width']
        ]
        
    def check_collision(self):
        """Check for collisions with obstacles."""
        dino_rect = pygame.Rect(
            Config.DINO_X + 5,
            self.state.dino_y + 5,
            Config.DINO_WIDTH - 10,
            Config.DINO_HEIGHT - 5
        )
        
        for obs in self.state.obstacles:
            obs_rect = pygame.Rect(
                obs['x'] + 5,
                obs['y'],
                obs['width'] - 10,
                obs['height']
            )
            if dino_rect.colliderect(obs_rect):
                self.state.game_over = True
                self.state.update_high_score()
                return True
        return False
        
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Process camera and hand detection
            result = self.detector.process_frame()
            if result is None:
                continue
            
            frame, hand_raised, hand_up = result
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state.game_over:
                            self.state.reset()
                        else:
                            self.handle_jump()
            
            # Handle hand gesture
            if hand_raised:
                if self.state.game_over:
                    self.state.reset()
                else:
                    self.handle_jump()
            
            # Update game state
            if not self.state.game_over:
                self.update_physics()
                self.update_day_night_cycle()
                self.state.score += 1
                self.update_difficulty()
                self.spawn_obstacle()
                self.update_obstacles()
                self.check_collision()
            
            # Render everything
            self.renderer.draw_background(self.state.is_night, self.state.score)
            self.renderer.draw_ground(self.state.is_night, self.state.score)
            
            for obs in self.state.obstacles:
                self.renderer.draw_obstacle(
                    obs['x'], obs['y'], obs['width'], obs['height'],
                    self.state.is_night
                )
            
            self.renderer.draw_dino(
                Config.DINO_X, self.state.dino_y,
                self.state.is_night, self.state.is_jumping,
                self.state.score
            )
            
            self.renderer.draw_hud(
                self.state.score, self.state.high_score,
                self.state.current_speed, self.state.is_night
            )
            
            if self.state.game_over:
                self.renderer.draw_game_over(
                    self.state.score, self.state.high_score,
                    self.state.is_night
                )
            
            self.renderer.draw_camera_feed(frame, hand_up)
            
            pygame.display.update()
            self.clock.tick(Config.FPS)
        
        # Cleanup
        self.detector.release()
        pygame.quit()
        sys.exit()

# ==================== MAIN ====================
if __name__ == "__main__":
    game = DinoGame()
    game.run()