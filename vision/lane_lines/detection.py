# importing the necessary libraries
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, freqz

FRAME_RATE = 960

# Creating a VideoCapture object to read the video
# video_path = './FRC team 1690 Orbit 2020 robot reveal - CHESTER.mp4'
video_path = './thrown_ball.mp4'
# video_path = './Team 118 Robonauts 2020.mp4'
# out = cv2.VideoWriter('output.avi', -1, 20.0, (1280, 720))
cap = cv2.VideoCapture(video_path)


def is_inside_other_circles(i, sorted_circles):
    for j in range(i):
        if math.sqrt((int(sorted_circles[i][0]) - int(sorted_circles[j][0])) ** 2 + (int(sorted_circles[i][1]) - int(sorted_circles[j][1])) ** 2) <= sorted_circles[j][2]:
            return True
    return False


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


ball_path = []

# Loop until the end of the video
while (cap.isOpened()):

    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (1280, 720), fx=0, fy=0,
                       interpolation=cv2.INTER_CUBIC)

    # Display the resulting frame
    # cv2.imshow('Frame', frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower_red = np.array([16, 86, 17])
    # upper_red = np.array([33, 255, 255])

    # lower_red = np.array([8, 71, 118])
    # upper_red = np.array([63, 216, 255])
    # lower_red = np.array([8, 71, 118])
    # upper_red = np.array([63, 216, 255])
    # lower_red = np.array([16, 78, 100])
    # upper_red = np.array([50, 195, 255])
    lower_red = np.array([19, 102, 114])
    upper_red = np.array([43, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)

    # cv2.imshow('mask', mask)

    # adaptive thresholding to use different threshold
    # values on different regions of the frame.
    Thresh = cv2.adaptiveThreshold(mask, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # cv2.imshow('Thresh', Thresh)

    # minDist = 20*3
    # param1 = 10  # 500
    # param2 = 20  # 200 #smaller value-> more false circles
    # minRadius = 5*2
    # maxRadius = 60*3  # 10

    minDist = 30
    param1 = 100  # 500
    param2 = 22  # 200 #smaller value-> more false circles
    minRadius = 15
    maxRadius = 100  # 10

    circles = cv2.HoughCircles(Thresh, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1,
                               param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    mask2 = cv2.cvtColor(Thresh, 0)

    if circles is not None:
        circles = np.uint16(np.around(circles))

        circles = circles[0, :]
        red_circles = []
        green_circles = []
        sorted_circles = sorted(circles, key=lambda cir: -cir[2])
        # print(sorted_circles)
        for i in range(len(sorted_circles)):
            if is_inside_other_circles(i, sorted_circles):
                red_circles.append(sorted_circles[i])
            else:
                green_circles.append(sorted_circles[i])

        ball_path.append(green_circles[0])

        for i in green_circles:
            cv2.circle(mask2, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # print(len(circles))

    # cv2.imshow('circles', mask2)

    # define q as the exit button
    if 0xFF == ord('q'):  # cv2.waitKey(25) &
        break

print(ball_path)

# release the video capture object
cap.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()


def average_positions(positions):
    average = [0, 0, 0]
    for pos in positions:
        for i in range(len(pos)):
            average[i] += pos[i]
    for i in range(len(average)):
        average[i] /= len(positions)
    return average


def distance(pos1, pos2):
    return math.sqrt((float(pos1[0]) - float(pos2[0]))**2 + (float(pos1[1]) - float(pos2[1]))**2)


def xdistance(pos1, pos2):
    return math.sqrt((float(pos1[0]) - float(pos2[0]))**2)


def ydistance(pos1, pos2):
    return math.sqrt((float(pos1[1]) - float(pos2[1]))**2)


previous_positions = []
for i in range(50):
    previous_positions.append(ball_path[0])
filtered_positions = []
time = []

x = []
y = []


for i in range(len(ball_path)):
    previous_positions = previous_positions[1:]
    previous_positions.append(ball_path[i])
    filtered_positions.append(average_positions(previous_positions))
    # filtered_positions.append(ball_path[i])
    time.append(i/FRAME_RATE)
    x.append(filtered_positions[i][0])
    y.append(720-filtered_positions[i][1])

print(x)
print(y)


# # Filter requirements.
# order = 6
# fs = FRAME_RATE       # sample rate, Hz
# cutoff = 20  # desired cutoff frequency of the filter, Hz

# x_position_filtered = butter_lowpass_filter(x, cutoff, fs, order)
# y_position_filtered = butter_lowpass_filter(y, cutoff, fs, order)

fig, axs = plt.subplots(2, 2)

axs[0, 0].plot(x, y)
axs[0, 0].set_xlim([0, 1280])
axs[0, 0].set_ylim([0, 720])
axs[0, 0].set_title('Position')
# axs[0].xlim([0, 1280])
# axs[0].ylim([0, 720])

velocities = []
x_velocities = []
y_velocities = []
# velocities_filtered = []
# x_velocities_filtered = []
# y_velocities_filtered = []
for i in range(1, len(filtered_positions)):
    # velocities_filtered.append((distance([x_position_filtered[i-1], y_position_filtered[i-1]], [
    #                            x_position_filtered[i], y_position_filtered[i]]) * 7/70) * FRAME_RATE)
    # x_velocities_filtered.append((xdistance([x_position_filtered[i-1], y_position_filtered[i-1]], [
    #                              x_position_filtered[i], y_position_filtered[i]]) * 7/70) * FRAME_RATE)
    # y_velocities_filtered.append((ydistance([x_position_filtered[i-1], y_position_filtered[i-1]], [
    #                              x_position_filtered[i], y_position_filtered[i]]) * 7/70) * FRAME_RATE)
    velocities.append(
        (distance(filtered_positions[i-1], filtered_positions[i]) * 7/70) * FRAME_RATE)
    x_velocities.append(
        (xdistance(filtered_positions[i-1], filtered_positions[i]) * 7/70) * FRAME_RATE)
    y_velocities.append(
        (ydistance(filtered_positions[i-1], filtered_positions[i]) * 7/70) * FRAME_RATE)


axs[0, 1].plot(time[:-1], velocities)
axs[0, 1].set_title('Velocity')

axs[1, 0].plot(time[:-1], x_velocities)
axs[1, 0].set_title('X Velocity')

axs[1, 1].plot(time[:-1], y_velocities)
axs[1, 1].set_title('Y Velocity')


plt.show()
