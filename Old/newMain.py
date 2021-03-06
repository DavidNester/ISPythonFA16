import time
import numpy as np
import cv2
from PyQt4 import QtCore
from PyQt4 import QtGui
from Tkinter import *
import tkFileDialog
import os
from multiprocessing import Process, Queue
from Queue import Empty
import cv2.cv as cv
from PIL import Image, ImageTk
import extra
from scipy.interpolate import interp1d
#object tracking
from collections import deque
import argparse
import imutils

import matplotlib
#from skimage.io._plugins.qt_plugin import ImageLabel
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from circleTracker import CircleTracker

global size, r_pixel, f, a, count, w
count = 1
size = 0
speed = 0



def submitData():
    global size, fps
    size = float(e1.get())
    fps = e2.get()

"""INPUT FILE"""
root = Tk()
print root.tk.call('info', 'patchlevel')
root.withdraw() #use to hide tkinter window
currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV")
                                                         ,("HTML files", "*.html;*.htm")
                                                         ,("All files", "*.*"))) #requests file name and type of files
#root.destroy()

#tkinter GUI functions----------------------------------------------------------
def quit_(root):
   root.destroy()
   
def update_image(image_label, list, count):
   frame = list[count]
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   a = Image.fromarray(im)
   b = ImageTk.PhotoImage(image=a)
   image_label.configure(image=b)
   image_label._image_cache = b  # avoid garbage collection
   root.update()

pause = True

def update_all(root, image_label, list):
    global count, speed
    if speed < 0:
        time.sleep((speed*.1)*-1)
    elif speed > 0:
        count = count + (1*speed)
    if pause == False and count+1 < len(list):
       count += 1
       w.set(count)
       update_image(image_label, list, count)
       root.after(0, func=lambda: update_all(root, image_label, list))

#multiprocessing image processing functions-------------------------------------
def image_capture(list):
   vidFile = cv2.VideoCapture(tempdir)
   while True:
      try:
         flag, frame=vidFile.read()
         if flag==0:
             break
         list.append(frame)
         
      except:
         continue
     
def playVideo(root, image_label, list):
    global pause
    pause = False
    update_all(root, image_label, list)
    
def pauseVideo():
    global pause
    pause = True
    
def updateCount(image_label, list):
    global count
    count = w.get()
    update_image(image_label, list, count)

def slowDown():
    global speed
    speed -= 1

def fastForward():
    global speed
    speed += 1



if __name__ == '__main__':
   list = list()
   #root = Tk()
   image_label = Label(master=root)# label for the video frame
   image_label.grid(row=0, column=0, columnspan=2)
   p = image_capture(list)
   
   f = Figure(figsize=(5,5), dpi=100)
   a = f.add_subplot(111)
   
   canvas = FigureCanvasTkAgg(f, master=root)
   canvas.show()
   canvas.get_tk_widget().grid(row=0, column=2, rowspan=4)
   
   size = len(list)
   update_image(image_label, list, 0)
   slider_width = image_label.winfo_width()
   w = Scale(master=root, from_=0, to=size, orient=HORIZONTAL, length=slider_width)
   w.bind("<ButtonRelease-1>", updateCount)
   w.grid(row=1, column=0, columnspan=2)

   # pause button
   pauseButton = Button(master=root, text="Pause", command=pauseVideo)
   pauseButton.grid(row=2, column=0)
   
   #play button
   playButton = Button(master=root, text="Play", command= lambda: playVideo(root, image_label, list))
   playButton.grid(row=2, column=1)
   
   #slow down
   slowButton = Button(master=root, text='Slow Down', command=slowDown)
   slowButton.grid(row=2, column=2)
   
   #fast forward
   fastButton = Button(master=root, text='Fast Forward', command=fastForward)
   fastButton.grid(row=2, column=3)
   
   instruction = Label(master=root, text="Click on the center of the circle")
   instruction.grid(row=3, column=0, columnspan=2)
   # setup the update callback
   root.after(0, func=lambda: update_all(root, image_label, list))
   print 'finished video'
   
   root.lift()
   root.attributes('-topmost',True)
   root.after_idle(root.attributes,'-topmost',False)
   mainloop()

