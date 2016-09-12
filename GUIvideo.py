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


cap = cv2.VideoCapture('pendulum.MOV')

font = cv2.FONT_HERSHEY_SIMPLEX
pause = False

while(cap.isOpened()):
    if not pause:
        ret, frame = cap.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame',gray)
    cv2.createTrackbar('Frames','frame',0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)),onChanged)
    cv2.setTrackbarPos('Frames','frame',int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)))
    cv2.putText(gray,str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),(int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))/2,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))/2), font, 5,(255,0,255))
    print str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)))
    if cv2.waitKey(1) & 0xFF == ord('p'):
        if pause:
            pause = False
        else:
            pause = True
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()