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
from scipy.interpolate import interp1d
#object tracking
from collections import deque
import argparse
import imutils
import matplotlib
from skimage.io._plugins.qt_plugin import ImageLabel
#from alembic.command import current
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

global size, r_pixel, f, a, count, w
count = 1
size = 120
speed = 0
circleCoords = {} #all the (x,y,r) data for all of the circles
plot = True
lastFrameWithCircle = 0
currentFrame = 0
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
center = None
outside = None
first = None
bottom = ''
frame = ''
xCoords = []
tCoords = []
pause = True

"""INPUT FILE"""
root = Tk()
root.withdraw() #use to hide tkinter window
currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("HTML files", "*.html;*.htm"),("Movie files", "*.MOV"),("All files", "*.*"))) #requests file name and type of files
root.destroy()

"""checks to see if a circle is in a reasonable place based on the previous circles"""
def normal(x,y,r):
    global circleCoords,lastFrameWithCircle,currentFrame
    #accept data if we have no prior knowledge
    if lastFrameWithCircle == 0:
        return True
    oldX,oldY,oldR = circleCoords[lastFrameWithCircle]
    #make sure that the new circle agrees with the old circle
    if abs(oldX-x) < oldR/2 and abs(oldY-y) < oldR/2 and abs(r-oldR) < oldR/2:
        return True
    return False

"""given a frame it finds the circle and returns the frame with the circle drawn on it"""
def findCircles(frame):
    global lastFrameWithCircle,pause
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
    return frame

"""distance between two coordinates"""
def distance(p1,p2):
    dx = (p1[0]-p2[0])*1.0
    dy = (p1[1]-p2[1])*1.0
    return int((dx**2 + dy**2)**.5)

"""Creating windows"""
#tkinter GUI functions----------------------------------------------------------
def quit_(root):
    root.destroy()

  
def update_image(image_label, list, count):
   global circleCoords, pause, plot, size, xAxis, yAxis,canvas, foundR, size_pixel, frame
   frame = list[count]
   currentFrame = count
   
   #if we already have the frame in memory then use circles that were found
   if currentFrame in circleCoords.keys():
       x,y,r = circleCoords[currentFrame]
   
   #find new circles if new frame and not paused
   else:
       if not pause:
           frame = findCircles(frame)
            
  
    
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
          tCoords += [count]
          
          if foundR == False:
              r_pixel = r
              foundR=True
              size_pixel = int(r_pixel)/size
              
      #plot the data
      xAxis.plot(tCoords,xCoords,'ro')
      yAxis.plot(tCoords,yCoords,'ro')
      
      canvas.draw()
   
   im = cv2.cvtColor(list[count], cv2.COLOR_BGR2RGB)
   a = Image.fromarray(im)
   b = ImageTk.PhotoImage(image=a)
   image_label.configure(image=b)
   image_label._image_cache = b  # avoid garbage collection
   root.update()

def update_all(root, image_label, list):
   global count, speed, bottom
   if speed < 0:
       time.sleep((speed*.1)*-1) 
   elif speed > 0:
       count = count + (1*speed)
   if pause == False and count+1 < len(list):
       count += 1
       w.set(count)
       update_image(image_label, list, count)
       root.after(0, func=lambda: update_all(root, image_label, list))
   elif count+1 >= len(list):
       bottom.config(text='Total Distance')
       

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

"""Function called when the image is clicked on"""
"""used to get user input on location when no object is found by clicking center and outside of object"""
def on_mouse(event):
    #global rect,startPoint,endPoint
    global center,outside,currentFrame,circleCoords,lastFrameWithCircle,pause,length,height,width,fps,cap,first,points,ax,plot, frame, list, count
    #get only left mouse click
    x=event.x
    y=event.y
    print x, y
    
    #only use if paused (paused when nothing is found)'
    if pause:
        #if second click (outside)
        if center is not None:
            outside = (x,y)
            if first is None:
                first = (center[0],center[1],distance(center,outside),currentFrame)
                #points = ax.plot(currentFrame,center[0],'ro')[0]
                plot = True
            
            
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
        #if first click (center)
        else:
            center = (x,y)
            cv2.rectangle(list[count-1], (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            bottom.config(text='Click the outside')
                 
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

def submitData():
    global size, bottom
    size = float(input.get())
    information.destroy()
    input.destroy()
    submit.destroy()
    bottom = Label(master=root, text="Click on the middle")
    bottom.grid(row=3, column=0, columnspan=4)
 
    
if __name__ == '__main__':
   list = list()
   root = Tk()
   root.wm_title("Object Tracker")
   
   image_label = Label(master=root)# label for the video frame
   image_label.grid(row=0, column=0, columnspan=4)
   p = image_capture(list)
   image_label.bind('<Button-1>',on_mouse)
   
   f = Figure(figsize=(10,5), dpi=100)
   xAxis = f.add_subplot(121)
   yAxis = f.add_subplot(122)
   
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
   
   information = Label(master=root, text="Enter the size of the object (cm): ")
   information.grid(row=3, column=0, columnspan=2)
   
   input = Entry(master=root)
   input.grid(row=3, column=2)
   
   submit = Button(master=root, text='Submit', command=submitData)
   submit.grid(row=3, column=3)
   
   # setup the update callback
   root.after(0, func=lambda: update_all(root, image_label, list))
   print 'finished video'
   
   root.lift()
   root.attributes('-topmost',True)
   root.after_idle(root.attributes,'-topmost',False)
   mainloop()


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
