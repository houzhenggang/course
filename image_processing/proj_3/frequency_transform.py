from math import e
from math import pi
import dependence.spatial_enhancement as dev
import time
from dependence.spatial_enhancement import cv
from dependence.spatial_enhancement import math
from dependence.spatial_enhancement import plt
from dependence.spatial_enhancement import np
np.set_printoptions(threshold=np.nan)
from dependence.spatial_enhancement import matplotlib
from dependence.spatial_enhancement import product

import pdb

# check if a number is a power of two
def _is_power_2(num):
  return ( num != 0 and ((num & (num - 1)) == 0))



# calc highest bit position then complete to power of 2
def _complete_to_power_2(num):
  num = math.log2(num)
  hb = num if type(num) == int else int(num) + 1

  return 2 ** hb


# let image be power of 2
def _padding(img):
  height, width = img.shape[0], img.shape[1]
  new_height, new_width = height, width

  if not _is_power_2(height):
    new_height = _complete_to_power_2(height)
  if not _is_power_2(width):
    new_width = _complete_to_power_2(width)

  img = np.pad(
          img,
          ((0, new_height - height), (0, new_width - width)),
          'constant', 
          constant_values=0
        )
  
  return img


# implement DFT
def dft(img):
  height, width = img.shape[0], img.shape[1]
  f = img
  F = np.zeros((height, width, 1), np.float)

  for u, v in product(range(0, height), range(0, width)):
    for x, y in product(range(0, height), range(0, width)):
      F[u, v] += f[x, y] * e ** (2 * pi * (u * x / height + v * y / width)) * (-1) ** (x + y)

  return F


def _bit_swap(x, i, j):
  ib = (x >> i) & 1
  jb = (x >> j) & 1
  if (ib ^ jb):
    x ^= ((1 << i) | (1 << j))

  return x


def _bit_reverse(x, hb):
  for i in range(0, math.ceil(hb / 2)):
    x = _bit_swap(x, i, hb - i - 1)

  return x


def _get_period_order(m):
  return list(map(lambda x: _bit_reverse(x, int(math.log2(m))), range(0, m)))


def _sort(data, order):
  return list(map(lambda x: data[ order[x] ], range(0, len(data))))


# Fast Fourier Transform
def fft():
  return 0


# High-Frequency-Emphasis Filtering
def hightpass_filter():
  return 0


# Butterworth band reject filter
def butterworth_filter():
  return 0



if __name__ == '__main__':


