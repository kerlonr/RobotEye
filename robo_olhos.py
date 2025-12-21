import pygame
import sys
import random

# =========================================================
# INICIALIZAÇÃO
# =========================================================
pygame.init()
pygame.mouse.set_visible(False)

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
# OLHOS (PRÉ-CALCULADO)
# =========================================================
EYE_WIDTH = sx(640)  # 320 * 2
EYE_HEIGHT = sy(640)  # 320 * 2
BLINK_MIN_HEIGHT = sy(8)  # A LISTRINHA É AQUI!
BORDER_RADIUS = sy(150)
EYE_Y_OFFSET = sy(-150)

LEFT_EYE_BASE_X = WIDTH // 3
RIGHT_EYE_BASE_X = 2 * WIDTH // 3
EYE_Y = HEIGHT // 2 + EYE_Y_OFFSET

# Pré-calcular diferença de altura para evitar cálculo a cada frame
HEIGHT_DIFF = EYE_HEIGHT - BLINK_MIN_HEIGHT
HALF_EYE_WIDTH = EYE_WIDTH // 2

# =========================================================
# ESTADOS (USANDO INTEIROS PARA PERFORMANCE)
# =========================================================
STATE_NORMAL = 0
STATE_SLEEP = 1
STATE_DIZZY = 2
state = STATE_NORMAL
sleeping = False

# =========================================================
# BLINK
# =========================================================
blink_progress = 0.0
blink_timer = 0
blink_interval = max(1, int(300 / SCALE))

BLINK_CLOSE_SPEED = 0.09
BLINK_OPEN_SPEED = 0.08
WAKE_BLINK_CLOSE_SPEED = 0.14
WAKE_BLINK_OPEN_SPEED = 0.18

space_held = False

# =========================================================
# OLHAR
LOOK_LEFT = sx(-380)
LOOK_CENTER = 0
LOOK_RIGHT = sx(380)
LOOK_OPTIONS = [LOOK_LEFT, LOOK_CENTER, LOOK_RIGHT]

LOOK_SPEED = WAKE_BLINK_CLOSE_SPEED * 100
look_offset = 0.0
look_target = LOOK_CENTER
last_look_target = None
look_timer = 0
LOOK_CHANGE_INTERVAL = max(1, int(60 / SCALE))

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
DIZZY_DELAY = max(1, int(40 / SCALE))
dizzy_timer = 0

# =========================================================
# CACHE DE FONTE
# =========================================================
_font_cache = None
_font_size = 0

def get_font(size):
    global _font_cache, _font_size
    scaled_size = sy(size)
    if _font_cache is None or _font_size != scaled_size:
        _font_size = scaled_size
        _font_cache = pygame.font.Font(None, scaled_size)
    return _font_cache

# =========================================================
# FUNÇÕES OTIMIZADAS
# =========================================================
def choose_random_look():
    global last_look_target
    if last_look_target is None:
        return random.choice(LOOK_OPTIONS)
    
    # Filtrar a opção atual
    available = [opt for opt in LOOK_OPTIONS if opt != last_look_target]
    last_look_target = random.choice(available)
    return last_look_target

