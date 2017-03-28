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
import xlwt

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from circleTracker import CircleTracker

reset = ""
height = 0
width = 0
radio = 0
currentFrame = 1
size = 0
speed = 0
plot = False
xCoords = []
yCoords = []
rCoords = []
tCoords = []
size_pixel = 0
r_pixel = 0
var  = 0
f = None
fps = 123
xdistance_cm = 0
xdistance_in = 0
ydistance_cm = 0
ydistance_in = 0
center = None
outside = None
first = None
bottom = None
frame = None
pause = True
input = None
tempdir = None
title = None
xPlot = ""
w = ""
yPlot = ""
noPlot = None
bothPlot = ""
displayPlot = ""
var = ""
information  = ""
submit = ""
image_label = ""
backgrounds = []
axes = []
lines = []
canvas = None
old = 0

tracker = CircleTracker()

"""distance between two coordinates"""
def distance(p1,p2):
    dx = (p1[0]-p2[0])*1.0
    dy = (p1[1]-p2[1])*1.0
    return int((dx**2 + dy**2)**.5)

"""Creating windows"""
#tkinter GUI functions----------------------------------------------------------
def quit_(root):
    root.destroy()

  
def update_image(image_label, video, currentFrame):
   global tracker, pause, plot, size, xAxis, yAxis,canvas, size_pixel, frame, f,xLine,yLine,height,width, xCoords, var, lines, backgrounds,canvas,axes
   frame = video[currentFrame]
   x = None
   y = None
   if height == 0:
       height = len(frame)
       width = len(frame[0])
   
   #if we already have the frame in memory then use circles that were found
   if currentFrame in tracker.coords.keys():
       x,y,r = tracker.coords[currentFrame]
   
   #find new circles if new frame and not paused
   elif not pause and first is not None:
       frame,lost,x,y = tracker.find(frame,currentFrame,pause)
       if lost:
           bottom.config(text='Circle is lost. Please click on the center')
           pauseVideo()
   
   """Plots motion in matplotlib"""
   if plot and first is not None and x is not None:
      items = enumerate(zip(lines,axes,backgrounds),start = 1)
      for j,(line,ax,background) in items:
          f.canvas.restore_region(background)
          
          if j == 1:
              if var.get() == 1 or var.get() == 3:
                  line.set_ydata(x)
                  line.set_xdata(old)
              if var.get() == 2:
                  line.set_ydata(y)
                  line.set_xdata(old)
          if j == 2:
             line.set_ydata(y)
             line.set_xdata(old)
          ax.draw_artist(line)
          f.canvas.blit(ax.bbox)
      backgrounds = [f.canvas.copy_from_bbox(ax.bbox) for ax in axes]
   
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   a = Image.fromarray(im)
   b = ImageTk.PhotoImage(image=a)
   image_label.configure(image=b)
   image_label._image_cache = b  #avoid garbage collection
   root.update()

def update_all(root, image_label, video):
   global currentFrame, speed, bottom, xCoords, tracker, w, old
   old = currentFrame
   if speed < 0:
       time.sleep((speed*.1)*-1) 
   elif speed > 0:
       currentFrame = currentFrame + (1*speed)
   if pause == False and currentFrame < len(video):
       currentFrame += 1
       w.set(currentFrame)
       update_image(image_label, video, currentFrame)
       root.after(0, func=lambda: update_all(root, image_label, video))
       

#multiprocessing image processing functions-------------------------------------
def image_capture(video):
   global tempdir
   vidFile = cv2.VideoCapture(tempdir)
   while True:
      try:
         flag, frame=vidFile.read()
         if flag==0:
             break
         video.append(frame)
      except:
         continue

"""Function called when the image is clicked on"""
"""used to get user input on location when no object is found by clicking center and outside of object"""
def on_mouse(event):
    global center,outside,currentFrame,tracker,pause,first,points,ax,plot,frame,video,currentFrame, image_label
    #get only left mouse click
    x=event.x
    y=event.y
    
    #only use if paused (paused when nothing is found)'
    if pause:
        #if second click (outside)
        if center is not None:
            outside = (x,y)
            if var.get() != 0:
                plot = True
            if first is None:
                first = (center[0],center[1],distance(center,outside),currentFrame)
            
            
            x,y = center
            r = distance(center,outside)
            tracker.insert(x,y,r,currentFrame)
            cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            tracker.lastFrameWith = currentFrame
            #return to normal state
            playVideo(root,image_label,video)
            center = outside = None
            bottom.config(text='')
            # pause button
            pauseButton = Button(master=root, text="Pause", command=pauseVideo)
            pauseButton.grid(row=2, column=0)

            #play button
            playButton = Button(master=root, text="Play", command= lambda: playVideo(root, image_label, video))
            playButton.grid(row=2, column=1)
    
            #slow down
            slowButton = Button(master=root, text='Slow Down', command=slowDown)
            slowButton.grid(row=2, column=2)
    
            #fast forward
            fastButton = Button(master=root, text='Speed Up', command=fastForward)
            fastButton.grid(row=2, column=3)
    
            #export button
            export = Button(master=root, text='Export', command= lambda: exportData())
            export.grid(row = 4, column = 1)
        

        #if first click (center)
        else:
            center = (x,y)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            bottom.config(text='Click on the outside of the circle')
                 
