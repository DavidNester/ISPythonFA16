import time
import numpy as np
import cv2
from PyQt4 import QtCore
from PyQt4 import QtGui
from Tkinter import *
import tkFileDialog
import os
import cv2.cv as cv

from colorTracker import ColorTracker
from Window import MainWindow
from CircleWindow import CircleWindow
from ColorWindow import ColorWindow

"""Class for controlling the initial window - opens the proper window afterwards"""
class OpenWindow(object):

    """Initialize with label, options, and submit button"""
    def __init__(self):
        self.openWin = Tk()
        self.openWin.withdraw() #use to hide tkinter window
        self.video = list()
        self.openWin = Toplevel()
        self.openWin.wm_title("Object Tracker")

        self.title = Label(master=self.openWin, text="Welcome to the Object Tracker!")
        self.title.config(font=("Courier", 30))
        self.title.grid(row=0, column=0, padx=100, pady=50)

        self.type = IntVar()
        self.holder = Frame(master=self.openWin)

        self.circleButton = Radiobutton(master=self.holder, text="Circle Track", variable=self.type, value=0)
        self.circleButton.grid(row=0, column=0)

        self.colorButton = Radiobutton(master=self.holder, text="Color Track", variable=self.type, value=1)
        self.colorButton.grid(row=0, column=1, padx = 150)

        self.bothButton = Radiobutton(master=self.holder, text="Both", variable=self.type, value=2)
        self.bothButton.grid(row=0, column=2)

        self.openVideo = Button(master=self.holder, text="Open Video...", command=self.open)
        self.openVideo.grid(row=1, column=1, pady=25)

        self.holder.grid(row=1, column=0)

        self.openWin.lift()
        self.openWin.attributes('-topmost',True)
        self.openWin.after_idle(self.openWin.attributes,'-topmost',False)

    """When 'open' button is clicked - opens a directory window to choose video"""
    def open(self):
        selection = self.type.get()
        """INPUT FILE"""
        currdir = os.getcwd() #sets current directory
        self.tempdir = tkFileDialog.askopenfilename( filetypes = (("Movie files", "*.MOV"), ("HTML files", "*.html;*.htm"),("All files", "*.*"))) #requests file name and type of files
        if self.tempdir:
            self.image_capture() #create video array
            self.tempdir = None
            if selection == 0:
                main = CircleWindow(self.video)
            if selection == 1:
                main = ColorWindow(self.video)
            if selection == 2:
                main1 = CircleWindow(self.video)
                main2 = ColorWindow(self.video)
        else:
            print 'no file selected' #need to make a real error statement
    


    """takes the video and converts it into an array"""
    def image_capture(self):
        vidFile = cv2.VideoCapture(self.tempdir)
        """Processing Window"""
        """***********************"""
        process = Tk()
        process.withdraw() #use to hide tkinter window
        process.grid_propagate(False)
        process = Toplevel()
        process.minsize(width=180, height=100)
        title = Label(master = process, text = 'Processing')
        dots = Label(master = process, text = '')
        title.config(font=("Courier", 30))
        dots.config(font=("Courier", 30))
        title.grid(row=0, column=0)
        dots.grid(row=1,column=0)
        process.after(0)
        counter1 = 0
        counter2 = 0
        """***********************"""
        while True:
            """Processing Window"""
            """***********************"""
            if counter1 > 10:
                counter1 = -1
                dots.config(text='.'*counter2)
                if counter2 > 4:
                    counter2 = -1
                counter2 += 1
            counter1 += 1
            process.update()
            """***********************"""
            try:
                flag, frame=vidFile.read()
                if flag==0:
                    break
                self.video.append(frame)
            except:
                continue
        process.destroy()
