import time
import numpy as np
import cv2
from PyQt4 import QtCore
from PyQt4 import QtGui
import Tkinter
import tkFileDialog
import os


"""Code for retrieving file name"""

root = Tkinter.Tk()
root.withdraw() #use to hide tkinter window

currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV")
                                                         ,("HTML files", "*.html;*.htm")
                                                         ,("All files", "*.*"))) #requests file name and type of files
root.destroy()

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

def circleChoice():
    global option
    option = 1

def lineChoice():
    global option
    option = 2

def blackColor():
    global color
    color = (0,0,0)

def whiteColor():
    global color
    color = (255, 255, 255)
    
"""Function to create the window"""
class MyWindow(QtGui.QDialog):    # any super class is okay
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        layout = QtGui.QGridLayout()
        circleButton = QtGui.QPushButton('Circle')
        lineButton = QtGui.QPushButton('Line')
        blackButton = QtGui.QPushButton('Black')
        whiteButton = QtGui.QPushButton('White')
        label1 = QtGui.QLabel("Shape")
        label2 = QtGui.QLabel("Color")
        layout.addWidget(label1,0,0)
        layout.addWidget(circleButton ,1,0)
        layout.addWidget(lineButton ,1,1)
        layout.addWidget(label2, 2, 0)
        layout.addWidget(blackButton,3,0)
        layout.addWidget(whiteButton,3,1)
        circleButton.clicked.connect(circleChoice)
        lineButton.clicked.connect(lineChoice)
        blackButton.clicked.connect(blackColor)
        whiteButton.clicked.connect(whiteColor)
        self.setLayout(layout)
        self.setWindowTitle("Toolbar");
    def create_child(self):
        # here put the code that creates the new window and shows it.
        child = MyWindow(self)
        child.show()
while True:
    try:
        fps = int(raw_input("How many frames per second does the video have? "))
        break
    except:
        print "Please enter an Integer value"

font = cv2.FONT_HERSHEY_SIMPLEX
cap = cv2.VideoCapture(tempdir)
height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))


#Code for creating windows
# QApplication created only here.
app = QtGui.QApplication([])
window = MyWindow()
"""End"""
length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

"""
Function called when track bar is moved
Changes video frame along with movement
"""
def onChanged(x):
    global currentFrame,finalFrame
    finalFrame = False
    currentFrame = x

"""returns the (minimum,maximum) x values of the centers of the circles"""
def extremesX():
    global circleCoords
    minimum = float("inf")
    maximum = float("-inf")
    
    for (x,y,r) in circleCoords:
        minimum = min(minimum,x)
        maximum = max(maximum,x)
    return (minimum,maximum)

"""returns the (minimum,maximum) y values of the centers of the circles"""
def extremesY():
    global circleCoords
    minimum = float("inf")
    maximum = float("-inf")
    
    for (x,y,r) in circleCoords:
        minimum = min(minimum,y)
        maximum = max(maximum,y)
    return (minimum,maximum)

"""stores all the frames in an array and puts some information on them"""
memory = [-1]
print "Processing video...May take a few seconds"
for j in range(length):
    ret,frame = cap.read()
    
    #add frame number to video
    cv2.putText(frame,str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),(0,height), font, 2,(255,255,255))
    #add seconds to video
    cv2.putText(frame,str("{0:.2f}".format(float(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)/float(fps))))+'s',(0,height-50), font, 1,(255,255,255))
    for i in range(1+(height/100)):
        cv2.line(frame,(0,i*100),(width,i*100),(0,0,0),1)
    for i in range(1+(width/100)):
        cv2.line(frame,(i*100,0),(i*100,height),(0,0,0),1)
    frame = cv2.resize(frame,(0,0),fx=2,fy=2)
    memory += [frame]

  
"""advances current frame and considers pause and speed"""  
def advance():
    global finalFrame,currentFrame,pause,drawn
    if not pause and not finalFrame:
        drawn = False
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
                
    
currentFrame = 1
speed = 0
finalFrame = False
pause = True #video starts paused
drawn = False#if circle has been drawn on page
cv2.namedWindow('frame')
#create trackbar with length = to the number of frames, linked to onChanged function
cv2.createTrackbar('Frames','frame',0,length,onChanged)
cv2.setMouseCallback('frame', on_mouse)
circleCoords = []

while(cap.isOpened()):
    
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
    circles = cv2.HoughCircles(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.cv.CV_HOUGH_GRADIENT, 1.2, 100)
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
 
        # loop over the (x, y) coordinates and radius of the circles
        if not drawn:
            for (x, y, r) in circles:
                circleCoords += [(x,y,r)]
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
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
