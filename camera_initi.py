import cv2
import numpy as np
from ctypes import *
import imutils
import os
import multiprocessing as mp
import threading

Dll = cdll.LoadLibrary("./libJHCap.so")
class CamProcess(mp.Process):
    def __init__(self,camID):
        mp.Process.__init__(self)
	#threading.Thread.__init__(self)
        self.camID = camID
    def run(self):
        print("Starting initi"+str(self.camID))
        camPreview(self.camID,Dll)
def camPreview(camID,cmdl):
    cmdl.CameraInit(camID)
    cmdl.CameraSetResolution(camID,5,0,0)
    cmdl.CameraSetGain(camID,400)
    cmdl.CameraSetExposure(camID,30)
    cmdl.CameraSetContrast.argtypes = [c_int, c_double]
    cmdl.CameraSetContrast(camID,1.1)
    buflen = c_int()
    width = c_int()
    height = c_int()
    cmdl.CameraGetImageSize(camID,byref(width), byref(height))
    cmdl.CameraGetImageBufferSize(camID, byref(buflen), 0x4)
    inbuf = create_string_buffer(buflen.value)
    #cv2.namedWindow("Camera" + str(camID))
    avg = None
    while 1 :
        cmdl.CameraQueryImage(camID,inbuf,byref(buflen),0x104)
        arr = np.frombuffer(inbuf,np.uint8)
        img = np.reshape(arr,(height.value,width.value,3))
        #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray,(21,21),0)
        #if avg is None:
        #    avg = gray.copy().astype("float")
        #cv2.accumulateWeighted(gray,avg,0.5)
        #frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        #thresh = cv2.threshold(frameDelta, 5, 255,cv2.THRESH_BINARY)[1]
        #thresh = cv2.dilate(thresh,None,iterations =2)
        #cnts = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.THRESH_BINARY)[1]
        #cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        #for c in cnts:
        #    if cv2.contourArea(c) < 20000:
        #        continue
        #    (x, y, w, h) = cv2.boundingRect(c)
        #    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Camera"+str(camID), img)
	print("hello",camID)
        key = cv2.waitKey(2)
        if key == 27:
            break
    cv2.destroyWindow("Camera" + str(camID))
        

if __name__=='__main__':
	thread1 = CamProcess(1)
	thread2 = CamProcess(0)
        thread1.start()
	thread2.start()
