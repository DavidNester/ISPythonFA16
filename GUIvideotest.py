import time
import numpy as np
import cv2
from PyQt4 import QtCore
from PyQt4 import QtGui
import Tkinter
import tkFileDialog
import os
import matplotlib.pyplot as plt
import extra
#object tracking
from collections import deque
import argparse
import imutils


"""INPUT FILE"""
"""
root = Tkinter.Tk()
root.withdraw() #use to hide tkinter window

currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV")
                                                         ,("HTML files", "*.html;*.htm")
                                                         ,("All files", "*.*"))) #requests file name and type of files
root.destroy()
    """
#Code for creating windows
# QApplication created only here.
app = QtGui.QApplication([])
window = extra.MyWindow()

"""variables for drawing"""
rect = (0,0,0,0)
startPoint = False
endPoint = False
option = 1
color = (255, 0, 255)

center = None
outside = None

"""Function called when the image is clicked on"""
def on_mouse(event,x,y,flags,params):
    #global rect,startPoint,endPoint
    global center,outside,currentFrame,circleCoords,lastFrameWithCircle,pause,length,width
    # get mouse click
    if event == cv2.EVENT_LBUTTONDOWN:
        print x,y
        if x<0 or x>width or y<0 or y>height:
            pass
        elif pause:
            if center is not None:
                outside = (x,y)
                frame = memory[currentFrame]
                x,y = center
                r = distance(center,outside)
                circleCoords[currentFrame] = (x,y,r)
                cv2.setTrackbarPos('Frames','frame',currentFrame)
                cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                lastFrameWithCircle = currentFrame
                
                cv2.imshow('frame', frame)
                
                pause = False
                center = outside = None
            else:
                center = (x,y)
                print "Please click on the edge of the circle"

def distance(p1,p2):
    dx = (p1[0]-p2[0])*1.0
    dy = (p1[1]-p2[1])*1.0
    return int((dx**2 + dy**2)**.5)

def gamma_correction(img, correction):
    img = img/255.0
    img = cv2.pow(img, correction)
    return np.uint8(img*255)

"""
Function called when track bar is moved
Changes video frame along with movement
"""
def onChanged(x):
    global currentFrame,finalFrame,lastFrameWithCircle, circleCoords
    finalFrame = False
    currentFrame = x
    frames = circleCoords.keys()
    previous = [i for i in frames if i < currentFrame]
    lastFrameWithCircle = max(previous)


"""advances current frame and considers pause and speed"""  
def advance():
    global finalFrame,currentFrame,pause
    if not pause and not finalFrame:
        if speed == 0:
            if currentFrame + 1 < length:
                currentFrame += 1
        elif speed > 0:
            if currentFrame + speed**2 < length:
                currentFrame += speed**2

        elif speed < 0:
            for i in range(speed**2):
                time.sleep(.1)
            if currentFrame + 1 < length:
                currentFrame += 1

"""checks to see if a circle is in a reasonable place based on the previous circles"""
def normal(x,y,r):
    global circleCoords,lastFrameWithCircle,currentFrame
    if lastFrameWithCircle == 0:
        return True
    oldX,oldY,oldR = circleCoords[lastFrameWithCircle]
    if abs(oldX-x) < oldR/2 and abs(oldY-y) < oldR/2 and abs(r-oldR) < oldR/2:
        return True
    return False

def findCircles(frame):
    global lastFrameWithCircle,pause
    original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   
    retval, image = cv2.threshold(original, 50, 255, cv2.cv.CV_THRESH_BINARY)
    
    el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    image = cv2.dilate(image, el, iterations=4)
    
    image = cv2.GaussianBlur(image, (13, 13), 0)

    found = False
    alpha = 90
    while not found:
        circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT, 1.2, 100, param2 = alpha)  
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            #x,y,r = circles[0]
            for x,y,r in circles:
            # loop over the (x, y) coordinates and radius of the circles
                if normal(x,y,r):
                    found = True
                    circleCoords[currentFrame] = (x,y,r)
                    # draw the circle in the output image, then draw a rectangle
                    # corresponding to the center of the circle
                    cv2.circle(frame, (x, y), r+5, (228, 20, 20), 4)
                    cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                    
                    lastFrameWithCircle = currentFrame
            if not found:
                alpha -= 5
                if alpha <= 30:
                    found = True
        else:
            alpha -= 5
            if alpha <= 30:
                found = True
    if currentFrame-lastFrameWithCircle > 10:
        pause = True
        print "Please click on center of circle"
    return frame

