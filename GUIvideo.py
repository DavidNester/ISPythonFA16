import numpy as np
import cv2
from PyQt4 import QtCore
from PyQt4 import QtGui
import Tkinter
import tkFileDialog
import os

"""
Function called when track bar is moved
Changes video frame along with movement
"""
def onChanged(x):
    global finalFrame
    #allow video to start again after movement if we have reached the final frame
    finalFrame = False
    #set video to frame corresponding to slider bar
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,x)
    err,img = cap.read()
    #switch to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #add frame number
    cv2.putText(gray,str(x),(0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))), font, 2,(255,255,255))


"""Code for retrieving file name"""
root = Tkinter.Tk()
root.withdraw() #use to hide tkinter window

currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV")
                                                         ,("HTML files", "*.html;*.htm")
                                                         ,("All files", "*.*"))) #requests file name and type of files
    
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
    color = (0, 255,0)

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
pause = False
cap = cv2.VideoCapture(tempdir) #open file from the selected before
frameMemory = []
#offset so that we dont have to subtract 1 every time we access a frame
frameMemory += [-1]

height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))

finalFrame = False

#variables used to control speed of playback
speed = 1
#counts up to speed variable. next frame is returned when counter = speed
counter = 0
#wrapper function to get next frame that throttles based on speed variable and counter
def getFrame():
    global counter, frame
    #stop getting new frames if we are on the final frame
    if not finalFrame:
        #if not paused get frame
        if not pause:
            if (counter + 1) >= speed:
                ret, frame = cap.read()
                counter = 0
            else:
                counter += 1
#Code for creating windows
# QApplication created only here.
app = QtGui.QApplication([])
window = MyWindow()
window.show()
"""End"""

overlay = cv2.imread("C:/Users/Kyle/Documents/GitHub/ISPythonFA16/overlay2.png", 1)

while(cap.isOpened()):
    if cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT) == cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES):
        finalFrame = True
    #global option, color
    cv2.namedWindow('frame')
    getFrame()


    cv2.addWeighted(overlay, .90, frame, .10, 0, frame)
    
    #switch to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    
    #add frame number to video
    cv2.putText(gray,str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),(0,height), font, 2,(255,255,255))
    #add seconds to video
    cv2.putText(gray,str("{0:.2f}".format(float(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)/float(fps))))+'s',(0,height-50), font, 1,(255,255,255))
    #create trackbar with length = to the number of frames, linked to onChanged function
    cv2.createTrackbar('Frames','frame',0,int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)),onChanged)
    #sets the trackbar position equal to the frame number
    cv2.setTrackbarPos('Frames','frame',int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)))
    
    cv2.setMouseCallback('frame', on_mouse)
    
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
        speed *= 2
        print speed
    #faster
    if key == ord('e'):
        if speed != 1:
            speed = speed/2
        print speed
    #drawing options
    if key == ord('t'):
        window.show()


    """Code for drawing on video"""
    #drawing line
    if startPoint == True and endPoint == True:
        if option == 2:
            cv2.line(overlay, (rect[0]/2, rect[1]/2), (rect[2]/2, rect[3]/2), color, 2)
        elif option == 1:
            cv2.circle(overlay, (rect[0]/2, rect[1]/2), 50, color, -1)
        
    for i in range(1+(height/100)):
        cv2.line(gray,(0,i*100),(width,i*100),(0,255,255),1)
    for i in range(1+(width/100)):
        cv2.line(gray,(i*100,0),(i*100,height),(0,255,255),1)
        
    gray = cv2.resize(gray,(0,0),fx=2,fy=2)
    cv2.imshow('frame', gray)
    #put frame in memory array indexed by frame number
    frameMemory += [gray]
    """End"""

    
    



cap.release()
cv2.destroyAllWindows()
