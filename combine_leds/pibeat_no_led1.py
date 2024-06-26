import RPi.GPIO as GPIO
import pygame, pigame
from pygame.locals import *
import os
from time import sleep
import time
import board
import adafruit_mma8451
from adafruit_mma8451 import PL_PUF, PL_PUB, PL_PDF, PL_PDB, PL_LRF, PL_LRB, PL_LLF, PL_LLB
import random


code_run = True
starttime = time.time()


# set colors
BLACK = 0,0,0
RED = 255,0,0
GREEN = 0,255,0
WHITE = 255,255,255

# run on piTFT
os.putenv('SDL_VIDEODRV','fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV','dummy')
os.putenv('SDL_MOUSEDEV','/dev/null')
os.putenv('DISPLAY','')

pygame.init()
pygame.mouse.set_visible(False)
pitft = pigame.PiTft()

# set screen dimensions
size = width, height = 320, 240
lcd = pygame.display.set_mode((width, height))
lcd.fill((0,0,0))
pygame.display.update()

# load graphics
get_started_button = pygame.image.load("graphics/get_started_button.png")
get_started_button = pygame.transform.scale(get_started_button, (200,(int)(200/get_started_button.get_width() * get_started_button.get_height())))
get_started_rect = get_started_button.get_rect()
start_button = pygame.image.load("graphics/start_button.png")
pause = pygame.image.load("graphics/pause_button.png")
     
# create font types
font_big = pygame.font.SysFont("nimbusmonops", 28)
font_small = pygame.font.Font(None, 20)

# draw text
def display_text(k, v, font_type):
    text_surface = font_type.render('%s'%k, True, WHITE)
    rect = text_surface.get_rect(center=v)
    lcd.blit(text_surface, rect)

# draw control buttons
def display_touch_buttons(touch_buttons):
    for k,v in touch_buttons.items():
        display_text(k,v,font_big)