"""BEGINNING OF THE CODE"""

    
"""GET FRAMES PER SECOND OF VIDEO"""
"""while True:
    try:
        fps = int(raw_input("How many frames per second does the video have? "))
        break
    except:
        print "Please enter an Integer value"
"""        
video = 'pendulum.MOV'
fps = 123

cap = cv2.VideoCapture(video)
font = cv2.FONT_HERSHEY_SIMPLEX
height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))*2
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))*2
length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

"""STORE VIDEO IN ARRAY"""
print "Processing video...May take a few seconds"
memory = extra.process(length,height,width,fps,cap)

print "Please click on the center of the circle"


"""VIDEO CONTROL VARIABLES AND DATA VARIABLES"""
currentFrame = 1
speed = 0
finalFrame = False
pause = True #video starts paused

cv2.namedWindow('frame')
#create trackbar with length = to the number of frames, linked to onChanged function
cv2.createTrackbar('Frames','frame',0,length,onChanged)
cv2.setMouseCallback('frame', on_mouse)
circleCoords = {} #all the (x,y,r) data for all of the circles
#used for predicting location of next circle if one is not found for a while based on previous activity
lastFrameWithCircle = 0



"""LOOP FOR DISPLAYING VIDEO"""
while(True):
    
    advance()
    
    #get button press
    key = cv2.waitKey(1) & 0xFF
    #pause
    if key == ord('p'):
        if pause:
            pause = False
        else:
            pause = True
    #quit
    if key == ord('q'):
        break
    #slower
    if key == ord('w'):
        if speed > -3:
            speed -= 1
    #faster
    if key == ord('e'):
        if speed < 4:
            speed += 1
    #drawing options
    if key == ord('t'):
        window.show()

    frame = memory[currentFrame]
    
    #sets the trackbar position equal to the frame number
    cv2.setTrackbarPos('Frames','frame',currentFrame)
    
    """registers circles and draws them"""
    if currentFrame in circleCoords.keys():
        x,y,r = circleCoords[currentFrame]
        
        # draw the circle in the output image, then draw a rectangle
        # corresponding to the center of the circle
        cv2.circle(frame, (x, y), r+5, (228, 20, 20), 4)
        cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    else:
        if not pause:
            frame = findCircles(frame)
    
    cv2.imshow('frame', frame)
    

    


"""
    #COLOR DETECTION
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
    args = vars(ap.parse_args())
    pts = deque(maxlen=args["buffer"])
    dst = gamma_correction(frame, 0.40)

    
    # define range of red color in HSV
    lower_red = np.array([40, 90, 120])
    upper_red = np.array([90, 255, 255])

    # Threshold the HSV image to get only red colors
    mask = cv2.inRange(dst, lower_red, upper_red)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
           
        # only proceed if the radius meets a minimum size
        if int(x)<544 and int(x)>45:
            count+=1
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print count, "-", int(x) , int(y)
             
    # update the points queue
    pts.appendleft(center)
                
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)
    cv2.imshow('hsv', dst)
    cv2.imshow('mask',mask)

"""
    
    
    
    

cap.release()
cv2.destroyAllWindows()


"""Plots motion in matplotlib"""
xCoords = []
yCoords = []
rCoords = []
tCoords = [] 

for frame in circleCoords.keys():
    x,y,r = circleCoords[frame]
    xCoords += [x]
    yCoords += [y]
    rCoords += [r]
    tCoords += [frame]
plt.figure(1)
plt.subplot(211)
plt.plot(tCoords,xCoords,'ro')
plt.subplot(212)
plt.plot(tCoords,yCoords,'ro')
plt.show()