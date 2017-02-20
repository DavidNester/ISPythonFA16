import cv2
import matplotlib
import numpy as np

class CircleTracker:

    def __init__(self):
        #instance variables
        self.lastFrameWithCircle = 0
        self.circleCoords = {}
    
    def normal(self,x,y,r):
        #accept data if we hae no prior knowledge
        if self.lastFrameWithCircle == 0:
            return True
        oldX,oldY,oldR = self.circleCoords[self.lastFrameWithCircle]
        #make sure that the new circle agrees with the old circle
        if abs(oldX-x) < oldR/2 and abs(oldY-y) < oldR/2 and abs(r-oldR) < oldR/2:
           return True
        return False
    
    def findCircles(self,frame,currentFrame, pause):
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
                        self.circleCoords[currentFrame] = (x,y,r)
                        # draw the circle in the output image, then draw a rectangle
                        # corresponding to the center of the circle
                        cv2.circle(frame, (x, y), r+5, (228, 20, 20), 4)
                        cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                        self.lastFrameWithCircle = currentFrame
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
        if currentFrame-self.lastFrameWithCircle > 10:
                self.pause = True
        return frame, pause

    def processImage(self,frame):
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #switch to grayscale
        retval, image = cv2.threshold(original, 50, 255, cv2.cv.CV_THRESH_BINARY)
        el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        image = cv2.dilate(image, el, iterations=4)
        image = cv2.GaussianBlur(image, (13, 13), 0)
        return image
    
    
    """For The End"""
    def plot(self):
        #need to add xcoords, tcoords, etc.
        plt.figure(1)
        plt.subplot(211)
        plt.plot(tCoords,xCoords,'ro')
        plt.xlabel('Frame')
        plt.ylabel('x-pixel')
        plt.subplot(212)
        plt.plot(tCoords,yCoords,'ro')
        plt.xlabel('Frame')
        plt.ylabel('y-pixel')
        """attempt at data smoothing"""
        """plt.figure(2)
        plt.subplot(211)
        plt.plot(tCoords,rCoords,'r--')"""
        """f = interp1d(tCoords,xCoords, kind = 'cubic')
        plt.subplot(212)
        xnew = np.linspace(0,max(tCoords),num = 2*len(tCoords),endpoint = True)
        plt.plot(xnew,f(xCoords),'--')"""
        plt.show()
