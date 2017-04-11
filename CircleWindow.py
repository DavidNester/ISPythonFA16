from Tkinter import *
import tkFileDialog
import matplotlib
import numpy as np
import cv2
from scipy.interpolate import CubicSpline
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from circleTracker import CircleTracker
from Window import MainWindow

class CircleWindow(MainWindow):

    def __init__(self,video):
        self.tracker = CircleTracker()
        super(CircleWindow, self).__init__(video)

    def reset(self):
        self.tracker = CircleTracker()
        self.root.destroy()
        super(CircleWindow,self).__init__(self.video)
    
    def update_image(self):
        self.frame = self.video[self.currentFrame]
        x = None
        y = None
        lost = False
        if self.height == 0:
           self.height = len(self.frame)
           self.width = len(self.frame[0])
       
       #if we already have the frame in memory then use circles that were found
        if self.currentFrame in self.tracker.coords.keys():
           x,y,r = self.tracker.coords[self.currentFrame]
       
        #find new circles if new frame and not paused
        elif not self.pause and self.first is not None:
            self.frame,lost,x,y = self.tracker.find(self.frame,self.currentFrame,self.pause)
            if lost:
                self.bottom.config(text='Circle is lost. Please click on the center')
                self.pauseVideo()
       
        """Plots motion in matplotlib"""
        if self.plot and self.first is not None and x is not None:
            items = enumerate(zip(self.lines,self.axes,self.backgrounds),start = 1)
            for j,(line,ax,background) in items:
                self.f.canvas.restore_region(background)
                if j == 1:
                    if self.var.get() == 1 or self.var.get() == 3:
                        line.set_ydata(x)
                        line.set_xdata(self.old)
                    if self.var.get() == 2:
                        line.set_ydata(y)
                        line.set_xdata(self.old)
                if j == 2:
                    line.set_ydata(y)
                    line.set_xdata(self.old)
                ax.draw_artist(line)
                self.f.canvas.blit(ax.bbox)
                self.backgrounds = [self.f.canvas.copy_from_bbox(ax.bbox) for ax in self.axes]
       
        im = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        a = Image.fromarray(im)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  #avoid garbage collection
        self.root.update()

    def moved(self):
        if self.w.get() not in self.tracker.coords.keys():
            self.pauseVideo()
            self.bottom.config(text='Click on the center of the circle')
        self.updateCurrentFrame()

    def makePlaybackButtons(self):
        # pause button
        self.pauseButton = Button(master=self.root, text="Pause", command=self.pauseVideo)
        self.pauseButton.grid(row=2, column=0)
            
        #play button
        self.playButton = Button(master=self.root, text="Play", command= self.playVideo)
        self.playButton.grid(row=2, column=1)
        
        #slow down
        self.slowButton = Button(master=self.root, text='Slow Down', command=self.slowDown)
        self.slowButton.grid(row=2, column=2)
        
        #fast forward
        self.fastButton = Button(master=self.root, text='Speed Up', command=self.fastForward)
        self.fastButton.grid(row=2, column=3)
        
        #export button
        self.export = Button(master=self.root, text='Export', command= self.exportData)
        self.export.grid(row = 4, column = 1)
        
        #interactive data mode button
        self.dataButton = Button(master=self.root, text='Data Mode', command=self.dataMode)
        self.dataButton.grid(row = 4, column = 0)
        
        self.update_image()
        slider_width = self.image_label.winfo_width()
        self.w = Scale(master=self.root, from_=0, to=len(self.video), orient=HORIZONTAL, length=slider_width)
        self.w.bind("<ButtonRelease-1>", lambda event: self.moved())
        self.w.grid(row=1, column=0, columnspan=4)


    def on_mouse(self,event):
        x=event.x
        y=event.y

        #only use if paused (paused when nothing is found)'
        if self.pause:
            #if second click (outside)
            if self.center is not None:
                self.outside = (x,y)
                if self.var.get() != 0:
                    self.plot = True

                x,y = self.center
                r = self.distance(self.center,self.outside)
                self.tracker.insert(x,y,r,self.currentFrame)
                cv2.circle(self.frame, (x, y), r, (228, 20, 20), 4)
                cv2.rectangle(self.frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                self.tracker.lastFrameWith = self.currentFrame
                #return to normal state
                self.playVideo()
                self.bottom.config(text='')
                if self.first is None:
                    self.first = (self.center[0],self.center[1],self.distance(self.center,self.outside),self.currentFrame)
                    self.makePlaybackButtons()
                self.center = self.outside = None
                
        
            #if first click (center)
            else:
                self.center = (x,y)
                cv2.rectangle(self.frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                self.bottom.config(text='Click on the outside of the circle')
