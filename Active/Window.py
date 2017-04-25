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
import xlwt
import cv2

from InteractiveDataWindow import InteractiveDataWindow

"""Parent Class for the main window GUI
    Has all methods that are not specific to child classes (currently circle and color)
"""
class MainWindow(object):

    """Constructor Method - creates window and initializes variables for playback"""
    def __init__(self):
        self.root = Tk()#create window
        self.root.withdraw()
        self.root = Toplevel()
        
        self.image_label = Label(master=self.root) #label for the video frame
        self.image_label.grid(row=0, column=0, columnspan=4)
   
        self.init_buttons() #create initial buttons to get info

        self.root.after(0, func=self.update_all)# setup the update callback
    
        #playback variables
        self.size = 0
        self.speed = 0
        self.currentFrame = 1
        self.old = 0
        self.pause = True
        self.tCoords = []
        self.xCoords = []
        self.yCoords = []
        self.rCoords = []
        self.w = None
        self.height = 0
        self.width = 0
        self.fps = 0
        self.center = None
        self.outside = None
        self.first = None
        self.frame = None
        self.plot = False
    
        self.update_image()

    """Labels and inpute boxes for size and fps - info used for converting frames to seconds and pixels to centimeters"""
    def init_buttons(self):
        self.information = Label(master=self.root, text="Enter the Radius of the object (cm): ")
        self.information.grid(row=3, column=0, columnspan=2)
        
        self.input = Entry(master=self.root)
        self.input.grid(row=3, column=2)
        
        self.fpsInfo = Label(master=self.root, text="Enter the Frames Per Second of the video: ")
        self.fpsInfo.grid(row=4, column=0, columnspan=2)
        
        self.fpsinput = Entry(master=self.root)
        self.fpsinput.grid(row=4, column=2)
        
        self.submit = Button(master=self.root, text='Submit', command=self.submitData)
        self.submit.grid(row=4, column=3)
        
        self.end = Button(master=self.root, text='End', bg = 'red', command= self.quit_)
        self.end.grid(row = 5, column = 3)
        
        self.reset = Button(master=self.root, text='Reset', bg = 'red', command = self.reset)
        self.reset.grid(row = 5, column = 2)
    
    """method to receive fps and size data and initialize plot option input"""
    def submitData(self):
        try:
            self.tracker.setSize(float(self.input.get())) #save data
            self.tracker.setFPS(float(self.fpsinput.get()))
            self.information.destroy()#destroy buttons
            self.input.destroy()
            self.fpsinput.destroy()
            self.fpsInfo.destroy()
            self.submit.destroy()

            self.holder = Frame(master=self.root)
            self.var = IntVar()
            
            self.noPlot = Radiobutton(master=self.holder, text="No Live Plots", variable=self.var, value=0)
            self.noPlot.pack(side="left")
            
            self.xPlot = Radiobutton(master=self.holder, text="X Axis", variable=self.var, value=1)
            self.xPlot.pack(side="left")
            
            self.yPlot = Radiobutton(master=self.holder, text="Y Axis", variable=self.var, value=2)
            self.yPlot.pack(side="left")
            
            self.bothPlot = Radiobutton(master=self.holder, text="Both Axis", variable=self.var, value=3)
            self.bothPlot.pack(side="left")
            
            self.displayPlot = Button(master=self.holder, text="Submit", command=self.displayChoice)
            self.displayPlot.pack(side="bottom", fill = "x")
            self.holder.grid(row=3, column=1, columnspan=4)
        except:
            master = Tk()
            master.withdraw()
            master = Toplevel()
            error = Label(master = master, text = 'Please enter numbers in both boxes')
            error.grid(row=0, column=0)
            error.after(0)


    """creates buttons that allo playback control of the video as well as data viewing options"""
    def makePlaybackButtons(self):
        # pause button
        self.pauseButton = Button(master=self.root, text='Pause', command=self.pauseVideo)
        self.pauseButton.grid(row=2, column=0)
        
        #play button
        self.playButton = Button(master=self.root, text='Play', command= self.playVideo)
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

    """Displays results of plot choice"""
    def displayChoice(self):
        self.holder.destroy() #destroy plotting buttons
        
        #enable clicking on the video
        self.image_label.bind('<Button-1>',self.on_mouse)
        
        if self.var.get() != 0: #if not "no plots"
            self.axes = []
            self.f = Figure(figsize=(5,5), dpi=100)
            if self.var.get()==1: #x
                axis = self.f.add_subplot(111)
                axis.set_xlim([0,len(self.video)])
                axis.set_ylim([0,self.width])
                self.axes +=[axis]
                self.lines = [self.axes[0].plot(self.tCoords,self.xCoords,'ro',animated=True)[0]]
            elif self.var.get() == 2: #y
                axis = self.f.add_subplot(111)
                axis.set_xlim([0,len(self.video)])
                axis.set_ylim([0,self.height])
                self.axes +=[axis]
                self.lines = [self.axes[0].plot(self.tCoords,self.yCoords,'ro',animated=True)[0]]
            elif self.var.get() == 3: #both
                self.f = Figure(figsize=(10,5), dpi=100)
                axis = self.f.add_subplot(121)
                axis.set_xlim([0,len(self.video)])
                axis.set_ylim([0,self.width])
                self.axes +=[axis]
                axis = self.f.add_subplot(122)
                axis.set_xlim([0,len(self.video)])
                axis.set_ylim([0,self.height])
                self.axes += [axis]
                self.lines = [self.axes[0].plot(self.tCoords,self.xCoords,'ro',animated=True)[0],self.axes[1].plot(self.tCoords,self.yCoords,'ro',animated=True)[0]]
            self.canvas = FigureCanvasTkAgg(self.f, master=self.root)
            self.canvas.show()
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=4, rowspan=4)

            self.backgrounds = [self.f.canvas.copy_from_bbox(ax.bbox) for ax in self.axes]
        
        self.bottom = Label(master=self.root, text="Click on the center of the circle. Move the trackbar if the object is not on the frame yet")
        self.bottom.grid(row=3, column=0, columnspan=4)
        self.create_slider()
        
    def create_slider(self):
        slider_width = self.image_label.winfo_width()
        self.w = Scale(master=self.root, from_=0, to=len(self.video), orient=HORIZONTAL, length=slider_width)
        self.w.bind("<ButtonRelease-1>", lambda event: self.moved())
        self.w.grid(row=1, column=0, columnspan=4)

    def updateCurrentFrame(self):
        self.currentFrame = self.w.get()
        self.update_image()

    def update_all(self):
        self.old = self.currentFrame
        if self.speed < 0:
            time.sleep((self.speed*.1)*-1)#may need to find better way for this
        elif self.speed > 0:
            self.currentFrame = self.currentFrame + (1*self.speed)
        if self.pause == False and self.currentFrame < len(self.video):
            self.currentFrame += 1
            self.w.set(self.currentFrame)
            self.update_image()
            self.root.after(0, func= self.update_all)

    """export data to spreadsheet"""
    def exportData(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Data')
        worksheet.write(0, 0, 'Frame')
        worksheet.write(0, 1, 'X Axis')
        worksheet.write(0, 2, 'Y Axis')
        worksheet.write(0, 3, 'Radius')
        
        worksheet.write(0, 5, 'Size of Object: ' + str(self.size) + "cm")
        
        count = 1
        for t,x,y,r in zip(self.tracker.getTCoords(),self.tracker.getXCoords(),self.tracker.getYCoords(),self.tracker.getRCoords()):
            worksheet.write(count, 0, t)
            worksheet.write(count, 1, x)
            worksheet.write(count, 2, y)
            worksheet.write(count, 3, r)
            count += 1

        
        #centimeters / pixel
        #conversions taken care of somewhere else. I (David) will take care of this. Still need to add conversions to the sheet
        centConversion = (self.size*1.0)/(self.tracker.getRadius()*1.0)
        
        xdistance_cm = (self.tracker.xMax() - self.tracker.xMin()) * centConversion
        ydistance_cm = (self.tracker.yMax() - self.tracker.yMin()) * centConversion
        
        xdistance_in = xdistance_cm/2.54#could be more exact in the future
        xdistance_in = xdistance_cm/2.54#could be more exact in the future
        
        file_name = tkFileDialog.asksaveasfile(mode='a', defaultextension=".xls")
        workbook.save(file_name.name)

    def playVideo(self):
        self.pause = False
        self.update_all()

    def pauseVideo(self):
        self.pause = True

    def slowDown(self):
        self.speed -= 1

    def fastForward(self):
        self.speed += 1

    def quit_(self):
        self.root.destroy()
    
    def dataMode(self):
        dataMode = InteractiveDataWindow(self.tracker)

    """distance between two coordinates"""
    def distance(self,p1,p2):
        dx = (p1[0]-p2[0])*1.0
        dy = (p1[1]-p2[1])*1.0
        return int((dx**2 + dy**2)**.5)

    """main method that updates the GUI (image plots)"""
    def update_image(self):
        print 'Must be implemented by child'
        pass
    """Responds to mouse input (initial location of the circle"""
    def on_mouse(self):
        print 'Must be implemented by child'
        pass
    """How to respond to the movement of the slider"""
    def moved(self):
        print 'Must be implemented by child'
        pass
