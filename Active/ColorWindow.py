from Tkinter import *
import tkFileDialog
import matplotlib
import numpy as np
#from scipy.interpolate import CubicSpline
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from colorTracker import ColorTracker
from Window import MainWindow
import cv2

class ColorWindow(MainWindow):

    def __init__(self,video):
        self.tracker = ColorTracker()
        self.e1 = None
        self.video = video
        self.upper_threshold = 0
        self.lower_threshold = 0
        self.start = False
        super(ColorWindow, self).__init__()
        self.root.wm_title("Circle Tracker")

    def update_image(self):
        self.frame = self.video[self.currentFrame]
        x = None
        y = None
        r = None
        lost = False
        fr = None
        if self.height == 0:
           self.height = len(self.frame)
           self.width = len(self.frame[0])
       
        #if we already have the frame in memory then use circles that were found
        if self.currentFrame in self.tracker.coords.keys():
           x,y,r = self.tracker.coords[self.currentFrame]
       
        #find new circles if new frame and not paused
        elif not self.pause and self.first is not None:
            fr,lost,x,y = self.tracker.findColor(self.lower_threshold,self.upper_threshold,self.frame,self.currentFrame)
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

        if fr == None:
            fr = self.frame.copy()
        im = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        a = Image.fromarray(im)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  #avoid garbage collection
        self.root.update()


    def reset(self):
        self.root.destroy()
        self.__init__(self.video)

    def submitThreshold(self,lower, upper, master):
        self.tracker.findColor(lower, upper, self.frame,self.currentFrame)
        master.destroy()
        self.bottom.config(text='')
        self.playVideo()

    def updateHSV(self,img, lower, upper, panel, master):
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        
        pic = cv2.imread(img)
        mask = cv2.inRange(pic, lower, upper)
        output = cv2.bitwise_and(pic, pic, mask = mask)
        
        cv2.imwrite('output.jpg', output)
        
        final = ImageTk.PhotoImage(Image.open("output.jpg"))
        panel.configure(image=final)
        panel.image = final
        if self.start == False:
            mainloop()
            start = True
        else:
            master.update()

    def moved(self):
        if self.w.get() not in self.tracker.coords.keys():
            self.pauseVideo()
            self.bottom.config(text='Click on the center of the circle')
        self.updateCurrentFrame()
    
    def on_mouse(self,event):
        x=event.x
        y=event.y
        
        #only use if paused (paused when nothing is found)'
        if self.pause:
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            hsv1 = hsv[y,x]
            cv2.imwrite('hsv.jpg', self.frame)
            master = Toplevel()
            img = ImageTk.PhotoImage(Image.open("hsv.jpg"))

            panel = Label(master, image = img)
            panel.grid(row=0, column=0, columnspan=2)

            Label(master, text="What threshold would you like? ").grid(row=1, columnspan=2)
            Label(master, text="Lower H: ").grid(row=2, column=0)
            Label(master, text="Lower S: ").grid(row=3, column=0)
            Label(master, text="Lower V: ").grid(row=4, column=0)
            Label(master, text="Upper H: ").grid(row=5, column=0)
            Label(master, text="Upper S: ").grid(row=6, column=0)
            Label(master, text="Upper V: ").grid(row=7, column=0)

            lower_h = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            lower_s = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            lower_v = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            upper_h = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            upper_s = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            upper_v = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)

            lower_h.bind("<ButtonRelease-1>", lambda event: self.updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel,master))
            lower_s.bind("<ButtonRelease-1>", lambda event: self.updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel,master))
            lower_v.bind("<ButtonRelease-1>", lambda event: self.updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel,master))
            upper_h.bind("<ButtonRelease-1>", lambda event: self.updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel,master))
            upper_s.bind("<ButtonRelease-1>", lambda event: self.updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel,master))
            upper_v.bind("<ButtonRelease-1>", lambda event: self.updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel,master))

            lower_h.set(hsv1[0]-40)
            lower_s.set(hsv1[1]-100)
            lower_v.set(hsv1[2]-40)
            upper_h.set(hsv1[0]+80)
            upper_s.set(hsv1[1]+80)
            upper_v.set(hsv1[2]+80)

            lower_h.grid(row=2, column=1)
            lower_s.grid(row=3, column=1)
            lower_v.grid(row=4, column=1)
            upper_h.grid(row=5, column=1)
            upper_s.grid(row=6, column=1)
            upper_v.grid(row=7, column=1)
            Button(master, text='Submit', command=lambda: self.submitThreshold([lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], master)).grid(row=8, column=1, sticky=W, pady=4)
            mainloop( )


