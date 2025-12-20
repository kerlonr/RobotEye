import pygame
import sys
import random

# =========================================================
# INICIALIZAÇÃO
# =========================================================
pygame.init()

# =========================================================
# JANELA (SEM FULLSCREEN – X11 SAFE)
# =========================================================
FPS = 60
WIDTH, HEIGHT = 800, 480   # ajuste para o seu LCD
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Eyes")

clock = pygame.time.Clock()

# =========================================================
# CORES
# =========================================================
BG_COLOR = (0, 0, 0)
EYE_COLOR = (4, 201, 253)
TEXT_COLOR = (120, 120, 120)

# =========================================================
# OLHOS
# =========================================================
EYE_WIDTH = 260
EYE_HEIGHT = 260
BLINK_MIN_HEIGHT = 8
BORDER_RADIUS = 80
EYE_Y_OFFSET = -40

LEFT_EYE_POS = (WIDTH // 3, HEIGHT // 2 + EYE_Y_OFFSET)
RIGHT_EYE_POS = (2 * WIDTH // 3, HEIGHT // 2 + EYE_Y_OFFSET)

# =========================================================
# ESTADOS
# =========================================================
STATE_NORMAL = "normal"
STATE_SLEEP = "sleep"
state = STATE_NORMAL
sleeping = False

# =========================================================
# BLINK
# =========================================================
blink = 0.0
BLINK_CLOSE = 0.10
BLINK_OPEN = 0.08
blink_timer = 0
BLINK_INTERVAL = 180

# =========================================================
# OLHAR
# =========================================================
LOOK_LEFT = -120
LOOK_CENTER = 0
LOOK_RIGHT = 120

look_offset = 0
look_target = 0
LOOK_SPEED = 4
look_timer = 0
LOOK_INTERVAL = 140

# =========================================================
# CRT – SCANLINES HORIZONTAIS
# =========================================================
SCANLINE_ALPHA = 30

def draw_scanlines():
    line = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
    line.fill((0, 0, 0, SCANLINE_ALPHA))
    for y in range(0, HEIGHT, 4):
        screen.blit(line, (0, y))

# =========================================================
# FUNÇÕES
# =========================================================
def draw_eye(center, blink_amount, look_x):
    x, y = center
    h = int(EYE_HEIGHT - (EYE_HEIGHT - BLINK_MIN_HEIGHT) * blink_amount)
    rect = pygame.Rect(
        x - EYE_WIDTH // 2 + look_x,
        y - h // 2,
        EYE_WIDTH,
        h
    )
    radius = 0 if h <= BLINK_MIN_HEIGHT + 2 else min(BORDER_RADIUS, h // 2)
    pygame.draw.rect(screen, EYE_COLOR, rect, border_radius=radius)

def update_blink():
    global blink, blink_timer

    blink_timer += 1

    if blink_timer > BLINK_INTERVAL:
        blink += BLINK_CLOSE
        if blink >= 1:
            blink = 1
            blink_timer = 0

    elif blink > 0:
        blink = max(blink - BLINK_OPEN, 0)

def update_look():
    global look_offset, look_target, look_timer

    look_timer += 1
    if look_timer > LOOK_INTERVAL:
        look_target = random.choice([LOOK_LEFT, LOOK_CENTER, LOOK_RIGHT])
        look_timer = 0

    if look_offset < look_target:
        look_offset += LOOK_SPEED
    elif look_offset > look_target:
        look_offset -= LOOK_SPEED

def handle_events():
    global state, sleeping
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            return False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return False
            if e.key == pygame.K_s:
                sleeping = not sleeping
                state = STATE_SLEEP if sleeping else STATE_NORMAL
    return True

def draw_help():
    font = pygame.font.Font(None, 24)
    text = "S: dormir/acordar | ESC: sair"
    screen.blit(font.render(text, True, TEXT_COLOR), (20, HEIGHT - 30))

# =========================================================
# LOOP PRINCIPAL
# =========================================================
def main():
    global blink

    running = True
    while running:
        running = handle_events()
        screen.fill(BG_COLOR)

        if state == STATE_NORMAL:
            update_blink()
            update_look()

        elif state == STATE_SLEEP:
            blink = min(blink + BLINK_CLOSE, 1)

        draw_eye(LEFT_EYE_POS, blink, look_offset)
        draw_eye(RIGHT_EYE_POS, blink, look_offset)

        draw_scanlines()
        draw_help()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
