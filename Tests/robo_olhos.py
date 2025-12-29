import pygame
import sys
import random
import time

# =========================================================
# INICIALIZAÇÃO
# =========================================================
pygame.init()
pygame.mouse.set_visible(False)

FPS = 60
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("RoboEyes - Auto Animations")

# =========================================================
# CORES
# =========================================================
BG_COLOR = (0, 0, 0)
EYE_COLOR = (4, 201, 253)
TEXT_COLOR = (100, 100, 100)

# =========================================================
# ESCALA PARA RESPONSIVIDADE (CACHE)
# =========================================================
BASE_WIDTH = 2560
BASE_HEIGHT = 1440
SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)

_scale_cache = {}
def sx(v): 
    key = ('x', v)
    if key not in _scale_cache:
        _scale_cache[key] = int(v * SCALE)
    return _scale_cache[key]

def sy(v): 
    key = ('y', v)
    if key not in _scale_cache:
        _scale_cache[key] = int(v * SCALE)
    return _scale_cache[key]

# =========================================================
# OLHOS (PRÉ-CALCULADO)
# =========================================================
EYE_WIDTH = sx(640)
EYE_HEIGHT = sy(640)
BLINK_MIN_HEIGHT = sy(8)
BORDER_RADIUS = sy(300)
EYE_Y_OFFSET = sy(-150)

LEFT_EYE_BASE_X = WIDTH // 3
RIGHT_EYE_BASE_X = 2 * WIDTH // 3
EYE_Y = HEIGHT // 2 + EYE_Y_OFFSET

HEIGHT_DIFF = EYE_HEIGHT - BLINK_MIN_HEIGHT
HALF_EYE_WIDTH = EYE_WIDTH // 2

# =========================================================
# ESTADOS E ANIMAÇÕES AUTOMÁTICAS
# =========================================================
STATE_NORMAL = 0
STATE_SLEEP = 1
STATE_DIZZY = 2
STATE_HAPPY = 3
STATE_LAUGH = 4
STATE_ANGRY = 5

# Estados que podem ser ativados aleatoriamente
AUTO_STATES = [STATE_NORMAL, STATE_DIZZY, STATE_HAPPY, STATE_LAUGH, STATE_ANGRY]
state = STATE_NORMAL
sleeping = False

# Controle de animações automáticas
auto_animation_timer = 0
AUTO_ANIMATION_INTERVAL = 300  # 5 segundos em frames (300/60 = 5s)
last_auto_state = None

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
# SLEEP (CONTROLADO MANUALMENTE)
# =========================================================
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
# LAUGH (TEMPORÁRIO)
# =========================================================
laugh_start_time = 0
LAUGH_DURATION = 2.0  # segundos
laugh_phase = 0
laugh_direction = 1

# =========================================================
# ANGRY (PRÉ-CALCULADO)
# =========================================================
ANGRY_FADE_THRESHOLD = 0.7
ANGRY_BROW_HEIGHT = sy(160)
ANGRY_BROW_OFFSET_Y = sy(60)
ANGRY_BROW_WIDTH = EYE_WIDTH
ANGRY_BROW_THICKNESS = 120

# =========================================================
# CACHE DE FONTE E TEXTOS
# =========================================================
_font_cache = None
_font_size = 0
_help_text = None
_help_text_pos = (0, 0)

def init_text_cache():
    """Inicializa cache de texto uma vez"""
    global _help_text, _help_text_pos, _font_cache
    scaled_size = sy(24)
    _font_cache = pygame.font.Font(None, scaled_size)
    _help_text = _font_cache.render(
        "S: dormir/acordar | SPACE: piscar manual | ESC: sair (Animações automáticas ativas)", 
        True, TEXT_COLOR
    )
    _help_text_pos = (sx(20), HEIGHT - sy(40))

# =========================================================
# FUNÇÕES PARA ANIMAÇÕES AUTOMÁTICAS
# =========================================================
def choose_random_animation():
    """Escolhe uma animação aleatória, evitando repetir a última"""
    global last_auto_state
    
    available_states = [s for s in AUTO_STATES if s != last_auto_state]
    
    # Peso para estados (ajuste conforme preferência)
    weights = {
        STATE_NORMAL: 4,    # Mais frequente
        STATE_HAPPY: 3,
        STATE_DIZZY: 2,
        STATE_LAUGH: 2,
        STATE_ANGRY: 2
    }
    
    weighted_states = []
    for state in available_states:
        weight = weights.get(state, 1)
        weighted_states.extend([state] * weight)
    
    chosen = random.choice(weighted_states)
    last_auto_state = chosen
    return chosen

