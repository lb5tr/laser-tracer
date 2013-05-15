import cv
import math
import struct
import sys
import usb

trs = 10
distance = 150.0
x_ratio = (math.sqrt(3.0)/3.0) * distance
vendorid  = 0x0477
productid = 0x5620
usb_dev = 0

def start_usb():
    global usb_dev
    usb_dev = usb.core.find(idVendor=vendorid, idProduct=productid)
    
    if usb_dev is None:
        raise ValueError('Device not found')

    usb_dev.detach_kernel_driver(0)
    usb_dev.set_configuration(1)

def setup_env():
    global interface
    global distance
    global x_ratio
    
    if len(sys.argv) >= 2:
        interface = sys.argv[1]
    if len(sys.argv) >= 3:
        distance = sys.argv[2]
        x_ratio = (math.sqrt(3.0)/3.0) * distance

def angle(x):
    a = (math.atan((((320.0 - x)*x_ratio)/320.0)/(distance))*180.0)/3.14
    return 30 - a
    
def trackbar(x):
    print x
    global trs
    trs = x

def a2s(angle):
    return 1650 + 10*angle;

def cam_view():
    global interface

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

    cv.CreateTrackbar('threshold', 'cam-view',10,255,trackbar)

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
	    print "%d" % a2s(angle(x))
            r = struct.pack('HH', a2s(angle(x)), a2s(angle(y)))
            
            usb_dev.write(1,r,0)
            print angle(x)
            
        cv.ShowImage('cam-view',img)
        cv.WaitKey(1)

start_usb()
setup_env()
cam_view()
