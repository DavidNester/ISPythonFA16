from Tkinter import *
import tkFileDialog
import matplotlib
import numpy as np
import cv2
#from scipy.interpolate import CubicSpline
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from circleTracker import CircleTracker
from Window import MainWindow


"""Inherits from window - runs GUI for any window using circle tracking"""
class CircleWindow(MainWindow):

    """constructor - requires a video"""
    def __init__(self,video):
        self.tracker = CircleTracker()
        self.video = video
        super(CircleWindow, self).__init__() #Call parent constructor
        self.root.wm_title("Circle Tracker")

    """destroy window and then call constructor"""
    def reset(self):
        self.root.destroy()
        self.__init__(self.video)

    """updates the video, draws the circle, updates the plot"""
    def update_image(self):
        self.frame = self.video[self.currentFrame]
        x = None
        y = None
        r = None
        lost = False #if the tracker has lost the circle
        if self.height == 0:
           self.height = len(self.frame)
           self.width = len(self.frame[0])
       
        #if we already have the frame in memory then use circles that were found
        if self.currentFrame in self.tracker.coords.keys():
           x,y,r = self.tracker.coords[self.currentFrame]
       
        #find new circles if new frame and not paused
        elif not self.pause and self.first is not None:
            lost,x,y,r = self.tracker.find(self.frame,self.currentFrame,self.pause)
            if lost:
                self.bottom.config(text='Circle is lost. Please click on the center')
                self.pauseVideo()
       
        """Plots motion in matplotlib"""
        if self.plot and self.first is not None and x is not None:
            items = enumerate(zip(self.lines,self.axes,self.backgrounds),start = 1)
            for j,(line,ax,background) in items:
                self.f.canvas.restore_region(background) #puts picture of old graph as new graph and only graphs one point
                if j == 1:
                    if self.var.get() == 1 or self.var.get() == 3: #x graph
                        line.set_ydata(x)
                        line.set_xdata(self.old)
                    if self.var.get() == 2: #y graph
                        line.set_ydata(y)
                        line.set_xdata(self.old)
                if j == 2: #y graph
                    line.set_ydata(y)
                    line.set_xdata(self.old)
                ax.draw_artist(line)
                self.f.canvas.blit(ax.bbox)
                self.backgrounds = [self.f.canvas.copy_from_bbox(ax.bbox) for ax in self.axes] #save background
        fr = self.frame.copy()
        if x:
            cv2.circle(fr, (x, y), r, (228, 20, 20), 4)
            cv2.rectangle(fr, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        im = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        a = Image.fromarray(im)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  #avoid garbage collection
        self.root.update()

    """called when the slide bar is moved"""
    def moved(self):
        if self.w.get() not in self.tracker.coords.keys(): #if it is an unseen frame
            self.pauseVideo()
            self.bottom.config(text='Click on the center of the circle')
        self.updateCurrentFrame()

    """called when the mouse is clicked on the video - used to input center and outside of the circle"""
    def on_mouse(self,event):
        x=event.x
        y=event.y
        #only use if paused (paused when nothing is found)'
        if self.pause:
            if self.center is not None: #if second click (outside)
                self.outside = (x,y)
                if self.var.get() != 0:
                    self.plot = True
                self.tracker.insert(self.center[0],self.center[1],self.distance(self.center,self.outside),self.currentFrame)
                self.tracker.lastFrameWith = self.currentFrame
                self.bottom.config(text='')#return to normal state
                if self.first is None:
                    self.first = (self.center[0],self.center[1],self.distance(self.center,self.outside),self.currentFrame)
                    self.makePlaybackButtons()
                self.center = self.outside = None
                self.playVideo()
            else:#if first click (center)
                self.center = (x,y)
                self.bottom.config(text='Click on the outside of the circle') #need second click for outside
