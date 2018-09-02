# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 22:03:58 2017

@author: jt
"""
import serial
import time
import numpy as np
import json
#sku_list  = {"北冰洋":359, "百事可乐":360, "雪碧":653, "可乐": 655, "红烧牛肉面":158,
#             "酸弟南酸糟糕":186, "趣多多":107, "卫龙小辣棒":62, "卫龙魔芋爽":102, "薯愿":138,
#             "乐事海盐黑胡椒":78, "乐事大波浪薯片":78}
sku_list  = {"1":359, "2":360, "3":653, "4": 655, "5":158,
             "6":186, "7":107, "8":62, "9":102, "10":138,
             "11":78, "12":78}



def open_com(n):
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = n
    ser.open()
    return ser

def read_com(ser):
    ser.flushInput()
    s = ""
    while len(s)==0:
        time.sleep(0.1)
        s = ser.readline().strip()
    return s

def gravity_out(serindex):

    s = read_com(serindex)
    f0 = float(s.split()[0])*0.00936575
    f1 = float(s.split()[1])*0.0093696
    #print(f0,f1)
    return f0,f1
    
def gravity_search(last_g,current_g,ser0):
    #last_g = [1,2,3,4],current_g = [12,2,3,4]
    # state = 0 放进 
    # state = 1 拿出
    # gravity_check = 当前重力状态值，用于多进程判断
    ab = []
    #f0, f1 = gravity_out(ser0)
    #current_g[0] = f0
    #current_g[1] = f1
    state = -1
    gravity_check = [0, 0]
    for index,k_value in enumerate(current_g):
       # print(k_value,last_g[index])
#        if(k_value - last_g[index] < -70):
#            print(k_value,last_g[index])
#            print("拿出")
#        elif((k_value - last_g[index] > 70)):
#            print(k_value,last_g[index])

#            print("放进")
        if (abs(k_value - last_g[index]) < 700) and (k_value - last_g[index])> 70:
            time.sleep(0.3)
            f0, f1 = gravity_out(ser0)
            if index == 0:

                gravity = f0
                gravity_check[0] = gravity
            else:
                gravity = f1
                gravity_check[1] = gravity
            if abs(gravity - k_value) < 10:
                first_state = last_g[index]
                #print("first_state",last_g[index])
                #print("now state",gravity)
                state = 0
                print("放进")
                predict_first = last_g[index]
                #print(gravity)
                if(abs(gravity - predict_first) > 70 ):
                    value = abs(gravity - predict_first)
                    ##predict_first = temp
                    # for k,v in sku_list.items():
                    #     if abs(value - v) < 5:
                    #         print(k)
                    ab = sorted(sku_list.copy().items(), key = lambda e:abs(e[1]- abs(gravity - last_g[index])))[:2]
                    #result = json.dumps(ab, encoding='UTF-8', ensure_ascii=False)
                    #print(index)
                    #print(result)
                last_g[index] = gravity
                
                
                # print(abs(f0),abs(temp))

        elif(abs(k_value - last_g[index]))< 700 and (k_value- last_g[index]) < -70:
            time.sleep(0.3)
            f0, f1 = gravity_out(ser0)
            if index == 0:
                gravity = f0
                gravity_check[0] = gravity
            else:
                gravity = f1
                gravity_check[1] = gravity
            if abs(gravity - k_value) < 10:
                first_state = last_g[index]
                #print("first_state",last_g[index])
                #print("now state",gravity)
                print('拿出')
                #print(gravity)
                state = 1
                predict_first = last_g[index]
                if(abs(gravity - predict_first) > 70 ):
                    value = abs(gravity - predict_first)
                    ##predict_first = temp
                    # for k,v in sku_list.items():
                    #     if abs(value - v) < 5:
                    #         print(k)
                    ab = sorted(sku_list.copy().items(), key = lambda e:abs(e[1]- abs(gravity - last_g[index])))[:2]
                    
                    #print(index)
                    #print(result)
                last_g[index] = gravity
    #[托盘索引，拿出状态，当前重力状态值，返回结果]
    return [index,state,gravity_check,ab]

if __name__ == "__main__":
    ser0 = open_com('/dev/ttyUSB0')
    record = list()
    is_wait = False
    temp = [0,0]
    f0,f1 = gravity_out(ser0)
    temp[0] = f0
    temp[1] = f1
    current = [0,0]
    while True:
        f0,f1 = gravity_out(ser0)
        current[0] = f0
        current[1] = f1
        result = gravity_search(temp,current,ser0)
        if result[3]:
            print(result)
          
"""
    while True:
        f0, f1 = gravity_out(ser0)
        
        # if is_wait:
        #     #time.sleep(2)
        #     f0, f1 = gravity_out(ser0)
        #     #print(abs(f0))
        #     is_wait = False
        # # time.sleep(0.5)
        if ((abs(f0) - abs(temp)) < 700) and (abs(f0) - abs(temp))> 70:
            time.sleep(0.2)
            f0, f1 = gravity_out(ser0)
            first_state = temp
            print("first_state",temp)
            print("now state",f0)
            print('放进')
            predict_first = temp
            if(abs(f0 - predict_first) > 70 ):
                value = abs(f0 - predict_first)
                ##predict_first = temp
                # for k,v in sku_list.items():
                #     if abs(value - v) < 5:
                #         print(k)
                ab = sorted(sku_list.copy().items(), key = lambda e:abs(e[1]- (abs(f0) - abs(temp))))[:2]
                result = json.dumps(ab, encoding='UTF-8', ensure_ascii=False)
                print(result)
            temp = f0
            
            
            # print(abs(f0),abs(temp))

        elif((abs(f0) - abs(temp))< 700) and (abs(f0) - abs(temp)) < -70:
            time.sleep(0.2)
            f0, f1 = gravity_out(ser0)
            first_state = temp
            print("first_state",temp)
            print("now state",f0)
            print("拿出")
            predict_first = temp
            if(abs(f0 - predict_first) > 70 ):
                value = abs(f0 - predict_first)
                ##predict_first = temp
                # for k,v in sku_list.items():
                #     if abs(value - v) < 5:
                #         print(k)  
                ab = sorted(sku_list.copy().items(), key = lambda e:abs(e[1]- abs(abs(f0) - abs(temp))))[:2]
                result = json.dumps(ab, encoding='UTF-8', ensure_ascii=False)
                print(result)
            temp = f0



#a = sorted(sku_list.items(), key = lambda e:abs(e[1]- 100))
"""

            


            
        
    
        

    # """
    # f = open('read.txt','w')
    # count = 0
    # num = [] 
    # while True:
    #     f0,f1 = gravity_out(ser0)
    #     print(abs(f1))
    #     if count > 200:
    #          break
    #     count +=1
    #     if abs(f1) < 60000:
    #         num.append(abs(f1))
    #         #f.write(str(abs(f0))+'\n')
    # index = sum(num) // len(num)
    # print(index)
    # f.close()
    # """
