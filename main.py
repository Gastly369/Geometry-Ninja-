import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FLAME_COLOR = (255, 69, 0)  # Color for the flame mode
ICE_COLOR = (173, 216, 230)  # Color for the ice mode
BOSS_COLOR = (255, 0, 0)  # Color for the boss
CHI_COLOR = (255, 255, 0)  # Color for the chi

# Game settings
FPS = 60
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
game_over = False
score = 0
lives = 3
level = 1
chi_spawn_level = 4  # Level at which chi starts spawning
block_drop_speed = 2
block_frequency = 2000
blocks = []
power_ups = []
chis = []
time_stop_active = False
time_stop_activated_time = 0
flame_mode_active = False
flame_mode_activated_time = 0
ice_mode_active = False
ice_mode_activated_time = 0
draw_points = []  # Points for drawing lines

def reset_game():
    global game_over, score, lives, level, blocks, power_ups, chis, block_drop_speed, block_frequency, time_stop_active, flame_mode_active, ice_mode_active, draw_points
    game_over = False
    score = 0
    lives = 3
    level = 1
    blocks = []
    power_ups = []
    chis = []
    block_drop_speed = 2
    block_frequency = 2000
    time_stop_active = False
    flame_mode_active = False
    ice_mode_active = False
    draw_points = []

def add_chi():
    erratic_movement = level > 3 and random.choice([True, False])
    chi_speed = 1 + (level - chi_spawn_level) / 2 if level >= chi_spawn_level else 0
    chi = {
        "x": random.randint(0, SCREEN_WIDTH),
        "y": random.randint(0, SCREEN_HEIGHT),
        "speed": chi_speed,
        "size": 5 + (level - chi_spawn_level),
        "erratic": erratic_movement
    }
    chis.append(chi)

def update_chis():
    for chi in chis[:]:
        if chi["erratic"]:
            chi["x"] += random.choice([-3, 3])
            chi["y"] += random.choice([-3, 3])
        chi["x"] += random.choice([-1, 1]) * chi["speed"]
        chi["y"] += random.choice([-1, 1]) * chi["speed"]

        # Remove chi if it goes off-screen
      
def draw_chis():
    for chi in chis:
        pygame.draw.circle(screen, CHI_COLOR, (chi["x"], chi["y"]), chi["size"])

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def add_block():
    shape = random.choice(["square", "circle", "triangle", "boss"])
    size = random.randint(20, 40)
    if shape == "boss":
        size *= 2  # Bosses are bigger
    color = get_random_color()
    x_pos = random.randint(40, SCREEN_WIDTH - 40 - size)
    erratic = random.choice([True, False]) if level > 1 else False
    block = {"shape": shape, "size": size, "color": color, "x": x_pos, "y": 0, "erratic": erratic, "is_boss": shape == "boss"}
    blocks.append(block)

