# importing the necessary libraries
import cv2
import numpy as np

# Creating a VideoCapture object to read the video
# video_path = 'FRC team 1690 Orbit 2020 robot reveal - CHESTER.mp4'
video_path = './118_trimmed.mp4'
# video_path = './Team 118 Robonauts 2020.mp4'
cap = cv2.VideoCapture(video_path)


# Loop until the end of the video
while (cap.isOpened()):

    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1280, 720), fx=0, fy=0,
                       interpolation=cv2.INTER_CUBIC)

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower_red = np.array([16, 86, 17])
    # upper_red = np.array([33, 255, 255])

    # lower_red = np.array([8, 71, 118])
    # upper_red = np.array([63, 216, 255])
    # lower_red = np.array([8, 71, 118])
    # upper_red = np.array([63, 216, 255])
    # lower_red = np.array([16, 78, 100])
    # upper_red = np.array([50, 195, 255])
    # lower_red = np.array([19, 102, 114])
    # upper_red = np.array([43, 255, 255])
    # lower_red = np.array([29, 84, 167])
    # upper_red = np.array([39, 253, 255])
    lower_red = np.array([20, 84, 130])
    upper_red = np.array([39, 253, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)

    cv2.imshow('mask', mask)

    # adaptive thresholding to use different threshold
    # values on different regions of the frame.
    Thresh = cv2.adaptiveThreshold(mask, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    cv2.imshow('Thresh', Thresh)

    # minDist = 20*3
    # param1 = 10  # 500
    # param2 = 20  # 200 #smaller value-> more false circles
    # minRadius = 5*2
    # maxRadius = 60*3  # 10

    minDist = 30
    param1 = 1000  # 500
    param2 = 22  # 200 #smaller value-> more false circles
    minRadius = 10
    maxRadius = 115  # 10

    circles = cv2.HoughCircles(Thresh, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1,
                               param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    mask2 = cv2.cvtColor(Thresh, 0)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            cv2.circle(mask2, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # print(len(circles))

    cv2.imshow('circles', mask2)

    # define q as the exit button
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break


# release the video capture object
cap.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()