def draw_eye(x, y, blink_amount, look_offset):
    """Versão otimizada do draw_eye mantendo a listrinha"""
    # Cálculo da altura atual
    current_height = int(EYE_HEIGHT - HEIGHT_DIFF * blink_amount)
    
    # A MAGIA DA LISTRINHA: Sempre desenha mesmo quando pequeno
    # Isso garante que BLINK_MIN_HEIGHT seja respeitado
    if current_height <= 0:
        return
    
    top_y = y - (current_height // 2)
    
    # AQUI ESTÁ O SEGREDO DA LISTRINHA!
    # Quando a altura está perto do mínimo, border_radius = 0
    # Isso cria uma linha reta (a listrinha) em vez de bordas arredondadas
    if current_height <= BLINK_MIN_HEIGHT + 2:
        radius = 0  # LISTRINHA! Sem bordas arredondadas
    else:
        # Limita o border_radius à metade da altura ou BORDER_RADIUS
        radius = min(BORDER_RADIUS, current_height // 2)
    
    # Calcular posição X com look_offset
    rect_x = int(x - HALF_EYE_WIDTH + look_offset)
    
    # Desenhar o olho
    pygame.draw.rect(
        screen, 
        EYE_COLOR, 
        (rect_x, top_y, EYE_WIDTH, current_height), 
        border_radius=radius
    )

def update_blink():
    global blink_progress, blink_timer
    if space_held:
        blink_progress = min(blink_progress + BLINK_CLOSE_SPEED, 1.0)
        return
    
    blink_timer += 1
    if blink_timer >= blink_interval:
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress >= 1.0:
            blink_progress = 1.0
            blink_timer = 0
    elif blink_progress > 0.0:
        blink_progress = max(blink_progress - BLINK_OPEN_SPEED, 0.0)

def update_look():
    global look_offset, look_target, look_timer
    look_timer += 1
    if look_timer >= LOOK_CHANGE_INTERVAL:
        look_target = choose_random_look()
        look_timer = 0
    
    # Movimento suave
    if look_offset < look_target:
        look_offset = min(look_offset + LOOK_SPEED, look_target)
    elif look_offset > look_target:
        look_offset = max(look_offset - LOOK_SPEED, look_target)

def update_sleep():
    global blink_progress, sleep_phase, sleep_blink_count, wake_blink_phase, state
    if sleep_phase == "closing":
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress >= 1.0:
            blink_progress = 1.0
            sleep_phase = "sleeping"
    elif sleep_phase == "waking":
        blink_progress -= BLINK_OPEN_SPEED
        if blink_progress <= 0.0:
            blink_progress = 0.0
            sleep_phase = "blinking"
            sleep_blink_count = 0
            wake_blink_phase = "closing"
    elif sleep_phase == "blinking":
        if wake_blink_phase == "closing":
            blink_progress += WAKE_BLINK_CLOSE_SPEED
            if blink_progress >= 1.0:
                blink_progress = 1.0
                wake_blink_phase = "opening"
        else:
            blink_progress -= WAKE_BLINK_OPEN_SPEED
            if blink_progress <= 0.0:
                blink_progress = 0.0
                sleep_blink_count += 1
                wake_blink_phase = "closing"
        
        if sleep_blink_count >= SLEEP_BLINKS and not sleeping:
            state = STATE_NORMAL
            sleep_phase = "closing"

def update_dizzy():
    global left_eye_blink, right_eye_blink, dizzy_timer, state
    dizzy_timer += 1
    
    if left_eye_blink > 0.0:
        left_eye_blink = max(left_eye_blink - DIZZY_OPEN_SPEED, 0.0)
    
    if dizzy_timer > DIZZY_DELAY and right_eye_blink > 0.0:
        right_eye_blink = max(right_eye_blink - DIZZY_OPEN_SPEED, 0.0)
    
    if left_eye_blink <= 0.0 and right_eye_blink <= 0.0:
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
                left_eye_blink = 1.0
                right_eye_blink = 1.0
                dizzy_timer = 0
        
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            space_held = False
    
    return True

def draw_help():
    font = get_font(24)
    text = font.render("SPACE: piscar | S: dormir/acordar | T: tonto | ESC: sair", 
                       True, TEXT_COLOR)
    screen.blit(text, (sx(20), HEIGHT - sy(40)))

# =========================================================
# LOOP PRINCIPAL OTIMIZADO
# =========================================================
def main():
    running = True
    
    while running:
        running = handle_events()
        screen.fill(BG_COLOR)
        
        # Estado NORMAL
        if state == STATE_NORMAL:
            update_blink()
            update_look()
            draw_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
        
        # Estado SLEEP
        elif state == STATE_SLEEP:
            update_sleep()
            draw_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
        
        # Estado DIZZY
        elif state == STATE_DIZZY:
            update_dizzy()
            draw_eye(LEFT_EYE_BASE_X, EYE_Y, left_eye_blink, look_offset)
            draw_eye(RIGHT_EYE_BASE_X, EYE_Y, right_eye_blink, look_offset)
        
        draw_help()
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
