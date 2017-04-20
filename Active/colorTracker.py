import cv2
import numpy as np
from Tracker import Tracker
import PIL

class ColorTracker(Tracker):

    
    def findColor(self,lower, upper, frame, currentFrame):
        lost = False
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
            
            # Bitwise-AND mask and original image
            #res = cv2.bitwise_and(frame,frame, mask= mask)
        
        return frame,lost,x,y
    
    def on_mouse(self):
        if pause:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            print hsv[y,x]
            hsv1 = hsv[y,x]
            print hsv1[1]
            
            cv2.imwrite('hsv.jpg', frame)
            master = Toplevel()
            img = ImageTk.PhotoImage(Image.open("hsv.jpg"))
            
            panel = Label(master, image = img)
            panel.grid(row=0, column=0, columnspan=2)
            
            Label(master, text="What threshold would you like? ").grid(row=1, columnspan=2)
            Label(master, text="Lower H: ").grid(row=2, column=0)
            Label(master, text="Lower S: ").grid(row=3, column=0)
            Label(master, text="Lower V: ").grid(row=4, column=0)
            Label(master, text="Upper H: ").grid(row=5, column=0)
            Label(master, text="Upper S: ").grid(row=6, column=0)
            Label(master, text="Upper V: ").grid(row=7, column=0)
            
            lower_h = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            lower_s = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            lower_v = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            upper_h = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            upper_s = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            upper_v = Scale(master, from_=0, to=255, orient=HORIZONTAL, length=255)
            
            lower_h.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master))
            lower_s.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master))
            lower_v.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master))
            upper_h.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master))
            upper_s.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master))
            upper_v.bind("<ButtonRelease-1>", lambda event: updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master))
            
            lower_h.set(hsv1[0]-40)
            lower_s.set(hsv1[1]-60)
            lower_v.set(hsv1[2]-40)
            upper_h.set(hsv1[0]+40)
            upper_s.set(hsv1[1]+60)
            upper_v.set(hsv1[2]+40)
            
            lower_h.grid(row=2, column=1)
            lower_s.grid(row=3, column=1)
            lower_v.grid(row=4, column=1)
            upper_h.grid(row=5, column=1)
            upper_s.grid(row=6, column=1)
            upper_v.grid(row=7, column=1)
            Button(master, text='Submit', command=lambda: submitThreshold(intensity, master)).grid(row=8, column=1, sticky=W, pady=4)
            updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], master)
    
    def submitThreshold(lower, upper, master):
        findColor(lower, upper, frame)
        master.destroy()