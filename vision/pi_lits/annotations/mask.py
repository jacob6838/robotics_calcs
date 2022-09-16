import glob
import cv2
import numpy as np

images = glob.glob('./images_2/*')
i = 0
if __name__ == '__main__':
    for path in images:
        # print(path)
        img = cv2.imread(path)
        # img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask_lo = np.array([0, 53, 0])
        mask_hi = np.array([38, 255, 255])

        # # Mask image to only select browns
        mask = cv2.inRange(hsv, mask_lo, mask_hi)
        img[mask <= 0] = (0, 0, 0)

        name_suffix = path.split('\\')[-1]
        cv2.imwrite(f"images_masked/{name_suffix}", img)
