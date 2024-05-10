import os
import time
import board
import random
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
import numpy as np
import adafruit_mma8451 as acc
from threading import Thread
import pygame

code_run = True

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
      global code_run
      while code_run:
        pos = self.screen.width

        self.screen.Clear()

        arrow = acc_translate(acc.PL_PUF)
        instruction = pad_random(arrow)
        extra = np.zeros((27,16,3), dtype=np.uint8)
        led_matrix = np.concatenate((instruction, extra), axis = 0)

        for x in range(self.screen.width):
            for y in range(self.screen.height):
              r, g, b = led_matrix[x][y]
              self.screen.SetPixel(x, y, r, g, b)
      
        self.screen = self.matrix.SwapOnVSync(self.screen)
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

os.putenv('SDL_VIDEODRV','fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV','dummy')
os.putenv('SDL_MOUSEDEV','/dev/null')
os.putenv('DISPLAY','')

pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode()

try:
  run_text = RunMatrix()
  t1 = Thread(target=run_text.run)
  t1.start()

  time.sleep(5)
finally:
  print("here")
  code_run = False
  t1.join()
  pygame.quit()
  print("exiting script")