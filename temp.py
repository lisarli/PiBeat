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
from translation import *


code_run = True
starttime = time.time()

# set GPIO mode to BCM numbering
GPIO.setmode(GPIO.BCM)

# quit button
def GPIO17_callback(channel):
    global code_run
    code_run = False

# set up GPIO pins
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up GPIO callback2
GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300)

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
# pygame.display.flip()

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


try:
    # set up initial menu
    menu_level = 3
    menu_display_dict[menu_level]()
    # pygame.display.flip()
    time_limit = 180

    run_text = RunMatrix()

    while(True):
        arrow = acc_translate(acc.PL_PUF)
        instruction = pad_random(arrow)
        extra = np.zeros((27,16,3), dtype=np.uint8)
        led_matrix = np.concatenate((instruction, extra), axis = 0)
        run_text.run(led_matrix)
        time.sleep(1)
finally:
    pygame.quit()
    del(pitft)