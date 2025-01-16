import pygame
import random
from pytmx import load_pygame

pygame.init()

tile_size = 32
map_width = 25
map_height = 26
screen_width = tile_size * map_width
screen_height = tile_size * map_height
screen = pygame.display.set_mode((screen_width, screen_height))

tmx_data = load_pygame("map/PAcmaznGame.tmx")

pacman_images = {
    "up": pygame.image.load("assets/pacman_haut.png"),
    "down": pygame.image.load("assets/pacman_bas.png"),
    "left": pygame.image.load("assets/pacman_gauche.png"),
    "right": pygame.image.load("assets/pacman.png"),
}
ghost_image = pygame.image.load("assets/ghost.png")
current_direction = "right"
pacman_image = pacman_images[current_direction]
pacman_rect = pacman_image.get_rect()

lives = 3
font = pygame.font.SysFont("Arial", 24)

def find_start_position():
    for obj in tmx_data.objects:
        if obj.name == 'start':
            return obj.x, obj.y
    return 100, 100

pacman_rect.topleft = find_start_position()

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

def find_ghost_positions():
    positions = []
    for obj in tmx_data.objects:
        if obj.name == 'startghost':
            positions.append((obj.x, obj.y))
    return positions

ghost_positions = find_ghost_positions()
ghosts = [{"rect": pygame.Rect(pos[0], pos[1], 32, 32), "direction": random.choice(list(DIRECTIONS.keys()))} for pos in ghost_positions]

def check_collision(rect):
    for obj in tmx_data.objects:
        if obj.name == 'murs' and hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'width') and hasattr(obj, 'height'):
            object_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            if rect.colliderect(object_rect):
                return True
    return False

def check_pacman_ghost_collision():
    global lives
    for ghost in ghosts:
        if pacman_rect.colliderect(ghost["rect"]):
            lives -= 1
            reset_pacman_position()

def reset_pacman_position():
    pacman_rect.topleft = find_start_position()

def move_pacman(keys):
    global pacman_image, current_direction

    new_x = pacman_rect.x
    new_y = pacman_rect.y

    if keys[pygame.K_LEFT]:
        new_x -= 1
        current_direction = "left"
    if keys[pygame.K_RIGHT]:
        new_x += 1
        current_direction = "right"
    if keys[pygame.K_UP]:
        new_y -= 1
        current_direction = "up"
    if keys[pygame.K_DOWN]:
        new_y += 1
        current_direction = "down"

    pacman_image = pacman_images[current_direction]

    if not check_collision(pygame.Rect(new_x, new_y, pacman_rect.width, pacman_rect.height)):
        pacman_rect.x = new_x
        pacman_rect.y = new_y
    
    check_teleport_collision()

just_teleported = False

def check_teleport_collision():
    global pacman_rect, just_teleported
    teleport_positions = find_teleport_positions()

    if just_teleported:
        for pos in teleport_positions:
            teleport_rect = pygame.Rect(pos[0], pos[1], tile_size, tile_size)
            if pacman_rect.colliderect(teleport_rect):
                return
        just_teleported = False
    
    for pos in teleport_positions:
        teleport_rect = pygame.Rect(pos[0], pos[1], tile_size, tile_size)
        if pacman_rect.colliderect(teleport_rect) and not just_teleported:
            index = teleport_positions.index(pos)
            next_index = (index + 1) % len(teleport_positions)
            pacman_rect.topleft = teleport_positions[next_index]
            just_teleported = True
            break

def find_teleport_positions():
    teleport_positions = []
    for obj in tmx_data.objects:
        if obj.name.startswith('teleportation'):
            teleport_positions.append((obj.x, obj.y))
    return teleport_positions

ghost_speed = 0.8

def move_ghost(ghost, speed=ghost_speed):
    direction = ghost["direction"]  
    dx, dy = DIRECTIONS[direction]
    new_x = ghost["rect"].x + dx * speed
    new_y = ghost["rect"].y + dy * speed

    if not check_collision(pygame.Rect(new_x, new_y, ghost["rect"].width, ghost["rect"].height)):
        ghost["rect"].x = new_x
        ghost["rect"].y = new_y
    else:
        opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
        valid_directions = [d for d in DIRECTIONS.keys() if d != opposite[direction]]
        ghost["direction"] = random.choice(valid_directions)

def draw_map():
    for layer in tmx_data.layers:
        if hasattr(layer, 'tiles'):
            for x, y, tile in layer.tiles():
                image = tmx_data.get_tile_image(x, y, tmx_data.layers.index(layer))
                if image:
                    screen.blit(image, (x * tile_size, y * tile_size))

def draw_lives():
    lives_text = font.render(f"Vie: {lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    move_pacman(keys)
    check_pacman_ghost_collision()

    for ghost in ghosts:
        move_ghost(ghost)

    screen.fill((0, 0, 0))

    draw_map()

    screen.blit(pacman_image, pacman_rect)

    for ghost in ghosts:
        screen.blit(ghost_image, ghost["rect"])

    draw_lives()

    pygame.display.flip()

pygame.quit()