# set up control button locations
menu0 = {'Welcome to PiBeat!': (width // 2, height // 2 - 20), 'Quit': (280,220)}
menu1 = {'Choose Your Team:': (width // 2, height // 2), 'Quit': (280,220)}
menu2 = {'Start': (width // 2, height // 2 - 20), 'Leaderboard': (width // 2, height // 2 + 20) , 'Quit': (280,220)}
menu3 = {'Pause': (width // 2, height // 2 - 20), 'Back': (40,220) , 'Quit': (280,220)}
menu4 = {'Resume': (width // 2, height // 2 - 20), 'Back': (40,220) , 'Quit': (280,220)}
menu5 = {'Leaderboard': (width // 2, height // 2 - 80), 'Back': (40,220), 'Quit': (280,220)}


def display_menu0():
    display_touch_buttons(menu0)
    get_started_rect.x = 60
    get_started_rect.y = 120
    lcd.blit(get_started_button, get_started_rect)
    

def display_menu5():
    display_touch_buttons(menu5)

    # TODO: display leaderboard


menu_display_dict = {
    0: display_menu0,
    1: lambda: display_touch_buttons(menu1),
    2: lambda: display_touch_buttons(menu2),
    3: lambda: display_touch_buttons(menu3),
    4: lambda: display_touch_buttons(menu4),
    5: display_menu5
}

# set up initial menu
menu_level = 3
menu_display_dict[menu_level]()
pygame.display.update()
time_limit = 180


def menu0_event(x,y):
    global menu_level
    # get started
    if y > height//2+15 and y < height//2+45:
        menu_level = 1

def menu1_event(x,y):
    pass

def menu2_event(x,y):
    global menu_level
    # if start, menu_level = 3
    menu_level = 3
    # if leaderboard, menu_level = 5

def menu3_event(x,y):
    global menu_level
    # if pause, menu_level = 4
    # if back, menu_level = 2

def menu4_event(x,y):
    global menu_level
    # if resume, menu_level = 3
    # if back, menu_level = 2

def menu5_event(x,y):
    global menu_level
    # if back, menu_level = 2


menu_event_dict = {
    0: menu0_event,
    1: menu1_event,
    2: menu2_event,
    3: menu3_event,
    4: menu4_event,
}

# set up game state
GAME_HEIGHT = 10
INSN_SIZE = 5
# PL_PUF is reserved as neutral orientation
INSNS = [PL_LRF, PL_LLF] # [PL_PUB, PL_PDF, PL_PDB, PL_LRF, PL_LRB, PL_LLF, PL_LLB]
game_time = 0
insns = [] # list of tuples of (insn, time_generated)
cur_score = 0

def orientation_to_string(orientation):
    if orientation == PL_PUF:
        return "Portrait, up, front"
    elif orientation == PL_PUB:
        return "Portrait, up, back"
    elif orientation == PL_PDF:
        return "Portrait, down, front"
    elif orientation == PL_PDB:
        return "Portrait, down, back"
    elif orientation == PL_LRF:
        return "Landscape, right, front"
    elif orientation == PL_LRB:
        return "Landscape, right, back"
    elif orientation == PL_LLF:
        return "Landscape, left, front"
    elif orientation == PL_LLB:
        return "Landscape, left, back"

def get_target_time(time_generated):
    return time_generated + GAME_HEIGHT + INSN_SIZE // 2

# set up accelerometer
i2c = board.I2C() 
sensor = adafruit_mma8451.MMA8451(i2c)

my_clock = pygame.time.Clock()


try:
    while (time.time()-starttime < time_limit) and code_run:
        # update buffer for new touch events
        pitft.update()

        # get touchscreen events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                # clear screen
                lcd.fill(BLACK)
                pygame.display.flip()
                pygame.quit()
                
                # clean up pins
                GPIO.cleanup()

                import sys
                sys.exit(0)
            if(event.type is MOUSEBUTTONUP):
                x,y = pygame.mouse.get_pos()
                
                # quit button
                if y > 170 and x > 250:
                    # clear screen
                    lcd.fill(BLACK)
                    pygame.display.flip()
                    pygame.quit()
                    
                    # clean up pins
                    GPIO.cleanup()

                    import sys
                    sys.exit(0)
                
                # process button press
                menu_event_dict[menu_level](x,y)

                # generate new menu
                print("displaying menu", menu_level)
                lcd.fill(BLACK)
                menu_display_dict[menu_level]()
                pygame.display.flip()
        
        # display the game
        if menu_level == 3:
            print(game_time)

            # get current accelerometer orientation
            orientation = sensor.orientation
            
            # check if we need to generate a new instruction
            if game_time % INSN_SIZE == 0:
                next_insn = random.choice(INSNS)
                print("adding a new instruction:", orientation_to_string(next_insn))
                insns.append((next_insn, game_time))

            # get the current instruction
            if len(insns) == 0:
                print("ERROR: insns is empty")
            cur_insn, cur_insn_time_generated = insns[0]
            print(f"detected {orientation_to_string(orientation)}, expected {orientation_to_string(cur_insn)}")
            target_time = get_target_time(cur_insn_time_generated)

            # check if cur_insn is expired and missed
            if game_time > target_time + 2:
                if cur_insn != None:
                    # TODO: mark instruction as missed, show red gradient
                    pass
                print(f"removing insn ({orientation_to_string(cur_insn)},{cur_insn_time_generated})")
                insns.pop(0)
            elif game_time > target_time-3:
                # process current orientation
                if orientation != PL_PUF and cur_insn != None:
                    if orientation != cur_insn:
                        # TODO: mark instruction as missed, show red gradient
                        print("instruction hit wrong")
                    else:
                        # got instruction correctly
                        cur_score += INSN_SIZE - abs(game_time - target_time)
                        print("instruction hit correctly")
                        # TODO: show green gradient
                    print(f"removing insn ({orientation_to_string(cur_insn)},{cur_insn_time_generated})")
                    insns.pop(0)

            game_time += 1
        
        time.sleep(1)
        
except KeyboardInterrupt:
    pass
finally:
    pygame.quit()
    del(pitft)

# clean up pins
GPIO.cleanup()
