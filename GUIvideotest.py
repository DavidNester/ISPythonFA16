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
import time
import matplotlib.pyplot as plt
import extra
from scipy.interpolate import interp1d
#object tracking
from collections import deque
import argparse
import imutils

import matplotlib
from skimage.io._plugins.qt_plugin import ImageLabel
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

global size, r_pixel, f, a, count, w
count = 1
size = 0
speed = 0

def submitData():
    global size, fps
    size = float(e1.get())
    fps = e2.get()
    master.destroy()

"""INPUT FILE"""
root = Tk()
root.withdraw() #use to hide tkinter window
currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("HTML files", "*.html;*.htm")
                                                        ,("Movie files", "*.MOV")
                                                         ,("All files", "*.*"))) #requests file name and type of files
root.destroy()
print tempdir
"""Creating windows"""
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
   root = Tk()
   image_label = Label(master=root)# label for the video frame
   image_label.grid(row=0, column=0, columnspan=4)
   p = image_capture(list)
   
   f = Figure(figsize=(5,5), dpi=100)
   a = f.add_subplot(111)
   
   canvas = FigureCanvasTkAgg(f, master=root)
   canvas.show()
   canvas.get_tk_widget().grid(row=0, column=4, rowspan=4)
   
   size = len(list)
   update_image(image_label, list, 0)
   slider_width = image_label.winfo_width()
   w = Scale(master=root, from_=0, to=size, orient=HORIZONTAL, length=slider_width)
   w.bind("<ButtonRelease-1>", lambda event: updateCount(image_label, list))
   w.grid(row=1, column=0, columnspan=4)

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
   instruction.grid(row=3, column=0, columnspan=3)
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


#used for mouse input from user
center = None
outside = None

"""Function called when the image is clicked on"""
"""used to get user input on location when no object is found by clicking center and outside of object"""
def on_mouse(event,x,y,flags,params):
    #global rect,startPoint,endPoint
    global center,outside,currentFrame,circleCoords,lastFrameWithCircle,pause,length,height,width,fps,cap,img,first,points,ax,plot
    #get only left mouse click
   
    if event == cv2.EVENT_LBUTTONDOWN:
        #make sure click was in window
        if x<0 or x>width or y<0 or y>height:
            pass
        #only use if paused (paused when nothing is found)'
        if pause:
            #if second click (outside)
            if center is not None:
                outside = (x,y)
                if first is None:
                    first = (center[0],center[1],distance(center,outside),currentFrame)
                    #points = ax.plot(currentFrame,center[0],'ro')[0]
                    plot = True
                #draw inputted cricle on frame and then show it
                cap.set(1,currentFrame)
                ret, frame = cap.read()
                #frame = extra.process(frame,height,width,fps,cap)
                #frame = memory[currentFrame]
                x,y = center
                r = distance(center,outside)
                circleCoords[currentFrame] = (x,y,r)
                #cv2.setTrackbarPos('Frames','frame',currentFrame)
                
                cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                lastFrameWithCircle = currentFrame
                #cv2.imshow('frame', frame)
                
                #return to normal state
                pause = False
                center = outside = None
                img = extra.clear(pause)
            #if first click (center)
            else:
                center = (x,y)
                img = extra.feedback("Please click on the edge of the circle",pause)

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
    global currentFrame,finalFrame,lastFrameWithCircle, circleCoords
    finalFrame = False
    currentFrame = x
    if lastFrameWithCircle != 0:
        #lastFrameWith circle is highest frame in record that is less than the new currentFrame
        lastFrameWithCircle = max([i for i in circleCoords.keys() if i < currentFrame])


"""advances current frame and considers pause and speed"""  
def advance():
    global finalFrame,currentFrame,pause,plot
    #only advance if video is not paused or at the end
    if not pause and not finalFrame:
        plot = True
        if speed == 0:
            if currentFrame + 1 < length:
                currentFrame += 1
        #if sped up then skip frames
        elif speed > 0:
            if currentFrame + speed**2 < length:
                currentFrame += speed**2
        #if slowed down then pause before giving next frame
        elif speed < 0:
            for i in range(speed**2):
                time.sleep(.1)
            if currentFrame + 1 < length:
                currentFrame += 1

"""checks to see if a circle is in a reasonable place based on the previous circles"""
def normal(x,y,r):
    global circleCoords,lastFrameWithCircle,currentFrame
    #accept data if we hae no prior knowledge
    if lastFrameWithCircle == 0:
        return True
    oldX,oldY,oldR = circleCoords[lastFrameWithCircle]
    #make sure that the new circle agrees with the old circle
    if abs(oldX-x) < oldR/2 and abs(oldY-y) < oldR/2 and abs(r-oldR) < oldR/2:
        return True
    return False

"""given a frame it finds the circle and returns the frame with the circle drawn on it"""
def findCircles(frame):
    global lastFrameWithCircle,pause,img
    original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #switch to grayscale   
    retval, image = cv2.threshold(original, 50, 255, cv2.cv.CV_THRESH_BINARY)
    
    el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    image = cv2.dilate(image, el, iterations=4)
    
    image = cv2.GaussianBlur(image, (13, 13), 0)
    
    found = False
    alpha = 90
    while not found:
        circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT, 1.2, 100, param2 = alpha) #find circles 
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            #check if the circles agree with previous data
            for x,y,r in circles:
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
            #if no circles found then try again with new threshold (threshold stops at 30)
            alpha -= 5
            if alpha <= 30:
                found = True
    #if we havent found a circle in more than 10 frames then ask the user for help
    if currentFrame-lastFrameWithCircle > 10:
        pause = True
        img = extra.feedback("Please click on the center of the circle",pause)
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
video = tempdir

