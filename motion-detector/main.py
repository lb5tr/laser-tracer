import cv
trs = 10

def trackbar(x):
    print x
    global trs
    trs = x

def cam_view():
    cv.NamedWindow('cam-view')
    cv.NamedWindow('trs')
    
    cam = cv.CaptureFromCAM(0)
    bg = cv.CreateImage((640,480), cv.IPL_DEPTH_8U,1)

    #Grab few frames, before choosing final background frame
    for i in range(0,30):
        cv.QueryFrame(cam)
    
    cv.CvtColor(cv.QueryFrame(cam), bg, cv.CV_BGRA2GRAY)    
    gray = cv.CloneImage(bg)

    cv.CreateTrackbar('threshold', 'cam-view',10,255,trackbar)
   
    while True:
        img = cv.QueryFrame(cam)

        cv.CvtColor(img,gray,cv.CV_BGRA2GRAY)

        cv.AbsDiff(bg,gray,gray)
        
        cv.Threshold(gray,gray,trs,255,cv.CV_THRESH_BINARY)
               
        cv.Erode(gray,gray,None,10)
        cv.Dilate(gray,gray,None,5)
        cv.ShowImage('trs', gray)
        
        #Calculate center
        mom = cv.Moments(cv.GetMat(gray),1)
        ar = cv.GetCentralMoment(mom,0,0)

        if ar > 0:
            x = cv.GetSpatialMoment(mom,1,0) / ar
            y = cv.GetSpatialMoment(mom,0,1) / ar
            cv.Circle(img,(int(x),int(y)),10,cv.RGB(255,255,29),10)
            
        cv.ShowImage('cam-view',img)
        cv.WaitKey(1)


#start
cam_view()
