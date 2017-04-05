import cv2
import numpy as np
from Tracker import Tracker

class ColorTracker(Tracker):
    
    def findColor(self,frame, threshold):
        lost = False
        
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #switch to grayscale
        retval, image = cv2.threshold(original, threshold, 255, cv2.cv.CV_THRESH_BINARY)
        cv2.imshow('color', image)
        contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, contours, -1, (0,255,0), 3)
        
        
        # Bitwise-AND mask and original image
        #res = cv2.bitwise_and(frame,frame, mask= mask)
        
        return frame, lost