def update_auto_animation():
    """Atualiza o timer e muda animações automaticamente"""
    global auto_animation_timer, state, laugh_start_time
    
    if state == STATE_SLEEP:
        return  # Não muda animações enquanto dormindo
    
    auto_animation_timer += 1
    
    if auto_animation_timer >= AUTO_ANIMATION_INTERVAL:
        auto_animation_timer = 0
        
        # Se estiver rindo, não interromper
        if state == STATE_LAUGH:
            if time.time() - laugh_start_time < LAUGH_DURATION:
                return
        
        new_state = choose_random_animation()
        
        # Inicializar estado escolhido
        if new_state == STATE_DIZZY:
            state = STATE_DIZZY
            global left_eye_blink, right_eye_blink, dizzy_timer
            left_eye_blink = 1.0
            right_eye_blink = 1.0
            dizzy_timer = 0
        
        elif new_state == STATE_LAUGH:
            state = STATE_LAUGH
            laugh_start_time = time.time()
            global laugh_phase, laugh_direction
            laugh_phase = 0
            laugh_direction = 1
        
        else:
            state = new_state

# =========================================================
# FUNÇÕES OTIMIZADAS - OLHAR
# =========================================================
def choose_random_look():
    global last_look_target
    if last_look_target is None:
        last_look_target = random.choice(LOOK_OPTIONS)
    else:
        options = LOOK_OPTIONS[:]
        options.remove(last_look_target)
        last_look_target = random.choice(options)
    return last_look_target

