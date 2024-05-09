import RPi.GPIO as GPIO
import pygame, pigame
from pygame.locals import *
import os
from time import sleep
import time
import board
from adafruit_mma8451 import PL_PUF, PL_PUB, PL_PDF, PL_PDB, PL_LRF, PL_LRB, PL_LLF, PL_LLB
import random
from samplebase import SampleBase
from rgbmatrix import graphics
import numpy as np
import adafruit_mma8451 as acc
from threading import Thread

class RunMatrix(SampleBase):
    def __init__(self, *args, **kwargs):
        print("runmatrix starting init")
        super(RunMatrix, self).__init__(*args, **kwargs)
        print("runmatrix done init")
        self.process()
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()


    def run(self):
      global code_run
      while code_run:
        pos = self.offscreen_canvas.width

        self.offscreen_canvas.Clear()

        arrow = acc_translate(acc.PL_PUF)
        instruction = pad_random(arrow)
        extra = np.zeros((27,16,3), dtype=np.uint8)
        led_matrix = np.concatenate((instruction, extra), axis = 0)

        for x in range(self.offscreen_canvas.width):
            for y in range(self.offscreen_canvas.height):
              r, g, b = led_matrix[x][y]
              self.offscreen_canvas.SetPixel(x, y, r, g, b)
      
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
        time.sleep(0.5)
      
    

def acc_translate(orientation):
  front = (100,100,200)
  back = (200,0, 50)
  if orientation == acc.PL_PUF:
      print("Portrait, up, front")
      return up_arr(front)
  elif orientation == acc.PL_PUB:
      print("Portrait, up, back")
      return up_arr(back)
  elif orientation == acc.PL_PDF:
      print("Portrait, down, front")
      return down_arr(front)
  elif orientation == acc.PL_PDB:
      print("Portrait, down, back")
      return down_arr(back)
  elif orientation == acc.PL_LRF:
      print("Landscape, right, front")
      return right_arr(front)
  elif orientation == acc.PL_LRB:
      print("Landscape, right, back")
      return right_arr(back)
  elif orientation == acc.PL_LLF:
      print("Landscape, left, front")
      return left_arr(front)
  elif orientation == acc.PL_LLB:
      print("Landscape, left, back")
      return left_arr(back)

def random_offset():
  return random.randint(0, 11)

def up_arr(color):
  arr = np.zeros((5,5,3), dtype=np.uint8)

  arr[0][2] = color
  arr[1][1] = color
  arr[1][3] = color
  arr[2][0] = color
  arr[2][4] = color
  arr[1][2] = color
  arr[2][2] = color
  arr[3][2] = color
  arr[4][2] = color
  return arr

def left_arr(color):
  return np.transpose(up_arr(color), (1, 0, 2))

def right_arr(color):
  return np.flip(left_arr(color))

def down_arr(color):
  return np.flip(np.flip(up_arr(color), axis=0), axis=1)

def pad_random(arr):
  offset = random_offset() # must be 0-11
  front_off = np.zeros((5,offset,3), dtype=np.uint8)
  back_off = np.zeros((5,11-offset,3), dtype=np.uint8)
  if offset > 0:
    arr = np.concatenate((front_off, arr), axis=1)
  if offset < 11:
    arr = np.concatenate((arr, back_off), axis = 1)
  return arr

# run on piTFT
os.putenv('SDL_VIDEODRV','fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV','dummy')
os.putenv('SDL_MOUSEDEV','/dev/null')
os.putenv('DISPLAY','')

pygame.init()
pygame.mouse.set_visible(False)
pitft = pigame.PiTft()

# set colors
BLACK = 0,0,0
RED = 255,0,0
GREEN = 0,255,0
WHITE = 255,255,255

# set screen dimensions
size = width, height = 320, 240
print("before lcb")
lcd = pygame.display.set_mode((width, height))
print("before fill")
lcd.fill((0,0,0))
print("pygame first flip")
pygame.display.flip()

# load graphics
get_started_button = pygame.image.load("graphics/get_started_button.png")
get_started_button = pygame.transform.scale(get_started_button, (200,(int)(200/get_started_button.get_width() * get_started_button.get_height())))
get_started_rect = get_started_button.get_rect()
start_button = pygame.image.load("graphics/start_button.png")
pause = pygame.image.load("graphics/pause_button.png")
     
font_big = pygame.font.SysFont("nimbusmonops", 28)

def display_text(k, v, font_type):
    text_surface = font_type.render('%s'%k, True, WHITE)
    rect = text_surface.get_rect(center=v)
    lcd.blit(text_surface, rect)

# draw control buttons
def display_touch_buttons(touch_buttons):
    for k,v in touch_buttons.items():
        display_text(k,v,font_big)

menu0 = {'Welcome to PiBeat!': (width // 2, height // 2 - 20), 'Quit': (280,220)}
def display_menu0():
    display_touch_buttons(menu0)
    get_started_rect.x = 60
    get_started_rect.y = 120
    lcd.blit(get_started_button, get_started_rect)

menu_display_dict = {
    0: display_menu0
}

# set up initial menu
menu_level = 0
menu_display_dict[menu_level]()
print("pygame first update")
pygame.display.update()
print("pitft update")
pitft.update()
print("pygame second flip")
pygame.display.flip()

code_run = True

print("before run_text")
run_text = RunMatrix()

t1 = Thread(target=run_text.run)
t1.start()
    
try:
    time.sleep(2)
except KeyboardInterrupt:
    print("got KeyboardInterrupt")
finally:
    code_run = False
    t1.join()
    pygame.quit()
    del(pitft)