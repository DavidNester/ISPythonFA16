import numpy as np
import cv2
from PyQt4 import QtCore
from PyQt4 import QtGui

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

def redColor():
    global color
    color = (255,0,0)

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
        redButton = QtGui.QPushButton('Red')
        whiteButton = QtGui.QPushButton('White')
        label1 = QtGui.QLabel("Shape")
        label2 = QtGui.QLabel("Color")
        layout.addWidget(label1,0,0)
        layout.addWidget(circleButton ,1,0)
        layout.addWidget(lineButton ,1,1)
        layout.addWidget(label2, 2, 0)
        layout.addWidget(redButton,3,0)
        layout.addWidget(whiteButton,3,1)
        circleButton.clicked.connect(circleChoice)
        lineButton.clicked.connect(lineChoice)
        redButton.clicked.connect(redColor)
        whiteButton.clicked.connect(whiteColor)
        self.setLayout(layout)
        self.setWindowTitle("Toolbar");
    def create_child(self):
        # here put the code that creates the new window and shows it.
        child = MyWindow(self)
        child.show()
        
font = cv2.FONT_HERSHEY_SIMPLEX
pause = False
cap = cv2.VideoCapture('pendulum.MOV')
frameMemory = []
#offset so that dont have to subtract 1 every time we access a frame
frameMemory += [-1]

height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))



while(cap.isOpened()):
    global option, color
    cv2.namedWindow('frame')
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
    
    cv2.setMouseCallback('frame', on_mouse) 
    
    if cv2.waitKey(1) & 0xFF == ord('p'):
        if pause:
            pause = False
        else:
            pause = True
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('t'):
        """Code for creating windows"""
        # QApplication created only here.
        app = QtGui.QApplication([])
        window = MyWindow()
        window.show()
        app.exec_()
        """End"""

    """Code for drawing on video"""

    #drawing line
    if startPoint == True and endPoint == True:
        if option == 2:
            cv2.line(gray, (rect[0], rect[1]), (rect[2], rect[3]), color, 2)
        elif option == 1:
            cv2.circle(gray, (rect[0], rect[1]), 50, color, -1)
        
    for i in range(1+(height/100)):
        cv2.line(gray,(0,i*100),(width,i*100),(0,255,255),1)
    for i in range(1+(width/100)):
        cv2.line(gray,(i*100,0),(i*100,height),(0,255,255),1)
    cv2.imshow('frame', gray)
    #put frame in memory array indexed by frame number
    frameMemory += [gray]
    """End"""

    
    



cap.release()
cv2.destroyAllWindows()