# =========================================================
# DESENHO DE OLHOS OTIMIZADO
# =========================================================
def draw_eye(x, y, blink_amount, look_offset):
    """Olho normal otimizado"""
    current_height = int(EYE_HEIGHT - HEIGHT_DIFF * blink_amount)
    if current_height <= 0:
        return
    
    top_y = y - (current_height // 2)
    
    if current_height > BLINK_MIN_HEIGHT + 2:
        radius = BORDER_RADIUS if BORDER_RADIUS < (current_height // 2) else (current_height // 2)
    else:
        radius = 0
    
    rect_x = int(x - HALF_EYE_WIDTH + look_offset)
    pygame.draw.rect(
        screen, EYE_COLOR, 
        (rect_x, top_y, EYE_WIDTH, current_height), 
        border_radius=radius
    )

def draw_happy_eye(x, y, blink_amount, look_offset):
    """Olho feliz otimizado"""
    current_height = int(EYE_HEIGHT - HEIGHT_DIFF * blink_amount)
    if current_height <= 0:
        return
    
    top_y = y - (current_height // 2)
    radius = min(BORDER_RADIUS, current_height * 2)
    rect_x = int(x - HALF_EYE_WIDTH + look_offset)
    
    pygame.draw.rect(
        screen, EYE_COLOR, 
        (rect_x, top_y, EYE_WIDTH, current_height), 
        border_radius=radius
    )
    
    pygame.draw.line(
        screen, BG_COLOR, 
        (rect_x, top_y), 
        (rect_x + EYE_WIDTH, top_y), 
        3
    )
    
    black_height = max(1, int(current_height * 0.2))
    black_rect = (
        rect_x, 
        top_y + current_height - black_height, 
        EYE_WIDTH, 
        black_height * 3
    )
    pygame.draw.ellipse(screen, BG_COLOR, black_rect)

def draw_laugh_eye(x, y, blink_amount, look_offset, laugh_phase):
    """Olho rindo otimizado"""
    current_height = int(EYE_HEIGHT - HEIGHT_DIFF * blink_amount)
    if current_height <= 0:
        return
    
    top_y = y - (current_height // 2) + laugh_phase
    radius = min(BORDER_RADIUS, current_height * 2)
    rect_x = int(x - HALF_EYE_WIDTH + look_offset)
    
    pygame.draw.rect(
        screen, EYE_COLOR, 
        (rect_x, top_y, EYE_WIDTH, current_height), 
        border_radius=radius
    )
    
    pygame.draw.line(
        screen, BG_COLOR, 
        (rect_x, top_y), 
        (rect_x + EYE_WIDTH, top_y), 
        3
    )
    
    black_height = max(1, int(current_height * 0.2))
    black_rect = (
        rect_x, 
        top_y + current_height - black_height, 
        EYE_WIDTH, 
        black_height * 3
    )
    pygame.draw.ellipse(screen, BG_COLOR, black_rect)

def draw_angry_eye(x, y, blink_amount, look_offset, side="left"):
    """Olho bravo otimizado"""
    rect_x = int(x - HALF_EYE_WIDTH + look_offset)
    current_height = int(EYE_HEIGHT - HEIGHT_DIFF * blink_amount)
    
    if blink_amount < ANGRY_FADE_THRESHOLD:
        top_y = y - (current_height // 2)
        
        if current_height > BLINK_MIN_HEIGHT + 2:
            radius = BORDER_RADIUS if BORDER_RADIUS < (current_height // 2) else (current_height // 2)
        else:
            radius = 0
        
        pygame.draw.rect(
            screen, EYE_COLOR, 
            (rect_x, top_y, EYE_WIDTH, current_height), 
            border_radius=radius
        )
        
        brow_start_y = top_y - ANGRY_BROW_OFFSET_Y
        if side == "left":
            start_pos = (rect_x, brow_start_y)
            end_pos = (rect_x + ANGRY_BROW_WIDTH, brow_start_y + ANGRY_BROW_HEIGHT)
        else:
            start_pos = (rect_x + EYE_WIDTH, brow_start_y)
            end_pos = (rect_x + EYE_WIDTH - ANGRY_BROW_WIDTH, brow_start_y + ANGRY_BROW_HEIGHT)
        
        pygame.draw.line(
            screen, BG_COLOR, 
            start_pos, end_pos, 
            ANGRY_BROW_THICKNESS
        )
    
    if blink_amount >= ANGRY_FADE_THRESHOLD:
        t = (blink_amount - ANGRY_FADE_THRESHOLD) / (1.0 - ANGRY_FADE_THRESHOLD)
        line_height = max(4, int(4 * t))
        line_y = y - (line_height // 2)
        
        pygame.draw.rect(
            screen, EYE_COLOR, 
            (rect_x, line_y, EYE_WIDTH, line_height)
        )

# =========================================================
# ATUALIZAÇÕES DE ESTADO
# =========================================================
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
    
    diff = look_target - look_offset
    if abs(diff) < LOOK_SPEED:
        look_offset = look_target
    elif diff > 0:
        look_offset += LOOK_SPEED
    else:
        look_offset -= LOOK_SPEED

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

# =========================================================
# HANDLER DE EVENTOS
# =========================================================
def handle_events():
    global space_held, state, sleeping, sleep_phase, left_eye_blink, right_eye_blink, dizzy_timer, laugh_start_time, laugh_phase, laugh_direction
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        if event.type == pygame.KEYDOWN:
            key = event.key
            
            if key == pygame.K_ESCAPE:
                return False
            
            elif key == pygame.K_SPACE:
                space_held = True
            
            elif key == pygame.K_s:
                if state != STATE_SLEEP:
                    state = STATE_SLEEP
                    sleeping = True
                    sleep_phase = "closing"
                    # Resetar animação automática quando dormir
                    global auto_animation_timer
                    auto_animation_timer = 0
                else:
                    sleeping = False
                    sleep_phase = "waking"
        
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            space_held = False
    
    return True

# =========================================================
# LOOP PRINCIPAL
# =========================================================
def main():
    global state, laugh_start_time, laugh_phase, laugh_direction
    
    # Inicializar cache de texto
    init_text_cache()
    
    running = True
    while running:
        running = handle_events()
        screen.fill(BG_COLOR)
        
        # Atualizar animação automática (exceto quando dormindo)
        update_auto_animation()
        
        # Estado NORMAL
        if state == STATE_NORMAL:
            update_blink()
            update_look()
            draw_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
        
        # Estado SLEEP (controlado apenas por S)
        elif state == STATE_SLEEP:
            update_sleep()
            draw_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
        
        # Estado DIZZY
        elif state == STATE_DIZZY:
            update_dizzy()
            draw_eye(LEFT_EYE_BASE_X, EYE_Y, left_eye_blink, look_offset)
            draw_eye(RIGHT_EYE_BASE_X, EYE_Y, right_eye_blink, look_offset)
        
        # Estado HAPPY
        elif state == STATE_HAPPY:
            update_blink()
            update_look()
            draw_happy_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
            draw_happy_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset)
        
        # Estado LAUGH
        elif state == STATE_LAUGH:
            update_blink()
            update_look()
            
            # Animação de riso
            laugh_phase += 15 * laugh_direction
            if laugh_phase > 30 or laugh_phase < -30:
                laugh_direction *= -1
            
            draw_laugh_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset, laugh_phase)
            draw_laugh_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset, laugh_phase)
            
            # Checar duração do riso
            if time.time() - laugh_start_time > LAUGH_DURATION:
                state = STATE_HAPPY
                laugh_phase = 0
        
        # Estado ANGRY
        elif state == STATE_ANGRY:
            update_blink()
            update_look()
            draw_angry_eye(LEFT_EYE_BASE_X, EYE_Y, blink_progress, look_offset, "left")
            draw_angry_eye(RIGHT_EYE_BASE_X, EYE_Y, blink_progress, look_offset, "right")
        
        # Desenhar ajuda
        screen.blit(_help_text, _help_text_pos)
        
        # Atualizar display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
