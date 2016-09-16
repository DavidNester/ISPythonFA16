import numpy as np
import cv2


"""
Function called when track bar is moved
Changes video frame along with movement
"""
def onChanged(x):
    #set video to frame corresponding to slider bar
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,x)
    err,img = cap.read()
    #switch to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #add frame number
    cv2.putText(gray,str(x),(0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))), font, 2,(255,255,255))
    cv2.imshow('frame', gray)



rect = (0,0,0,0)
startPoint = False
endPoint = False

"""Function called when the image is clicked on"""
def on_mouse(event,x,y,flags,params):

    global rect,startPoint,endPoint

    # get mouse click
    if event == cv2.EVENT_LBUTTONDOWN:

        if startPoint == True and endPoint == True:
            startPoint = False
            endPoint = False
            rect = (0, 0, 0, 0)

        if startPoint == False:
            rect = (x, y, 0, 0)
            startPoint = True
        elif endPoint == False:
            rect = (rect[0], rect[1], x, y)
            endPoint = True


font = cv2.FONT_HERSHEY_SIMPLEX
pause = False
cap = cv2.VideoCapture('pendulum.MOV')
frameMemory = []
#offset so that dont have to subtract 1 every time we access a frame
frameMemory += [-1]

height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
while(cap.isOpened()):
    #get next frame if not paused
    if not pause:
        ret, frame = cap.read()
    #switch to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #add frame number to video
    cv2.putText(gray,str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),(0,height), font, 2,(255,255,255))
    #create trackbar with length = to the number of frames, linked to onChanged function
    cv2.createTrackbar('Frames','frame',0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)),onChanged)
    #sets the trackbar position equal to the frame number
    cv2.setTrackbarPos('Frames','frame',int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)))
    
    
    if cv2.waitKey(1) & 0xFF == ord('p'):
        if pause:
            pause = False
        else:
            pause = True
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    """Code for drawing on video"""

    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)    

    #drawing line
    if startPoint == True and endPoint == True:
        cv2.line(gray, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 255), 2)
        cv2.circle(gray, (rect[0], rect[1]), 50, (255, 0, 255), -1)
        
    for i in range(1+(height/100)):
        cv2.line(gray,(0,i*100),(width,i*100),(0,255,255),1)
    for i in range(1+(width/100)):
        cv2.line(gray,(i*100,0),(i*100,height),(0,255,255),1)
    cv2.imshow('frame', gray)
    #put frame in memory array indexed by frame number
    frameMemory += [gray]

    #key = cv2.waitKey(1)#I commented this out because I think it was interfering with the p and q commands. Im not sure what it was doing.
    """End"""


    



cap.release()
cv2.destroyAllWindows()
