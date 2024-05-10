import numpy as np
import adafruit_mma8451 as acc
import random

def acc_translate(orientation):
  front = (100,100,200)
  back = (200,0, 50)
  if orientation == acc.PL_PUF:
      return up_arr(front)
  elif orientation == acc.PL_PUB:
      return up_arr(back)
  elif orientation == acc.PL_PDF:
      return down_arr(front)
  elif orientation == acc.PL_PDB:
      return down_arr(back)
  elif orientation == acc.PL_LRF:
      return right_arr(front)
  elif orientation == acc.PL_LRB:
      return right_arr(back)
  elif orientation == acc.PL_LLF:
      return left_arr(front)
  elif orientation == acc.PL_LLB:
      return left_arr(back)
  elif orientation == None:
    return np.zeros((5,5,3))

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

def get_hash(number):
    hashed_value = hash(number)
    return (hashed_value & 0xFFFFFFFF) % 12

def pad_random(arr, gen_time):
  offset = get_hash(gen_time) # must be 0-11
  front_off = np.zeros((5,offset,3), dtype=np.uint8)
  back_off = np.zeros((5,11-offset,3), dtype=np.uint8)
  if offset > 0:
    arr = np.concatenate((front_off, arr), axis=1)
  if offset < 11:
    arr = np.concatenate((arr, back_off), axis = 1)
  return arr
  

def get_insn_leds(insns, game_time):
    if len(insns)==0:
        return np.zeros((25,16,3), dtype=np.uint8)

    insn_leds = np.zeros((35,16,3), dtype=np.uint8)
    top_idx = 29+(game_time-insns[-1][1])
    for i in range(len(insns)):
        cur_insn, gen_time = insns[len(insns)-1-i]
        arrow = acc_translate(cur_insn)
        instruction = pad_random(arrow, gen_time)
        insn_leds[35-5*(i+1):35-5*i][:][:] = instruction
    cropped_leds = insn_leds[top_idx-24:top_idx+1]
    return cropped_leds[::-1]

def get_bottom_leds(feedback):
    target_line = np.full((1, 16, 3), 255)
    feedback_leds = np.zeros((6,16,3), dtype=np.uint8)
    bottom_leds = np.concatenate((target_line, feedback_leds), axis = 0)
    return bottom_leds