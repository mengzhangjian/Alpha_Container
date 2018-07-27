import cv2
import numpy as np
from ctypes import *
import imutils
import os
import multiprocessing as mp
from pydarknet import Detector, Image

net = Detector(bytes("cfg_yolo/yolov3.cfg"), bytes("cfg_yolo/yolo-obj_60000.weights"), 0, bytes("cfg_yolo/coco.data"))
index = [0]
cmdl = []
inbuf = []
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

while True:
    for camID in index:
        cmdl[camID].CameraQueryImage(camID,inbuf[camID],byref(buflen),0x104)
	print(camID)
        arr = np.frombuffer(inbuf[camID],np.uint8)
        img = np.reshape(arr,(height.value,width.value,3))
	img2 = Image(img)
	results = net.detect(img2)
	for cat,score,bounds in results:
		x,y,w,h = bounds
		cv2.rectangle(img, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0), thickness=2)
		cv2.putText(img,str(cat.decode("utf-8")),(int(x),int(y)),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,0))
		print(cat)
        cv2.imshow("Camera"+str(camID), img)
        key = cv2.waitKey(2)
        if key & 0XFF == ord('q'):
            break
cv2.destroyAllWindows()
