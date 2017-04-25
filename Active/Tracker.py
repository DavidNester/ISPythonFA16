"""Parent class for the trackers"""
class Tracker:
    
    """initializes with variables that need to be kept track of no matter the type"""
    def __init__(self):
        #instance variables
        self.lastFrameWith = 0
        self.coords = {}
        self.xCoords = []
        self.yCoords = []
        self.rCoords = []
        self.tCoords = []
        self.fps = 0
        self.size = 0
    
    """used to makse sure the circle is the same one that was chosen at the beginning"""
    def normal(self,x,y,r):
        #accept data if we hae no prior knowledge
        if self.lastFrameWith == 0:
            return True
        oldX,oldY,oldR = self.coords[self.lastFrameWith]
        #make sure that the new circle agrees with the old circle
        if abs(oldX-x) < oldR/2 and abs(oldY-y) < oldR/2 and abs(r-oldR) < oldR/2:
           return True
        return False

    """add the coordinates of a circle to the dictionary and lists"""
    def insert(self,x,y,r,t):
        self.coords[t] = (x,y,r)
        self.xCoords += [x]
        self.yCoords += [y]
        self.rCoords += [r]
        self.tCoords += [t]
    
    """method for finding object using tracker - must be implemented by child"""
    def find(self):
        print 'find() must be implemented by child class'
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
    
    def getRadius(self):
        #we probably want to check how spread out the range is
        return sum(self.rCoords)/len(self.rCoords)

    """Method for returning the x-velocity of each frame"""
    def xVelocity(self):
        """Must return tCoords as well because it cuts one off on either end"""
        return self.tCoords[1:len(self.tCoords)-1],self._SimpleVelocity(self.xCoords)
    """Method for returning the y-velocity of each frame"""
    def yVelocity(self):
        """Must return tCoords as well because it cuts one off on either end"""
        return self.tCoords[1:len(self.tCoords)-1],self._SimpleVelocity(self.yCoords)
    """method for calcualting velocity given position coords (very simplistic)"""
    def _SimpleVelocity(self,coords):
        vel = []
        if len(coords) > 3:
            for i in range(1,len(coords)-1):
                vel += [((coords[i+1]-coords[i-1])*1.0)/(self.tCoords[i+1]-self.tCoords[i-1])]
        return vel
    """method for returning x-acceleration"""
    def xAcceleration(self):
        """Must return tCoords as well because it cuts one off on either end"""
        return self.tCoords[2:len(self.tCoords)-2],self._SimpleAcceleration(self._SimpleVelocity(self.xCoords))
    """method for returning y-acceleration"""
    def yAcceleration(self):
        """Must return tCoords as well because it cuts one off on either end"""
        return self.tCoords[2:len(self.tCoords)-2],self._SimpleAcceleration(self._SimpleVelocity(self.yCoords))
    """method for calcualting acceleration given velocity coords (very simplistic)"""
    def _SimpleAcceleration(self,vel):
        acc = []
        if len(vel) > 3:
            for i in range(1,len(vel)-1):
                acc += [((vel[i+1]-vel[i-1])*1.0)/(self.tCoords[i+2]-self.tCoords[i])]
        return acc

    def setFPS(self,fps):
        self.fps = fps
    def setSize(self,size):
        self.size = size
    def getFPS(self):
        return self.fps
    def getSize(self):
        return self.size
