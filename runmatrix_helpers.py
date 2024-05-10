import numpy as np
import adafruit_mma8451 as acc
import random

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
