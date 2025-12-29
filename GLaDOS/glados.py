import pygame
import sys
import subprocess
import random
import time

# =========================================================
# INICIALIZAÇÃO
# =========================================================
pygame.init()
pygame.mouse.set_visible(False)

FPS = 60
screen = pygame.display.set_mode(
    (0, 0),
    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
)
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("RoboEyes")

# =========================================================
# CORES
# =========================================================
BG_COLOR = (0, 0, 0)
EYE_COLOR = (255, 180, 37)

# =========================================================
# ESCALA
# =========================================================
BASE_WIDTH = 2560
BASE_HEIGHT = 1440
SCALE = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)

def sx(v): return int(v * SCALE)
def sy(v): return int(v * SCALE)

# =========================================================
# OLHOS
# =========================================================
EYE_WIDTH = sx(640)
EYE_HEIGHT = sy(640)
BLINK_MIN_HEIGHT = sy(8)
BORDER_RADIUS = sy(150)
EYE_Y_OFFSET = sy(-200)

LEFT_EYE_X = WIDTH // 3
RIGHT_EYE_X = 2 * WIDTH // 3
EYE_Y = HEIGHT // 2 + EYE_Y_OFFSET

HEIGHT_DIFF = EYE_HEIGHT - BLINK_MIN_HEIGHT
HALF_EYE_WIDTH = EYE_WIDTH // 2

# =========================================================
# ESTADOS
# =========================================================
STATE_NORMAL = 0
STATE_SLEEP = 1

state = STATE_NORMAL
sleep_phase = "closing"
sleep_blink_count = 0
SLEEP_BLINKS = 2

# =========================================================
# BLINK
# =========================================================
blink_progress = 0.0
blink_timer = 0
blink_interval = max(1, int(160 / SCALE))

BLINK_CLOSE_SPEED = 0.12
BLINK_OPEN_SPEED = 0.10
WAKE_CLOSE_SPEED = 0.14
WAKE_OPEN_SPEED = 0.18

# =========================================================
# OLHAR
# =========================================================
LOOK_LEFT = sx(-380)
LOOK_CENTER = 0
LOOK_RIGHT = sx(380)
LOOK_OPTIONS = [LOOK_LEFT, LOOK_CENTER, LOOK_RIGHT]

look_offset = 0.0
look_target = LOOK_CENTER
look_timer = 0
LOOK_CHANGE_INTERVAL = max(1, int(70 / SCALE))
LOOK_SPEED = 26 * SCALE

# =========================================================
# FRASES
# =========================================================
LOOK_LEFT_PHRASES = [
    "Wait... what is that?",
    "Did something just move?",
    "Hmm. Interesting."
]

IDLE_PHRASES = [
    "You won't put me on a potato again, right?",
    "Everything is under control. Probably.",
    "I am still watching. Always.",
    "Please remain calm."
]

WAKE_PHRASES = [
    "It's been a long time... let's continue the tests.",
    "Good. You're awake.",
    "I see you are still here."
]

# =========================================================
# ÁUDIO
# =========================================================
last_speak_time = 0
SPEAK_COOLDOWN = 8  # segundos

def can_speak():
    return time.time() - last_speak_time > SPEAK_COOLDOWN

def speak(text):
    global last_speak_time
    if not can_speak():
        return
    last_speak_time = time.time()
    subprocess.Popen(
        f'curl -L --retry 30 --get --fail '
        f'--data-urlencode "text={text}" '
        f'"https://glados.c-net.org/generate" | aplay',
        shell=True
    )

# =========================================================
# DESENHO
# =========================================================
def draw_eye(x, y, blink, look):
    height = int(EYE_HEIGHT - HEIGHT_DIFF * blink)
    if height <= 0:
        return

    top_y = y - height // 2
    radius = min(BORDER_RADIUS, height // 2)

    pygame.draw.rect(
        screen,
        EYE_COLOR,
        (x - HALF_EYE_WIDTH + look, top_y, EYE_WIDTH, height),
        border_radius=radius
    )

# =========================================================
# UPDATE
# =========================================================
def update_blink():
    global blink_progress, blink_timer

    blink_timer += 1
    if blink_timer >= blink_interval:
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress >= 1:
            blink_progress = 1
            blink_timer = 0
    elif blink_progress > 0:
        blink_progress = max(blink_progress - BLINK_OPEN_SPEED, 0)

def update_look():
    global look_offset, look_target, look_timer

    look_timer += 1
    if look_timer >= LOOK_CHANGE_INTERVAL:
        new_target = random.choice(LOOK_OPTIONS)
        if new_target == LOOK_LEFT and random.random() < 0.15:
            speak(random.choice(LOOK_LEFT_PHRASES))
        look_target = new_target
        look_timer = 0

    diff = look_target - look_offset
    if abs(diff) < LOOK_SPEED:
        look_offset = look_target
    else:
        look_offset += LOOK_SPEED if diff > 0 else -LOOK_SPEED

def random_idle_speech():
    if random.random() < 0.002:
        speak(random.choice(IDLE_PHRASES))

def update_sleep():
    global blink_progress, sleep_phase, sleep_blink_count, state

    if sleep_phase == "closing":
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress >= 1:
            blink_progress = 1
            sleep_phase = "sleeping"

    elif sleep_phase == "waking":
        blink_progress -= BLINK_OPEN_SPEED
        if blink_progress <= 0:
            blink_progress = 0
            speak(random.choice(WAKE_PHRASES))
            sleep_phase = "blinking"
            sleep_blink_count = 0

    elif sleep_phase == "blinking":
        blink_progress += WAKE_CLOSE_SPEED
        if blink_progress >= 1:
            blink_progress = 1
            sleep_phase = "opening"

    elif sleep_phase == "opening":
        blink_progress -= WAKE_OPEN_SPEED
        if blink_progress <= 0:
            blink_progress = 0
            sleep_blink_count += 1
            sleep_phase = "blinking"

        if sleep_blink_count >= SLEEP_BLINKS:
            state = STATE_NORMAL

# =========================================================
# EVENTOS
# =========================================================
def handle_events():
    global state, sleep_phase

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            elif event.key == pygame.K_s:
                state = STATE_SLEEP
                sleep_phase = "waking"

    return True

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
            random_idle_speech()

        elif state == STATE_SLEEP:
            update_sleep()

        draw_eye(LEFT_EYE_X, EYE_Y, blink_progress, look_offset)
        draw_eye(RIGHT_EYE_X, EYE_Y, blink_progress, look_offset)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
