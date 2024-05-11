import RPi.GPIO as GPIO
import pygame, pigame
from pygame.locals import *
import os
from time import sleep
import time
import board
from adafruit_mma8451 import PL_PUF, PL_PUB, PL_PDF, PL_PDB, PL_LRF, PL_LRB, PL_LLF, PL_LLB
import random
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
import numpy as np
import adafruit_mma8451 as acc
from threading import Thread
from runmatrix_helpers import *


game_time = 0
insns = [] # list of tuples of (insn, time_generated)
feedback = None
menu_level = 0
player_team = None
cur_score = 0

code_run = True
WELCOME_MESSAGE = "♪ WELCOME TO PIBEAT ♪"

class RunMatrix():
    def __init__(self):
        print("runmatrix starting init")
        options = RGBMatrixOptions()

        options.hardware_mapping = 'adafruit-hat'
        options.rows = 16
        options.cols = 32
        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = 'RGB'
        options.pixel_mapper_config = ''
        options.panel_type = ''
        options.gpio_slowdown = 4
        options.drop_privileges = True
        options.disable_hardware_pulsing = True

        self.matrix = RGBMatrix(options=options)
        self.screen = self.matrix.CreateFrameCanvas()
        print("runmatrix done init")


    def run(self):
      global code_run, insns, game_time, menu_level, feedback
      pos = self.screen.width
      font = graphics.Font()
      font.LoadFont("./fonts/helvR12.bdf")
      textColor = graphics.Color(20, 160, 220)

      while code_run:
        if menu_level == 3:
            self.screen.Clear()

            insn_leds = get_insn_leds(insns, game_time)
            bottom = get_bottom_leds(feedback)
            led_matrix = np.concatenate((insn_leds, bottom), axis = 0)

            for x in range(self.screen.width):
                for y in range(self.screen.height):
                    r, g, b = led_matrix[x][y]
                    self.screen.SetPixel(x, y, r, g, b)
        
            self.screen = self.matrix.SwapOnVSync(self.screen)
            time.sleep(0.05)
        elif menu_level == 0:
            self.screen.Clear()
            
            total_len = graphics.DrawText(self.screen, font, pos, 12, textColor, WELCOME_MESSAGE)
            pos -= 1
            if (pos <= -total_len):
                pos = self.screen.width
            time.sleep(0.05)
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 1:
            self.screen.Clear()
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 2:
            self.screen.Clear()
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 4:
            self.screen.Clear()
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 5:
            self.screen.Clear()
            self.screen = self.matrix.SwapOnVSync(self.screen)

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
pygame.display.flip()


# --- load graphics ---

get_started_button = pygame.image.load("graphics/get_started_button.png")
get_started_button = pygame.transform.scale(get_started_button, (200,(int)(200/get_started_button.get_width() * get_started_button.get_height())))
get_started_rect = get_started_button.get_rect()

start_button = pygame.image.load("graphics/start_button.png")
start_button = pygame.transform.scale(start_button, (150,(int)(150/start_button.get_width() * start_button.get_height())))
start_button_rect = start_button.get_rect()

pause_button= pygame.image.load("graphics/pause_button.png")
pause_button = pygame.transform.scale(pause_button, (150,(int)(150/pause_button.get_width() * pause_button.get_height())))
pause_button_rect = pause_button.get_rect()

resume_button= pygame.image.load("graphics/resume_button.png")
resume_button = pygame.transform.scale(resume_button, (150,(int)(150/resume_button.get_width() * resume_button.get_height())))
resume_button_rect = resume_button.get_rect()

trophy_button = pygame.image.load("graphics/trophy.png")
trophy_button = pygame.transform.scale(trophy_button, (70,(int)(70/trophy_button.get_width() * trophy_button.get_height())))
trophy_button_rect = trophy_button.get_rect()

