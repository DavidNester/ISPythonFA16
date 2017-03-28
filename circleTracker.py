import cv2
import numpy as np
from Tracker import Tracker

class CircleTracker(Tracker):

    def find(self,frame,currentFrame, pause):
        lost = False
        x = None
        y = None
        if currentFrame-self.lastFrameWith > 10:
          lost = True
          return frame, lost, x,y
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
                    if self.normal(x,y,r):
                        found = True
                        self.insert(x,y,r,currentFrame)
                        cv2.circle(frame, (x, y), r+5, (228, 20, 20), 4) #draw circle on image
                        cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1) #draw rectangle on center
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
        return frame, lost, x,y

    def processImage(self,frame):
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #switch to grayscale
        retval, image = cv2.threshold(original, 50, 255, cv2.cv.CV_THRESH_BINARY)
        el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        image = cv2.dilate(image, el, iterations=4)
        image = cv2.GaussianBlur(image, (13, 13), 0)
        return image
