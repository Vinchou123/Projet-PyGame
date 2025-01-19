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
piece_image = pygame.image.load("assets/pieces.png")
bop_sound = pygame.mixer.Sound("sounds/bop.wav")
pacman_death_sound = pygame.mixer.Sound("sounds/pacman_death.wav")



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

ghost_images = {
    "blue": pygame.image.load("assets/ghost_blue.png"),
    "orange": pygame.image.load("assets/ghost_orange.png"),
    "pink": pygame.image.load("assets/ghost_pink.png"),
    "red": pygame.image.load("assets/ghost_red.png"),
}

def find_new_ghost_positions():
    positions = []
    for obj in tmx_data.objects:
        if obj.name == 'ghostprison':
            positions.append((obj.x, obj.y))
    return positions

ghost_images_list = [ghost_images["blue"], ghost_images["orange"], ghost_images["pink"], ghost_images["red"]]

new_ghost_positions = find_new_ghost_positions()
new_ghosts = [
    {"rect": pygame.Rect(pos[0], pos[1], 32, 32), "direction": random.choice(list(DIRECTIONS.keys())), "image": ghost_images_list[i]}
    for i, pos in enumerate(new_ghost_positions)
]

ghosts.extend(new_ghosts)

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

pacman_speed = 0.6

def move_pacman(keys):
    global pacman_image, current_direction

    new_x = pacman_rect.x
    new_y = pacman_rect.y

    if keys[pygame.K_LEFT]:
        new_x -= pacman_speed
        current_direction = "left"
    if keys[pygame.K_RIGHT]:
        new_x += pacman_speed
        current_direction = "right"
    if keys[pygame.K_UP]:
        new_y -= pacman_speed
        current_direction = "up"
    if keys[pygame.K_DOWN]:
        new_y += pacman_speed  
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
prison_ghost_speed = 0.001 

def move_ghost(ghost, speed=ghost_speed):
    direction = ghost["direction"]
    dx, dy = DIRECTIONS[direction]
    new_x = ghost["rect"].x + dx * speed
    new_y = ghost["rect"].y + dy * speed

    for prison in new_ghost_positions:
        prison_rect = pygame.Rect(prison[0], prison[1], tile_size, tile_size)
        if prison_rect.colliderect(ghost["rect"]):
            speed = prison_ghost_speed
            break

    if not check_collision(pygame.Rect(new_x, new_y, ghost["rect"].width, ghost["rect"].height)):
        ghost["rect"].x = new_x
        ghost["rect"].y = new_y
    else:
        opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
        valid_directions = [d for d in DIRECTIONS.keys() if d != opposite[direction]]
        ghost["direction"] = random.choice(valid_directions)

def move_all_ghosts():
    for ghost in ghosts:
        move_ghost(ghost)

def draw_map():
    for layer in tmx_data.layers:
        if hasattr(layer, 'tiles'):
            for x, y, tile in layer.tiles():
                image = tmx_data.get_tile_image(x, y, tmx_data.layers.index(layer))
                if image:
                    screen.blit(image, (x * tile_size, y * tile_size))

def draw_lives_and_score():
    """Affiche le nombre de vies et le score à l'écran."""
    lives_text = font.render(f"Vie: {lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 15))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (360, 15))
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_text = font.render(f"Temps: {minutes:02}:{seconds:02}", True, (255, 255, 255))
    screen.blit(time_text, (670, 15))

def find_piece_positions():
    pieces = []
    for obj in tmx_data.objects:
        if obj.name == 'piece':
            pieces.append((obj.x, obj.y))
    return pieces

piece_positions = find_piece_positions()

def draw_pieces():
    for pos in piece_positions:
        screen.blit(piece_image, pos)

score = 0
start_time = pygame.time.get_ticks()

def check_piece_collision():
    """Vérifie les collisions entre Pac-Man et les pièces."""
    global piece_positions, score
    new_positions = []
    for pos in piece_positions:
        piece_rect = pygame.Rect(pos[0], pos[1], piece_image.get_width(), piece_image.get_height())
        if pacman_rect.colliderect(piece_rect):
            score += 1
            bop_sound.play()
        else:
            new_positions.append(pos)
    piece_positions = new_positions

    

def check_pacman_ghost_collision():
    global lives
    for ghost in ghosts:
        if pacman_rect.colliderect(ghost["rect"]):
            lives -= 1
            reset_pacman_position()
            pacman_death_sound.play()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    move_pacman(keys)
    check_pacman_ghost_collision()
    check_piece_collision()
    move_all_ghosts()
    screen.fill((0, 0, 0))
    draw_map()
    draw_pieces()
    screen.blit(pacman_image, pacman_rect)

    for ghost in ghosts:
        if "image" not in ghost:
            ghost["image"] = ghost_image
        screen.blit(ghost["image"], ghost["rect"])

    draw_lives_and_score()
    
    pygame.mixer.init()

    pygame.display.flip()

pygame.quit()
