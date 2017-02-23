import cv2
import numpy as np
from Tracker import Tracker

class OtherTracker(Tracker):
    """
    Inherits from generic tracking object that can be found in Tracker.py
    Has instance variables:
    self.lastFrameWith,self.coords, self.xCoords, self.yCoords,self.rCoords, self.tCoords
    Has functions for getting x,y,r,t coords.
    Has function for normalizing new found objects.
    May need to change a few things if there is no radius data (or something comparable to radius)

    """

    def find(self,frame,currentFrame, pause):
        #Insert new tracking function here
        pass

    def processImage(self,frame):
        pass
