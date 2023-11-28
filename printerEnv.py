import random
import numpy as np
from predictNN import ErrorDNN 
import tensorflow as tf
#Printer Class
class FDM:
    def __init__(self, gameLength = 1800, feedRate = 200, stageSpeed = 200, layerHeight = 1.0):
        '''Predictor'''
        self.dynamicsNN = ErrorDNN()     
        '''Feed Rate'''
        self.nominalFR = feedRate   
        self.deltaFR = 100 
        '''Stage Speed'''
        self.nominalSS = stageSpeed      
        self.deltaSS = 100
        '''Layer Height'''
        self.nominalLH = layerHeight
        self.deltaLH = 0.5
        '''Error'''
        self.error_0 = random.uniform(-1, 1) #Distrubance
        '''Game Progression''' 
        self.terminalGameStep = gameLength
        '''State/Action Space'''
        self.observation_space = 7 #(7,)
        self.action_space = 3
        '''Reward Distribution'''
        self.earlyTerminalReward = -200
        self.minParameterReward = -5 #-2
        self.maxParameterReward = 0
        self.stepSurvivalReward = 10
        self.minCheckPntReward = 20
        self.maxCheckPntReward = 2000
        '''Error Tolerance'''
        self.maxAbsErrToler = 0.55
        self.minAbsErrToler = 0.15
        '''Game Check Points'''
        gameSteps = np.array([x * 20 for x in range(10)])
        errorBreakdown = np.linspace(self.maxAbsErrToler, self.minAbsErrToler, len(gameSteps))
        ckpntRwrdBreakdown = np.linspace(self.minCheckPntReward, self.maxCheckPntReward, len(gameSteps))
        self.gameCheckPnts = [[gameSteps[i], errorBreakdown[i], ckpntRwrdBreakdown[i]] for i in range(len(gameSteps))]
        self.checkPntIdx = 0
    
    #Reset bird to original state
    def reset(self, newGame = True):
        '''Reset Parameters'''
        self.feedRate_0 = random.uniform(self.nominalFR - self.deltaFR, self.nominalFR + self.deltaFR)
        self.stageSpeed_0 = random.uniform(self.nominalSS - self.deltaSS, self.nominalSS + self.deltaSS)
        self.layerHeight_0 = random.uniform(self.nominalLH - self.deltaLH, self.nominalLH + self.deltaLH)
        #self.error_0 = tf.constant(random.uniform(0.95, 1), dtype = tf.float64) #Distrubance
        val = self.gameCheckPnts[self.checkPntIdx][1]
        self.error_0 = tf.constant(random.uniform(val, 1), dtype = tf.float64)
        voidRandom = random.uniform(-1,1)
        if (voidRandom <= 0):
            self.error_0 = -1 * self.error_0

        '''Reset Position'''
        if (newGame):
            self.currentGameStep = 0 
            self.checkPntIdx = 0
        '''
        else:
            val = self.gameCheckPnts[self.checkPntIdx][1]
            self.error_0 = tf.constant(random.uniform(val, 1), dtype = tf.float64)
        '''
        '''Reset State'''
        currentState = [self.feedRate_0, self.stageSpeed_0, self.layerHeight_0, self.error_0]
        currentState = np.array(currentState)

        return currentState  
    
    #Step in game
    def step(self, outputArray):
        '''Parameter Selection'''
        self.updateFeedRate(outputArray[0])
        self.updateStageSpeed(outputArray[1])
        self.updateLayerHeight(outputArray[2])

        '''Calculate Error_1'''
        tempInputArray = np.array((self.feedRate_0, self.stageSpeed_0, self.layerHeight_0, self.error_0,\
                      self.feedRate_1, self.stageSpeed_1, self.layerHeight_1))
        inputArray = tempInputArray.reshape((-1,7))
        error_1 = self.dynamicsNN.dnn_model.predict(inputArray).flatten()

        ''''Print Chosen Param'''
        print("Init Param: [" + str(self.feedRate_0) + ", " + str(self.stageSpeed_0) + ", " + str(self.layerHeight_0) + "] " + "Initial Error: " + str(self.error_0))
        print("New Param: [" + str(self.feedRate_1) + ", " + str(self.stageSpeed_1) + ", " + str(self.layerHeight_1) + "] " + "New Error: " + str(error_1))
        #Return Reward, State, Done Flag
        reward, isDone = self.getReward(error_1) #Reward
        
        #Next State
        currentState = np.array(self.reset(False))
        #Incerement Game Step
        self.currentGameStep += 1

        return currentState, reward, isDone
    
    '''Method for updating feed rate'''
    def updateFeedRate(self, output):
        self.feedRate_1 = (output * self.deltaFR) + self.nominalFR       

    '''Method for updating stage speed'''
    def updateStageSpeed(self, output):
        self.stageSpeed_1 = (output * self.deltaSS) + self.nominalSS            

    '''Method for updating layer height'''
    def updateLayerHeight(self, output):
        self.layerHeight_1 = (output * self.deltaLH) + self.nominalLH

    def rescaleParameterReward(self, input):
        xLow = -1
        xHigh = 0
        rewardLow = self.minParameterReward
        rewardHigh = self.maxParameterReward
        reward = rewardLow + ((input - xLow) * (rewardHigh - rewardLow) / (xHigh - xLow))
        return reward

    def getReward(self, error_1):
        '''Error Reward/Survival Check'''
        isDone = False   
        gameStepReward = 0   
        #Survival check
        if (abs(error_1) > self.gameCheckPnts[self.checkPntIdx][1]):
            gameStepReward = self.earlyTerminalReward
            isDone = True
            return gameStepReward, isDone
        #Passed
        else:
            gameStepReward += self.stepSurvivalReward

        #Passed a checkpoint
        if (self.currentGameStep > self.gameCheckPnts[self.checkPntIdx][0]):
            gameStepReward += self.gameCheckPnts[self.checkPntIdx][2] #Check point reward
            self.checkPntIdx += 1 #Add check point reward         
            if (self.checkPntIdx >= len(self.gameCheckPnts)):
                isDone = True    

        '''Parameter Reward'''
        #Feed Rate Fitness Calc
        fitnessFR = abs(self.feedRate_0 - self.nominalFR)
        fitnessFR = fitnessFR * (-1 / (self.deltaFR)) #Normalized, between 0 and -1
        fitnessFR = self.rescaleParameterReward(fitnessFR)
        #Stage Speed Fitness Calc
        fitnessSS = abs(self.stageSpeed_0 - self.nominalSS)
        fitnessSS = fitnessSS * (-1 / (self.deltaSS)) #Normalized, between 0 and -1
        fitnessSS = self.rescaleParameterReward(fitnessSS)
        #Layer Height Fitness Calc
        fitnessLH = abs(self.layerHeight_0 - self.nominalLH)
        fitnessLH = fitnessLH * (-1 / (self.deltaLH)) #Normalized, between 0 and -1
        fitnessLH = self.rescaleParameterReward(fitnessLH)
        parameterReward = fitnessFR + fitnessSS + fitnessLH

        '''Total Step Reward'''
        reward = parameterReward + gameStepReward

        return reward, isDone