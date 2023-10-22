import random
import numpy
#import pygame
#Observer Class, Predicts ideal line width based on VF and OE
class ObserverNN:
    def __init__(self):
        return
    
    #Method for predicting next desired line width based on observations
    def update(self, currentWidth, voidFraction, overextFraction):
        newWidth = currentWidth * (1 + voidFraction) / (1 + overextFraction)
        return newWidth

#Dynamics Class, Predicts resultant line width based on FR, SS, and LH
class DynamicsNN:
    def __init__(self):
        return
    
    #Method for predicting next printed line width based on process params
    def predict(self, feedRate, stageSpeed, layerHeight):
        widthPrediction = (feedRate / (stageSpeed * layerHeight)) * 200
        return widthPrediction

#Line width goal indicator class
class Base:
    def __init__(self, y1, y2, y3, terminalX, goal1Img = None, goal2Img = None, goal3Img = None):
        self.y1 = y1
        self.y2 = y2 #secondary nominal width
        self.y3 = y3
        '''Goal Divisions'''
        self.x1 = 0 #first marker x pos
        self.x2 = terminalX / 3 #second marker x pos
        self.x3 = 2 * terminalX / 3 #third marker x pos
        '''Images'''
        self.IMG1 = goal1Img #first marker img
        self.IMG2 = goal2Img #second marker img
        self.IMG3 = goal3Img #third marker img
    
    def reset(self, y1, y2, y3):
        self.y1 = y1
        self.y2 = y2 #secondary nominal width
        self.y3 = y3        

    #Method to draw red dotted desired width
    def draw(self, win):
        #Draw initial nominal width
        win.blit(self.IMG1, (self.x1, self.y1))
        #Draw secondary nominal width
        win.blit(self.IMG2, (self.x2, self.y2))
        #Draw tertiary nominal width
        win.blit(self.IMG3, (self.x3, self.y3))

