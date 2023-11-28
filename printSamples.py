import numpy as np
import pandas as pd
import math
#CSV File Class
class CSVFile:
    def __init__(self, fileName):
        self.fileName = fileName
        self.csvFile = open(self.fileName,"w")
        titleString = "X, Y, Z, A, B, C \n 0, 0, 0, 0, 0, 0 \n"
        self.csvFile.write(titleString)
        self.csvFile.close()
        
    def printToCSV(self, commandArray):  
        self.csvFile = open(self.fileName,"a")
        lineToWrite = ','.join(str(value) for value in commandArray)
        lineToWrite = lineToWrite + "\n"
        self.csvFile.write(lineToWrite)
        self.csvFile.close()

#Square Printer
class SquarePrint:
    def __init__(self, makeErrorHotOne, errorMechanismHotOne, firstLayerTest, movementIntervals, zMovementInterval, extruderIntervals, retractDist, length, layerHeight, numLinePairs, beadWidth, sampleSeperation, csvHandler):
        self.positionX = 0.0 #X Cartesian
        self.positionY = 0.0 #Y Cartesian
        self.positionZ = 0.0 #Z Cartesian
        self.currentLinePair = 0 #Line pair current 
        self.travelDirX = False #Negative Dir
        self.movementIntervals = movementIntervals #X,Y Movement Intervals
        self.zMovementInterval = zMovementInterval #Z Movement Intervals
        self.extruderIntervals = extruderIntervals #Ext Movement Intervals
        self.retractDist = retractDist #retract after making first layer
        self.length = length #Length of line pair to be printed
        self.layerHeight = layerHeight #Dist btwn base layer and next
        self.numLinePairs = numLinePairs #Total num of line pairs to be made
        self.beadWidth = beadWidth #step over for pair print
        self.sampleSeperation = sampleSeperation #step over for new sample print
        self.csvHandler = csvHandler #CSVFile class
        self.errorMechanismHotOne = errorMechanismHotOne #type of error mechanism (fr, ss, lh)
        #NO Error
        #if (makeErrorHotOne == 0):
        self.errorExtruderIntervals = [1 for x in range(self.numLinePairs)]
        self.adjustedMovementInterval = self.movementIntervals
        self.zAdjustment = 0.0
        #Void Error
        if (makeErrorHotOne == 1):
            if (self.errorMechanismHotOne == 0):
                self.errorExtruderIntervals = np.linspace(0.8, 0.25, self.numLinePairs)     
            elif (self.errorMechanismHotOne == 1):
                self.adjustedMovementInterval = self.movementIntervals * 2
            elif (self.errorMechanismHotOne == 2):
                self.zAdjustment = 0.3
        #Overlap Error
        elif (makeErrorHotOne == 2):
            if (self.errorMechanismHotOne == 0):
                self.errorExtruderIntervals = np.linspace(1.2, 2, self.numLinePairs)
            elif (self.errorMechanismHotOne == 1):
                self.adjustedMovementInterval = self.movementIntervals * 0.5
            elif (self.errorMechanismHotOne == 2):
                self.zAdjustment = -0.2                
        
        #Print a first layer
        if (not firstLayerTest):
            self.printFirstLayer()

        self.printDisturbanceSquare()
    
    def printFirstLayer(self):
        #print("Printing Base")
        #Print Base Layer
        while self.currentLinePair < (self.numLinePairs * 2):
            #Moving in negative X dir
            start = self.positionX
            end = (-1 * self.length)
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update X Position
                absDistX = move - self.positionX
                self.positionX += absDistX
                self.csvHandler.printToCSV([absDistX, 0.0, 0.0, self.extruderIntervals, 0.0, 0.0])
            
            #Moving in positive Y dir
            start = self.positionY
            end = self.positionY + self.beadWidth
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update Y Position
                absDistY = move - self.positionY
                self.positionY += absDistY
                self.csvHandler.printToCSV([0.0, absDistY, 0.0, self.extruderIntervals, 0.0, 0.0])            

            #Moving in positive X dir
            start = self.positionX
            end = 0
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update X Position
                absDistX = move - self.positionX
                self.positionX += absDistX
                self.csvHandler.printToCSV([absDistX, 0.0, 0.0, self.extruderIntervals, 0.0, 0.0])
            
            #Moving in positive Y dir
            start = self.positionY
            end = self.positionY + self.beadWidth
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update Y Position
                absDistY = move - self.positionY
                self.positionY += absDistY
                self.csvHandler.printToCSV([0.0, absDistY, 0.0, self.extruderIntervals, 0.0, 0.0]) 

            #Increment Number of Line Pairs Printed
            self.currentLinePair +=1
        
        #Retract Filament
        self.csvHandler.printToCSV([0.0, 0.0, 0.0, retractDist, 0.0, 0.0])
        #Move Up In Z-Axis
        start = self.positionZ
        end = self.layerHeight
        printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / (self.zMovementInterval)))
        for move in printMovementArray[1:]:
                #Update Z Position
                absDistZ = move - self.positionZ
                self.positionZ += absDistZ
                self.csvHandler.printToCSV([0.0, 0.0, absDistZ, 0.0, 0.0, 0.0])
        
        #Move to origin
        startX = self.positionX
        startY = self.positionY
        endX = 0
        endY = 0
        printMovementArrayX = np.linspace(startX, endX, math.ceil(abs(endX - startX) / self.movementIntervals))
        printMovementArrayY = np.linspace(startY, endY, math.ceil(abs(endY - startY) / self.movementIntervals))
        #Move in X
        for move in printMovementArrayX[1:]:
            #Update X Position
            absDistX = move - self.positionX
            self.positionX += absDistX
            self.csvHandler.printToCSV([absDistX, 0.0, 0.0, 0.0, 0.0, 0.0])
        #Move in Y
        for move in printMovementArrayY[1:]:
            #Update Y Position
            absDistY = move - self.positionY
            self.positionY += absDistY
            self.csvHandler.printToCSV([0.0, absDistY, 0.0, 0.0, 0.0, 0.0])   
        #Redeposit Filament
        self.csvHandler.printToCSV([0.0, 0.0, 0.0, (-1 * retractDist), 0.0, 0.0])


    def printDisturbanceSquare(self):
        #print("Printing Voids")
        self.currentLinePair = 0
        #Loop to print all lines
        while self.currentLinePair < self.numLinePairs:
            #Moving in negative X dir
            start = self.positionX
            end = (-1 * self.length)
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update X Position
                absDistX = move - self.positionX
                self.positionX += absDistX
                self.csvHandler.printToCSV([absDistX, 0.0, 0.0, self.extruderIntervals, 0.0, 0.0])
            
            #Moving in positive Y dir
            start = self.positionY
            end = self.positionY + self.beadWidth
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update Y Position
                absDistY = move - self.positionY
                self.positionY += absDistY
                self.csvHandler.printToCSV([0.0, absDistY, 0.0, self.extruderIntervals, 0.0, 0.0])            

            '''
            ERROR IMPLEMENTED HERE
            '''
            #Moving in positive X dir
            start = self.positionX
            end = 0
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            #Stage speed error 
            if (self.errorMechanismHotOne == 1):
                printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.adjustedMovementInterval))
            firstErrorMove = True #Will move the Z axis on first error move
            firstCorrectionMove = True #Will un-move the Z axis on first non-error move            
            for move in printMovementArray[1:]:
                #Update X Position
                absDistX = move - self.positionX
                self.positionX += absDistX
                if ((self.positionX > (-1 * self.length * 3 / 4)) and (self.positionX < (-1 * self.length * 1 / 4))):
                    newExtruderRate = self.errorExtruderIntervals[self.currentLinePair] * self.extruderIntervals
                    #Z-Error
                    if (firstErrorMove and (self.errorMechanismHotOne == 2)):
                        self.csvHandler.printToCSV([absDistX, 0.0, self.zAdjustment, newExtruderRate, 0.0, 0.0])
                        firstErrorMove = False
                    else:
                        self.csvHandler.printToCSV([absDistX, 0.0, 0.0, newExtruderRate, 0.0, 0.0])
                else:
                    if (firstCorrectionMove and (not firstErrorMove) and (self.errorMechanismHotOne == 2)):
                        self.csvHandler.printToCSV([absDistX, 0.0, (-1 * self.zAdjustment), newExtruderRate, 0.0, 0.0])
                        firstCorrectionMove = False
                    self.csvHandler.printToCSV([absDistX, 0.0, 0.0, self.extruderIntervals, 0.0, 0.0])
            
            #Moving in positive Y dir
            start = self.positionY
            end = self.positionY + self.sampleSeperation
            printMovementArray = np.linspace(start, end, math.ceil(abs(end - start) / self.movementIntervals))
            for move in printMovementArray[1:]:
                #Update Y Position
                absDistY = move - self.positionY
                self.positionY += absDistY
                self.csvHandler.printToCSV([0.0, absDistY, 0.0, self.extruderIntervals, 0.0, 0.0]) 

            #Increment Number of Line Pairs Printed
            self.currentLinePair +=1


if __name__ == "__main__":
    fileName = r'cyberPrint.csv'
    csvWriter = CSVFile(fileName)
    #0 For NO Error
    #1 For Void Error
    #2 For Overlap Error
    makeErrorHotOne = 2
    #0 for feed rate
    #1 for stage speed
    #2 for layer height
    errorMechanismHotOne = 2
    #First layer test bool
    firstLayerTest = True
    movementIntervals = 0.5
    zMovementInterval = 0.1
    extruderIntervals = 2.0
    retractDist = -5
    length = 45
    layerHeight = 0.5
    numLinePairs = 3
    beadWidth = 4.5
    sampleSeperation = 9
    squarePrint = SquarePrint(makeErrorHotOne, errorMechanismHotOne, firstLayerTest, movementIntervals, zMovementInterval, extruderIntervals, retractDist, length, layerHeight, numLinePairs, beadWidth, sampleSeperation, csvWriter)
