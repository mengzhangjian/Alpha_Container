# -*- coding: utf-8 -*-
import cv2
import numpy as np
from ctypes import *
import imutils
import os
import multiprocessing as mp
from pydarknet import Detector, Image
from collections import deque
import time
from check_serial import *
from multiprocessing import Process
from multiprocessing import Manager
import multiprocessing
net = Detector(bytes("cfg_yolo/yolov3.cfg"), bytes("cfg_yolo/yolo-obj_110000.weights"), 0, bytes("cfg_yolo/coco.data"))
index = [0]
cmdl = []
inbuf = []
pts = deque(maxlen = 32)
(dX,dY) = (0,0)
direction = ""
counter = 0

sku_list  = ["北冰洋","百事可乐", "雪碧", "可乐", "红烧牛肉面","酸弟南酸糟糕", "趣多多", "卫龙小辣棒", "卫龙魔芋爽", "薯愿",
             "乐事海盐黑胡椒", "乐事大波浪薯片"]
avg = None
for id in index:
    cmdl.append(cdll.LoadLibrary("./libJHCap.so"))
for camID in index:
    #cmdl[camID] = cdll.LoadLibrary("./libJHCap.so")
    print(camID)
    cmdl[camID].CameraInit(camID)
    cmdl[camID].CameraSetResolution(camID,5,0,0)
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
sku_code = []


global ser0 
ser0= open_com('/dev/ttyUSB0')
record = list()
temp = [0,0]
f0,f1 = gravity_out(ser0)
temp[0] = f0
temp[1] = f1
current = [0,0]

def gravity_process(return_dict):
    global ser0
    while True:
        f0,f1 = gravity_out(ser0)
        current[0] = f0
        current[1] = f1
        ab = gravity_search(temp,current,ser0)
        
        if  ab[1] != -1:
            #result = json.dumps(ab, encoding='UTF-8', ensure_ascii=False)
            
            #print(result)
            return_dict["result"] = ab



if __name__ =="__main__":
    
    mananger = Manager()
    return_dict = mananger.dict()

    p = multiprocessing.Process(target = gravity_process,args = (return_dict,))

    p.start()
    
    count = 0
    list_state = [0,0]
    gravity_list = []
    while True:
            
        if return_dict:
            
            if list_state[0] !=0 or list_state[1] !=0:
                if return_dict["result"][0] == 0:
                    if abs(return_dict["result"][2][0]-list_state[0][2][0]) > 0:
                        #result = json.dumps(return_dict["result"][3], encoding='UTF-8', ensure_ascii=False)
                        #print(return_dict["result"][3])
                        index_sku = return_dict["result"][3]  # [('1', 359), ('2', 360)]
                        gravity_list.append(int(index_sku[0][0]))
                        gravity_list.append(int(index_sku[1][0]))
                        #print(sku_list[int(index_sku[0][0]) - 1],sku_list[int(index_sku[1][0]) - 1])
                if return_dict["result"][0] == 1:
                     if abs(return_dict["result"][2][1]-list_state[1][2][1]) > 0:
                        #result = json.dumps(return_dict["result"][3], encoding='UTF-8', ensure_ascii=False)
                        #print(return_dict["result"][3])
                        index_sku = return_dict["result"][3]
                        gravity_list.append(int(index_sku[0][0]))
                        gravity_list.append(int(index_sku[1][0]))                        
                        #print(sku_list[int(index_sku[0][0]) - 1],sku_list[int(index_sku[1][0]) - 1])
            count +=1
            if count > 1:
                if return_dict["result"][0] == 0:
                    list_state[0] = return_dict["result"]
                if return_dict["result"][0] == 1:
                    list_state[1] = return_dict["result"]
            else:
                #print(return_dict["result"][3])
                index_sku = return_dict["result"][3]
                gravity_list.append(int(index_sku[0][0]))
                gravity_list.append(int(index_sku[1][0]))                
                #print(sku_list[int(index_sku[0][0]) - 1],sku_list[int(index_sku[1][0]) - 1])

            # return_dict = None
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
                    center = (int(x),int(y),str(cat.decode("utf-8")))
                    pts.appendleft(center)
            
            for i in np.arange(1, len(pts)):
                
                if pts[i - 1] is None or pts[i] is None:
                    continue
                if counter >= 10 and i == 1 and len(pts) > 5 and pts[-5] is not None:
                    dX = pts[-5][0] - pts[i][0]
                    dY = pts[-5][1] - pts[i][1]
                    dX1 = pts[i-1][0] - pts[i][0]
                    dY1 = pts[i-1][1] - pts[i][1]
                    (dirX,dirY) = ("","")

                    if np.abs(dX) > 20:
                        dirX = "East" if np.sign(dX) == 1 else "West"
                    
                    if np.abs(dY) > 20:
                        dirY = "North" if np.sign(dY) ==1 else "South"
                    
                    if dirX != "" and dirY != "":
                        direction = "{}-{}".format(dirY,dirX)
                    else:
                        direction = dirX if dirX !="" else dirY
                    if np.abs(dX1) > 20 and  np.abs(dY1) > 20:
                        sku_code.append((pts[i][2]))
                thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
                cv2.line(img, pts[i - 1][:2], pts[i][:2], (0, 0, 255), thickness)
            cv2.putText(img, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 3)
            cv2.putText(img, "dx: {}, dy: {}".format(dX, dY),
            (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.35, (0, 0, 255), 1)

            cv2.imshow("Camera"+str(camID), img)
            counter +=1
            key = cv2.waitKey(1)
            if key & 0XFF == ord('q'):
                break
            
            set_sku = set(sku_code)

            dict_sku = {}
            for item in set_sku:
                dict_sku.update({item:sku_code.count(item)})
            print(dict_sku)

        if len(gravity_list) > 0 and len(dict_sku) > 0:
            sku_dict = [int(k) for k in dict_sku.keys()]
            intersection = list(set(gravity_list).intersection(set(sku_dict)))
            for item in intersection:
               # print(sku_list[item -1])
               result = json.dumps(sku_list[item -1], encoding='UTF-8', ensure_ascii=False)
               print(result)
            gravity_list = []
            dict_sku = {}

    cv2.destroyAllWindows()
    p.join()