import cv2
from PyQt4 import QtGui

"""returns the (minimum,maximum) x values of the centers of the circles"""
def extremesX(circleCoords):
    minimum = float("inf")
    maximum = float("-inf")
    
    for (x,y,r) in circleCoords:
        minimum = min(minimum,x)
        maximum = max(maximum,x)
    return (minimum,maximum)

"""returns the (minimum,maximum) y values of the centers of the circles"""
def extremesY(circleCoords):
    minimum = float("inf")
    maximum = float("-inf")
    
    for (x,y,r) in circleCoords:
        minimum = min(minimum,y)
        maximum = max(maximum,y)
    return (minimum,maximum)

"""adds info and grid to video"""
def process(frame,height,width,fps,cap):
    #add frame number to video
    cv2.putText(frame,str(int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))),(0,height), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255))
    #add seconds to video
    cv2.putText(frame,str("{0:.2f}".format(float(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)/float(fps))))+'s',(0,height-50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    for i in range(1+(height/100)):
        cv2.line(frame,(0,i*100),(width,i*100),(0,0,0),1)
    for i in range(1+(width/100)):
        cv2.line(frame,(i*100,0),(i*100,height),(0,0,0),1)
    #frame = cv2.resize(frame,(0,0),fx=2,fy=2)
    return frame


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
        
def feedback(feedback):
    img=clear()
    cv2.putText(img,feedback,(0,20), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0))
    return img
def clear():
    img = cv2.imread('white.png')
    cv2.putText(img,'q = quit',(0,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    cv2.putText(img,'w = slow down',(0,105), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    cv2.putText(img,'e = speed up',(0,130), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    cv2.putText(img,'p = pause',(0,155), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    cv2.putText(img,'delete = clear mouse input (when paused)',(300,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    cv2.putText(img,'->    = next frame (when paused)',(300,105), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    cv2.putText(img,'<-    = previous frame (when paused)',(300,130), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255))
    return img
