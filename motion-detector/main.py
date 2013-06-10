import cv
import math
import struct
import sys
import usb
import time

trs = 44
distance = 2600.0
vendorid  = 0x0477
productid = 0x5620
usb_dev = 0
x_offset = 461
y_offset = 387
ll = 800
lr = 2000

def test():
    start_usb()
    for i in range(800,2000):
        print i
        r = struct.pack('HH',i,i)
        usb_dev.write(1,r,0)
        time.sleep(0.01);

    exit(1);

def start_usb():
    global usb_dev
    usb_dev = usb.core.find(idVendor=vendorid, idProduct=productid)
    
    if usb_dev is None:
        raise ValueError('Device not found')

    usb_dev.detach_kernel_driver(0)
    usb_dev.set_configuration(1)

def angle(x):
    global distance
    x_ratio = (math.sqrt(3.0)/3.0) * distance
    a = (math.atan((((320.0 - x)*x_ratio)/320.0))*180.0)/3.14
    return a
    
def trackbar(x):
    print x
    global trs
    trs = x

def trackbarx(x):
    global x_offset
    x_offset = x - 500

def trackbary(y):
    global y_offset
    y_offset = y - 500

def trackbardist(d):
    global distance
    distance = d / 10000.0

def trackbarll(d):
    global ll
    ll = d

def trackbarlr(d):
    global lr
    lr = d

def a2s(angle):
    return -20*angle + (ll + (lr - ll)/2)

def cam_view():
    global interface, x_offset, y_offset, distance, ll, lr, trs

    cv.NamedWindow('cam-view')
    cv.NamedWindow('trs')
    
    cam = cv.CaptureFromCAM(0)
    bg = cv.CreateImage((640,480), cv.IPL_DEPTH_8U,1)
    
    #Grab few frames, before choosing final background frame
    for i in range(0,30):
        print cv.QueryFrame(cam)

    cv.ShowImage('trs', cv.QueryFrame(cam));

    cv.CvtColor(cv.QueryFrame(cam), bg, cv.CV_BGR2GRAY)    
    gray = cv.CloneImage(bg)

    cv.CreateTrackbar('thr',   'cam-view',trs,200,trackbar)
    cv.CreateTrackbar('x-off', 'cam-view',x_offset,1000,trackbarx)
    cv.CreateTrackbar('y-off', 'cam-view',y_offset,1000,trackbary)
    cv.CreateTrackbar('dist',  'cam-view',int(distance),20000,trackbardist)
    cv.CreateTrackbar('ll',    'cam-view',ll,2000,trackbarll)
    cv.CreateTrackbar('lr',    'cam-view',lr,2000,trackbarlr)

    while True:
        img = cv.QueryFrame(cam)

        cv.CvtColor(img,gray,cv.CV_BGR2GRAY)

        cv.AbsDiff(bg,gray,gray)
        
        cv.Threshold(gray,gray,trs,255,cv.CV_THRESH_BINARY)
               
        cv.Erode(gray,gray,None,10)
        cv.Dilate(gray,gray,None,5)
        cv.ShowImage('trs', gray)
        
        #Calculate center
        mom = cv.Moments(cv.GetMat(gray),1)
        ar = cv.GetCentralMoment(mom,0,0)

        if ar > 0:
            x = cv.GetSpatialMoment(mom,1,0) /  ar
            y = cv.GetSpatialMoment(mom,0,1) / ar
            cv.Circle(img,(int(x),int(y)),10,cv.RGB(255,255,29),10)
	    #print "%d" % a2s(angle(x))
            offset = (((lr-ll)/2) + ll)*2              
            #print  offset - a2s(angle(x))

            x = abs(offset - a2s(angle(x)) + x_offset)
            y = abs(a2s(angle(y)) + y_offset)
            
            print "%d %d\n" % (x, y)
            #print x_offset
            r = struct.pack('HH',x,y);
            usb_dev.write(1,r,0)
            
            
        cv.ShowImage('cam-view',img)
        cv.WaitKey(1)

#test()
start_usb()
cam_view()
