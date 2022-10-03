import time

import numpy as np
import pyautogui
import cv2
import keyboard
from playsound import playsound as play
import ctypes
import time

SendInput = ctypes.windll.user32.SendInput


# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Actuals Functions
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


highbeams_on_threshold = 30
highbeams_off_threshold = 35
bright_threshold = 170
not_threshold = 50
amount_hotspots = 5

turn_on_frames = 2

check_active = False
highbeams_on = False
frames_turned_on = 0
while True:
    try:
        if keyboard.is_pressed('b'):
            check_active = True
        if keyboard.is_pressed('n'):
            check_active = False
    except:
        break

    if check_active:
        image_width = 2560
        image_height = 1440

        image = pyautogui.screenshot()
        image: np.ndarray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        cropped_image = image[520: 820, 1000: 1800]

        '''
        blue_image = image[520: 820, 1000: 1800, 0]
        green_image = image[520: 820, 1000: 1800, 1]
        red_image = image[520: 820, 1000: 1800, 2]

        # image = cv2.GaussianBlur(image, (11, 11), 0)
        blue_hotspot_image = cv2.threshold(blue_image, hotspot_threshold, 255, cv2.THRESH_BINARY)[1]
        green_hotspot_image = cv2.threshold(green_image, hotspot_threshold, 255, cv2.THRESH_BINARY)[1]
        red_hotspot_image = cv2.threshold(red_image, hotspot_threshold, 255, cv2.THRESH_BINARY)[1]
        '''

        # brightness = np.average(gray_image)
        brightness = 0

        hotspots = 0
        for x in range(800):
            for y in range(300):
                if cropped_image[y, x, 2] > bright_threshold and cropped_image[y, x, 0] < not_threshold and cropped_image[y, x, 1] < not_threshold:
                    hotspots += 1
                if bright_threshold <= cropped_image[y, x, 2] <= cropped_image[y, x, 0] and cropped_image[y, x, 2] <= cropped_image[y, x, 1]:
                    hotspots += 1

        print(f"{brightness}; {hotspots}")

        should_deactivate = brightness > highbeams_off_threshold or hotspots > amount_hotspots
        should_activate = brightness < highbeams_on_threshold and hotspots < amount_hotspots

        if highbeams_on and should_deactivate:
            highbeams_on = False
            PressKey(0x25)
            time.sleep(0.1)
            ReleaseKey(0x25)
            play('./beep-off.mp3')
            cv2.imwrite('./game.jpg', image)
            cv2.imwrite('./cropped.jpg', cropped_image)
        elif not highbeams_on and should_activate:
            frames_turned_on += 1
            if frames_turned_on >= turn_on_frames:
                highbeams_on = True
                frames_turned_on = 0
                PressKey(0x25)
                time.sleep(0.1)
                ReleaseKey(0x25)
                play('./beep-on.mp3')

        if keyboard.is_pressed('u'):
            cv2.imwrite('./game.jpg', image)
            cv2.imwrite('./cropped.jpg', cropped_image)

        print(highbeams_on)
