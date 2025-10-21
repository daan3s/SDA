import pygame
from pygame.locals import *
import random

statusList = ['Plain', 'Raw', 'Heating up', 'Done']

class Pasta():
    def __init__(self, toppings, pastaType, pastaSauce, pastaID):
        self.pastaID = pastaID
        self.toppingsList = toppings #get the toppings of the pizza
        self.price = len(toppings) * 0.75 #set a price based on toppings
        self.status = statusList[0]
        self.type = pastaType
        self.sauce = pastaSauce
        self.bakingTime = 0

    def GetPrize(self): #Determine price based on type and sauce
        if (self.type == 'Spaghetti' or self.type == 'Macaroni' or self.type == 'Penne'):
            self.price + 1
        elif (self.type == 'Tagliatelle' or self.type == 'Gnocchi'):
            self.price + 3
        if (self.sauce == 'Alfredo' or self.type == 'Bolognese' or self.type == 'Arrabiata'):
            self.price + 3
        elif (self.type == 'Tomato' or self.type == 'Pesto'):
            self.price + 1
        return self.price
        
    def GetStatus(self):#Determine status of pasta
        return self.status

    def GetID(self):#Determine status of pasta
        return self.pastaID
    
    def IsBaking(self, maxTime, InOven): 
        if (self.status == 'Raw'): 
            if (self.bakingTime < maxTime):
                self.bakingTime = self.bakingTime + 1
                self.status = statusList[1]
            else:
                self.status = statusList[2]

    def GetDescription(self):
        for i in self.toppingsList:
            self.toppings = self.toppings + self.toppingsList[i] + ', ' 
        self.PastaDescription = self.pastaID + ': The pasta with toppings: ' + self.toppings + 'and size: '+ self.type + ' has status ' + self.status + '.'
        print(self.PastaDescription)