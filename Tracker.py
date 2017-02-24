

class Tracker:

    def __init__(self):
        #instance variables
        self.lastFrameWith = 0
        self.coords = {}
        self.xCoords = []
        self.yCoords = []
        self.rCoords = []
        self.tCoords = []
    
    def normal(self,x,y,r):
        #accept data if we hae no prior knowledge
        if self.lastFrameWith == 0:
            return True
        oldX,oldY,oldR = self.coords[self.lastFrameWith]
        #make sure that the new circle agrees with the old circle
        if abs(oldX-x) < oldR/2 and abs(oldY-y) < oldR/2 and abs(r-oldR) < oldR/2:
           return True
        return False
    
    def insert(self,x,y,r,t):
        self.coords[t] = (x,y,r)
        self.xCoords += [x]
        self.yCoords += [y]
        self.rCoords += [r]
        self.tCoords += [t]
    
    def find(self):
        pass
    
    def getXCoords(self):
       return self.xCoords
    
    def getYCoords(self):
       return self.yCoords
    
    def getRCoords(self):
       return self.rCoords

    def getTCoords(self):
       return self.tCoords
    
    def xMax():
        return max(xCoords)

    def xMin():
        return min(xCoords)

    def yMax():
        return max(yCoords)
      
    def yMin():
        return min(yCoords)