def playVideo(root, image_label, video):
    global pause
    pause = False
    update_all(root, image_label, video)
    
def pauseVideo():
    global pause
    pause = True
    
def updateCurrentFrame(image_label, video):
    global currentFrame
    currentFrame = w.get()
    update_image(image_label, video, currentFrame)
    
def slowDown():
    global speed
    speed -= 1
    
def fastForward():
    global speed
    speed += 1

def reset():
    global radio,currentFrame,size,speed, var,plot,xCoords,rCoords,yCoords,tCoords,size_pixel,r_pixel,var,f,xAxis,yAxis,fps,xdistance_cm,ydistance_cm,xdistance_in,ydistance_in,center,outside,first,bottom,frame,pause, xLine,yLine,tracker



    radio = 0
    currentFrame = 1
    size = 120
    speed = 0
    plot = False
    xCoords = []
    yCoords = []
    rCoords = []
    tCoords = []
    size_pixel = 0
    r_pixel = 0
    var  = 0
    f = ""
    xAxis = ""
    yAxis = ""
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
    pause = True
    xLine = 0
    yLine = 0

    tracker = CircleTracker()
    update_all(root,image_label,video)

def submitData():
    global size, bottom, input, information, submit,xPlot,yPlot,bothPlot,noPlot,displayPlot
    size = float(input.get())
    information.destroy()
    input.destroy()
    submit.destroy()
    
    holder = Frame(master=root)
    
    noPlot = Radiobutton(master=holder, text="No Live Plots", variable=var, value=0)
    noPlot.pack(side="left")
    
    xPlot = Radiobutton(master=holder, text="X Axis", variable=var, value=1)
    xPlot.pack(side="left")
   
    yPlot = Radiobutton(master=holder, text="Y Axis", variable=var, value=2)
    yPlot.pack(side="left")
   
    bothPlot = Radiobutton(master=holder, text="Both Axis", variable=var, value=3)
    bothPlot.pack(side="left")
   
    displayPlot = Button(master=holder, text="Submit", command=displayChoice)
    displayPlot.pack(side="bottom", fill = "x")
    holder.grid(row=3, column=1, columnspan=4)
    
def displayChoice():
    global plot, f, yPlot, xPlot, bothPlot, displayPlot, var, bottom, axes, backgrounds, canvas, lines,old,noPlot
    xPlot.destroy()
    yPlot.destroy()
    bothPlot.destroy()
    noPlot.destroy()
    displayPlot.destroy()
    axes = []
    f = Figure(figsize=(5,5), dpi=100)

    if var.get()==1:
        axis = f.add_subplot(111)
        axis.set_xlim([0,len(video)])
        axis.set_ylim([0,width])
        axes +=[axis]
    elif var.get() == 2:
        axis = f.add_subplot(111)
        axis.set_xlim([0,len(video)])
        axis.set_ylim([0,height])
        axes +=[axis]
    elif var.get() == 3:
        f = Figure(figsize=(10,5), dpi=100)
        axis = f.add_subplot(121)
        axis.set_xlim([0,len(video)])
        axis.set_ylim([0,width])
        axes +=[axis]
        axis = f.add_subplot(122)
        axis.set_xlim([0,len(video)])
        axis.set_ylim([0,height])
        axes +=[axis]
   
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.show()
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=4, rowspan=4)

    if var.get() == 1:
        lines = [axes[0].plot(tCoords,xCoords,'ro',animated=True)[0]]
    elif var.get() == 2:
        lines = [axes[0].plot(tCoords,yCoords,'ro',animated=True)[0]]
    elif var.get() == 3:
        lines = [axes[0].plot(xCoords,tCoords,'ro',animated=True)[0],axes[1].plot(xCoords,tCoords,'ro',animated=True)[0]]
    backgrounds = [f.canvas.copy_from_bbox(ax.bbox) for ax in axes]


    bottom = Label(master=root, text="Click on the center of the circle. Move the trackbar if the object is not on the frame yet")
    bottom.grid(row=3, column=0, columnspan=4)


  
