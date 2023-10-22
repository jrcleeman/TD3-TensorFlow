"""
Generate Synthetic Data for Void/Overlap Prediction
"""
import numpy as np
import math
"""
Teminology
-------------
FR = FeedRate
SS = StageSpeed
LH = LayerHeight
E = Error (-1 is largest void, 1 is largest overlap)

Architecture
-------------
7 Inputs [FR_0, SS_0, LH_0, E_0, FR_1, SS_1, LH_1]
1 Output [E_1]

Low Fidelity Equation
---------------------
E_1 = (FR_1 / FR_0 - 1) + (SS_0 / SS_1 - 1) + (LH_0 / LH_1 - 1) + E_0 
"""

class SyntheticDataSet:
    def __init__(self):
        #Hardware Parameters
        self.nominalFR = 200.0
        self.nominalSS = 200.0
        self.nominalLH = 1.0
        self.hardwareDelta = 0.5 #Hardware bounds for each parameter is +/- 50%
        #Disturbance
        self.errorRange = [-1.0, 1.0]
        #
        self.numVariants = 5
        #CSV File Writing
        self.fileName = "syntheticData.csv"
        self.initCSV()
        self.generateData()
    
    def initCSV(self):
        self.csvFile = open(self.fileName,"w") #Create csv file
        #columnList = "FR_0, SS_0, LH_0, E_0, FR_1, SS_1, LH_1, E_1 \n" #Column name list
        #self.csvFile.write(columnList) #Join string array NEW LINE
        self.csvFile.close() #Close csv file
    
    def errorCalculator(self, fr_0, ss_0, lh_0, E_0, fr_1, ss_1, lh_1):
        deltaFR = (fr_1 / fr_0 - 1)
        if (deltaFR > 0):
            deltaFR = math.pow(deltaFR, 0.5)
        elif (deltaFR < 0):
            deltaFR = -1 * math.pow(abs(deltaFR), 0.5)

        #e_1 = (fr_1 / fr_0 - 1) + (ss_0 / ss_1 - 1) + (lh_0 / lh_1 - 1) + E_0
        e_1 = deltaFR + (ss_0 / ss_1 - 1) + (lh_0 / lh_1 - 1) + E_0
        if e_1 < -1:
            return -1.0
        elif e_1 > 1:
            return 1.0
        
        return e_1
    
    def generateData(self):
        feedRate = np.linspace(self.nominalFR * self.hardwareDelta, self.nominalFR * (1 + self.hardwareDelta), self.numVariants)
        stageSpeed = np.linspace(self.nominalSS * self.hardwareDelta, self.nominalSS * (1 + self.hardwareDelta), self.numVariants)
        layerHeight = np.linspace(self.nominalLH * self.hardwareDelta, self.nominalLH * (1 + self.hardwareDelta), self.numVariants)
        error = np.linspace(self.errorRange[0], self.errorRange[1], self.numVariants*2)
        labeledArray = [str(fr_0) + "," + str(ss_0) + "," + str(lh_0) + "," + str(e_0) + "," + str(fr_1) + "," + str(ss_1) + "," + str(lh_1) + "," + \
                        str(self.errorCalculator(fr_0, ss_0, lh_0, e_0, fr_1, ss_1, lh_1)) + "\n" \
                        for fr_0 in feedRate for ss_0 in stageSpeed for lh_0 in layerHeight for e_0 in error\
                        for fr_1 in feedRate for ss_1 in stageSpeed for lh_1 in layerHeight]
        
        for labeledPoint in labeledArray:
            self.csvFile = open(self.fileName, "a")
            self.csvFile.write(labeledPoint)
            self.csvFile.close()


#Main Method Call    
if __name__ == "__main__":
    dataSet = SyntheticDataSet()