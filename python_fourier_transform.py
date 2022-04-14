import numpy as np
import sys
import matplotlib.pyplot as plt
from skimage.io import imread, imshow
from skimage.color import rgb2hsv, rgb2gray, rgb2yuv
from skimage import color, exposure, transform
from skimage.exposure import equalize_hist


def main():
    if len(sys.argv) <= 1 or not sys.argv[1]:
        print("Error: Please specify an image path, with: python .\python_fourier_transform.py \"image.png\"")
        return
    IMAGE_FILE_NAME = sys.argv[1]

    try:
        dark_image_grey = imread(IMAGE_FILE_NAME)
    except:
        print(
            f"Error: The image {IMAGE_FILE_NAME} does not exist. Please ensure it is place in the this directory and spelled correctly")
        return

    try:
        dark_image_grey = rgb2gray(dark_image_grey)
    except ValueError:
        pass

    # Comment this line if the image is in gray scale

    plt.figure(num=None, figsize=(8, 6), dpi=80)
    plt.imshow(dark_image_grey, cmap='gray')

    dark_image_grey_fourier = np.fft.fftshift(np.fft.fft2(dark_image_grey))
    plt.figure(num=None, figsize=(8, 6), dpi=80)
    plt.imshow(np.log(abs(dark_image_grey_fourier)), cmap='gray')

    plt.show()


if __name__ == "__main__":
    main()
