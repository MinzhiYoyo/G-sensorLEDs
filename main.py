from particle import update_information
import time
import cv2
import numpy as np
import _rpi_ws281x as ws
import mpu6050
import math
import RPi.GPIO as GPIO

btnPIN = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(btnPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


sensor = mpu6050.mpu6050(0x68)
yaw = 0

# LED configuration.
LED_CHANNEL = 0
LED_COUNT = 256         # How many LEDs to light.
# Frequency of the LED signal.  Should be 800khz or 400khz.
LED_FREQ_HZ = 800000
LED_DMA_NUM = 10         # DMA channel to use, can be 0-14.
LED_GPIO = 18         # GPIO connected to the LED signal line.  Must support PWM!
LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
LED_INVERT = 0          # Set to 1 to invert the LED signal, good if using NPN
# transistor as a 3.3V->5V level converter.  Keep at 0
# for a normal/non-inverted signal.
# 刷新频率
# x 和 y
x = 16
y = 16

# Create a ws2811_t structure from the LED configuration.
# Note that this structure will be created on the heap so you need to be careful
# that you delete its memory by calling delete_ws2811_t when it's not needed.
leds = ws.new_ws2811_t()
# 初始化
for channum in range(2):
    channel = ws.ws2811_channel_get(leds, channum)
    ws.ws2811_channel_t_count_set(channel, 0)
    ws.ws2811_channel_t_gpionum_set(channel, 0)
    ws.ws2811_channel_t_invert_set(channel, 0)
    ws.ws2811_channel_t_brightness_set(channel, 0)
channel = ws.ws2811_channel_get(leds, LED_CHANNEL)
ws.ws2811_channel_t_count_set(channel, LED_COUNT)
ws.ws2811_channel_t_gpionum_set(channel, LED_GPIO)
ws.ws2811_channel_t_invert_set(channel, LED_INVERT)
ws.ws2811_channel_t_brightness_set(channel, LED_BRIGHTNESS)
ws.ws2811_t_freq_set(leds, LED_FREQ_HZ)
ws.ws2811_t_dmanum_set(leds, LED_DMA_NUM)
# 初始化灯带
resp = ws.ws2811_init(leds)
if resp != ws.WS2811_SUCCESS:
    message = ws.ws2811_get_return_t_str(resp)
    raise RuntimeError(
        'ws2811_init failed with code {0} ({1})'.format(resp, message))


def update_ws2812(myws, image):
    for i in range(LED_COUNT):
        row = i // x
        col = i % x
        col = col if row % 2 == 1 else x - 1 - col
        blue = image[row][col][0]
        green = image[row][col][2]
        red = image[row][col][1]
        blue = int(blue)
        green = int(green)
        red = int(red)
        color = (red << 16) | (green << 8) | blue
        # print('color',type(color),'0x%x'%color)
        myws.ws2811_led_set(channel, i, color)  # 设置到缓冲区中


srcimg = np.zeros((y, x, 3), np.uint8)
# srcimg[0:8,0:8,:] = (255,0,0)
# srcimg[8:16,0:8,:] = (0,255,0)
# srcimg[0:8,8:16,:] = (0,0,255)
# srcimg[8:16,8:16,:] = (255,255,255)
# srcimg[:,:,:] = (0,0,127)


def show(src):
    # r = 8
    # e = 2
    # dstimg = np.zeros((2*(r+e)*y, 2*(r+e)*x, 3), np.uint8)
    # for i in range(x):
    #     for j in range(y):
    #         cent = (i * 2 * (r+e) + r + e, j * 2 * (r+e) + r + e)
    #         color_tmp = src[j][i]
    #         # color_tmp = (int(src[i,j,0]), int(src[i,j,1]), int(src[i,j,2]))
    #         color_tmp = (int(color_tmp[0]), int(
    #             color_tmp[1]), int(color_tmp[2]))
    #         cv2.circle(dstimg, cent, r, color_tmp, -1)
    #         cv2.circle(dstimg, cent, r, (255, 255, 255), 1)
    # cv2.imshow("dst", dstimg)

    cv2.imshow("src",cv2.resize(src,(256,256)))

    # cv2.imshow("srcimg",srcimg)
    return cv2.waitKey(1)


def showRPY(roll, pitch, yaw):
    rpy = np.zeros((100, 300, 3), np.uint8)
    h = 30
    cv2.putText(rpy, 'roll = ' + str(roll), (15, h), 1, 1.5, (255, 0, 0))
    cv2.putText(rpy, 'pitch = ' + str(pitch), (15, 2 * h), 1, 1.5, (0, 255, 0))
    cv2.putText(rpy, 'yaw = ' + str(yaw), (15, 3 * h), 1, 1.5, (0, 0, 255))
    cv2.imshow('rpy', rpy)


gz0 = sensor.get_gyro_data()['z']


def isClicked():
    if not GPIO.input(btnPIN):
        while True:
            if GPIO.input(btnPIN):
                return True
    return False


rate = 30  # 大约 30 fps
lasttime = -1
# f = open('log.txt', 'w')
mode = int(4)
# 切换模式
modecounter = 45
roll = 0
pitch = 0
try:
    while True:
        srcimg = np.zeros((y, x, 3), np.uint8)
        # 开始时间
        startTime = time.time()

        # 监听键盘  use multi thread
        # isClicked()

        # 这里加一个更新颜色的即可，打算使用 opencv 来更新
        # 使用 mpu6050
        acc_gro_tmp = sensor.get_all_data()
        try:
            Ax = math.atan(acc_gro_tmp[0]['x']/math.sqrt(acc_gro_tmp[0]['z']**2 + acc_gro_tmp[0]['y']**2))
            Ay = math.atan( acc_gro_tmp[0]['y']/math.sqrt(acc_gro_tmp[0]['z']**2 + acc_gro_tmp[0]['x']**2))
            roll = math.degrees(Ax)
            pitch = math.degrees(Ay)
        except ZeroDivisionError:
            print('ZeroDivisionError\troll:{:.3f}\tpitch:{:.3f}'.format(roll,pitch))
            pass
        
        if abs(acc_gro_tmp[1]['z'] - gz0) > 0.3:
            yaw += (acc_gro_tmp[1]['z'] - gz0) / rate
        # showRPY(roll,pitch,yaw)

        # 更新所有灯光的位置到srcimg中
        lasttime = update_information(-roll, pitch, yaw, lasttime, srcimg, mode)

        # 更新灯光的颜色
        update_ws2812(ws, srcimg)

        # 将原图扩大之后，打印在屏幕上
        if show(srcimg) == 27:
            break

        # 将所有的灯光都更新一下
        resp = ws.ws2811_render(leds)
        if resp != ws.WS2811_SUCCESS:
            message = ws.ws2811_get_return_t_str(resp)
            raise RuntimeError(
                'ws2811_render failed with code {0} ({1})'.format(resp, message))

        # 延时固定频率
        endTime = time.time()
        delay = 1.0 / rate - (endTime - startTime)
        # info = '[MainInfo]:\taz:{:<.3f}\troll:{:<.3f}\tpitch:{:<.3f}\tdelay:{:<.3f}\tmode:{:>3d}'.format(
        #     acc_gro_tmp[0]['z'], roll, pitch, delay, mode)
        # with open('log.txt','w+') as f:
        # f.write(info + '\n')
        # print(info)

        if delay > 0:
            time.sleep(delay)
        if acc_gro_tmp[0]['z'] < -18:
            if modecounter <= 0:
                mode = mode % 6 + 1
                lasttime = -1
                modecounter = 45
        if modecounter > 0:
            modecounter -= 1
		
		
except KeyboardInterrupt:
    # f.close()
    cv2.destroyAllWindows()
    # GPIO.cleanup()
finally:
    # Ensure ws2811_fini is called before the program quits.
    ws.ws2811_fini(leds)
    # Example of calling delete function to clean up structure memory.  Isn't
    # strictly necessary at the end of the program execution here, but is good practice.
    ws.delete_ws2811_t(leds)
# print('end')
# f.close()
# cv2.destroyAllWindows()
# GPIO.cleanup()
# ws.delete_ws2811_t(leds)
