import pygame, sys, random
pygame.init()

FPS = 60
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()

# cores
BG_COLOR = (0,0,0)
EYE_COLOR = (4,201,253)
TEXT_COLOR = (100,100,100)

# olhos
EYE_W, EYE_H = 450, 450
BLINK_MIN_H = 10
EYE_Y_OFFSET = -120
LEFT_EYE_POS = (WIDTH//2 - 350, HEIGHT//2 + EYE_Y_OFFSET)
RIGHT_EYE_POS = (WIDTH//2 + 350, HEIGHT//2 + EYE_Y_OFFSET)

# estados
STATE_NORMAL, STATE_SLEEP, STATE_DIZZY = "normal","sleep","dizzy"
state = STATE_NORMAL
sleeping = False

# blink
blink_progress = 0.0
blink_timer = 0
blink_interval = 300
BLINK_CLOSE_SPEED = 0.06
BLINK_OPEN_SPEED = 0.05
space_held = False

# olhar
LOOK_LEFT, LOOK_CENTER, LOOK_RIGHT = -300,0,300
LOOK_SPEED = 6
look_offset = 0
look_target = LOOK_CENTER
last_look_target = None
look_timer = 0
LOOK_CHANGE_INTERVAL = 160

# sleep/dizzy
sleep_phase="closing"
sleep_blink_count=0
wake_blink_phase="closing"
SLEEP_BLINKS=2
left_eye_blink=right_eye_blink=1.0
DIZZY_OPEN_SPEED=0.015
DIZZY_DELAY=40
dizzy_timer=0

# cache de olhos
eye_cache = {}

def get_eye_surface(blink):
    key = round(blink,2)
    if key in eye_cache:
        return eye_cache[key]

    surf = pygame.Surface((EYE_W, EYE_H), pygame.SRCALPHA)
    h = int(EYE_H - (EYE_H-BLINK_MIN_H)*blink)
    radius = 50  # border radius
    rect_h = h - radius*2
    pygame.draw.rect(surf, EYE_COLOR, (0,radius,EYE_W,rect_h))
    pygame.draw.circle(surf, EYE_COLOR, (radius, radius), radius)
    pygame.draw.circle(surf, EYE_COLOR, (EYE_W-radius, radius), radius)
    pygame.draw.circle(surf, EYE_COLOR, (radius, h-radius), radius)
    pygame.draw.circle(surf, EYE_COLOR, (EYE_W-radius, h-radius), radius)

    eye_cache[key]=surf
    return surf

def draw_eye(pos, blink, look):
    x,y = pos
    eye = get_eye_surface(blink)
    screen.blit(eye, (int(x - EYE_W//2 + look), int(y - EYE_H//2)))

def choose_random_look():
    global last_look_target
    options = [LOOK_LEFT, LOOK_CENTER, LOOK_RIGHT]
    if last_look_target in options: options.remove(last_look_target)
    last_look_target = random.choice(options)
    return last_look_target

def update_blink():
    global blink_progress, blink_timer
    if space_held: blink_progress = min(blink_progress+BLINK_CLOSE_SPEED,1); return
    blink_timer += 1
    if blink_timer >= blink_interval:
        blink_progress += BLINK_CLOSE_SPEED
        if blink_progress>=1: blink_progress=1; blink_timer=0
    if blink_timer<blink_interval and blink_progress>0:
        blink_progress=max(blink_progress-BLINK_OPEN_SPEED,0)

def update_look():
    global look_offset, look_target, look_timer
    look_timer += 1
    if look_timer>=LOOK_CHANGE_INTERVAL:
        look_target = choose_random_look(); look_timer=0
    if look_offset<look_target: look_offset=min(look_offset+LOOK_SPEED,look_target)
    elif look_offset>look_target: look_offset=max(look_offset-LOOK_SPEED,look_target)

def handle_events():
    global space_held,state,sleeping,sleep_phase,left_eye_blink,right_eye_blink,dizzy_timer
    for e in pygame.event.get():
        if e.type==pygame.QUIT: return False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE: return False
            if e.key==pygame.K_SPACE: space_held=True
            if e.key==pygame.K_s:
                if state!=STATE_SLEEP: state=STATE_SLEEP; sleeping=True; sleep_phase="closing"
                else: sleeping=False; sleep_phase="waking"
            if e.key==pygame.K_t: state=STATE_DIZZY; left_eye_blink=right_eye_blink=1.0; dizzy_timer=0
        if e.type==pygame.KEYUP:
            if e.key==pygame.K_SPACE: space_held=False
    return True

def draw_help():
    font=pygame.font.Font(None,24)
    screen.blit(font.render("SPACE: piscar | S: dormir | T: tonto | ESC: sair",True,TEXT_COLOR),(20,HEIGHT-40))

def main():
    global blink_progress, left_eye_blink,right_eye_blink,look_offset
    running=True
    while running:
        running=handle_events()
        screen.fill(BG_COLOR)

        if state==STATE_NORMAL:
            update_blink(); update_look()
            draw_eye(LEFT_EYE_POS, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_POS, blink_progress, look_offset)
        elif state==STATE_SLEEP:
            draw_eye(LEFT_EYE_POS, blink_progress, look_offset)
            draw_eye(RIGHT_EYE_POS, blink_progress, look_offset)
        elif state==STATE_DIZZY:
            left_eye_blink = max(left_eye_blink-DIZZY_OPEN_SPEED,0)
            dizzy_timer += 1
            if dizzy_timer>DIZZY_DELAY: right_eye_blink = max(right_eye_blink-DIZZY_OPEN_SPEED,0)
            draw_eye(LEFT_EYE_POS,left_eye_blink,look_offset)
            draw_eye(RIGHT_EYE_POS,right_eye_blink,look_offset)

        draw_help()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
