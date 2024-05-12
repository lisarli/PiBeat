import RPi.GPIO as GPIO
import pygame, pigame
import os
from time import sleep
import time
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

# Run on Pi TFT
os.putenv("SDL_VIDEODRIVER", "fbcon")
os.putenv("SDL_FBDEV", "/dev/fb0")
  
# Use the touchscreen
os.putenv("SDL_MOUSEDRV", "TSLIB")
os.putenv("SDL_MOUSEDEV", "/dev/input/touchscreen")
pygame.init()
pygame.mouse.set_visible(False)
    
try:
    tft = pygame.display.set_mode((320, 240))
    time.sleep(1)

    # set screen dimensions
    size = width, height = 320, 240
    lcd = pygame.display.set_mode((width, height))
    time.sleep(1)
    lcd.fill((0,0,0))
    time.sleep(1)
    pygame.display.flip()
    time.sleep(1)

    code_run = True

    print("before run_text")
    run_text = RunMatrix()

    t1 = Thread(target=run_text.run)
    t1.start()
    time.sleep(5)
except KeyboardInterrupt:
    print("got KeyboardInterrupt")
finally:
    code_run = False
    # t1.join()
    pygame.quit()