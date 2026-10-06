import math
import random
import pygame

pygame.init()

WIDTH = 800
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids - Sha Alam :P")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

WHITE = (235, 240, 250)
RED = (255, 100, 100)
YELLOW = (255, 215, 100)
GRAY = (85, 95, 120)
PANEL = (25, 32, 52)
ASTEROID_COLOR = (125, 145, 175)
CYAN = (100, 220, 235)

DETECTION_RANGE = 300
FOV_THRESHOLD = 0.7

ship_position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
ship_velocity = pygame.Vector2(0, 0)
ship_acceleration = pygame.Vector2(0, 0)
ship_angle = 90
ship_radius = 15

enemy_position = pygame.Vector2(WIDTH / 4, HEIGHT / 2)
enemy_angle = 0
ROTATION_SPEED = 3
THRUST = 0.1
DRAG = 0.99
MAX_SPEED = 7

missile_speed = 7
fire_delay = 100
last_fire_time = -fire_delay

asteroids = []
for number in range(6):
    radius = 20 + number * 3
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius, 300)
    angle = random.uniform(0, math.tau)
    speed = 2 + number * 0.5

    asteroids.append({
        "position": pygame.Vector2(x, y),
        "velocity": pygame.Vector2(math.cos(angle), math.sin(angle)) * speed,
        "radius": radius,
    })

missiles = []

# Slightly transparent panels keep the ship visible behind the HUD.
hud_panel = pygame.Surface((230, 62), pygame.SRCALPHA)
pygame.draw.rect(hud_panel, (25, 32, 52, 175), hud_panel.get_rect(), border_radius=8)
controls_panel = pygame.Surface((WIDTH - 20, 32), pygame.SRCALPHA)
pygame.draw.rect(controls_panel, (25, 32, 52, 175), controls_panel.get_rect(), border_radius=8)

# Small background stars make the space scene feel less empty.
stars = []
for number in range(70):
    stars.append((
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.choice([1, 1, 2]),
    ))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # LEFT/A and RIGHT/D change the spaceship's orientation.
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ship_angle += ROTATION_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ship_angle -= ROTATION_SPEED

    # Convert degrees to radians before using sine and cosine.
    radians = math.radians(ship_angle)

    # The negative sine accounts for Pygame's downward-increasing y-axis.
    forward = pygame.Vector2(
        math.cos(radians),
        -math.sin(radians),
    )

    # Thrust accelerates the ship instead of moving it directly.
    ship_acceleration = pygame.Vector2(0, 0)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        ship_acceleration = forward * THRUST

    ship_velocity += ship_acceleration
    ship_velocity *= DRAG
    if ship_velocity.length() > MAX_SPEED:
        ship_velocity.scale_to_length(MAX_SPEED)
    ship_position += ship_velocity

    # Wrap the spaceship around the screen edges.
    if ship_position.x > WIDTH:
        ship_position.x = 0
    if ship_position.x < 0:
        ship_position.x = WIDTH
    if ship_position.y > HEIGHT:
        ship_position.y = 0
    if ship_position.y < 0:
        ship_position.y = HEIGHT

    # Check whether the player is close enough and in front of the enemy.
    enemy_radians = math.radians(enemy_angle)
    enemy_forward = pygame.Vector2(
        math.cos(enemy_radians),
        -math.sin(enemy_radians),
    )
    to_player = ship_position - enemy_position
    distance = to_player.length()
    dot = 0
    detected = False

    if distance > 0:
        to_player = to_player.normalize()
        dot = enemy_forward.dot(to_player)
        if distance < DETECTION_RANGE and dot > FOV_THRESHOLD:
            detected = True

    enemy_state = "ATTACK" if detected else "PATROL"

    current_time = pygame.time.get_ticks()

    # SPACE fires a missile along the ship's current forward vector.
    if keys[pygame.K_SPACE] and current_time - last_fire_time >= fire_delay:
        missiles.append({
            "position": ship_position + forward * 22,
            "velocity": forward * missile_speed,
            "radius": 5,
        })
        last_fire_time = current_time

    for asteroid in asteroids:
        asteroid["position"] += asteroid["velocity"]

        if asteroid["position"].x < -asteroid["radius"]:
            asteroid["position"].x = WIDTH + asteroid["radius"]
        if asteroid["position"].x > WIDTH + asteroid["radius"]:
            asteroid["position"].x = -asteroid["radius"]
        if asteroid["position"].y < -asteroid["radius"]:
            asteroid["position"].y = HEIGHT + asteroid["radius"]
        if asteroid["position"].y > HEIGHT + asteroid["radius"]:
            asteroid["position"].y = -asteroid["radius"]

    for missile in missiles[:]:
        missile["position"] += missile["velocity"]

        if not screen.get_rect().collidepoint(missile["position"]):
            missiles.remove(missile)

    # Check every missile against every asteroid.
    for missile in missiles[:]:
        for asteroid in asteroids[:]:
            distance = missile["position"].distance_to(asteroid["position"])

            if distance < missile["radius"] + asteroid["radius"]:
                missiles.remove(missile)
                asteroids.remove(asteroid)
                break

    screen.fill((12, 16, 30))

    for star_x, star_y, star_size in stars:
        pygame.draw.circle(screen, (105, 125, 160), (star_x, star_y), star_size)

    # Draw the enemy's detection range and facing direction.
    pygame.draw.circle(
        screen,
        GRAY,
        enemy_position,
        DETECTION_RANGE,
        1,
    )
    enemy_color = RED if detected else WHITE
    enemy_left = enemy_forward.rotate(140)
    enemy_right = enemy_forward.rotate(-140)
    pygame.draw.polygon(
        screen,
        enemy_color,
        [
            enemy_position + enemy_forward * 22,
            enemy_position + enemy_left * 16,
            enemy_position + enemy_right * 16,
        ],
        2,
    )
    # Draw the spaceship as a triangle facing the forward vector.
    left = forward.rotate(140)
    right = forward.rotate(-140)
    p1 = ship_position + forward * 22
    p2 = ship_position + left * 16
    p3 = ship_position + right * 16
    pygame.draw.polygon(screen, WHITE, [p1, p2, p3], 2)

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        pygame.draw.circle(screen, YELLOW, ship_position - forward * 18, 5)

    for asteroid in asteroids:
        pygame.draw.circle(
            screen,
            ASTEROID_COLOR,
            asteroid["position"],
            asteroid["radius"],
        )

    for missile in missiles:
        pygame.draw.circle(
            screen,
            YELLOW,
            missile["position"],
            missile["radius"],
        )

    # Keep the game information grouped in see-through dark panels.
    screen.blit(hud_panel, (10, 10))
    screen.blit(controls_panel, (10, HEIGHT - 42))

    speed_text = font.render(f"Speed: {ship_velocity.length():.2f}", True, WHITE)
    phase_text = font.render(
        f"Enemy Phase: {enemy_state}",
        True,
        RED if detected else WHITE,
    )
    controls_text = font.render("Left/Right or A/D: rotate   Up/W: thrust   Space: fire", True, WHITE)
    screen.blit(speed_text, (15, 15))
    screen.blit(phase_text, (15, 42))
    screen.blit(controls_text, (15, HEIGHT - 32))

    pygame.display.flip()
    clock.tick(50)

pygame.quit()
