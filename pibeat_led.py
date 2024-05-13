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
import bisect


game_time = 0
insns = [] # list of tuples of (insn, time_generated)
feedback = None
menu_level = 0
player_team = None
cur_score = 0
cur_misses = 0

# set up teams
ICE = 0
OCEAN = 1
RAIN = 2
SKY = 3

team_dict = {0: "ICE", 1: "OCEAN", 2: "RAIN", 3: "SKY"}
team_color = {1:  graphics.Color(64, 224, 208), 3:  graphics.Color(135, 206, 235), 0:  graphics.Color(167, 199, 231), 2:  graphics.Color(100, 149, 237)}


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
    
    def show_matrix(self,led_matrix):
        for x in range(self.screen.width):
            for y in range(self.screen.height):
                r, g, b = led_matrix[x][y]
                self.screen.SetPixel(x, y, r, g, b)


    def run(self):
      global code_run, insns, game_time, menu_level, feedback
      pos = self.screen.width
      font = graphics.Font()
      font.LoadFont("/home/pi/PiBeat/fonts/helvR12.bdf")
      textColor = graphics.Color(20, 160, 220)

      while code_run:
        if menu_level == 3:
            self.screen.Clear()

            insn_leds = get_insn_leds(insns, game_time)
            bottom = get_bottom_leds(feedback)
            led_matrix = np.concatenate((insn_leds, bottom), axis = 0)

            self.show_matrix(led_matrix)
        
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
            total_len = graphics.DrawText(self.screen, font, pos, 12, textColor, "CHOOSE A TEAM")
            pos -= 1
            if (pos <= -total_len):
                pos = self.screen.width
            time.sleep(0.05)
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 2:
            self.screen.Clear()
            total_len = graphics.DrawText(self.screen, font, pos, 12,team_color[player_team], team_dict[player_team])
            pos -= 1
            if (pos <= -total_len):
                pos = self.screen.width
            time.sleep(0.05)
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 4:
            self.screen.Clear()
            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 5:
            self.screen.Clear()
            max_team = np.argmax(np.array(team_scores))
            total_len = graphics.DrawText(self.screen, font, pos, 12, team_color[max_team], team_dict[max_team])
            pos -= 1
            if (pos <= -total_len):
                pos = self.screen.width
            time.sleep(0.05)

            self.screen = self.matrix.SwapOnVSync(self.screen)
        elif menu_level == 6:
            self.screen.Clear()
            
            GAME_OVER_MESSAGE = "GAME OVER"
            total_len = graphics.DrawText(self.screen, font, pos, 12, textColor, GAME_OVER_MESSAGE)
            pos -= 1
            if (pos <= -total_len):
                pos = self.screen.width
            time.sleep(0.05)

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

def load_image(img_path, scale_factor):
    button = pygame.image.load("/home/pi/PiBeat/graphics/" + img_path)
    button = pygame.transform.scale(button, (scale_factor,(int)(scale_factor/button.get_width() * button.get_height())))
    button_rect = button.get_rect()
    return button, button_rect

get_started_button, get_started_rect = load_image("get_started_button.png", 200)
start_button, start_button_rect = load_image("start_button.png", 150)
pause_button, pause_button_rect = load_image("pause_button.png", 150)
resume_button, resume_button_rect = load_image("resume_button.png", 150)
trophy_button, trophy_button_rect = load_image("trophy.png", 70)
ice_button, ice_button_rect = load_image("ice.png", 100)
ocean_button, ocean_button_rect = load_image("ocean.png", 150)
rain_button, rain_button_rect = load_image("rain.png", 120)
sky_button, sky_button_rect = load_image("sky.png", 100)
arrow_button, arrow_button_rect = load_image("arrow.png", 50)

# --- end load graphics ---