def exportData():
    global xCoords, yCoords, tracker, size, xdistance_cm,xdistance_in,ydistance_cm,ydistance_in
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Data')
    worksheet.write(0, 0, 'Frame')
    worksheet.write(0, 1, 'X Axis')
    worksheet.write(0, 2, 'Y Axis')
    worksheet.write(0, 3, 'Radius')
    worksheet.write(0, 5, 'Size of Object: ' + str(size) + 'cm')
    
    #centimeters / pixel
    centConversion = (size*1.0)/(tracker.getRadius()*1.0)
    
    xdistance_cm = (tracker.xMax() - tracker.xMin()) * centConversion
    ydistance_cm = (tracker.yMax() - tracker.yMin()) * centConversion
    
    xdistance_in = xdistance_cm/2.54#could be more exact in the future
    xdistance_in = xdistance_cm/2.54#could be more exact in the future
     
     
    frames = tracker.getTCoords()
    count = 1
    for f in frames:
        worksheet.write(count, 0, f)
        count += 1
          
    xCoords = tracker.getXCoords()
    count = 1
    for x in xCoords:
        worksheet.write(count, 1, x)
        count += 1
       
    count = 1
    yCoords = tracker.getYCoords()
    for y in yCoords:
       worksheet.write(count, 2, y)
       count += 1
        
    count = 1
    rCoords = tracker.getRCoords()
    for r in rCoords:
        worksheet.write(count, 3, r)
        count += 1
        
    
    
    file_name = tkFileDialog.asksaveasfile(mode='a', defaultextension=".xls")
    workbook.save(file_name.name)

def moved():
    global bottom
    if w.get() not in tracker.coords.keys():
        pauseVideo()
        bottom.config(text='Click on the center of the circle')
    updateCurrentFrame(image_label,video)

def open():
   global tempdir, title, xPlot, yPlot, bothPlot, displayPlot, var, input, reset, information, submit, image_label, w
   openButton.destroy()
   title.destroy()
   
   """INPUT FILE"""
   currdir = os.getcwd() #sets current directory
   tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV"), ("HTML files", "*.html;*.htm"),("All files", "*.*"))) #requests file name and type of files

   var = IntVar()
   image_label = Label(master=root) #label for the video frame
   image_label.grid(row=0, column=0, columnspan=4)
   p = image_capture(video)
   image_label.bind('<Button-1>',on_mouse)
   
   size = len(video)
   update_image(image_label, video, 0)
   slider_width = image_label.winfo_width()
   w = Scale(master=root, from_=0, to=size, orient=HORIZONTAL, length=slider_width)
   w.bind("<ButtonRelease-1>", lambda event: moved())
   w.grid(row=1, column=0, columnspan=4)

   information = Label(master=root, text="Enter the size of the object (cm): ")
   information.grid(row=3, column=0, columnspan=2)
   
   input = Entry(master=root)
   input.grid(row=3, column=2)
   
   submit = Button(master=root, text='Submit', command=submitData)
   submit.grid(row=3, column=3)
   
   end = Button(master=root, text='End', command= lambda: quit_(root))
   end.grid(row = 4, column = 3)
   
   reset = Button(master=root, text='Reset', command = reset)
   reset.grid(row = 4, column = 2)
   
   # setup the update callback
   root.after(0, func=lambda: update_all(root, image_label, video))    
  
if __name__ == '__main__':
   root = Tk()
   root.withdraw() #use to hide tkinter window
   video = list()
   root = Toplevel()
   root.wm_title("Object Tracker")

   title = Label(master=root, text="Welcome to the Object Tracker!")
   title.config(font=("Courier", 30))
   title.grid(row=0, column=0, padx=100,pady=50)
   
   openButton = Button(master=root, text="OPEN VIDEO", command= lambda: open())
   openButton.grid(row=1, column=0, padx=100, pady=50)
   
   root.lift()
   root.attributes('-topmost',True)
   root.after_idle(root.attributes,'-topmost',False)
   mainloop()


"""master = Tk()
master = Toplevel()
master.wm_title("Object Tracker")
resultx = StringVar()
resulty = StringVar()
xdistance_cm = tracker.xMax() - tracker.xMin()
ydistance_cm = tracker.yMax() - tracker.yMin()
#dont forget radius (avg(rCoords))
responsex = "The circle traveled " + str(xdistance_cm) + " cm horizontally (or " + str(xdistance_in) + "in)."
responsey = "The circle traveled " + str(ydistance_cm) + " cm vertically (or " + str(ydistance_in) + "in)."
resultx.set(responsex)
resulty.set(responsey)
Label(master, textvariable=resultx).grid(row=0)
Label(master, textvariable=resulty).grid(row=1)
mainloop()"""
