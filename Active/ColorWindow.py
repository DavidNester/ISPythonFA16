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

class ColorWindow(MainWindow):

    def __init__(self,video):
        self.tracker = ColorTracker()
        self.e1 = None
        self.video = video
        self.upper_threshold = 0
        self.lower_threshold = 0
        super(ColorWindow, self).__init__()
        self.root.wm_title("Circle Tracker")

    def reset(self):
        self.root.destroy()
        self.__init__(self.video)

    def submitThreshold(self,intensity,master):
        self.lower_threshold = int(intensity) - int(self.e1.get())
        if self.lower_threshold<0:
            self.lower_threshold = 0
        self.upper_threshold = int(intensity) + int(self.e1.get())
        master.destroy()
        print lower_threshold, upper_threshold

    def updateHSV(img, lower, upper, panel):
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
    
        pic = cv2.imread(img)
        mask = cv2.inRange(pic, lower, upper)
        output = cv2.bitwise_and(pic, pic, mask = mask)
    
        b = ImageTk.PhotoImage(image=np.hstack([img, output]))
        panel.configure(image=b)
        master.update()
    def moved(self):
        if self.w.get() not in self.tracker.coords.keys():
            self.pauseVideo()
            self.bottom.config(text='Click on the center of the circle')
        self.updateCurrentFrame()
    
    def on_mouse(self,event):
        x=event.x
        y=event.y
        
        """pixel = frame[y, x]
            print pixel
            """
        #only use if paused (paused when nothing is found)'
        if pause:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            intensity = gray[y, x]

            cv2.imwrite('hsv.jpg', frame)
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

            lower_h.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel))
            lower_s.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel))
            lower_v.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel))
            upper_h.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel))
            upper_s.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel))
            upper_v.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel))

            lower_h.grid(row=2, column=1)
            lower_s.grid(row=3, column=1)
            lower_v.grid(row=4, column=1)
            upper_h.grid(row=5, column=1)
            upper_s.grid(row=6, column=1)
            upper_v.grid(row=7, column=1)
            Button(master, text='Submit', command=lambda: submitThreshold(intensity, master)).grid(row=8, column=1, sticky=W, pady=4)
            mainloop( )


