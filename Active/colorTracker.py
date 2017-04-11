import cv2
import numpy as np
from Tracker import Tracker
import PIL

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
            updateHSV('hsv.jpg', [lower_h.get(), lower_s.get(), lower_v.get()], [upper_h.get(), upper_s.get(), upper_v.get()], panel, master)