""""""
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

master = Tk()
Label(master, text="Radius Size (cm): ").grid(row=0)
Label(master, text="Frames per Second: ").grid(row=1)

e1 = Entry(master)
e2 = Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

Button(master, text='Submit', command=submitData).grid(row=3, column=1, sticky=W, pady=4)

mainloop( )

#used for mouse input from user
center = None
outside = None

"""Function called when the image is clicked on"""
"""used to get user input on location when no object is found by clicking center and outside of object"""
def on_mouse(event,x,y,flags,params):
    global tracker, plot, center, outside
    #get only left mouse click
    print "click"   
    if event == cv2.EVENT_LBUTTONDOWN:
        #make sure click was in window
        if x<0 or x>tracker.width or y<0 or y>tracker.height:
            pass
        #only use if paused (paused when nothing is found)'
        if tracker.pause:
            #if second click (outside)
            if center is not None:
                outside = (x,y)
                if tracker.first is None:
                    tracker.first = (center[0],center[1],distance(center,outside),tracker.currentFrame)
                    #points = ax.plot(currentFrame,center[0],'ro')[0]
                    plot = True
                #draw inputted cricle on frame and then show it
                cap.set(1,tracker.currentFrame)
                ret, frame = cap.read()
                frame = extra.process(frame,tracker.height,tracker.width,fps,cap)
                tracker.updateFrame(frame)
                
                x,y = center
                r = distance(center,outside)
                tracker.circleCoords[tracker.currentFrame] = (x,y,r)
                cv2.setTrackbarPos('Frames','frame',tracker.currentFrame)
                
                cv2.circle(tracker.frame, (x, y), r, (228, 20, 20), 4)
                cv2.rectangle(tracker.frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                tracker.lastFrameWithCircle = tracker.currentFrame
                cv2.imshow('frame', tracker.frame)
                
                #return to normal state
                tracker.pause = False
                center = outside = None
                img = extra.clear(tracker.pause)
            #if first click (center)
            else:
                center = (x,y)
                img = extra.feedback("Please click on the edge of the circle",tracker.pause)

"""distance between two coordinates"""
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
updates currentFrame and lastFrameWithCircle
"""
def onChanged(x):
    global tracker
    tracker.finalFrame = False
    tracker.currentFrame = x
    if tracker.lastFrameWithCircle != 0:
        #lastFrameWith circle is highest frame in record that is less than the new currentFrame
        tracker.lastFrameWithCircle = max([i for i in tracker.circleCoords.keys() if i < tracker.currentFrame])

    
"""BEGINNING OF THE CODE"""
    
video = tempdir

#video data
cap = cv2.VideoCapture(video)
tracker = CircleTracker(cap)

"""VIDEO CONTROL VARIABLES AND DATA VARIABLES"""
plot = False
plt.ion()
"""
cv2.namedWindow('frame')
#create trackbar with length = to the number of frames, linked to onChanged function
cv2.createTrackbar('Frames','frame',0,tracker.length,onChanged)
cv2.setMouseCallback('frame', on_mouse)

img = cv2.imread('white.png')
cv2.moveWindow('frame',0,0)

cv2.namedWindow('Instructions')
cv2.moveWindow('Instructions',0,tracker.height+75)
img = extra.feedback("Please click on the center of the circle",tracker.pause)
cv2.imshow('Instructions',img)
"""
foundR = False
dCoords = []
size_pixel = 0
r_pixel = 0
fps = 123
xdistance_cm = 0
xdistance_in = 0
ydistance_cm = 0
ydistance_in = 0

fig, ax = plt.subplots(1, 1)
ax.set_xlim(0, tracker.length)

"""LOOP FOR DISPLAYING VIDEO"""
while(True):
    #advance frame
    tracker.advance()
    
    """BUTTON COMMANDS"""
    #get button press
    key = cv2.waitKey(1) & 0xFF

    if key == ord('p'):#pause
        if tracker.pause:
            tracker.pause = False
        else:
            tracker.pause = True
        img = extra.feedback("",tracker.pause)
    if key == ord('q'):#quit
        break
    if key == ord('w'):#slower
        if tracker.speed > -3:
            tracker.speed -= 1
    if key == ord('e'):#faster
        if tracker.speed < 3:
            tracker.speed += 1
    if key == 3: #right arrow
        tracker.currentFrame += 1
    if key == 2: #left arrow
        tracker.currentFrame -= 1
    if key == 127: #delete key -> get rid of mouse input
        if tracker.pause:
            center = None
            outside = None
            #img = extra.feedback("Please click on the center of the circle",tracker.pause)
        

    #get frame
    cap.set(1,tracker.currentFrame)
    ret, frame = cap.read()
    frame = extra.process(frame,tracker.height,tracker.width,fps,cap)
    tracker.updateFrame(frame)
    
    
    #sets the trackbar position equal to the frame number
    cv2.setTrackbarPos('Frames','frame',tracker.currentFrame)

    #if we already have the frame in memory then use circles that were found
    if tracker.currentFrame in tracker.circleCoords.keys():
        x,y,r = tracker.circleCoords[tracker.currentFrame]
        
        # draw the circle in the output image, then draw a rectangle
        # corresponding to the center of the circle
        cv2.circle(tracker.frame, (x, y), r+5, (228, 20, 20), 4)
        cv2.rectangle(tracker.frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    #find new circles if new frame and not paused
    if not tracker.pause:
        tracker.findCircles()
   
    if center and not outside:
        cv2.rectangle(tracker.frame, (center[0] - 5, center[1] - 5), (center[0] + 5, center[1] + 5), (0, 128, 255), -1)
    
    #show frames
    #cv2.imshow('Instructions',img)
    cv2.imshow('frame', tracker.frame)
    
    
    """Plots motion in matplotlib"""
    """if plot:
        
       xCoords = []
       yCoords = []
       rCoords = []
       tCoords = [] 
        
       #get all frames,x,y,r and store each in their own array
       for frame in circleCoords.keys():
           x,y,r = circleCoords[frame]
           xCoords += [x]
           yCoords += [y]
           rCoords += [r]
           tCoords += [frame]
           
           if foundR == False:
               r_pixel = r
               foundR=True
       size_pixel = int(r_pixel)/size
       #plot the data
       plt.figure(1)
       plt.subplot(211)
       plt.plot(tCoords,xCoords,'ro')
       plt.subplot(212)
       plt.plot(tCoords,yCoords,'ro')
       #plt.subplot(213)
       #plt.plot(tCoords,rCoords, 'ro')
       plot = False
       xdistance_cm = round(((max(xCoords) - min(xCoords)) / size_pixel),2)
       xdistance_in = round((xdistance_cm/ 2.54),2)  
       
       ydistance_cm = round(((max(yCoords) - min(yCoords)) / size_pixel),2)
       ydistance_in = round((ydistance_cm/ 2.54),2)
    """
    """
    if plot and first is not None:
        
        x,y,r = circleCoords[lastFrameWithCircle]
        """
    """Attempt at making plotting work on mac
        points.set_data(lastFrameWithCircle,x)
        # restore background
        fig.canvas.restore_region(background)

        # redraw just the points
        ax.draw_artist(points)

        # fill in the axes rectangle
        fig.canvas.blit(ax.bbox)
        """
    """
        xCoords += [x]
        tCoords += [lastFrameWithCircle]
        plt.plot(tCoords,xCoords,'ro')
        
        plot = False
        """

    

master = Tk()
resultx = StringVar()
resulty = StringVar()
response = "The circle traveled " + str(xdistance_cm) + " cm horizontally (or " + str(xdistance_in) + "in)."
responsey = "The circle traveled " + str(ydistance_cm) + " cm vertically (or " + str(ydistance_in) + "in)."
resultx.set(response)
resulty.set(responsey)
Label(master, textvariable=resultx).grid(row=0)
Label(master, textvariable=resulty).grid(row=1)

mainloop()

#end video viewing
cap.release()
cv2.destroyAllWindows()

plt.clf()

