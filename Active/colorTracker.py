import cv2
import numpy as np
from Tracker import Tracker
import PIL

class ColorTracker(Tracker):

    """Finds the circle usign the color based methods - Returns frame,lost,x,y"""
    def find(self,lower, upper, frame, currentFrame):
        lost = False
        
        #Convert Frame to HSV image
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        #changes the lower and upper passed in array to the 'np' array with type 'unit8'
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
     
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                self.insert(int(x),int(y),int(radius),currentFrame)
                cv2.circle(frame, (int(x), int(y)), int(radius), (228, 20, 20), 2)
                cv2.rectangle(frame, (int(x) - 5, int(y) - 5), (int(x) + 5, int(y) + 5), (0, 0, 255), -1)
                self.lastFrameWith = currentFrame
            
            return frame,lost,x,y
            
            # Bitwise-AND mask and original image
            #res = cv2.bitwise_and(frame,frame, mask= mask)
        return frame,lost,0,0
