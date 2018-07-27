from ctypes import *
import math
import random
import dlib
import cv2
import os
def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    

#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("cfg/libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res
def rectangle_face(img,center_x,center_y,width,height):
    # zou kuo  you kuo shang kuo  xia kuo
    left = (int(center_x - width / 2))  
    top  = (int(center_y - height / 2))
    right = (int(center_x + width / 2))
    bottom = (int(center_y + height / 2))
    return left,top,right,bottom
"""
    im_h,im_w,_ = img.shape
    down_d = abs(int((height-width)))
    if (left - down_d) > 0 :
        left = left - down_d
     
    
    if (right + down_d ) < im_w:
        right = right + down_d
    if (top - down_d ) > 0:
    	top = top - down_d
    if (bottom + down_d) < im_h:
    	bottom = bottom + down_d
    new_height = bottom - top
    new_width  = right - left
    if new_height > new_width:
       bottom = top + new_width
    else:
       right  = left + new_height
"""
net = load_net("cfg/yolo-obj.cfg", "cfg/yolo-obj_180000.weights", 0)
meta = load_meta("cfg/obj.data")
#landmark_predictor = dlib.shape_predictor('/home/bbt/Desktop/dlilb/shape_predictor_68_face_landmarks.dat')

def face_recog(img_path):
    points = []
    img = cv2.imread(img_path)
    r = detect(net, meta, img_path)
    if len(r) > 0:
	for d in r:

	    center_x = int(d[2][0])
	    center_y  = int(d[2][1])
	    width =int( d[2][2])
	    height =int(d[2][3])
            left,top,right,bottom = rectangle_face(img,center_x,center_y,width,height)
            points.append([left,top,right,bottom])
    return points
"""
if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    #print r[:10]
    net = load_net("cfg/yolo-obj.cfg", "cfg/yolo-obj_180000.weights", 0)
    meta = load_meta("cfg/obj.data")
    landmark_predictor = dlib.shape_predictor('/home/bbt/Desktop/dlilb/shape_predictor_68_face_landmarks.dat')
    img_path = '/media/bbt/data/ZHANGJIAN_WIDER/300wfacialannotation/ALL/300VW_Dataset_2015_12_14/002/image'
    for index in os.listdir(img_path):
	path = os.path.join(img_path,index)
        img = cv2.imread(path)
        r = detect(net, meta, path)
        
        print r
        print(len(r))
        if len(r) > 0 :
    		for d in r:
		
		
	            center_x = int(d[2][0])
		    center_y  = int(d[2][1])
		    width =int( d[2][2])
		    height =int(d[2][3])
	        #print(left,top,right,bottom)
                    left,top,right,bottom = rectangle_face(img,center_x,center_y,width,height)
		    print('width % height is ',float(width)/float(height))
		    cv2.rectangle(img, (left,top), (right,bottom), (255, 0, 0), thickness=2)
                    shape_d = dlib.rectangle(left,top,right,bottom)
		    shape = landmark_predictor(img,shape_d)
		    for i in range(68):
		        cv2.circle(img, (shape.part(i).x, shape.part(i).y),5,(0,255,0), -1, 8)
	                cv2.putText(img,str(i),(shape.part(i).x,shape.part(i).y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,2555,255))		
        cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)
        cv2.imshow('Frame',img)
        if cv2.waitKey(0) & 0XFF == ord('q'):
		continue
"""
