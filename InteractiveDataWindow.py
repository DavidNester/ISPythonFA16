from Tkinter import *
import tkFileDialog
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from circleTracker import CircleTracker

class InteractiveDataWindow:

    def __init__(self,tracker):
        self.tracker = tracker
        self.data = Tk()
        self.data.withdraw()
        self.data = Toplevel()
        self.makeButtons()

    def makeButtons(self):
        self.xButton = Button(master=self.data,text='x', command = self.xData )
        self.xButton.grid(row=0,column=0,columnspan=2)
        
        self.yButton = Button(master=self.data,text='y', command = self.yData )
        self.yButton.grid(row=1,column=0,columnspan=2)
        
        self.rButton = Button(master=self.data,text='r', command = self.rData )
        self.rButton.grid(row=2,column=0,columnspan=2)
        
        self.xVelButton = Button(master=self.data,text='x Velocity', command = self.xVelData)
        self.xVelButton.grid(row=3,column=0,columnspan=2)
        
        self.yVelButton = Button(master=self.data,text='y Velocity', command = self.yVelData)
        self.yVelButton.grid(row=4,column=0,columnspan=2)
        
        self.xAccButton = Button(master=self.data,text='x Acceleration', command = self.xAccData)
        self.xAccButton.grid(row=5,column=0,columnspan=2)
        
        self.yAccButton = Button(master=self.data,text='y Acceleration', command = self.yAccData)
        self.yAccButton.grid(row=6,column=0,columnspan=2)
    

    def plotData(self,x,y,num):
        plt.figure(num)
        plt.plot(x,y,'ro')
        plt.show()

    def xData(self):
        self.plotData(self.tracker.getTCoords(),self.tracker.getXCoords(),1)
    def yData(self):
        self.plotData(self.tracker.getTCoords(),self.tracker.getYCoords(),2)
    def rData(self):
        self.plotData(self.tracker.getTCoords(),self.tracker.getRCoords(),3)
    def xVelData(self):
        x,y = self.tracker.xVelocity()
        self.plotData(x,y,4)
    def yVelData(self):
        x,y = self.tracker.yVelocity()
        self.plotData(x,y,5)
    def xAccData(self):
        x,y = self.tracker.xAcceleration()
        self.plotData(x,y,6)
    def yAccData(self):
        x,y = self.tracker.yAcceleration()
        self.plotData(x,y,7)
