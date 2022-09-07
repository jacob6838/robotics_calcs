import depthai
import cv2
import nn
import time

pipeline = depthai.Pipeline()

# creating rgb camera
cam_rgb = pipeline.create(depthai.node.ColorCamera)
cam_rgb.setResolution(
    depthai.ColorCameraProperties.SensorResolution.THE_12_MP)
cam_rgb.setInterleaved(False)
# cam_rgb.setIspScale(12, 19)
# cam_rgb.setPreviewSize(2560, 1920)
cam_rgb.setIspScale(6, 35)  # 696,522
cam_rgb.setPreviewSize(696, 522)
cam_rgb.setColorOrder(depthai.ColorCameraProperties.ColorOrder.RGB)

# full fov frame
xoutIsp = pipeline.create(depthai.node.XLinkOut)
xoutIsp.setStreamName("isp")
cam_rgb.isp.link(xoutIsp.input)

# creating imu stream and enabling imu sensor
imu = pipeline.createIMU()
xlinkOut = pipeline.createXLinkOut()
xlinkOut.setStreamName("imu")
imu.enableIMUSensor(
    depthai.IMUSensor.ARVR_STABILIZED_GAME_ROTATION_VECTOR, 400)
imu.setBatchReportThreshold(1)
imu.setMaxBatchReports(10)
imu.out.link(xlinkOut.input)

# creating stream for rgb frames and camera config
xout_rgb = pipeline.create(depthai.node.XLinkOut)
configIn = pipeline.create(depthai.node.XLinkIn)
configIn.setStreamName('config')
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)
controlIn = pipeline.create(depthai.node.XLinkIn)
controlIn.setStreamName('control')
controlIn.out.link(cam_rgb.inputControl)

# Define a source - two mono (grayscale) cameras
monoLeft = pipeline.createMonoCamera()
monoRight = pipeline.createMonoCamera()
stereo = pipeline.createStereoDepth()
spatialLocationCalculator = pipeline.createSpatialLocationCalculator()

# create streams for depth data
xoutDepth = pipeline.createXLinkOut()
xoutSpatialData = pipeline.createXLinkOut()
xinSpatialCalcConfig = pipeline.createXLinkIn()
xoutDepth.setStreamName("depth")
xoutSpatialData.setStreamName("spatialData")
xinSpatialCalcConfig.setStreamName("spatialCalcConfig")

# MonoCamera
monoLeft.setResolution(depthai.MonoCameraProperties.SensorResolution.THE_720_P)
monoLeft.setBoardSocket(depthai.CameraBoardSocket.LEFT)
monoRight.setResolution(
    depthai.MonoCameraProperties.SensorResolution.THE_720_P)
monoRight.setBoardSocket(depthai.CameraBoardSocket.RIGHT)

# depth settings
outputDepth = True
outputRectified = False
lrcheck = True
subpixel = False
extended = True

# StereoDepth
stereo.setOutputDepth(outputDepth)
stereo.setOutputRectified(outputRectified)
stereo.setConfidenceThreshold(255)
stereo.setDepthAlign(depthai.CameraBoardSocket.RGB)
stereo.setOutputSize(640*4, 480*4)
stereo.setLeftRightCheck(lrcheck)
stereo.setSubpixel(subpixel)
# stereo.setExtendedDisparity(extended)
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)
stereo.depth.link(xoutDepth.input)

topLeft = depthai.Point2f(0.4, 0.4)
bottomRight = depthai.Point2f(0.6, 0.6)

spatialLocationCalculator.setWaitForConfigInput(False)
config = depthai.SpatialLocationCalculatorConfigData()
config.depthThresholds.lowerThreshold = 0
config.depthThresholds.upperThreshold = 10000
config.roi = depthai.Rect(topLeft, bottomRight)
spatialLocationCalculator.initialConfig.addROI(config)
spatialLocationCalculator.out.link(xoutSpatialData.input)
xinSpatialCalcConfig.out.link(spatialLocationCalculator.inputConfig)

expTime = 1
sensIso = 0

# finding device by specific ip
found, device_info = depthai.Device.getDeviceByMxId("10.0.20.2")
depthaiDevice = depthai.Device(pipeline, device_info)
depthaiDevice.startPipeline()

# create queues
q_rgb = depthaiDevice.getOutputQueue("rgb", maxSize=1, blocking=False)
depthQueue = depthaiDevice.getOutputQueue(
    name="depth", maxSize=1, blocking=False)
spatialCalcQueue = depthaiDevice.getOutputQueue(
    name="spatialData", maxSize=1, blocking=False)
spatialCalcConfigInQueue = depthaiDevice.getInputQueue("spatialCalcConfig")
qIsp = depthaiDevice.getOutputQueue("isp", maxSize=1, blocking=False)
frame = None
imuQueue = depthaiDevice.getOutputQueue(name="imu", maxSize=1, blocking=False)
disparityMultiplier = 255 / stereo.getMaxDisparity()
controlQueue = depthaiDevice.getInputQueue('control')
ctrl = depthai.CameraControl()
ctrl.setAutoFocusMode(depthai.CameraControl.AutoFocusMode.CONTINUOUS_PICTURE)
ctrl.setAutoWhiteBalanceMode(
    depthai.CameraControl.AutoWhiteBalanceMode.WARM_FLUORESCENT)
controlQueue.send(ctrl)


i = 0
run = round(time.time())
while True:
    in_rgb = q_rgb.tryGet()
    if in_rgb is not None:
        frame = qIsp.get().getCvFrame()
        resizedFrame = cv2.resize(
            frame, (640, 480), interpolation=cv2.INTER_LINEAR)
        cv2.imshow('frame', frame)

        key = cv2.waitKey(3)
        if key == ord('q'):
            break
        elif key == ord('t'):  # Quit
            path = f'{run}_{i}.png'

            # out_dir = 'calibration'
            # name_suffix = path.split('\\')[-1]
            # cv2.imwrite(f"{out_dir}/source_{name_suffix}", resizedFrame)
            i += 1
            # continue
            lane_lines = nn.detect(resizedFrame, path)
            lanes = nn.retrieve_lanes(lane_lines, path)
