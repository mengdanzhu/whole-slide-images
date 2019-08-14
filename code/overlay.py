from os import makedirs, walk
from os.path import exists, join, basename, dirname
from collections import defaultdict
from random import randint, shuffle
import pickle
from shutil import copy2

import xlrd
import xlwt
from PIL import Image, ImageDraw, ImageFont
import numpy


def draw_overlay(filepath, draw_indices=True):
    cell_size = 800
    img = Image.open(filepath)
    w, h = img.size
    n_w = w // cell_size
    n_h = h // cell_size
    if w % cell_size > 0 or h % cell_size > 0:
        img = img.crop([0, 0, n_w*cell_size, n_h*cell_size])
    draw = ImageDraw.Draw(img)

    for j in range(1, n_h):
        draw.line((0, cell_size*j, w, cell_size*j), fill=(0, 0, 0), width=5)
    for i in range(1, n_w):
        draw.line((cell_size*i, 0, cell_size*i, h), fill=(0, 0, 0), width=5)

    if draw_indices:
        font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 48)
        # counter = 1
        for j in range(n_h):
            for i in range(n_w):
                index = 1 + j*n_w + i
                draw.text((20+i*cell_size, 20+j*cell_size), str(index), (0, 0, 0), font=font)
    filename, ext = basename(filepath).split('.')
    new_filepath = join(dirname(filepath), filename+'_overlay.'+ext)
    img.save(new_filepath)

draw_overlay('/home/mengdan/sample/_full_jpg_images/203622.jpg')