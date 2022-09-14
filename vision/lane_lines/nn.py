

from lib.config import cfg
from lib.config import update_config
from lib.utils.utils import create_logger, select_device, time_synchronized
from lib.models import get_net
from lib.dataset import LoadImages, LoadStreams
from lib.core.general import non_max_suppression, scale_coords
from lib.utils import plot_one_box, show_seg_result
from lib.core.function import AverageMeter
from lib.core.postprocess import morphological_process, connect_lane
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
from tqdm import tqdm
import random
import argparse
import pixel_angles
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

scale = 0.5

height = 480/scale
width = 640/scale

# TODO: verify this value
shapes = ((height, width), ((0.0, scale), (0.0, 0.0)))
device = torch.device('cpu')
weights = "weights/End-to-end.pth"

# Load model
model = get_net(cfg)
checkpoint = torch.load(weights, map_location=device)
model.load_state_dict(checkpoint['state_dict'])
model = model.to(device)

model.eval()
# model.cuda()

print("loaded model")


def detect(img, path):
    return get_lane_points(img, path)


def get_lane_points(img, path):
    frame = img
    img = transform(img).to(device)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    det_out, da_seg_out, ll_seg_out = model(img)
    _, _, height, width = img.shape
    pad_w, pad_h = shapes[1][1]
    pad_w = int(pad_w)
    pad_h = int(pad_h)
    ratio = shapes[1][0][1]

    da_predict = da_seg_out[:, :, 0:height, 0:width]
    da_seg_mask = torch.nn.functional.interpolate(
        da_predict, scale_factor=int(1/ratio), mode='bilinear')
    _, da_seg_mask = torch.max(da_seg_mask, 1)
    da_seg_mask = da_seg_mask.int().squeeze().cpu().numpy()
    # da_seg_mask = morphological_process(da_seg_mask, kernel_size=7)

    ll_predict = ll_seg_out[:, :, 0:height, 0:width]
    ll_seg_mask = torch.nn.functional.interpolate(
        ll_predict, scale_factor=int(1/ratio), mode='bilinear')
    _, ll_seg_mask = torch.max(ll_seg_mask, 1)
    ll_seg_mask = ll_seg_mask.int().squeeze().cpu().numpy()

    img_det = show_seg_result(
        frame, (da_seg_mask, ll_seg_mask), _, _, is_demo=True)

    name_suffix = path.split('\\')[-1]

    # Lane line post-processing
    ll_seg_mask = morphological_process(
        ll_seg_mask, kernel_size=7, func_type=cv2.MORPH_OPEN)
    ll_seg_mask, lines = connect_lane(ll_seg_mask)
    cv2.imwrite(f"{out_dir}/da_seg_mask_{name_suffix}", da_seg_mask)
    cv2.imwrite(f"{out_dir}/img_det_{name_suffix}", img_det)
    cv2.imwrite(f"{out_dir}/ll_seg_mask_{name_suffix}", ll_seg_mask)
    cv2.imwrite(f"{out_dir}/img_{name_suffix}", frame)
    # cv2.imwrite('output.png', ll_seg_mask)
    cv2.imshow('img_det', img_det)
    cv2.imshow('ll_seg_mask', cv2.resize(
        ll_seg_mask, (640, 480), interpolation=cv2.INTER_AREA))
    return lines


# Identify and generate left and right lane line positions + angles
def retrieve_lanes(lines, path):
    left_lane = None
    right_lane = None
    results = {}
    for line in lines:
        line = list(line)
        x_intercept, dx_sign, angle, x0, y0, x1, y1 = pixel_angles.get_line_equations(
            line, 0, (0, 0), (0, -15), 0.175)
        # line, 0, (0, 0), (0, -15.55), 0.195)

        # print(x_intercept, dx_sign, angle, x0, y0)

        if not angle or not x_intercept:  # No points on road, or horizontal
            continue

        elif x_intercept < 320 and dx_sign >= 0:  # Left side, pointing right
            if left_lane:
                if x_intercept > left_lane[0]:  # Find closest to center
                    left_lane = (x_intercept, dx_sign, angle, x0, y0)
                    results['left'] = {
                        'x_intercept': x_intercept, 'dx_sign': dx_sign, 'angle': angle, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
            else:
                left_lane = (x_intercept, dx_sign, angle, x0, y0)
                results['left'] = {'x_intercept': x_intercept,
                                   'dx_sign': dx_sign, 'angle': angle, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
        if x_intercept > 320 and dx_sign <= 0:  # Right side, pointing left
            if right_lane:
                if x_intercept < right_lane[0]:  # Find closest to center
                    right_lane = (x_intercept, dx_sign, angle, x0, y0)
                    results['right'] = {
                        'x_intercept': x_intercept, 'dx_sign': dx_sign, 'angle': angle, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
            else:
                right_lane = (x_intercept, dx_sign, angle, x0, y0)
                results['right'] = {'x_intercept': x_intercept,
                                    'dx_sign': dx_sign, 'angle': angle, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}

    name_suffix = path.split('\\')[-1]
    print(results)
    open(f"{out_dir}/results_{name_suffix.replace('.jpg', '.json').replace('.png', '.json')}",
         'w').write(json.dumps(results))
    return left_lane, right_lane


out_dir = 'calibration'
# images = glob.glob('./parking_lanes/*.jpg')
# images = glob.glob('./lane_pictures/costco_9_7/*.png')
# images = glob.glob('./lane_pictures/neighberhood_9_9/img_1*.png')
# images = ['.\\lane_pictures\\costco_9_7\\img_1662576257_4.png']
# images = ['C://Users/rando/Downloads\img_1662757721_7.png']
images = ['C://Users/rando/Downloads\img_1662941406_0.png']
if __name__ == '__main__':
    # path = "inference/input/img_1661985240_1.png"
    # path = "mirv_lane_lines.png"
    # path = "img_01.png"
    for path in images:
        print(path)
        img = cv2.imread(path)
        img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)

        lane_lines = detect(img, path)
        lanes = retrieve_lanes(lane_lines, path)
        # cv2.waitKey()
