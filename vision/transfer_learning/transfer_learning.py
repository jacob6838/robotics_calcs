# Importing MobileNet V2
from keras.applications.mobilenet_v2 import preprocess_input, MobileNetV2
import cv2
import imageio
import glob
import numpy as np

model = MobileNetV2(weights='imagenet')

# Loading the data ang generating labels

data = np.empty((155, 480, 640, 3))
for i, f in enumerate(glob.glob('./pi_lit_images/*')):
    img = cv2.imread(f)
    img = preprocess_input(img)
    # img = cv2.resize(img, (640, 480))
    data[i] = img
