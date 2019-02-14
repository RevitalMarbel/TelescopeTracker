
import cv2
import numpy as np
import math
import serial
import time
import codecs
import os
import Telcontrol

import zwoasi as asi

telescope=Telcontrol.Telcontrol()
time.sleep(2)
print("connected")
#telescope.setAzimut(0.5)
telescope.setAltitude(4)