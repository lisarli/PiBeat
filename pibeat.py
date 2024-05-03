import RPi.GPIO as GPIO
import pygame, pigame
from pygame.locals import *
import os
from time import sleep
import time


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
menu1 = {'Enter Your Name:': (width // 2, height // 2), 'Quit': (280,220)}
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
menu_level = 0
menu_display_dict[menu_level]()
pygame.display.update()
time_limit = 30


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

my_clock = pygame.time.Clock()

try:
    while (time.time()-starttime < time_limit) and code_run:
        # update buffer for new touch events
        pitft.update()

        # get touchscreen events
        for event in pygame.event.get():
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
                print("displaying menu",menu_level)
                lcd.fill(BLACK)
                menu_display_dict[menu_level]()
                pygame.display.flip()

        
except KeyboardInterrupt:
    pass
finally:
    pygame.quit()
    del(pitft)

# clean up pins
GPIO.cleanup()
