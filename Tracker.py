

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
    
    def xMax(self):
        return max(self.xCoords)

    def xMin(self):
        return min(self.xCoords)

    def yMax(self):
        return max(self.yCoords)
      
    def yMin(self):
        return min(self.yCoords)

    def xVelocity(self):
        return _SimpleVelocity(self.xCoords)

    def yVelocity(self):
        return _SimpleVelocity(self.yCoords)

    def _SimpleVelocity(self,coords):
        vel = []
        if len(coords) > 3:
            for i in range(1,len(coords)-1):
                vel += [(coords[i+1]-coords[i-1])/(self.tCoords[i+1]-self.tCoords[i-1])]
        return vel

    def xAcceleration(self):
        return _SimpleAcceleration(_SimpleVelocity(self.xCoords))

    def xAcceleration(self):
        return _SimpleAcceleration(_SimpleVelocity(self.yCoords))

    def _SimpleAcceleration(self,vel):
        acc = []
        if len(vel) > 3:
            for i in range(1,len(vel)-1):
                acc += [(vel[i+1]-vel[i-1])/(self.tCoords[i+2]-self.tCoords[i])]
        return acc