# create font types
font_big = pygame.font.SysFont("nimbusmonops", 28)
font_small = pygame.font.SysFont("nimbusmonops", 20)

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
menu3 = {'Quit': (280,220)}
menu4 = {'Quit': (280,220)}
menu5 = {'Leaderboard': (width // 2, height // 2 - 80), 'Quit': (280,220)}
menu6 = {'Quit': (280,220)}

def display_menu0():
    display_touch_buttons(menu0)
    get_started_rect.x = 60
    get_started_rect.y = 120
    lcd.blit(get_started_button, get_started_rect)
    
def display_menu1():
    display_touch_buttons(menu1)

    # show ice button
    ice_button_rect.x = 20
    ice_button_rect.y = 140
    lcd.blit(ice_button, ice_button_rect)

    # show ocean button
    ocean_button_rect.x = 160
    ocean_button_rect.y = 60
    lcd.blit(ocean_button, ocean_button_rect)

    # show rain button
    rain_button_rect.x = 20
    rain_button_rect.y = 60
    lcd.blit(rain_button, rain_button_rect)

    # show sky button
    sky_button_rect.x = 190
    sky_button_rect.y = 140
    lcd.blit(sky_button, sky_button_rect)

def display_menu2():
    reset_game()
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
    global cur_score
    display_touch_buttons(menu3)

    # show pause button
    pause_button_rect.x = 80
    pause_button_rect.y = 80
    lcd.blit(pause_button, pause_button_rect)

    # show score
    display_text("Score: " + str(cur_score), (160,40), font_small)

    # show misses
    display_text("Misses Remaining: " + str(MISSES_ALLOWED-cur_misses), (160,60), font_small)

    # show arrow button
    arrow_button_rect.x = 10
    arrow_button_rect.y = 190
    lcd.blit(arrow_button, arrow_button_rect)

def display_menu4():
    display_touch_buttons(menu4)

    # show resume button
    resume_button_rect.x = 80
    resume_button_rect.y = 80
    lcd.blit(resume_button, resume_button_rect)
    #TODO: are we saying that if you are resuming, you can't go back (it automatically restarts the game)

    # show score
    display_text("Score: " + str(cur_score), (160,40), font_small)

    # show misses
    display_text("Misses Remaining: " + str(MISSES_ALLOWED-cur_misses), (160,60), font_small)

    # show arrow button
    arrow_button_rect.x = 10
    arrow_button_rect.y = 190
    lcd.blit(arrow_button, arrow_button_rect)

def display_menu5():
    display_touch_buttons(menu5)

    # TODO: make leaderboard high something? and font formatting

    # show ice team
    ice_button_rect.x = 20
    ice_button_rect.y = 130
    lcd.blit(ice_button, ice_button_rect)
    display_text(str(team_scores[ICE]), (75,190), font_big)

    # show ocean team
    ocean_button_rect.x = 160
    ocean_button_rect.y = 60
    lcd.blit(ocean_button, ocean_button_rect)
    display_text(str(team_scores[OCEAN]), (230,120), font_big)

    # show rain team
    rain_button_rect.x = 20
    rain_button_rect.y = 60
    lcd.blit(rain_button, rain_button_rect)
    display_text(str(team_scores[RAIN]), (80,120), font_big)

    # show sky team
    sky_button_rect.x = 190
    sky_button_rect.y = 130
    lcd.blit(sky_button, sky_button_rect)
    display_text(str(team_scores[SKY]), (235,190), font_big)

    # show arrow button
    arrow_button_rect.x = 10
    arrow_button_rect.y = 190
    lcd.blit(arrow_button, arrow_button_rect)



def display_menu6():
    display_touch_buttons(menu6)
    # show score
    display_text("Score: " + str(cur_score), (160,70), font_big)

    # show overall ranking
    ranking = bisect.bisect_right(all_scores, cur_score)
    display_text("Your Global Ranking: " + str(len(all_scores)-ranking+1), (160,100), font_small)

    # check if new high
    if cur_score >= team_scores[player_team]:
        team_names = ["ICE","OCEAN","RAIN","SKY"]
        display_text("You got a high score", (160,130), font_small)
        display_text("for team " + team_names[player_team] + "!", (160,150), font_small)
        team_scores[player_team] = cur_score

    # show arrow button
    arrow_button_rect.x = 10
    arrow_button_rect.y = 190
    lcd.blit(arrow_button, arrow_button_rect)


menu_display_dict = {
    0: display_menu0,
    1: display_menu1,
    2: display_menu2,
    3: display_menu3,
    4: display_menu4,
    5: display_menu5,
    6: display_menu6
}

# set up initial menu
menu_display_dict[menu_level]()
pygame.display.update()
time_limit = 3000

def reset_game():
    global game_time, insns, feedback, cur_score, cur_misses
    game_time = 0
    insns = []
    feedback = None
    cur_score = 0
    cur_misses = 0

def menu0_event(x,y):
    global menu_level
    # get started
    if y > height//2 and y < height//2+45 and x > 20 and x < 300:
        menu_level = 1

def menu1_event(x,y):
    global menu_level, player_team
    if y > 20:
        if x < width//2:
            if y > height//2:
                player_team = ICE
            else:
                player_team = RAIN
        else:
            if y > height//2:
                player_team = SKY
            else:
                player_team = OCEAN
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

def menu6_event(x,y):
    global menu_level
    if y > 180 and x < 80:
        # arrow button pressed
        menu_level = 2


menu_event_dict = {
    0: menu0_event,
    1: menu1_event,
    2: menu2_event,
    3: menu3_event,
    4: menu4_event,
    5: menu5_event,
    6: menu6_event
}

# set up game state
GAME_HEIGHT = 25
INSN_SIZE = 5
GOOD_POINT_VAL = 10
MISSES_ALLOWED = 5
# PL_PUF is reserved as neutral orientation
INSNS =  [PL_PUB, PL_PDF, PL_PDB, PL_LRF, PL_LRB, PL_LLF, PL_LLB, None] # [PL_PDF, PL_LRF, PL_LLF, None]

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

# set up leaderboard
with open('/home/pi/PiBeat/leaderboard/scores.txt', 'r') as scores:
    all_scores = scores.readline().strip()
    all_scores = [int(num) for num in all_scores.split(',')]
    team_scores = scores.readline().strip()
    team_scores = [int(num) for num in team_scores.split(',')]


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
            if event.type == pygame.QUIT:
                # code_run = False
                break
            if(event.type is MOUSEBUTTONUP):
                x,y = pygame.mouse.get_pos()
                
                # quit button
                if y > 170 and x > 250:
                    if menu_level == 0:
                        code_run = False
                        break
                    menu_level = 0
                else:
                    # process button press
                    menu_event_dict[menu_level](x,y)

                # generate new menu
                print("displaying menu", menu_level)
                lcd.fill(BLACK)
                menu_display_dict[menu_level]()
                pygame.display.flip()
        
        if menu_level == 3 or menu_level == 4:
            lcd.fill(BLACK)
            menu_display_dict[menu_level]()
            pygame.display.flip()
        
        # display the game
        if menu_level == 3:
            print("in game:",cur_misses)
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
                    cur_misses += 1
                    pass
                print(f"removing missed insn ({orientation_to_string(cur_insn)},{cur_insn_time_generated})")
                insns.pop(0)
            elif game_time > target_time-3:
                # process current orientation
                if orientation != PL_PUF and cur_insn != None:
                    if orientation != cur_insn:
                        feedback = "BAD"
                        cur_misses += 1
                        print("instruction hit wrong")
                    else:
                        # got instruction correctly
                        mis_time = abs(game_time - target_time)
                        cur_score += GOOD_POINT_VAL // (mis_time+1)
                        print("instruction hit correctly")
                        if mis_time == 0:
                            feedback = "GOOD"
                        elif mis_time == 1:
                            feedback = "MISTIME_CLOSE"
                        else:
                            feedback = "MISTIME_FAR"
                    print(f"removing insn ({orientation_to_string(cur_insn)},{cur_insn_time_generated})")
                    insns.pop(0)

            game_time += 1

            if cur_misses == MISSES_ALLOWED:
                menu_level = 6

                # add score to all scores
                ranking = bisect.bisect_left(all_scores, cur_score)
                all_scores.insert(ranking, cur_score)

                # generate new menu
                lcd.fill(BLACK)
                menu_display_dict[menu_level]()
                pygame.display.flip()
        
        time.sleep(0.5)
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
    

    # save scores
    with open('/home/pi/PiBeat/leaderboard/scores.txt', 'w') as scores:
        scores.write(','.join(map(str, all_scores)))
        scores.write('\n')
        scores.write(','.join(map(str, team_scores)))

    import sys
    sys.exit(0)
    
