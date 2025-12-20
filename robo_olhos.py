import pygame
import sys
import random

# =========================================================
# INICIALIZAÇÃO
# =========================================================
pygame.init()

FPS = 60
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("RoboEyes - Responsive")

# =========================================================
# CORES
# =========================================================
BG_COLOR = (0, 0, 0)
EYE_COLOR = (4, 201, 253)
TEXT_COLOR = (100, 100, 100)

# =========================================================
# ESCALA PARA RESPONSIVIDADE
# =========================================================
BASE_WIDTH = 2560
BASE_HEIGHT = 1440
SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)

def sx(v): return int(v * SCALE)
def sy(v): return int(v * SCALE)

# =========================================================
# OLHOS
# =========================================================
EYE_WIDTH = sx(320 * 1.4)
EYE_HEIGHT = sy(320 * 1.4)
BLINK_MIN_HEIGHT = sy(8)
BORDER_RADIUS = sy(100)
EYE_Y_OFFSET = sy(-110)

LEFT_EYE_BASE_POS = (WIDTH // 3, HEIGHT // 2 + EYE_Y_OFFSET)
RIGHT_EYE_BASE_POS = (2 * WIDTH // 3, HEIGHT // 2 + EYE_Y_OFFSET)

# =========================================================
# ESTADOS
# =========================================================
STATE_NORMAL = "normal"
STATE_SLEEP = "sleep"
STATE_DIZZY = "dizzy"
state = STATE_NORMAL
sleeping = False

# =========================================================
# BLINK
# =========================================================
blink_progress = 0.0
blink_timer = 0
blink_interval = int(300 / SCALE)

BLINK_CLOSE_SPEED = 0.06
BLINK_OPEN_SPEED = 0.05

WAKE_BLINK_CLOSE_SPEED = 0.14
WAKE_BLINK_OPEN_SPEED = 0.18

space_held = False

# =========================================================
# OLHAR
LOOK_LEFT = sx(-300)
LOOK_CENTER = 0
LOOK_RIGHT = sx(300)

LOOK_SPEED = WAKE_BLINK_CLOSE_SPEED * 100  # igual a velocidade de acordar
look_offset = 0
look_target = LOOK_CENTER
last_look_target = None
look_timer = 0
LOOK_CHANGE_INTERVAL = int(160 / SCALE)

# =========================================================
# SLEEP
sleep_phase = "closing"
sleep_blink_count = 0
wake_blink_phase = "closing"
SLEEP_BLINKS = 2

# =========================================================
# DIZZY
left_eye_blink = 1.0
right_eye_blink = 1.0
DIZZY_OPEN_SPEED = 0.015
DIZZY_DELAY = int(40 / SCALE)
dizzy_timer = 0

# =========================================================
# FUNÇÕES
# =========================================================
def choose_random_look():
    global last_look_target
    options = [LOOK_LEFT, LOOK_CENTER, LOOK_RIGHT]
    if last_look_target in options:
        options.remove(last_look_target)
    last_look_target = random.choice(options)
    return last_look_target

def draw_eye(center_pos, blink_amount, look_offset):
    x, y = center_pos
    current_height = int(EYE_HEIGHT - (EYE_HEIGHT - BLINK_MIN_HEIGHT) * blink_amount)
    top_y = y - current_height // 2
    radius = 0 if current_height <= BLINK_MIN_HEIGHT + 2 else min(BORDER_RADIUS, current_height // 2)
    rect = pygame.Rect(int(x - EYE_WIDTH // 2 + look_offset), top_y, EYE_WIDTH, current_height)
    pygame.draw.rect(screen, EYE_COLOR, rect, border_radius=radius)

def update_blink():
    global blink_progress, blink_timer
    if space_held:
        blink_progress = min(blink_progress + BLINK_CLOSE_SPEED, 1)
        return
    blink_timer += 1
    if blink_timer >= blink_interval:
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress >= 1:
            blink_progress = 1
            blink_timer = 0
    if blink_timer < blink_interval and blink_progress > 0:
        blink_progress = max(blink_progress - BLINK_OPEN_SPEED, 0)

def update_look():
    global look_offset, look_target, look_timer
    look_timer += 1
    if look_timer >= LOOK_CHANGE_INTERVAL:
        look_target = choose_random_look()
        look_timer = 0
    if look_offset < look_target:
        look_offset = min(look_offset + LOOK_SPEED, look_target)
    elif look_offset > look_target:
        look_offset = max(look_offset - LOOK_SPEED, look_target)

def update_sleep():
    global blink_progress, sleep_phase, sleep_blink_count, wake_blink_phase, state
    if sleep_phase == "closing":
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress >= 1:
            blink_progress = 1
            sleep_phase = "sleeping"
    elif sleep_phase == "waking":
        blink_progress -= BLINK_OPEN_SPEED
        if blink_progress <= 0:
            blink_progress = 0
            sleep_phase = "blinking"
            sleep_blink_count = 0
            wake_blink_phase = "closing"
    elif sleep_phase == "blinking":
        if wake_blink_phase == "closing":
            blink_progress += WAKE_BLINK_CLOSE_SPEED
            if blink_progress >= 1:
                blink_progress = 1
                wake_blink_phase = "opening"
        else:
            blink_progress -= WAKE_BLINK_OPEN_SPEED
            if blink_progress <= 0:
                blink_progress = 0
                sleep_blink_count += 1
                wake_blink_phase = "closing"
        if sleep_blink_count >= SLEEP_BLINKS and not sleeping:
            state = STATE_NORMAL
            sleep_phase = "closing"

def update_dizzy():
    global left_eye_blink, right_eye_blink, dizzy_timer, state
    dizzy_timer += 1
    if left_eye_blink > 0:
        left_eye_blink = max(left_eye_blink - DIZZY_OPEN_SPEED, 0)
    if dizzy_timer > DIZZY_DELAY and right_eye_blink > 0:
        right_eye_blink = max(right_eye_blink - DIZZY_OPEN_SPEED, 0)
    if left_eye_blink <= 0 and right_eye_blink <= 0:
        state = STATE_NORMAL

def handle_events():
    global space_held, state, sleeping, sleep_phase, left_eye_blink, right_eye_blink, dizzy_timer
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_SPACE:
                space_held = True
            if event.key == pygame.K_s:
                if state != STATE_SLEEP:
                    state = STATE_SLEEP
                    sleeping = True
                    sleep_phase = "closing"
                else:
                    sleeping = False
                    sleep_phase = "waking"
            if event.key == pygame.K_t:
                state = STATE_DIZZY
                left_eye_blink = right_eye_blink = 1.0
                dizzy_timer = 0
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_held = False
    return True

def draw_help():
    font = pygame.font.Font(None, sy(24))
    txt = "SPACE: piscar | S: dormir/acordar | T: tonto | ESC: sair"
    screen.blit(font.render(txt, True, TEXT_COLOR), (sx(20), HEIGHT - sy(40)))

# =========================================================
# LOOP PRINCIPAL
# =========================================================
def main():
    running = True
    while running:
        running = handle_events()
        screen.fill(BG_COLOR)

        if state == STATE_NORMAL:
            update_blink()
            update_look()
            draw_eye(LEFT_EYE_BASE_POS, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_BASE_POS, blink_progress, look_offset)
        elif state == STATE_SLEEP:
            update_sleep()
            draw_eye(LEFT_EYE_BASE_POS, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_BASE_POS, blink_progress, look_offset)
        elif state == STATE_DIZZY:
            update_dizzy()
            draw_eye(LEFT_EYE_BASE_POS, left_eye_blink, look_offset)
            draw_eye(RIGHT_EYE_BASE_POS, right_eye_blink, look_offset)

        draw_help()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