def draw_blocks():
    for block in blocks:
        if block["shape"] == "square" or block["shape"] == "boss":
            pygame.draw.rect(screen, block["color"], (block["x"], block["y"], block["size"], block["size"]))
        elif block["shape"] == "circle":
            pygame.draw.circle(screen, block["color"], (block["x"] + block["size"]//2, block["y"] + block["size"]//2), block["size"]//2)
        elif block["shape"] == "triangle":
            points = [
                (block["x"] + block["size"] // 2, block["y"]),
                (block["x"], block["y"] + block["size"]),
                (block["x"] + block["size"], block["y"] + block["size"])
            ]
            pygame.draw.polygon(screen, block["color"], points)

def add_power_up():
    types = ["flame", "time_stop", "ice"]
    type = random.choice(types)
    power_up = {
        "type": type,
        "x": random.randint(40, SCREEN_WIDTH - 40 - 20),
        "y": 0,
        "size": 20
    }
    power_ups.append(power_up)

def draw_power_ups():
    for power_up in power_ups:
        if power_up["type"] == "flame":
            pygame.draw.circle(screen, FLAME_COLOR, (power_up["x"] + power_up["size"]//2, power_up["y"] + power_up["size"]//2), power_up["size"]//2)
        elif power_up["type"] == "time_stop":
            pygame.draw.circle(screen, (0, 0, 255), (power_up["x"] + power_up["size"]//2, power_up["y"] + power_up["size"]//2), power_up["size"]//2)
        elif power_up["type"] == "ice":
            pygame.draw.circle(screen, ICE_COLOR, (power_up["x"] + power_up["size"]//2, power_up["y"] + power_up["size"]//2), power_up["size"]//2)

def activate_power_up(type):
    global time_stop_active, flame_mode_active, ice_mode_active, time_stop_activated_time, flame_mode_activated_time, ice_mode_activated_time
    if type == "flame":
        flame_mode_active = True
        flame_mode_activated_time = pygame.time.get_ticks()
    elif type == "time_stop":
        time_stop_active = True
        time_stop_activated_time = pygame.time.get_ticks()
    elif type == "ice":
        ice_mode_active = True
        ice_mode_activated_time = pygame.time.get_ticks()

def update_blocks():
    global score, lives, game_over
    for block in blocks[:]:
        if not time_stop_active:
            if block["erratic"] and random.randint(0, 1):
                block["x"] += random.choice([-5, 5])
            block["y"] += block_drop_speed

        # Check for game over condition
        if block["y"] > SCREEN_HEIGHT:
            blocks.remove(block)
            lives -= 1
            if lives <= 0:
                game_over = True

        # Check for collision with power-ups in flame mode
        if flame_mode_active and block["y"] >= SCREEN_HEIGHT / 2:
            blocks.remove(block)
            score += 1

def update_power_ups():
    for power_up in power_ups[:]:
        if not time_stop_active:
            power_up["y"] += block_drop_speed
        if power_up["y"] > SCREEN_HEIGHT:
            power_ups.remove(power_up)

def check_collisions():
    global score, lives, flame_mode_active, ice_mode_active, draw_points
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Update draw_points with current mouse position
    if pygame.mouse.get_pressed()[0]:  # If left mouse button is pressed
        draw_points.append((mouse_x, mouse_y))
        if len(draw_points) > 2:  # Keep the trail short
            draw_points = draw_points[-2:]
    else:
        draw_points = []

    for block in blocks[:]:
        block_center_x = block["x"] + block["size"] / 2
        block_center_y = block["y"] + block["size"] / 2
        for i in range(len(draw_points) - 1):
            if line_intersects_circle(draw_points[i], draw_points[i + 1], (block_center_x, block_center_y), block["size"] / 2):
                blocks.remove(block)
                score += 1
                if block["is_boss"]:
                    break  # Only count as one slash for bosses

    for power_up in power_ups[:]:
        power_up_center_x = power_up["x"] + power_up["size"] / 2
        power_up_center_y = power_up["y"] + power_up["size"] / 2
        for point in draw_points:
            if math.sqrt((point[0] - power_up_center_x)**2 + (point[1] - power_up_center_y)**2) < power_up["size"] / 2:
                power_ups.remove(power_up)
                activate_power_up(power_up["type"])
                break

def line_intersects_circle(p1, p2, center, radius):
    # Check if the line formed by points p1 and p2 intersects the circle with given center and radius
    a = (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2
    b = 2 * ((p2[0] - p1[0]) * (p1[0] - center[0]) + (p2[1] - p1[1]) * (p1[1] - center[1]))
    c = center[0]**2 + center[1]**2 + p1[0]**2 + p1[1]**2 - 2 * (center[0] * p1[0] + center[1] * p1[1]) - radius**2
    discriminant = b**2 - 4 * a * c
    return discriminant >= 0

def update_game_state():
    global block_frequency, block_drop_speed, level, score, game_over, time_stop_active, flame_mode_active, ice_mode_active
    if not game_over:
        # Increase difficulty
        if score > level * 10:
            level += 1
            block_drop_speed += 1
            block_frequency -= 100
            if block_frequency < 500:
                block_frequency = 500

        # Update power-up states
        if time_stop_active and pygame.time.get_ticks() - time_stop_activated_time > 5000:
            time_stop_active = False
        if flame_mode_active and pygame.time.get_ticks() - flame_mode_activated_time > 5000:
            flame_mode_active = False
        if ice_mode_active and pygame.time.get_ticks() - ice_mode_activated_time > 5000:
            ice_mode_active = False

def draw_interface():
    score_text = font.render("Score: " + str(score), True, WHITE)
    lives_text = font.render("Lives: " + str(lives), True, WHITE)
    level_text = font.render("Level: " + str(level), True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(level_text, (10, 70))

def draw_lines():
    if len(draw_points) > 1:
        pygame.draw.lines(screen, WHITE, False, draw_points, 5)

# Main game loop
last_block_added_time = pygame.time.get_ticks()
last_power_up_added_time = pygame.time.get_ticks()
last_chi_added_time = pygame.time.get_ticks()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    screen.fill(BLACK)

    # Add new blocks and power-ups at intervals
    if pygame.time.get_ticks() - last_block_added_time > block_frequency:
        add_block()
        last_block_added_time = pygame.time.get_ticks()

    if pygame.time.get_ticks() - last_power_up_added_time > block_frequency * 5:
        add_power_up()
        last_power_up_added_time = pygame.time.get_ticks()

    if level >= chi_spawn_level and (pygame.time.get_ticks() - last_chi_added_time > (5000 - level * 100)):
        add_chi()
        last_chi_added_time = pygame.time.get_ticks()

    draw_blocks()
    draw_power_ups()
    update_chis()
    draw_chis()
    check_collisions()
    update_blocks()
    update_power_ups()
    update_game_state()
    draw_interface()
    draw_lines()  # Draw the lines representing the cutting trail

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
