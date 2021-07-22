import serial
import string
import math
import cv2

import os
import shutil

# Hora e Data
import datetime
from time import time
from time import sleep

if not os.path.exists("output-gps"): os.makedirs('./output-gps')

#dmesg |grep tty
ser = serial.Serial('/dev/ttyACM0',baudrate=115200, timeout=1)

filename1 = "GPS"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))+".nmea"
filename2 = "GPS"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))+".txt"

raw_data = open(filename1, 'w')
timeline = open(filename2, 'w')

#raw_data = open("GPS"+str(time())+".nmea", 'w')
#timeline = open("GPS"+str(time())+".txt", 'w')


while True:
	line = ser.readline()
	current_time = datetime.datetime.now().time()
	print(current_time,' ' ,line)                       # Write on console
	linetime = '{:%H:%M:%S:%f}'.format(current_time) + ',' + line.decode('ascii')
	timeline.write(linetime+'\n')
	raw_data.write(line)                      # Write to the output log file

	# frame=cv2.imread('HereGPS.jpg')
	# cv2.imshow('Input', frame)
	# c = cv2.waitKey(1)
	# if c == 27:
	# 	print ('Finishing...')
	# 	break

ser.close
f.close
#if not os.path.exists("output-gps"): os.makedirs('./output-gps')

#shutil.move(filename1,'/home/onsv/output-gps')
#shutil.move(filename2,'/home/onsv/output-gps')
