from math import e
from math import pi
import dependence.spatial_enhancement as dev
import dependence.debug_log as debug
import time
from dependence.spatial_enhancement import cv
from dependence.spatial_enhancement import math
from dependence.spatial_enhancement import plt
from dependence.spatial_enhancement import np
np.set_printoptions(threshold=np.nan)
from dependence.spatial_enhancement import matplotlib
from dependence.spatial_enhancement import product
from functools import lru_cache
from scipy import ndimage
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
@debug.log_msg
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


@lru_cache(maxsize=None)
def _raw_fft(data, flag):
  M = len(data)
  Wm = e ** (-1j * 2 * pi / M) if flag == 0 else np.conjugate(e ** (-1j * 2 * pi / M))
  F = [None] * M
  k = M // 2

  if M == 2:
    F[0] = data[0] + data[1]
    F[1] = data[0] - data[1]
    return F

  Feven = _raw_fft(data[0: k], flag)
  Fodd  = _raw_fft(data[k: ], flag)

  for u in range(0, k):
    F[u]     = Feven[u] + Fodd[u] * Wm ** u
    F[u + k] = Feven[u] - Fodd[u] * Wm ** u

  return F


def _get_period_order(m):
  return list(map(lambda x: _bit_reverse(x, int(math.log2(m))), range(0, m)))


def _sort(data, order):
  return list(map(lambda x: data[ order[x] ], range(0, len(data))))


# Inverse Fast Fourier Transform
@debug.log_msg
def ifft2(img):
  height, width = img.shape[0], img.shape[1]
  feq_img = np.zeros((height, width), np.complex)

  for i in range(0, height):
    row_data = _sort(img[i], _get_period_order(width))
    feq_img[i, :] = _raw_fft(tuple(row_data), -1)

  for j in range(0, width):
    col_data = _sort(feq_img[:, j], _get_period_order(height))
    feq_img[:, j] = _raw_fft(tuple(col_data), -1)

  return feq_img


# Fast Fourier Transform
@debug.log_msg
def fft2(img):
  height, width = img.shape[0], img.shape[1]
  feq_img = np.zeros((height, width), np.complex)

  for i in range(0, height):
    row_data = _sort(img[i], _get_period_order(width))
    feq_img[i, :] = _raw_fft(tuple(row_data), 0)

  for j in range(0, width):
    col_data = _sort(feq_img[:, j], _get_period_order(height))
    feq_img[:, j] = _raw_fft(tuple(col_data), 0)

  return feq_img


# High-Frequency-Emphasis Filtering
@debug.log_msg
def high_frequency_emphasis(shape, D0, k1, k2):
  height, width = shape
  H = np.zeros((height, width), np.float)

  for u, v in product(range(0, height), range(0, width)):
    Duv = ((u - height / 2) ** 2 + (v - width / 2) ** 2) ** 0.5
    H[u, v] = k1 + k2 * (1 - e ** (-1 * Duv ** 2 / (2 * D0 ** 2)))

  return H


# Butterworth band reject filter
@debug.log_msg
def butterworth_filter(shape, D0, n):
  height, width = shape
  A = 2 ** 0.5 - 1
  H = np.zeros((height, width), np.float)

  for u, v in product(range(0, height), range(0, width)):
    Duv = ((u - height / 2) ** 2 + (v - width / 2) ** 2) ** 0.5
    H[u, v] = 1 / (1 + A * (Duv / D0) ** (2 * n))

  return H

@debug.log_msg
def write_image_value(img):
  with open("output/img_value", "w") as f:
    f.write(str(img))


@debug.log_msg
def center_transform(img):
  return img * np.fromfunction(lambda x, y: (-1) ** (x + y), img.shape, dtype=float)


@debug.log_msg
def get_spectrum(feq_img):
  return np.absolute(feq_img)


if __name__ == '__main__':
  # Problem a
  # # load image and change array type to float #
  # img = cv.imread("images/Fig0424(a)(rectangle).tif", 0)
  # img = img.astype(float)
  # # padding image shape to power of 2 #
  # img = _padding(img)
  # # shift image to origin point (let DC fequency centered) #
  # img = center_transform(img)
  # feq_img = fft2(img)
  # # get specturm by image and real #
  # center_spectrum = get_spectrum(feq_img)
  # dev.show_and_write(center_spectrum, "center_spectrum")
  # log_img = np.log10(1 + np.abs(feq_img))
  # dev.show_and_write(log_img, "log transformation")

  # ## Problem b
  # # load image and change array type to float #
  # img = cv.imread("images/Fig0459(a)(orig_chest_xray).tif", 0)
  # img = img.astype(float)
  # origin_shape = img.shape
  # # padding image shape to power of 2 #
  # img = _padding(img)
  # # shift image to origin point (let DC fequency centered) #
  # img = center_transform(img)
  # feq_img = fft2(img)
  # HFE = high_frequency_emphasis(img.shape, 120, 0.5, 0.7)
  # # multiply mask to filter out high frequency part #
  # filtered_img = feq_img * HFE
  # time_img = ifft2(filtered_img).real
  # # re-shift image to origin image #
  # time_img = center_transform(time_img)
  # # slice array to cut redundant padding image #
  # time_img = time_img[:origin_shape[0], :origin_shape[1]]
  # time_img = dev.normalize(time_img)
  # dev.show_and_write(time_img, "after high-feqency-emphasis filtering", 0)
  # time_img_equ = dev.histogram_equalize(time_img)
  # dev.show_and_write(time_img_equ, "after histogram equalize")

  ## Problem c
  # load image and change array type to float #
  # orig_img = img = cv.imread("images/Fig0516(a)(applo17_boulder_noisy).tif", 0)
  # BPF = cv.imread("images/Fig0516(c)(BW_banreject_order4).tif", 0)
  # img = img.astype(float)
  # mask_shape = BPF.shape
  # origin_shape = img.shape
  # # padding image shape to power of 2 #
  # img = _padding(img)
  # feq_shape = img.shape
  # # shift image to origin point (let DC fequency centered) #
  # img = center_transform(img)
  # feq_img = fft2(img)
  # # scale mask to fit padding image
  # BPF_zoom = ndimage.zoom(
  #         BPF,
  #         (
  #           feq_shape[0] / mask_shape[0],
  #           feq_shape[1] / mask_shape[1]
  #         ),
  #         order=0
  #       )
  #
  # filtered_img = feq_img * BPF_zoom
  # time_img = ifft2(filtered_img).real
  # time_img = center_transform(time_img)
  # time_img = time_img[:origin_shape[0], :origin_shape[1]]
  # time_img = dev.normalize(time_img)
  #
  # dev.show_and_write(orig_img, "origin image", 0)
  # dev.show_and_write(time_img, "after band pass filtering", 0)