# --- end load graphics ---


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
menu1 = {'Choose Your Team:': (width // 2, 20), 'Quit': (280,220)}
menu2 = {'Quit': (280,220)}
menu3 = {'Back': (40,220) , 'Quit': (280,220)}
menu4 = {'Back': (40,220) , 'Quit': (280,220)}
menu5 = {'Leaderboard': (width // 2, height // 2 - 80), 'Back': (40,220), 'Quit': (280,220)}
# TODO: make end of game screen, display score and overall ranking


def display_menu0():
    display_touch_buttons(menu0)
    get_started_rect.x = 60
    get_started_rect.y = 120
    lcd.blit(get_started_button, get_started_rect)
    
def display_menu1():
    display_touch_buttons(menu1)

def display_menu2():
    display_touch_buttons(menu2)
    
    # show start button
    start_button_rect.x = 80
    start_button_rect.y = 80
    lcd.blit(start_button, start_button_rect)

    # show trophy button
    trophy_button_rect.x = 10
    trophy_button_rect.y = 190
    lcd.blit(trophy_button, trophy_button_rect)

def display_menu3():
    display_touch_buttons(menu3)

    # show pause button
    pause_button_rect.x = 80
    pause_button_rect.y = 80
    lcd.blit(pause_button, pause_button_rect)

def display_menu4():
    display_touch_buttons(menu4)

    # show resume button
    resume_button_rect.x = 80
    resume_button_rect.y = 80
    lcd.blit(resume_button, resume_button_rect)

def display_menu5():
    display_touch_buttons(menu5)

    # TODO: display leaderboard


menu_display_dict = {
    0: display_menu0,
    1: display_menu1,
    2: display_menu2,
    3: display_menu3,
    4: display_menu4,
    5: display_menu5
}

# set up initial menu
menu_display_dict[menu_level]()
pygame.display.update()
time_limit = 90

def reset_game():
    global game_time, insns, feedback, cur_score
    game_time = 0
    insns = []
    feedback = None
    cur_score = 0

def menu0_event(x,y):
    global menu_level
    # get started
    if y > height//2 and y < height//2+45 and x > 20 and x < 300:
        menu_level = 1

def menu1_event(x,y):
    global menu_level
    if y > 20:
        if x < width//2:
            if y > height//2:
                print("chose team snow")
                team = "SNOW"
            else:
                print("chose team rain")
                team = "RAIN"
        else:
            if y > height//2:
                print("chose team sky")
                team = "SKY"
            else:
                print("chose team ocean")
                team = "OCEAN"
    menu_level = 2

def menu2_event(x,y):
    global menu_level
    if y > 80 and y < 130 and x > 80 and x < 220:
        # start button pressed
        menu_level = 3
    elif y > 180 and x < 80:
        # trophy button pressed
        menu_level = 5

def menu3_event(x,y):
    global menu_level
    if y > 80 and y < 130 and x > 80 and x < 220:
        # pause button pressed
        menu_level = 4
    elif y > 160 and x < 100:
        # back button pressed
        reset_game()
        menu_level = 2

def menu4_event(x,y):
    global menu_level
    if y > 80 and y < 130 and x > 80 and x < 220:
        # resume button pressed
        menu_level = 3
    elif y > 160 and x < 100:
        # back button pressed
        reset_game()
        menu_level = 2

def menu5_event(x,y):
    global menu_level
    if y > 160 and x < 100:
        # back button pressed
        menu_level = 2


menu_event_dict = {
    0: menu0_event,
    1: menu1_event,
    2: menu2_event,
    3: menu3_event,
    4: menu4_event,
    5: menu5_event,
}

# set up game state
GAME_HEIGHT = 25
INSN_SIZE = 5
# PL_PUF is reserved as neutral orientation
INSNS = [PL_LRF, PL_LLF, None] # [PL_PUB, PL_PDF, PL_PDB, PL_LRF, PL_LRB, PL_LLF, PL_LLB, None]

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
sensor = acc.MMA8451(i2c)

my_clock = pygame.time.Clock()


try:
    # start LED display thread
    led_board = RunMatrix()
    t1 = Thread(target=led_board.run)
    t1.start()

    while (time.time()-starttime < time_limit) and code_run:
        # update buffer for new touch events
        pitft.update()

        # get touchscreen events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if(event.type is MOUSEBUTTONUP):
                x,y = pygame.mouse.get_pos()
                
                # quit button
                if y > 170 and x > 250:
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
            # print(game_time)

            # get current accelerometer orientation
            orientation = sensor.orientation
            print("currently detected:", orientation_to_string(orientation))
            
            # check if we need to generate a new instruction
            if game_time % INSN_SIZE == 0:
                next_insn = random.choice(INSNS)
                # print("adding a new instruction:", orientation_to_string(next_insn))
                insns.append((next_insn, game_time))

            # get the current instruction
            if len(insns) == 0:
                print("ERROR: insns is empty")
            cur_insn, cur_insn_time_generated = insns[0]
            # print(f"detected {orientation_to_string(orientation)}, expected {orientation_to_string(cur_insn)}")
            target_time = get_target_time(cur_insn_time_generated)

            # check if cur_insn is expired and missed
            if game_time > target_time + 2:
                if cur_insn != None:
                    feedback = "MISS"
                    pass
                print(f"removing missed insn ({orientation_to_string(cur_insn)},{cur_insn_time_generated})")
                insns.pop(0)
            elif game_time > target_time-3:
                # process current orientation
                if orientation != PL_PUF and cur_insn != None:
                    if orientation != cur_insn:
                        feedback = "BAD"
                        print("instruction hit wrong")
                    else:
                        # FIXME: change lights and score based on timing
                        # got instruction correctly
                        cur_score += INSN_SIZE - abs(game_time - target_time)
                        print("instruction hit correctly")
                        feedback = "GOOD"
                    print(f"removing insn ({orientation_to_string(cur_insn)},{cur_insn_time_generated})")
                    insns.pop(0)

            game_time += 1
        
        time.sleep(0.2)
        feedback = None
finally:
    # clean up LED display
    code_run = False
    t1.join()

    # clean up PiTFT
    lcd.fill(BLACK)
    pygame.display.flip()
    pygame.quit()
    del(pitft)

    # clean up pins
    GPIO.cleanup()
