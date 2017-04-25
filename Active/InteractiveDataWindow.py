from Tkinter import *
import tkFileDialog
import matplotlib
import numpy as np
#from scipy.interpolate import CubicSpline
from scipy.interpolate import UnivariateSpline
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from circleTracker import CircleTracker

"""Window for displaying the different graphs"""
class InteractiveDataWindow:

    """Constructor - needs to be provided with a tracker"""
    def __init__(self,tracker):
        self.tracker = tracker
        self.data = Tk()
        self.data.withdraw()
        self.data = Toplevel()
        self.makeButtons()

    """make a button for each graph option"""
    def makeButtons(self):
        self.xButton = Button(master=self.data,text='x', command = lambda: self.plotData(self.tracker.getTCoords(),self.tracker.getXCoords(),1))
        self.xButton.grid(row=0,column=0,columnspan=2)
        
        self.yButton = Button(master=self.data,text='y', command = lambda: self.plotData(self.tracker.getTCoords(),self.tracker.getYCoords(),2))
        self.yButton.grid(row=1,column=0,columnspan=2)
        
        self.rButton = Button(master=self.data,text='r', command = lambda: self.plotData(self.tracker.getTCoords(),self.tracker.getRCoords(),3))
        self.rButton.grid(row=2,column=0,columnspan=2)
        
        self.xVelButton = Button(master=self.data,text='x Velocity', command = self.xVelData)
        self.xVelButton.grid(row=3,column=0,columnspan=2)
        
        self.yVelButton = Button(master=self.data,text='y Velocity', command = self.yVelData)
        self.yVelButton.grid(row=4,column=0,columnspan=2)
        
        self.xAccButton = Button(master=self.data,text='x Acceleration', command = self.xAccData)
        self.xAccButton.grid(row=5,column=0,columnspan=2)
        
        self.yAccButton = Button(master=self.data,text='y Acceleration', command = self.yAccData)
        self.yAccButton.grid(row=6,column=0,columnspan=2)
    
        self.fitXButton = Button(master=self.data,text='Fit X', command = self.fitX)
        self.fitXButton.grid(row=0,column=2,columnspan=2)
    
        self.fitYButton = Button(master=self.data,text='Fit Y', command = self.fitY)
        self.fitYButton.grid(row=1,column=2,columnspan=2)
    
        self.fitXVelButton = Button(master=self.data,text='Fit X Velocity', command = self.fitXVelocity)
        self.fitXVelButton.grid(row=2,column=2,columnspan=2)
        
        self.fitYVelButton = Button(master=self.data,text='Fit Y Velocity', command = self.fitYVelocity)
        self.fitYVelButton.grid(row=3,column=2,columnspan=2)
    
        self.scaleXButton = Button(master=self.data,text='Scale X', command = self.scaleX)
        self.scaleXButton.grid(row=0,column=4,columnspan=2)
        
        self.scaleYButton = Button(master=self.data,text='Scale Y', command = self.scaleY)
        self.scaleYButton.grid(row=1,column=4,columnspan=2)
        
        self.scaleXVelButton = Button(master=self.data,text='Scale X Velocity', command = self.scaleXVelocity)
        self.scaleXVelButton.grid(row=2,column=4,columnspan=2)
        
        self.scaleYVelButton = Button(master=self.data,text='Scale Y Velocity', command = self.scaleYVelocity)
        self.scaleYVelButton.grid(row=3,column=4,columnspan=2)

    """Plots data given a list of coordinates"""
    def plotData(self,x,y,num):
        plt.figure(num)
        plt.plot(x,y,'ro')
        plt.show()
    
    """Gets data to send to plotting function - probably some refactoring that could be done - one for each button"""
    """**********************************************************************"""

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

    def fitX(self):
        self.trendline(self.tracker.getTCoords(),self.tracker.getXCoords(),8)

    def fitY(self):
        self.trendline(self.tracker.getTCoords(),self.tracker.getYCoords(),9)

    def fitXVelocity(self):
        x,y = self.tracker.xVelocity()
        self.trendline(x,y,10)

    def fitYVelocity(self):
        x,y = self.tracker.yVelocity()
        self.trendline(x,y,11)

    def trendline(self,x,y,num):
        plt.figure(num)
        cs = UnivariateSpline(x,y)
        plt.plot(x, cs(x), label="S")
        #plt.plot(x, cs(x, 2), label="S''")
        #plt.plot(x, cs(x, 3), label="S'''")
        plt.show()

    def scaleX(self):
        self.plotData(self.tracker.scaleT(),self.tracker.scaleX(),12)

    def scaleY(self):
        self.plotData(self.tracker.scaleT(),self.tracker.scaleY(),13)

    def scaleXVelocity(self):
        x,y = self.tracker.scaleXVelocity()
        self.plotData(x,y,14)

    def scaleYVelocity(self):
        x,y = self.tracker.scaleYVelocity()
        self.plotData(x,y,15)
    """**********************************************************************"""

