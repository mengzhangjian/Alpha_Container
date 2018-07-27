import cv2
import numpy as np
from ctypes import *
import imutils
import os
import multiprocessing as mp
from pydarknet import Detector, Image
from collections import deque
import time
net = Detector(bytes("cfg_yolo/yolov3.cfg"), bytes("cfg_yolo/yolo-obj_60000.weights"), 0, bytes("cfg_yolo/coco.data"))
index = [0]
cmdl = []
inbuf = []
pts = deque(maxlen = 32)
(dX,dY) = (0,0)
direction = ""
counter = 0

avg = None
for id in index:
    cmdl.append(cdll.LoadLibrary("./libJHCap.so"))
for camID in index:
    #cmdl[camID] = cdll.LoadLibrary("./libJHCap.so")
    print(camID)
    cmdl[camID].CameraInit(camID)
    cmdl[camID].CameraSetResolution(camID,4,0,0)
    cmdl[camID].CameraSetGain(camID,600)
    cmdl[camID].CameraSetExposure(camID,30)
    cmdl[camID].CameraSetContrast.argtypes = [c_int, c_double]
    cmdl[camID].CameraSetContrast(camID,1.15)
    buflen = c_int()
    width = c_int()
    height = c_int()
    cmdl[camID].CameraGetImageSize(camID,byref(width), byref(height))
    cmdl[camID].CameraGetImageBufferSize(camID, byref(buflen), 0x4)
    inbuf.append(create_string_buffer(buflen.value))   

time.sleep(2.0)
while True:
    for camID in index:
        cmdl[camID].CameraQueryImage(camID,inbuf[camID],byref(buflen),0x104)
        arr = np.frombuffer(inbuf[camID],np.uint8)
        img = np.reshape(arr,(height.value,width.value,3))
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(21,21),0)

        if avg is None:
            avg = gray.copy().astype("float")
        cv2.accumulateWeighted(gray,avg,0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        thresh = cv2.threshold(frameDelta, 5, 255,cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        center = None
        if len(cnts) > 0:

            img2 = Image(img)
            results = net.detect(img2)
            for cat,score,bounds in results:
                x,y,w,h = bounds
                cv2.rectangle(img, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0), thickness=2)
                cv2.putText(img,str(cat.decode("utf-8")),(int(x),int(y)),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,0))
                center = (int(x),int(y))
                pts.appendleft(center)
        print(pts)
        for i in np.arange(1, len(pts)):
            
            if pts[i - 1] is None or pts[i] is None:
			    continue
            if counter >= 10 and i == 1 and len(pts) > 5 and pts[-5] is not None:
                dX = pts[-5][0] - pts[i][0]
                dY = pts[-5][1] - pts[i][1]
                (dirX,dirY) = ("","")

                if np.abs(dX) > 20:
                    dirX = "East" if np.sign(dX) == 1 else "West"
                
                if np.abs(dY) > 20:
                    dirY = "North" if np.sign(dY) ==1 else "South"
                
                if dirX != "" and dirY != "":
                    direction = "{}-{}".format(dirY,dirX)
                else:
                    direction = dirX if dirX !="" else dirY
            thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
            cv2.line(img, pts[i - 1], pts[i], (0, 0, 255), thickness)
        cv2.putText(img, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 3)
        cv2.putText(img, "dx: {}, dy: {}".format(dX, dY),
		(10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)
        cv2.imshow("Camera"+str(camID), img)
        counter +=1
        key = cv2.waitKey(1)
        if key & 0XFF == ord('q'):
            break
cv2.destroyAllWindows()
