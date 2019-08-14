import threading
import os, sys
from os import listdir
from os.path import isfile, join, isdir

import numpy as np

from scipy.misc import imsave
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1e10
from random import randint
import time
from scipy.stats import mode
import cv2
import openslide

import skimage.measure
from skimage.transform import rescale, rotate
import time

# compression_factor = 7.5
# window_size = 10000
# compressed_window_size = int(window_size / compression_factor)


# svs to jpg converter class for a file of svs images, can specify compression factor
class myThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    
    def run(self):
        input_folder = os.getcwd()+'/img/'
        svs_to_jpg_converter = SvsToJpgConverter(input_folder, 7.5)
        svs_to_jpg_converter.convert()

class SvsToJpgConverter:
    def __init__(self, input_folder, compression_factor=7.5):
        self.input_folder = str(input_folder)
        self.tiles_folder = str(self.input_folder) + "_jpg_tiles"
        self.output_folder =  str(self.input_folder) + "_full_jpg_images"
        if not os.path.exists(self.tiles_folder):
            os.makedirs(self.tiles_folder)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.compression_factor = compression_factor
        self.window_size = 10000
        self.compressed_window_size = int(self.window_size / self.compression_factor)

    # from svs_to_jpg_tiles.py @author Jason
    def output_jpeg_tiles(self, image_name, output_path):  # converts svs image with meta data into just the jpeg image

        img = openslide.OpenSlide(image_name)
        width, height = img.level_dimensions[0]

        # img_np_rgb = np.zeros((23000, 30000, 3), dtype=np.uint8)
        increment_x = int(width / self.window_size) + 1
        increment_y = int(height / self.window_size) + 1

        print("converting", image_name.split("/")[-1][:-4], "with width", width, "and height", height)

        for incre_x in range(increment_x):  # have to read the image in patches since it doesn't let me do it for larger things
            for incre_y in range(increment_y):

                begin_x = self.window_size * incre_x
                end_x = min(width, begin_x + self.window_size)
                begin_y = self.window_size * incre_y
                end_y = min(height, begin_y + self.window_size)
                patch_width = end_x - begin_x
                patch_height = end_y - begin_y

                patch = img.read_region((begin_x, begin_y), 0, (patch_width, patch_height))
                patch.load()
                patch_rgb = Image.new("RGB", patch.size, (255, 255, 255))
                patch_rgb.paste(patch, mask=patch.split()[3])

                # compress the image
                patch_rgb = patch_rgb.resize(
                    (int(patch_rgb.size[0] / self.compression_factor), int(patch_rgb.size[1] / self.compression_factor)),
                    Image.ANTIALIAS)

                # save the image
                output_subfolder = join(output_path, image_name.split('/')[-1][:-4])
                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)
                output_image_name = join(output_subfolder,
                                         image_name.split('/')[1][:-4] + '_' + str(incre_x) + '_' + str(
                                             incre_y) + '.jpg')

                patch_rgb.save(output_image_name)

    # from repiece_jpg_tiles.py @author Jason
    def get_image_paths(self, folder):
        image_paths = [join(folder, f) for f in listdir(folder) if isfile(join(folder, f))]
        if join(folder, '.DS_Store') in image_paths:
            image_paths.remove(join(folder, '.DS_Store'))
        return image_paths

    # from repiece_jpg_tiles.py @author Jason
    def get_subfolder_paths(self, folder):
        subfolder_paths = [join(folder, f) for f in listdir(folder) if
                           (isdir(join(folder, f)) and '.DS_Store' not in f)]
        if join(folder, '.DS_Store') in subfolder_paths:
            subfolder_paths.remove(join(folder, '.DS_Store'))
        return subfolder_paths

    # from repiece_jpg_tiles.py @author Jason
    def get_num_horizontal_positions(self, input_folder):
        horizontal_positions = []
        image_paths = self.get_image_paths(input_folder)
        for image_path in image_paths:
            x_increment = int(image_path.split('/')[-1].split('.')[0].split('_')[1])
            horizontal_positions.append(x_increment)
        return len(set(horizontal_positions))

    # from repiece_jpg_tiles.py @author Jason
    def get_num_vertical_positions(self, input_folder):
        vertical_positions = []
        image_paths = self.get_image_paths(input_folder)
        for image_path in image_paths:
            x_increment = int(image_path.split('/')[-1].split('.')[0].split('_')[2])
            vertical_positions.append(x_increment)
        return len(set(vertical_positions))

    # from repiece_jpg_tiles.py @author Jason
    def output_repieced_image(self, input_folder, output_image_path):
        num_horizontal_positions = self.get_num_horizontal_positions(input_folder)
        num_vertical_positions = self.get_num_vertical_positions(input_folder)

        image_paths = self.get_image_paths(input_folder)
        images = map(Image.open, image_paths)
        widths, heights = zip(*(i.size for i in images))

        last_width = min(widths)
        last_height = min(heights)

        total_width = (num_horizontal_positions - 1) * self.compressed_window_size + last_width
        total_height = (num_vertical_positions - 1) * self.compressed_window_size + last_height

        new_im = Image.new('RGB', (total_width, total_height))

        for image_path in image_paths:
            x_increment = int(image_path.split('/')[-1].split('.')[0].split('_')[1])
            y_increment = int(image_path.split('/')[-1].split('.')[0].split('_')[2])

            image = Image.open(image_path)
            new_im.paste(image, (self.compressed_window_size * x_increment, self.compressed_window_size * y_increment))

        new_im.save(output_image_path)

    def convert(self):
        image_names = [f for f in listdir(self.input_folder) if isfile(join(self.input_folder, f))]
        if '.DS_Store' in image_names:
            image_names.remove('.DS_Store')

        for image_name in image_names:
            full_image_path = self.input_folder + '/' + image_name
            tiles_path = self.tiles_folder + '/'
            print(full_image_path)
            print(tiles_path)
            self.output_jpeg_tiles(full_image_path, tiles_path)  # svs to jpg tiles

        input_subfolders = self.get_subfolder_paths(self.tiles_folder)
        for input_subfolder in input_subfolders:
            output_image_path = join(self.output_folder, input_subfolder.split('/')[-1] + '.jpg')
            print(input_subfolder, output_image_path)
            self.output_repieced_image(input_subfolder, output_image_path)  # jpg tiles to full jpg image


if __name__ == "__main__":
    import os 

    input_folder = os.getcwd()+'/img/'
    svs_to_jpg_converter = SvsToJpgConverter(input_folder, 7.5)
    svs_to_jpg_converter.convert()
    #for i in [1,2,3]:
    #    tr = myThread(i)
    #    tr.start()
    #    threads.append(tr)
    #for tr in threads:
    #    tr.join()
