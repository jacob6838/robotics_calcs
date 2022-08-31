# importing the necessary libraries
import cv2
import numpy as np
import copy
import math

# path = "./FRC team 1690 Orbit 2020 robot reveal - CHESTER_Moment.jpg"
# path = "./118_trimmed_in_air_blurry.jpg"
path = "./orbit_in_air_3.jpg"
cv2.namedWindow("TrackedBars")
cv2.resizeWindow("TrackedBars", 640, 240)


def is_inside_other_circles(i, sorted_circles):
    for j in range(i):
        if math.sqrt((int(sorted_circles[i][0]) - int(sorted_circles[j][0])) ** 2 + (int(sorted_circles[i][1]) - int(sorted_circles[j][1])) ** 2) <= sorted_circles[j][2]:
            return True
    return False


def on_trackbar(val):
    minDist = cv2.getTrackbarPos("minDist", "TrackedBars")
    param1 = cv2.getTrackbarPos("param1", "TrackedBars")
    param2 = cv2.getTrackbarPos("param2", "TrackedBars")
    minRadius = cv2.getTrackbarPos("minRadius", "TrackedBars")
    maxRadius = cv2.getTrackbarPos("maxRadius", "TrackedBars")

    # lower = np.array([hue_min, sat_min, val_min])
    # upper = np.array([hue_max, sat_max, val_max])

    # imgMASK = cv2.inRange(hsv, lower, upper)

    # Thresh = cv2.adaptiveThreshold(mask, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    #                                cv2.THRESH_BINARY_INV, 11, 2)

    # cv2.imshow('Thresh', Thresh)

    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1,
                               param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    cv2.imshow("Output1", img)

    modifiedImage = cv2.cvtColor(mask, 0)
    if circles is not None:
        circles = np.uint16(np.around(circles))  # x, y, radius
        circles = circles[0, :]
        red_circles = []
        green_circles = []
        sorted_circles = sorted(circles, key=lambda cir: -cir[2])
        print(sorted_circles)
        for i in range(len(sorted_circles)):
            if is_inside_other_circles(i, sorted_circles):
                red_circles.append(sorted_circles[i])
            else:
                green_circles.append(sorted_circles[i])

        for i in green_circles:
            cv2.circle(modifiedImage, (i[0], i[1]), i[2], (0, 255, 0), 2)
        for i in red_circles:
            cv2.circle(modifiedImage, (i[0], i[1]), i[2], (0, 0, 255), 2)

    cv2.imshow("Output1", img)
    cv2.imshow("Mask", mask)
    cv2.imshow('circles', modifiedImage)


cv2.createTrackbar("minDist", "TrackedBars", 1, 255, on_trackbar)
cv2.createTrackbar("param1", "TrackedBars", 1, 1000, on_trackbar)
cv2.createTrackbar("param2", "TrackedBars", 1, 50, on_trackbar)
cv2.createTrackbar("minRadius", "TrackedBars", 1, 500, on_trackbar)
cv2.createTrackbar("maxRadius", "TrackedBars", 1, 500, on_trackbar)

cv2.setTrackbarPos("minDist", "TrackedBars", 30)
cv2.setTrackbarPos("param1", "TrackedBars", 100)
cv2.setTrackbarPos("param2", "TrackedBars", 25)
cv2.setTrackbarPos("minRadius", "TrackedBars", 15)
cv2.setTrackbarPos("maxRadius", "TrackedBars", 115)


img = cv2.imread(path)


img = cv2.resize(img, (1280, 720), fx=0, fy=0,
                 interpolation=cv2.INTER_CUBIC)

# Display the resulting frame
# cv2.imshow('Frame', img)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# lower_red = np.array([16, 86, 17])
# upper_red = np.array([33, 255, 255])
# lower_red = np.array([16, 78, 100])
# upper_red = np.array([50, 195, 255])
lower_red = np.array([19, 102, 114])
upper_red = np.array([43, 255, 255])

mask = cv2.inRange(hsv, lower_red, upper_red)

# cv2.imshow('mask', mask)

# minDist = 60
# param1 = 10  # 500
# param2 = 10  # 200 #smaller value-> more false circles
# minRadius = 30
# maxRadius = 60  # 10

# circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1,
#                            param2=param2, minRadius=minRadius, maxRadius=maxRadius)

# if circles is not None:
#     circles = np.uint16(np.around(circles))
#     for i in circles[0, :]:
#         cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)

# cv2.imshow('circles', img)


on_trackbar(0)

cv2.waitKey()
