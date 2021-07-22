import numpy as np
import cv2

import os
import shutil

 #Hora e Data
import datetime

#from datetime import date
from time import time
from time import sleep

#filename1 = format(current_time) +'(1).avi'

current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#current_time = date.today()
filename1 = format(current_time) +'(1).avi'
filename2 = format(current_time) +'(2).avi'
filename3 = format(current_time) +'(3).avi'
frames_per_seconds = 20.0
# numero da camera

cam1 = cv2.VideoCapture(1)
cam2 = cv2.VideoCapture(0)
cam3 = cv2.VideoCapture(3)

writer1 = cv2.VideoWriter_fourcc(*'XVID')
writer2 = cv2.VideoWriter_fourcc(*'XVID')
writer3 = cv2.VideoWriter_fourcc(*'XVID')

out1 = cv2.VideoWriter(filename1, writer1, frames_per_seconds, (640,480))
out2 = cv2.VideoWriter(filename2, writer2, frames_per_seconds, (640,480))
out3 = cv2.VideoWriter(filename3, writer3, frames_per_seconds, (640,480))

while (True):
    ret, frame1 = cam1.read()
    ret, frame2 = cam2.read()
    ret, frame3 = cam3.read()
    current_time = datetime.datetime.now()
    frame1 = cv2.putText(frame1, format(current_time), (10,50), 0, 1, (0, 255, 255), 2, cv2.LINE_AA)
    frame2 = cv2.putText(frame2, format(current_time), (10,50), 0, 1, (0, 255, 255), 2, cv2.LINE_AA)
    frame3 = cv2.putText(frame3, format(current_time), (10,50), 0, 1, (0, 255, 255), 2, cv2.LINE_AA)
    if ret==True:
        #flip inverte a imagem de cabeca para baixo
        # frame = cv2.flip(frame, 0)
        out1.write(frame1)
        out2.write(frame2)
        out3.write(frame3)
        cv2.imshow('cam1', frame1)
        # cv2.moveWindow('cam1', 0,0)
        cv2.imshow('cam2', frame2)
        # cv2.moveWindow('cam2', 630,0)
        cv2.imshow('cam3', frame3)
        # cv2.resizeWindow('cam3', 100,100)
        # cv2.moveWindow('cam3', 630,630)
    else:
        break
        #aperta q para sair:::
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

    pass

# Move os arquivos para o diretorio
if not os.path.exists("output-video"): os.makedirs('./output-video')

shutil.move(filename1,'/home/onsv/output-video')
shutil.move(filename2,'/home/onsv/output-video')
shutil.move(filename3,'/home/onsv/output-video')

cam1.release()
cam2.release()
cam3.release()
out1.release()
out2.release()
out3.release()
cv2.destroyAllWindows()
