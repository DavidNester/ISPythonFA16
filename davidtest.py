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
#from chaco.shell.commands import yaxis
import xlwt

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from circleTracker import CircleTracker

height = 0
width = 0
radio = 0
count = 1
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

"""INPUT FILE"""
root = Tk()
root.withdraw() #use to hide tkinter window
currdir = os.getcwd() #sets current directory
tempdir = tkFileDialog.askopenfilename( filetypes = (("HTML files", "*.html;*.htm"),("Movie files", "*.MOV"),("All files", "*.*"))) #requests file name and type of files

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
   global xAxis,yAxis,canvas,f,xLine,yLine,height,width,frame
   frame = list[count]
   if height == 0:
       height = len(frame)
       width = len(frame[0])
   
   #if we already have the frame in memory then use circles that were found
   if count in tracker.coords.keys():
       x,y,r = tracker.coords[count]
   
   #find new circles if new frame and not paused
   elif not pause:
       frame,lost = tracker.find(frame,count,pause)
       if lost:
           bottom.config(text='Circle is lost. Please click on the center')
           pauseVideo()

   """Plots motion in matplotlib"""
   if plot:
      #plot the data
      if var.get() == 1 or var.get()==3:
          xLine, = xAxis.plot(tracker.getTCoords(),tracker.getXCoords(),'ro')
          xAxis.draw_artist(xAxis.patch)
          xAxis.draw_artist(xLine)
      if var.get() == 2 or var.get()==3:
          yLine, = yAxis.plot(tracker.getTCoords(),tracker.getYCoords(),'ro')
          yAxis.draw_artist(yAxis.patch)
          yAxis.draw_artist(yLine)
      if count == len(list)-1:
          xCoords = tracker.getXCoords()
          print "yp"
      f.canvas.draw()
   
   im = cv2.cvtColor(list[count], cv2.COLOR_BGR2RGB)
   a = Image.fromarray(im)
   b = ImageTk.PhotoImage(image=a)
   image_label.configure(image=b)
   image_label._image_cache = b  #avoid garbage collection
   root.update()

def update_all(root, image_label, list):
   global count
   if speed < 0:
       time.sleep((speed*.1)*-1) 
   elif speed > 0:
       count = count + (1*speed)
   if pause == False and count < len(list):
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

"""Function called when the image is clicked on"""
"""used to get user input on location when no object is found by clicking center and outside of object"""
def on_mouse(event):
    global center,outside,tracker,pause,first,frame
    #get only left mouse click
    x=event.x
    y=event.y
    
    #only use if paused (paused when nothing is found)'
    if pause:
        #if second click (outside)
        if center is not None:
            outside = (x,y)
            if first is None:
                first = (center[0],center[1],distance(center,outside),count)
            
            x,y = center
            r = distance(center,outside)
            tracker.insert(x,y,r,count)
            cv2.circle(frame, (x, y), r, (228, 20, 20), 4)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            tracker.lastFrameWith = count
            #return to normal state
            playVideo(root,image_label,list)
            center = outside = None
            bottom.config(text='')
        #if first click (center)
        else:
            center = (x,y)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            bottom.config(text='Click on the outside of the circle')
                 
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

def reset():
    global radio,count,size,speed,plot,xCoords,rCoords,yCoords,tCoords,size_pixel,r_pixel,var,f,xAxis,yAxis,fps,xdistance_cm,ydistance_cm,xdistance_in,ydistance_in,center,outside,first,bottom,frame,pause, xLine,yLine,tracker
    radio = 0
    count = 1
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
    update_all(root,image_label,list)

def submitData():
    global size, bottom
    size = float(input.get())
    information.destroy()
    input.destroy()
    submit.destroy()
    bottom = Label(master=root, text="Click on the center of the circle. Move the trackbar if the object is not on the frame yet")
    bottom.grid(row=3, column=0, columnspan=4)
    
def displayChoice():
    global plot, f, xAxis, yAxis
    plot = True
    xPlot.destroy()
    yPlot.destroy()
    bothPlot.destroy()
    displayPlot.destroy()
    f = Figure(figsize=(5,5), dpi=100)
    
    if var.get()==1:
        xAxis = f.add_subplot(111)
        xAxis.set_xlim([0,len(list)])
        xAxis.set_ylim([0,width])
    elif var.get() == 2:
        yAxis = f.add_subplot(111)
        yAxis.set_xlim([0,len(list)])
        yAxis.set_ylim([0,height])
    elif var.get() == 3:
        f = Figure(figsize=(10,5), dpi=100)
        xAxis = f.add_subplot(121)
        xAxis.set_xlim([0,len(list)])
        xAxis.set_ylim([0,width])
        yAxis = f.add_subplot(122)
        yAxis.set_xlim([0,len(list)])
        yAxis.set_ylim([0,height])
   
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.show()
    canvas.get_tk_widget().grid(row=0, column=4, rowspan=4)
 
  
def exportData():
    global xCoords, yCoords, tCoords
    xCoords = tracker.getXCoords()
    yCoords = tracker.getYCoords()
    tCoords = tracker.getTCoords()
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Data')
    worksheet.write(0, 0, 'Frame')
    worksheet.write(0, 1, 'X Axis')
    worksheet.write(0, 2, 'Y Axis')
    
    num = 1
    for t in tCoords:
        worksheet.write(num, 0, t)
        num += 1

    num = 1
    for x in xCoords:
        worksheet.write(num, 1, x)
        num += 1
       
    num = 1
    for y in yCoords:
       worksheet.write(num, 2, y)
       num += 1

    workbook.save('array.xls')  #this wasnt working
    print "workbook"
    
  
if __name__ == '__main__':
   list = list()
   root = Toplevel()
   root.wm_title("Object Tracker")

   var = IntVar()
   image_label = Label(master=root) #label for the video frame
   image_label.grid(row=0, column=0, columnspan=4)
   p = image_capture(list)
   image_label.bind('<Button-1>',on_mouse)
   
   holder = Frame(master=root)
   xPlot = Radiobutton(master=holder, text="X Axis", variable=var, value=1)
   xPlot.pack(side="top")
   
   yPlot = Radiobutton(master=holder, text="Y Axis", variable=var, value=2)
   yPlot.pack(side="top")
   
   bothPlot = Radiobutton(master=holder, text="Both Axis", variable=var, value=3)
   bothPlot.pack(side="top")
   
   displayPlot = Button(master=holder, text="Plot", command=displayChoice)
   displayPlot.pack(side="top")
   holder.grid(row=0, column=4, rowspan=4)
   
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
   fastButton = Button(master=root, text='Speed Up', command=fastForward)
   fastButton.grid(row=2, column=3)
   
   information = Label(master=root, text="Enter the size of the object (cm): ")
   information.grid(row=3, column=0, columnspan=2)
   
   input = Entry(master=root)
   input.grid(row=3, column=2)
   
   submit = Button(master=root, text='Submit', command=submitData)
   submit.grid(row=3, column=3)
   
   export = Button(master=root, text='Export', command= lambda: exportData())
   export.grid(row = 4, column = 1)
   
   end = Button(master=root, text='End', command= lambda: quit_(root))
   end.grid(row = 4, column = 3)
   
   reset = Button(master=root, text='Reset', command = reset)
   reset.grid(row = 4, column = 2)
   
   # setup the update callback
   root.after(0, func=lambda: update_all(root, image_label, list))
   
   root.lift()
   root.attributes('-topmost',True)
   root.after_idle(root.attributes,'-topmost',False)
   mainloop()


master = Tk()
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


mainloop()
