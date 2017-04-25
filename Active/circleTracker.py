import cv2
import numpy as np
from Tracker import Tracker

"""Tracker for circles - Inherits from Tracker"""
class CircleTracker(Tracker):
    
    """Method for finding the circle - returns lost,x,y,r"""
    def find(self,frame,currentFrame, pause):
        lost = False
        x = None
        y = None
        r = None
        #return lost if it has been 10 frames since the last circle
        if currentFrame-self.lastFrameWith > 10:
          lost = True
          return lost,x,y,r
        image = self.processImage(frame)
        found = False
        alpha = 90
        while not found:
            circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT, 1.2, 100, param2 = alpha) #find circles 
            if circles is not None:
                # convert the (x, y) coordinates and radius of the circles to integers
                circles = np.round(circles[0, :]).astype("int")
                #check if the circles agree with previous data
                for x,y,r in circles:
                    r += 10 #because of dilate
                    if self.normal(x,y,r):
                        found = True
                        self.insert(x,y,r,currentFrame)
                        self.lastFrameWith = currentFrame
                if not found:
                    alpha -= 5
                    if alpha <= 30:
                        found = True
            else:
                #if no circles found then try again with new threshold (threshold stops at 30)
                alpha -= 5
                if alpha <= 30:
                    found = True
        #if we havent found a circle in more than 10 frames then ask the user for help
        if abs(currentFrame-self.lastFrameWith) > 10:
                lost = True
        return lost,x,y,r
    """converts image to simple black and white"""
    def processImage(self,frame):
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #switch to grayscale
        retval, image = cv2.threshold(original, 50, 255, cv2.cv.CV_THRESH_BINARY)
        el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        image = cv2.dilate(image, el, iterations=4)
        image = cv2.GaussianBlur(image, (13, 13), 0)
        return image
