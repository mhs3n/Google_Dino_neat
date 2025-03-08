import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 1600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Game")

# Colors
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

# Load assets (replace with your file paths)
ground_image = pygame.image.load("ground.png").convert_alpha()
ground_width = ground_image.get_width()
ground_height = ground_image.get_height()
ground_y = HEIGHT - ground_height - 20  # Lifted ground
ground_speed = 10
ground_x = 0  # Initialize ground_x here

dino_image = pygame.image.load("dino-idle.png").convert_alpha()
dino_width, dino_height = dino_image.get_size()
dino_x = 50
dino_y = ground_y - dino_height
dino_velocity_y = 0
gravity = 5000 / 60  # Adjust for 60 FPS (Phaser's 5000 gravity scaled)
jump_velocity = -1600 / 60  # Adjust for 60 FPS
is_ducking = False

# Cactus images (6 types: 3 small, 3 big)
cactus_images = [
    pygame.image.load("cactuses_small_1.png").convert_alpha(),  # Small 1
    pygame.image.load("cactuses_small_2.png").convert_alpha(),  # Small 2
    pygame.image.load("cactuses_small_3.png").convert_alpha(),  # Small 3
    pygame.image.load("cactuses_big_1.png").convert_alpha(),    # Big 1
    pygame.image.load("cactuses_big_2.png").convert_alpha(),    # Big 2
    pygame.image.load("cactuses_big_3.png").convert_alpha()     # Big 3
]
for i in range(len(cactus_images)):
    if i < 3:  # Small cacti
        cactus_images[i] = pygame.transform.scale(cactus_images[i], (20, 40))
    else:  # Big cacti
        cactus_images[i] = pygame.transform.scale(cactus_images[i], (40, 80))

# Clouds
cloud_images = [
    pygame.image.load("cloud.png").convert_alpha(),
    pygame.image.load("cloud.png").convert_alpha(),
    pygame.image.load("cloud.png").convert_alpha()
]
cloud_positions = [
    (WIDTH // 2, 170),
    (WIDTH - 80, 80),
    (WIDTH // 1.3, 100)
]
cloud_speed = 0.5

# Game over and restart images
game_over_image = pygame.image.load("game-over.png").convert_alpha()
restart_image = pygame.image.load("restart.png").convert_alpha()
game_over_x, game_over_y = WIDTH // 2, HEIGHT // 2 - 50

# Load sounds (assuming WAV or MP3 files)
pygame.mixer.init()

# Game variables
game_speed = 10
is_game_running = False
score = 0
high_score = 0
cacti = []
spawn_timer = 0
spawn_interval = random.randint(50, 150)  # Frames for arbitrary spawn rate
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 35, bold=True)

# Game over screen
game_over_visible = False

def reset_game():
    global dino_y, dino_velocity_y, is_game_running, cacti, game_speed, score, game_over_visible
    dino_y = ground_y - dino_height
    dino_velocity_y = 0
    is_game_running = True
    cacti.clear()
    game_speed = 10
    score = 0
    game_over_visible = False

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over_visible:
            if restart_rect.collidepoint(event.pos):
                reset_game()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_ducking and dino_y >= ground_y - dino_height:
                dino_velocity_y = jump_velocity
            elif event.key == pygame.K_DOWN and is_game_running:
                is_ducking = True
                dino_height = 58  # Duck height (approx. Phaser's 58)
                dino_y = ground_y - dino_height
            elif event.key == pygame.K_UP and is_ducking:
                is_ducking = False
                dino_height = dino_image.get_height()
                dino_y = ground_y - dino_height
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                is_ducking = False
                dino_height = dino_image.get_height()
                dino_y = ground_y - dino_height

    if not is_game_running and not game_over_visible:
        # Initial state (dino at start)
        if dino_x < 100:  # Move dino right slowly
            dino_x += 2
        else:
            is_game_running = True
            score = 0
    else:
        # Update ground position
        ground_x = (ground_x - game_speed) % ground_width  # Update ground_x here (not ground_y)

        # Update dino position
        dino_velocity_y += gravity
        dino_y += dino_velocity_y
        if dino_y > ground_y - dino_height:
            dino_y = ground_y - dino_height
            dino_velocity_y = 0

        # Update cacti spawn
        spawn_timer += 1
        if spawn_timer >= spawn_interval and is_game_running:
            cactus_type = random.randint(0, 5)
            cacti.append([WIDTH, ground_y - cactus_images[cactus_type].get_height(), cactus_type])
            spawn_timer = 0
            spawn_interval = random.randint(50, 150)

        # Update cacti positions
        for cactus in cacti[:]:
            cactus[0] -= game_speed
            if cactus[0] < -cactus_images[cactus[2]].get_width():
                cacti.remove(cactus)

        # Collision detection
        dino_rect = pygame.Rect(dino_x, dino_y, dino_width if not is_ducking else 44, dino_height)
        for cactus in cacti:
            cactus_rect = cactus_images[cactus[2]].get_rect(topleft=(cactus[0], cactus[1]))
            if dino_rect.colliderect(cactus_rect):
                is_game_running = False
                game_over_visible = True
                if score > high_score:
                    high_score = score
                break

        # Update score and game speed
        if is_game_running:
            score += 1
            game_speed += 0.01

        # Update clouds
        for i, (x, y) in enumerate(cloud_positions):
            cloud_positions[i] = (x - cloud_speed, y)
            if x < -cloud_images[i].get_width():
                cloud_positions[i] = (WIDTH + 30, y)

    # Draw everything
    screen.fill(WHITE)

    # Draw ground
    screen.blit(ground_image, (ground_x - ground_width, ground_y))
    screen.blit(ground_image, (ground_x, ground_y))

    # Draw clouds
    for (x, y), cloud in zip(cloud_positions, cloud_images):
        screen.blit(cloud, (x, y))

    # Draw dino (simple, no animation yet)
    if is_game_running and dino_velocity_y == 0:
        screen.blit(dino_image, (dino_x, dino_y))
    else:
        screen.blit(dino_image, (dino_x, dino_y))  # Placeholder; add animations later

    # Draw cacti
    for cactus in cacti:
        screen.blit(cactus_images[cactus[2]], (cactus[0], cactus[1]))

    # Draw score
    score_text = font.render(f"{score:05d}", True, (83, 83, 83))  # "00000" format
    screen.blit(score_text, (WIDTH - 10, 10))

    # Draw high score
    if game_over_visible:
        high_score_text = font.render(f"HI {high_score:05d}", True, (83, 83, 83))
        screen.blit(high_score_text, (WIDTH - 10 - score_text.get_width() - 20, 10))

        # Draw game over screen
        screen.blit(game_over_image, (game_over_x - game_over_image.get_width() // 2, game_over_y - game_over_image.get_height() // 2))
        restart_rect = restart_image.get_rect(center=(game_over_x, game_over_y + 80))
        screen.blit(restart_image, restart_rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()