#video data
cap = cv2.VideoCapture(video)
font = cv2.FONT_HERSHEY_SIMPLEX
height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))


"""VIDEO CONTROL VARIABLES AND DATA VARIABLES"""
currentFrame = 1
speed = 0
finalFrame = False
pause = True #video starts paused
plot = False
first = None
plt.ion()

"""
cv2.namedWindow('frame')
#create trackbar with length = to the number of frames, linked to onChanged function
cv2.createTrackbar('Frames','frame',0,length,onChanged)
cv2.setMouseCallback('frame', on_mouse)
circleCoords = {} #all the (x,y,r) data for all of the circles
#used for predicting location of next circle if one is not found for a while based on previous activity
lastFrameWithCircle = 0

cv2.moveWindow('frame',0,0)

cv2.namedWindow('Instructions')
cv2.moveWindow('Instructions',0,height+75)
img = extra.feedback("Please click on the center of the circle",pause)
#cv2.imshow('Instructions',img)
"""

foundR = False
xCoords = []
yCoords = []
rCoords = []
tCoords = []
dCoords = []
size_pixel = 0
r_pixel = 0
fps = 123
xdistance_cm = 0
xdistance_in = 0
ydistance_cm = 0
ydistance_in = 0
        
xCoords = []
tCoords = []

fig, ax = plt.subplots(1, 1)
ax.set_xlim(0, length)
"""
plt.show(False)
plt.draw()
background = fig.canvas.copy_from_bbox(ax.bbox)
"""     
"""LOOP FOR DISPLAYING VIDEO"""
while(True):
    #advance frame
    advance()
    
    """BUTTON COMMANDS"""
    #get button press
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('p'):#pause
        if pause:
            pause = False
        else:
            pause = True
        img = extra.feedback("",pause)
    if key == ord('q'):#quit
        break
    if key == ord('w'):#slower
        if speed > -3:
            speed -= 1
    if key == ord('e'):#faster
        if speed < 3:
            speed += 1
    """not really used anymore"""
    #if key == ord('t'):#drawing options
    #   window.show()
    if key == 3: #right arrow
        currentFrame += 1
    if key == 2: #left arrow
        currentFrame -= 1
    if key == 127: #delete key -> get rid of mouse input
        if pause:
            center = None
            outside = None
            img = extra.feedback("Please click on the center of the circle",pause)
        

    #get frame
    cap.set(1,currentFrame)
    ret, frame = cap.read()
    cv2.imshow('test', frame)
    #frame = extra.process(frame,height,width,fps,cap)
    
    
    #sets the trackbar position equal to the frame number
    #cv2.setTrackbarPos('Frames','frame',currentFrame)
    
    #if we already have the frame in memory then use circles that were found
    if currentFrame in circleCoords.keys():
        x,y,r = circleCoords[currentFrame]
        
        # draw the circle in the output image, then draw a rectangle
        # corresponding to the center of the circle
        #cv2.circle(frame, (x, y), r+5, (228, 20, 20), 4)
        #cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    #find new circles if new frame and not paused
    else:
        if not pause:
            frame = findCircles(frame)
            
    #if center and not outside:
        #cv2.rectangle(frame, (center[0] - 5, center[1] - 5), (center[0] + 5, center[1] + 5), (0, 128, 255), -1)
    
    #show frames
    #cv2.imshow('Instructions',img)
    #cv2.imshow('frame', frame)
    
    
    if center and not outside:
        cv2.rectangle(frame, (center[0] - 5, center[1] - 5), (center[0] + 5, center[1] + 5), (0, 128, 255), -1)
    
    #show frames
    cv2.imshow('Instructions',img)
    cv2.imshow('frame', frame)
    
    
    """Plots motion in matplotlib"""
    if plot:
        
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
       a.plot(tCoords,xCoords,'ro')
       plt.subplot(212)
       plt.plot(tCoords,yCoords,'ro')
       #plt.subplot(213)
       #plt.plot(tCoords,rCoords, 'ro')
       plot = False
       xdistance_cm = round(((max(xCoords) - min(xCoords)) / size_pixel),2)
       xdistance_in = round((xdistance_cm/ 2.54),2)  
       
       ydistance_cm = round(((max(yCoords) - min(yCoords)) / size_pixel),2)
       ydistance_in = round((ydistance_cm/ 2.54),2)
    
    if plot and first is not None:
        
        x,y,r = circleCoords[lastFrameWithCircle]
        
        """Attempt at making plotting work on mac"""
        """
        points.set_data(lastFrameWithCircle,x)
        # restore background
        fig.canvas.restore_region(background)
        # redraw just the points
        ax.draw_artist(points)
        # fill in the axes rectangle
        fig.canvas.blit(ax.bbox)
        """
        
        xCoords += [x]
        tCoords += [lastFrameWithCircle]
        plt.plot(tCoords,xCoords,'ro')
        
        plot = False
    


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
"""Plots motion in matplotlib"""
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
#plot the data

plt.figure(1)
plt.subplot(211)
plt.plot(tCoords,xCoords,'ro')
plt.xlabel('Frame')
plt.ylabel('x-pixel')
plt.subplot(212)
plt.plot(tCoords,yCoords,'ro')
plt.xlabel('Frame')
plt.ylabel('y-pixel')

"""attempt at data smoothing"""
"""plt.figure(2)
plt.subplot(211)
plt.plot(tCoords,rCoords,'r--')"""
"""f = interp1d(tCoords,xCoords, kind = 'cubic')
plt.subplot(212)
xnew = np.linspace(0,max(tCoords),num = 2*len(tCoords),endpoint = True)
plt.plot(xnew,f(xCoords),'--')"""


plt.show()
