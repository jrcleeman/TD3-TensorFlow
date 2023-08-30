import random
import numpy
import pygame
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
    def __init__(self, bgImg = None, birdImg = None, x = 0, terminalX = 600, feedRate = 200, stageSpeed = 200, layerHeight = 0.5, \
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
        self.desiredY1 = 400 #self.widthCalculator()
        self.desiredY2 = random.randint(self.desiredY1 - 200, self.desiredY1 + 200)
        self.desiredY3 = random.randint(self.desiredY1 - 200, self.desiredY1 + 200)
        self.bases = Base(self.desiredY1, self.desiredY2, self.desiredY3, terminalX, baseImg1, baseImg2, baseImg3)
        '''Position''' 
        self.x = x #Current X Position
        self.terminalX = terminalX
        self.y = self.widthCalculator() #Current Y Pos
        self.positionHistory = []
        self.travelSpeedX = 3
        '''Strike Counter'''
        self.strikeCounter = 0
        #Image
        self.birdImg = birdImg
        self.bgImg = bgImg
        #Info
        self.observation_space = 5 #(5,)
        self.action_space = 3
    
    #This makes pygame display
    def render(self, win):
        #Draw Background
        win.blit(self.bgImg, (0,0))
        #Draw Base
        self.bases.draw(win)
        #Draw Bead
        #self.draw(win)
        if isinstance(self.y, float) or isinstance(self.y, int):
            win.blit(self.birdImg, (self.x, self.y))     
        else:
            win.blit(self.birdImg, (self.x, self.y.numpy()))

        '''Print Process Parameters in Game'''
        '''
        STAT_FONT = pygame.font.SysFont("comicsans", 50) #In game font
        score_label = STAT_FONT.render("Feed Rate: " + str(round(self.feedRate, 2)),1,(0,255,0))
        win.blit(score_label, (self.terminalX - score_label.get_width() - 15, 50))
        score_label = STAT_FONT.render("Stage Speed: " + str(round(self.stageSpeed, 2)),1,(0,255,0))
        win.blit(score_label, (self.terminalX - score_label.get_width() - 15, 600))
        score_label = STAT_FONT.render("Layer Height: " + str(round(self.layerHeight, 2)),1,(0,255,0))
        win.blit(score_label, (self.terminalX - score_label.get_width() - 15, 700))
        #'''
        return
    
    #Reset bird to original state
    def reset(self):
        '''Reset Parameters'''
        self.feedRate = self.nominalFR
        self.stageSpeed = self.nominalSS
        self.layerHeight = self.nominalLH
        '''Reset Goals'''
        self.desiredY1 = 400 #self.widthCalculator()
        self.desiredY2 = random.randint(self.desiredY1 - 100, self.desiredY1 + 100)
        if self.desiredY2 < self.desiredY1:
            self.desiredY3 = random.randint(self.desiredY1 - 100, self.desiredY1)
        else:
            self.desiredY3 = random.randint(self.desiredY1, self.desiredY1 + 100)
        self.bases.reset(self.desiredY1, self.desiredY2, self.desiredY3)
        '''Reset Position'''
        self.x = 0
        self.y = self.widthCalculator()
        self.positionHistory = []
        '''Reset State'''
        self.desiredY = self.desiredY1 #self.widthCalculator()
        currentState = [self.desiredY, self.y, self.feedRate, self.stageSpeed, self.layerHeight]
        currentState = numpy.array(currentState)
        '''Reset Strikes'''
        self.strikeCounter = 0

        return currentState
    
    def calculateReward(self):
        '''Parameter Reward'''
        #Feed Rate Fitness Calc
        fitnessFR = abs(self.feedRate - self.nominalFR)
        fitnessFR = fitnessFR * (-1 / (self.nominalFR - self.deltaFR)) #Normalized, between 0 and -1
        #Stage Speed Fitness Calc
        fitnessSS = abs(self.stageSpeed - self.nominalSS)
        fitnessSS = fitnessSS * (-1 / (self.nominalSS - self.deltaSS)) #Normalized, between 0 and -1
        #Layer Height Fitness Calc
        fitnessLH = abs(self.layerHeight - self.nominalLH)
        fitnessLH = fitnessLH * (-1 / (self.nominalLH - self.deltaLH)) #Normalized, between 0 and -1

        '''Width reward'''
        isDone = False
        limit = -100
        x_low = -100 #Greatest Width Err
        x_high = 0 #Smallest Width Err
        Rlow = 0 #lowest reward
        Rhigh = 10 #highest reward
        error = -1 * abs(self.y - self.desiredY)
        '''Game Over'''
        if error < -150:
            self.strikeCounter += 1
            fitnessW = 0
            if self.strikeCounter >= 3:
                isDone = True #terminal flag
                timeStepFitness = -200 #Negative reward for losing
                return timeStepFitness, isDone

        else:
            fitnessW = Rlow + ((error - x_low) * (Rhigh - Rlow) / (x_high - x_low))
            
        '''Total Step Reward'''
        timeStepFitness = fitnessFR + fitnessSS + fitnessLH + fitnessW
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

        #Adjust Y Targets
        if (self.x <= (self.terminalX / 3)):
            self.desiredY = self.desiredY1
        elif (self.x <= (2 * self.terminalX / 3)):
            self.desiredY = self.desiredY2
        else:
            self.desiredY = self.desiredY3

        #Return Reward, State, Done Flag
        timeStepFitness, isDone = self.calculateReward() #Reward
        currentState = [self.desiredY, self.y, self.feedRate, self.stageSpeed, self.layerHeight]
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
        self.positionHistory.append([self.x, self.y])

    #Method for drawing the print
    def draw(self, win):
        #Draw bead
        win.blit(self.birdImg, (self.x, self.y))

        #Print Line History (Optional)
        #for i in range(len(self.positionHistory)):
        #    win.blit(self.img, (self.positionHistory[i][0], self.positionHistory[i][1]))