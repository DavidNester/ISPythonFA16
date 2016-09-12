import numpy as np
import cv2


"""
Function called when track bar is moved
Changes video frame along with movement
"""
def onChanged(x):
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,x)
    err,img = cap.read()
    cv2.imshow('frame', img)



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



cap = cv2.VideoCapture('pendulum.MOV')

font = cv2.FONT_HERSHEY_SIMPLEX
pause = False
cap = cv2.VideoCapture('pendulum.MOV')
waitTime = 50
                
while(cap.isOpened()):
    if not pause:
        ret, frame = cap.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.putText(gray,str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),(0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))), font, 2,(255,255,255))
    cv2.createTrackbar('Frames','frame',0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)),onChanged)
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

    cv2.imshow('frame', gray)

    key = cv2.waitKey(1)
    """End"""


    



cap.release()
cv2.destroyAllWindows()
