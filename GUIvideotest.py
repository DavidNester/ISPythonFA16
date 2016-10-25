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


"""INPUT FILE"""

root = Tkinter.Tk()
root.withdraw() #use to hide tkinter window

currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV")
                                                         ,("HTML files", "*.html;*.htm")
                                                         ,("All files", "*.*"))) #requests file name and type of files
root.destroy()

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

"""
Function called when track bar is moved
Changes video frame along with movement
"""
def onChanged(x):
    global currentFrame,finalFrame,lastFrameWithCircle,secondLastFrameWithCircle, circleCoords
    finalFrame = False
    currentFrame = x
    frames = circleCoords.keys()
    previous = [i for i in frames if i <= currentFrame]
    lastFrameWithCircle = max([i for i in frames if i <= currentFrame])
    secondLastFrameWithCircle = max([i for i in frames if i < lastFrameWithCircle])

"""BEGINNING OF THE CODE"""



"""GET FRAMES PER SECOND OF VIDEO"""
while True:
    try:
        fps = int(raw_input("How many frames per second does the video have? "))
        break
    except:
        print "Please enter an Integer value"

cap = cv2.VideoCapture(tempdir)
font = cv2.FONT_HERSHEY_SIMPLEX
height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

"""STORE VIDEO IN ARRAY"""
print "Processing video...May take a few seconds"
memory = extra.process(length,height,width,fps,cap)


"""advances current frame and considers pause and speed"""  
def advance():
    global finalFrame,currentFrame,pause,drawn
    if not pause and not finalFrame:
        drawn = False
        if speed == 0:
            if currentFrame + 1 < length:
                currentFrame += 1
            else:
                drawn = True
        elif speed > 0:
            if currentFrame + speed**2 < length:
                currentFrame += speed**2
            else:
                drawn = True
        elif speed < 0:
            for i in range(speed**2):
                time.sleep(.1)
            if currentFrame + 1 < length:
                currentFrame += 1
            else:
                drawn = True

"""checks to see if a circle is in a reasonable place based on the previous circles"""
def normal(x,y,r):
    #TODO: consider situation that first circle is bad
    global circleCoords,lastFrameWithCircle,secondLastFrameWithCircle,currentFrame
    if lastFrameWithCircle == 0:
        return True
    oldX,oldY,oldR = circleCoords[lastFrameWithCircle]
    if abs(oldX-x) < oldR and abs(oldY-y) < oldR and abs(r-normalizedRadius[0]) < 30:
        return True
    if secondLastFrameWithCircle == 0:
        return True
    olderX,olderY,olderR = circleCoords[secondLastFrameWithCircle]
    if abs((((oldX-olderX)/(lastFrameWithCircle-secondLastFrameWithCircle))*(currentFrame-lastFrameWithCircle)+oldX)-x)<oldR:
        return True
    return False

"""VIDEO CONTROL VARIABLES AND DATA VARIABLES"""
currentFrame = 1
speed = 0
finalFrame = False
pause = True #video starts paused
drawn = False#if circle has been drawn on page
cv2.namedWindow('frame')
#create trackbar with length = to the number of frames, linked to onChanged function
cv2.createTrackbar('Frames','frame',0,length,onChanged)
cv2.setMouseCallback('frame', on_mouse)
circleCoords = {} #all the (x,y,r) data for all of the circles
#used for predicting location of next circle if one is not found for a while based on previous activity
lastFrameWithCircle = 0
secondLastFrameWithCircle = 0
normalizedRadius = (0,0) #(radius,number of data points)


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
    
    edge = cv2.Canny(frame, 100, 200)
    cv2.imshow('Edge', edge)
    
    #sets the trackbar position equal to the frame number
    cv2.setTrackbarPos('Frames','frame',currentFrame)
    """registers circles and draws them"""
    if currentFrame in circleCoords.keys():
        x,y,r = circleCoords[currentFrame]
        
        # draw the circle in the output image, then draw a rectangle
        # corresponding to the center of the circle
        cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
        cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        secondLastFrameWithCircle = lastFrameWithCircle
        lastFrameWithCircle = currentFrame
        drawn = True
    else:
        circles = cv2.HoughCircles(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.cv.CV_HOUGH_GRADIENT, 1.2, 100)
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
 
            # loop over the (x, y) coordinates and radius of the circles
            if not drawn:
                for (x, y, r) in circles:
                    if normal(x,y,r):
                        normalizedRadius = ((normalizedRadius[0]*normalizedRadius[1]+r)/(normalizedRadius[1]+1),normalizedRadius[1]+1)
                        circleCoords[currentFrame] = (x,y,r)
                        # draw the circle in the output image, then draw a rectangle
                        # corresponding to the center of the circle
                        cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
                        cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                        
                        secondLastFrameWithCircle = lastFrameWithCircle
                        lastFrameWithCircle = currentFrame
                drawn = True
            

    
    """Code for drawing on video"""
    #drawing line
    if startPoint == True and endPoint == True:
        if option == 2:
            cv2.line(frame, (rect[0], rect[1]), (rect[2], rect[3]), color, 2)
        elif option == 1:
            cv2.circle(frame, (rect[0], rect[1]), 50, color, -1)

    cv2.imshow('frame', frame)
    
    
    

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