#Printer Class
class Bird:
    def __init__(self, bgImg = None, birdImg = None, x = 0, terminalX = 1800, feedRate = 200, stageSpeed = 200, layerHeight = 0.5, \
                 baseImg1 = None, baseImg2 = None, baseImg3 = None):
        '''Predictor'''
        self.dynamicsNN = DynamicsNN()        
        '''Feed Rate'''
        self.feedRate = feedRate #Current Feed Rate    
        self.nominalFR = 200   
        self.deltaFR = 100 
        '''Stage Speed'''
        self.stageSpeed = stageSpeed #Current Stage Speed        
        self.nominalSS = 200
        self.deltaSS = 100
        '''Layer Height'''
        self.layerHeight = layerHeight #Current Layer Height
        self.nominalLH = 0.5
        self.deltaLH = 0.25
        '''Goals'''
        self.disturbance = random.uniform(-1, 1) #Distrubance
        if (self.disturbance < 0): #Void
            self.newWidthGoal =  self.widthCalculator() * (1 + abs(self.disturbance))    
        elif (self.disturbance > 0): #Overlap
            self.newWidthGoal = self.widthCalculator() / (1 + abs(self.disturbance))
        else: #No disturbance
            self.newWidthGoal = self.widthCalculator()
        '''Position''' 
        self.x = x #Current X Position
        self.terminalX = terminalX
        self.y = self.widthCalculator() #Current Y Pos
        self.positionHistory = []
        self.travelSpeedX = 3
        #'''Strike Counter'''
        #self.strikeCounter = 0
        #Image
        self.birdImg = birdImg
        self.bgImg = bgImg
        #Info
        self.observation_space = 1 #(5,)
        self.action_space = 3
    
    #This makes pygame display
    '''
    def render(self):
        #print("Reward: ") #FIX ME????
        print(self.disturbance)
        print(self.newWidthGoal)
        print("Feed Rate: " + str(round(self.feedRate, 2)))
        print("Stage Speed: " + str(round(self.stageSpeed, 2)))
        print("Layer Height: " + str(round(self.layerHeight, 2)))
        return
    '''
    #Reset bird to original state
    def reset(self):
        '''Reset Parameters'''
        self.feedRate = self.nominalFR
        self.stageSpeed = self.nominalSS
        self.layerHeight = self.nominalLH
        '''Reset Goals'''
        self.disturbance = random.uniform(-1, 1) #Distrubance
        if (self.disturbance < 0): #Void
            self.newWidthGoal =  self.widthCalculator() * (1 + abs(self.disturbance))    
        elif (self.disturbance > 0): #Overlap
            self.newWidthGoal = self.widthCalculator() / (1 + abs(self.disturbance))
        else: #No disturbance
            self.newWidthGoal = self.widthCalculator()
        '''Reset Position'''
        self.x = 0
        self.y = self.widthCalculator()
        '''Reset State'''
        currentState = [self.disturbance]
        currentState = numpy.array(currentState)

        return currentState

    def semiSet(self):
        '''Reset Parameters'''
        self.feedRate = self.nominalFR
        self.stageSpeed = self.nominalSS
        self.layerHeight = self.nominalLH
        '''Reset Goals'''
        self.disturbance = random.uniform(-1, 1) #Distrubance
        if (self.disturbance < 0): #Void
            self.newWidthGoal =  self.widthCalculator() * (1 + abs(self.disturbance))    
        elif (self.disturbance > 0): #Overlap
            self.newWidthGoal = self.widthCalculator() / (1 + abs(self.disturbance))
        else: #No disturbance
            self.newWidthGoal = self.widthCalculator()
        '''Reset Position'''
        self.y = self.widthCalculator()    
    
    def rescaleReward(self, input, xLow, xHigh, rewardLow, rewardHigh):
        reward = rewardLow + ((input - xLow) * (rewardHigh - rewardLow) / (xHigh - xLow))
        return reward

    def calculateReward(self):
        '''Increasing Level Difficulty and Reward'''
        levelBonus = 1
        errorThreshold = -1
        failPenalty = -50
        checkpoint1 = 600
        checkpoint2 = 1200
        if (self.x > checkpoint1):
            constant = 0.75 / 1200
            errorThreshold = -1 + (constant * self.x)
            levelBonus = 1 + (0.01 * self.x)
            failPenalty = -25
        elif (self.x > checkpoint2):
            constant = 0.95 / 1800
            errorThreshold = -1 + (constant * self.x)
            levelBonus = 1 + (0.01 * self.x)
            failPenalty = -12  
        '''Mission Complete Bonus'''
        if (self.x >= (self.terminalX - self.travelSpeedX)):
            levelBonus = 5000

        '''Parameter Reward'''
        parameterLow = -5
        #Feed Rate Fitness Calc
        fitnessFR = abs(self.feedRate - self.nominalFR)
        fitnessFR = fitnessFR * (-1 / (self.nominalFR - self.deltaFR)) #Normalized, between 0 and -1
        fitnessFR = self.rescaleReward(fitnessFR, -1, 0, parameterLow, 0)
        #Stage Speed Fitness Calc
        fitnessSS = abs(self.stageSpeed - self.nominalSS)
        fitnessSS = fitnessSS * (-1 / (self.nominalSS - self.deltaSS)) #Normalized, between 0 and -1
        fitnessSS = self.rescaleReward(fitnessSS, -1, 0, parameterLow, 0)
        #Layer Height Fitness Calc
        fitnessLH = abs(self.layerHeight - self.nominalLH)
        fitnessLH = fitnessLH * (-1 / (self.nominalLH - self.deltaLH)) #Normalized, between 0 and -1
        fitnessLH = self.rescaleReward(fitnessLH, -1, 0, parameterLow, 0)
        parameterReward = fitnessFR + fitnessSS + fitnessLH

        '''Width reward'''
        widthError = self.y - self.newWidthGoal
        if (widthError < 0): #Void Present
            inputError = -1 * ((self.newWidthGoal / self.y) - 1)
            if (inputError < -1): #Error limiter
                inputError = 1                
        elif (widthError > 0): #Overlap Present
            inputError = (self.y / self.newWidthGoal) - 1
            if (inputError > 1): #Error limiter
                inputError = 1
        
        calculationError = -1 * abs(inputError)
        errorLow = -1 #Greatest Error Value
        errorHigh = 0 #Smallest Error Value
        Rlow = -10 #lowest reward
        Rhigh = 10 #highest reward
        errorReward = Rlow + ((calculationError - errorLow) * (Rhigh - Rlow) / (errorHigh - errorLow))

        isDone = False          
        '''Game Over'''
        if calculationError <= errorThreshold:
            isDone = True #terminal flag
            timeStepFitness = failPenalty #Negative reward for losing
            #print("death: " + str(self.x))
            return timeStepFitness, isDone
        elif (self.x > checkpoint1): #Parameter Constraints
            parameterThreshold = -0.9
            if (self.x > checkpoint2):
                parameterThreshold = -0.8
            if ((fitnessFR < parameterThreshold) or (fitnessSS < parameterThreshold) or (fitnessLH < parameterThreshold)):
                isDone = True #terminal flag
                timeStepFitness = failPenalty #Negative reward for losing
                #print("death: " + str(self.x))
                return timeStepFitness, isDone

        '''Total Step Reward'''
        #levelBonus = 1
        timeStepFitness = parameterReward + errorReward + levelBonus
        return timeStepFitness, isDone

    #Call global NN predictor
    def widthCalculator(self):
        width = self.dynamicsNN.predict(self.feedRate, self.stageSpeed, self.layerHeight)
        return width

    def step(self, outputArray):
        '''Parameter Update'''
        self.updateFeedRate(outputArray[0])
        self.updateStageSpeed(outputArray[1])
        self.updateLayerHeight(outputArray[2])
        self.move()

        #Return Reward, State, Done Flag
        timeStepFitness, isDone = self.calculateReward() #Reward

        #Render
        render = False
        if render:
            '''
            print("Disturbance: " + str(self.disturbance))
            print("New Width Goal: " + str(self.newWidthGoal))
            print("Reward: " + str(self.widthCalculator()))
            print("Feed Rate: " + str(round(self.feedRate, 2)))
            print("Stage Speed: " + str(round(self.stageSpeed, 2)))
            print("Layer Height: " + str(round(self.layerHeight, 2)))
            '''
            if (self.x == 600):
                print("level 1 passed")
            if (self.x > 1200):
                print("goated")

        self.semiSet() #semi reset
        currentState = [self.disturbance]
        currentState = numpy.array(currentState)
        terminalState = (True if self.x >= self.terminalX or isDone else False) #Done Flag
        return currentState, timeStepFitness, terminalState

    '''Method for updating feed rate'''
    def updateFeedRate(self, output):
        self.feedRate = (output * self.deltaFR) + self.nominalFR       

    '''Method for updating stage speed'''
    def updateStageSpeed(self, output):
        self.stageSpeed = (output * self.deltaSS) + self.nominalSS            

    '''Method for updating layer height'''
    def updateLayerHeight(self, output):
        self.layerHeight = (output * self.deltaLH) + self.nominalLH

    '''Method for updating position'''
    def move(self):
        #Update Y Position
        self.y = self.widthCalculator() #self.y + displacement
        #X Travel Speed (Constant)
        self.x += self.travelSpeedX
        #Update Position History
        #self.positionHistory.append([self.x, self.y])

    #Method for drawing the print
    def draw(self, win):
        #Draw bead
        win.blit(self.birdImg, (self.x, self.y))

        #Print Line History (Optional)
        #for i in range(len(self.positionHistory)):
        #    win.blit(self.img, (self.positionHistory[i][0], self.positionHistory[i][1]))