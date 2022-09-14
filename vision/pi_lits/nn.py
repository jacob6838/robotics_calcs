import time
import os
import shutil
from pathlib import Path
import torch
import torch.backends.cudnn as cudnn
import cv2
import numpy as np
import math
import torchvision.transforms as transforms
import glob
import json

# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


normalize = transforms.Normalize(
    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
)

transform = transforms.Compose([
    transforms.ToTensor(),
    normalize,
])

intakeSide = "switch_right"

runningNeuralNetwork = True
# global intakeSide
# intakeSide = "switch_right"

detections = 0

hFOV = 63
horizontalPixels = 640
verticalPixels = 480
degreesPerPixel = hFOV/horizontalPixels


device = torch.device('cuda:0')
half = device.type != 'cpu'

piLitModel = torch.load("weights/piLitModel.pth",
                        map_location='cpu')  # , map_location='cpu'
# piLitModel.cuda()
piLitModel.eval()
piLitModel.to(device)


print("loaded model")


def detect(img, path):
    return piLitDetect(img, path)


def piLitDetect(img, path):
    frame = img
    frame_orig = frame
    img = transform(img).to(device)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    mod_out = piLitModel(img)
    print(mod_out)
    piLitPrediction = mod_out[0]
    bboxList = []
    # print("DETECTING...")
    closest_track_location = None
    closest_track_distance = 5
    for bbox, score in zip(piLitPrediction["boxes"], piLitPrediction["scores"]):
        print(score, bbox)
        if(score > 0.85 or True):
            # print("GOT A PI LIT")
            x0, y0, x1, y1 = bbox
            centerX = int((x0 + x1)/2)
            centerY = int((y0 + y1)/2)
            bboxList.append(bbox)

            color = (0, 255, 0)
            if score > 0.85:
                color = (0, 255, 0)
            elif score > 0.5:
                color = (0, 255, 255)
            else:
                color = (0, 0, 255)

            frame = cv2.rectangle(frame, (int(x0), int(y0)),
                                  (int(x1), int(y1)), color, 3)

            angleToPiLit = math.radians(
                (centerX - horizontalPixels/2) * degreesPerPixel)

            continue

            depth = (depthFrame[centerY][centerX])/1000

            if(intakeSide == "switch_right"):
                intakeOffset = -0.0635
            else:
                intakeOffset = 0.0635

            complementaryAngle = math.pi/2 - angleToPiLit

            horizontalOffsetToPiLit = (depth * math.cos(complementaryAngle))

            verticalOffsetToPiLit = math.sqrt(
                (math.pow(depth, 2) - math.pow(horizontalOffsetToPiLit, 2)))

            if(depth < 3 and depth != 0):
                if depth < closest_track_distance:
                    closest_track_distance = depth
                    # angleToPiLitFromIntake = math.degrees(angleToPiLit)
                    angleToPiLitFromIntake = math.degrees(math.atan2(
                        horizontalOffsetToPiLit + intakeOffset, verticalOffsetToPiLit))
                    piLitLocation = [depth, angleToPiLitFromIntake]

                    locations = Float64MultiArray()
                    locations.data = piLitLocation
                    closest_track_location = locations

            else:
                angleToPiLitFromIntake = math.degrees(angleToPiLit)
            print("DEPTH: ", depth, " ORIGINAL ANGLE: ", math.degrees(
                angleToPiLit), "ANGLE: ", (angleToPiLitFromIntake), " SCORE: ", score)

    name_suffix = path.split('\\')[-1]
    cv2.imwrite(f"{out_dir}/img_det_{name_suffix}", frame)
    # cv2.imwrite(f"{out_dir}/img_{name_suffix}", frame_orig)
    cv2.imshow(name_suffix, frame)
    return bboxList

    if closest_track_location is not None:
        piLitLocationPub.publish(closest_track_location)


out_dir = 'calibration'
# images = glob.glob('./parking_lanes/*.jpg')
# images = glob.glob('./lane_pictures/costco_9_7/*.png')
# images = glob.glob('./lane_pictures/neighberhood_9_9/img_1*.png')
# images = ['.\\lane_pictures\\costco_9_7\\img_1662576257_4.png']
# images = ['C://Users/rando/Downloads\img_1662757721_7.png']
# images = ['C://Users/rando/Downloads\img_1662941406_0.png']
# images = glob.glob('C://Users/rando/Downloads/pilit_pictures/*.png')
# images = ['C://Users/rando/Downloads/pilit_pictures/img_1663014081_58.png']
images = [
    'C://Users/rando/Downloads/pilit_pictures/img_1663014081_100.png',
    'C://Users/rando/Downloads/pilit_pictures/img_1663014081_571.png',
    'C://Users/rando/Downloads/pilit_pictures/img_1663014081_542.png',
    'C://Users/rando/Downloads/pilit_pictures/img_1663014081_58.png']
# images = ['C://Users/rando/Downloads/pilit_pictures/img_1663014081_571.png']
i = 0
if __name__ == '__main__':
    # path = "inference/input/img_1661985240_1.png"
    # path = "mirv_lane_lines.png"
    # path = "img_01.png"
    for path in images:
        print(path)
        img = cv2.imread(path)
        img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
        # img = cv2.flip(img, 1)
        # img = cv2.flip(img, 0)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        brown_lo = np.array([0, 0, 0])
        brown_hi = np.array([255, 6, 255])

        # Mask image to only select browns
        mask = cv2.inRange(hsv, brown_lo, brown_hi)
        img[mask > 0] = (50, 50, 50)

        # Change image to red where we found brown

        pi_lits = piLitDetect(img, path)

        pi_lits = detect(img, path)
        # print(pi_lits)
        # print(i)
        i += 1
    cv2.waitKey()
