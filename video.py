import numpy as np
import cv2
from ctypes import *
import imutils
import os
dll = cdll.LoadLibrary("/home/alphax/Desktop/camera/ubuntu_x64/JHCap2/libJHCap.so")
dll.CameraInit(0)
dll.CameraSetResolution(0,5,0,0)
dll.CameraSetGain(0,400)
dll.CameraSetExposure(0,30)
dll.CameraSetContrast.argtypes = [c_int, c_double]
dll.CameraSetContrast(0, 1.1)
buflen = c_int()
width = c_int()
height = c_int()
dll.CameraGetImageSize(0,byref(width), byref(height))
dll.CameraGetImageBufferSize(0, byref(buflen), 0x4)
inbuf = create_string_buffer(buflen.value)

avg = None
cv2.namedWindow("s")
count = 0
while 1:
	dll.CameraQueryImage(0,inbuf,byref(buflen),0x104)
	arr=np.frombuffer(inbuf, np.uint8)
	img=np.reshape(arr, (height.value, width.value,3))
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray,(21,21),0)	
	if avg is None:
		avg = gray.copy().astype("float")
	cv2.accumulateWeighted(gray,avg,0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, 5, 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 20000:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		print cv2.contourArea(c)
		(x, y, w, h) = cv2.boundingRect(c)
		#cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        	count +=1
        	path = os.path.join('img2','liu_'+str(count)+'.jpg')
        	#cv2.imwrite(path,img)
	cv2.imshow("s", img)
	key=cv2.waitKey(1)
	if key == 27:
		break
