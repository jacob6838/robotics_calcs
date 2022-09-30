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
import copy

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

piLitModel = torch.load("weights/pi_lit_model_11.pth")  # , map_location='cpu'

# piLitModel = torch.load("weights/piLitModel.pth")  # , map_location='cpu'
# piLitModel.cuda()
piLitModel.eval()
piLitModel.to(device)


print("loaded model")


def detect(img, path):
    return piLitDetect(img, path)


def piLitDetect(img, path):
    frame = img
    img = transform(img).to(device)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    mod_out = piLitModel(img)
    piLitPrediction = mod_out[0]
    bboxList = []
    # print("DETECTING...")
    closest_track_location = None
    closest_track_distance = 5
    for bbox, score in zip(piLitPrediction["boxes"], piLitPrediction["scores"]):
        # print(score, bbox)
        if(score > 0.85 or True):
            # print("GOT A PI LIT")
            x0, y0, x1, y1 = bbox

            # if x0 == 0 or x1 == horizontalPixels or y0 == 0 or y1 == verticalPixels:
            #     print("Ignoring detection at edge")
            #     continue

            # if abs(x1 - x0) < 30 or abs(y1 - y0) < 8:  # abs((x1 - x0) * (y1 - y0)) < 200
            #     print("Ignoring small detection")
            #     continue

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

    name_suffix = path.split('\\')[-1].split('/')[-1]
    # cv2.imwrite(f"{out_dir}_orig/no_mask_{name_suffix}", frame_orig)
    cv2.imshow(name_suffix, frame)
    subdir = "no_matches"
    if len(bboxList) == 0:
        subdir = "no_matches"
    elif len(bboxList) == 1:
        subdir = "1_match"
    elif len(bboxList) == 2:
        subdir = "2_matches"
    elif len(bboxList) >= 3:
        subdir = "many_matches"
    print(subdir)
    # cv2.imwrite(f"{out_dir}/{subdir}/{name_suffix}", frame)
    return bboxList

    if closest_track_location is not None:
        piLitLocationPub.publish(closest_track_location)


out_dir = 'model_2'
# images = glob.glob('./pilit_pictures/*.png')
images = glob.glob('C://Users/rando/Downloads/pilit_pictures/*.png')
# images = ['./pilit_pictures/img_1663014081_59.png']
# images = ['C://Users/rando/Downloads/pilit_pictures/img_1663014081_418.png']
images = ['C://Users/rando/Downloads/pilit_pictures/img_1663014081_572.png']
i = 0
found = 0

singles = []
doubles = []
many = []
none = []
if __name__ == '__main__':
    for path in images:
        try:
            print(path)
            img = cv2.imread(path)
            img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
            # img = cv2.flip(img, 1)
            # img = cv2.flip(img, 0)

            # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # mask_lo = np.array([0, 53, 0])
            # mask_hi = np.array([38, 255, 255])

            # # # Mask image to only select browns
            # mask = cv2.inRange(hsv, mask_lo, mask_hi)
            # img[mask <= 0] = (0, 0, 0)

            # name_suffix = path.split('\\')[-1]
            # print(cv2.imwrite(f"{out_dir}/img_det_{name_suffix}", img))

            # Change image to red where we found brown

            pi_lits = piLitDetect(img, path)
            if pi_lits:
                found += 1
            if len(pi_lits) == 0:
                none.append(path)
            elif len(pi_lits) == 1:
                singles.append(path)
            elif len(pi_lits) == 2:
                doubles.append(path)
            elif len(pi_lits) >= 3:
                many.append(path)
            # print(pi_lits)
            # print(i)
            i += 1
            cv2.waitKey()
        except Exception as e:
            print("ERROR:", e)

print(len(singles), len(none), len(doubles), len(many))
# print("Singles:", singles)
# print("Doubles:", doubles)
# print("Many:", many)
# print("None:", none)
print(found/i, found, i)
