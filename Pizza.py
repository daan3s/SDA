import pygame
from pygame.locals import *
import random

statusList = ['Raw', 'Heating up', 'Done', 'On its way', 'Delivered']

class Pizza():
    def __init__(self, window, toppings, pizzaSize, pizzaID):
        self.window = window
        self.pizzaID = pizzaID
        self.toppingsList = toppings #get the toppings of the pizza
        self.price = len(toppings) * 0.75 #set a price based on toppings
        self.status = statusList[0]
        self.size = pizzaSize
        self.bakingTime = 0

    def GetPrize(self): #Determine price based on size
        if (self.size == 'Large'):
            return self.price + 5
        if (self.size == 'Medium'):
            return self.price + 3
        if (self.size == 'Small'):
            return self.price + 1
        
    def GetStatus(self, PizzaStatus):#Determine status of pizza
        self.status = statusList[PizzaStatus] 
        return self.status
    
    def IsBaking(self, InOven, maxTime):
        if (InOven):
            if (self.bakingTime < maxTime):
                self.bakingTime = self.bakingTime + 1
                self.status = statusList[1]
            else:
                self.status = statusList[2]

    
    def GetDescription(self):
        for i in self.toppingsList:
            self.toppings = self.toppings + self.toppingsList[i] + ', ' 
        self.PizzaDescription = self.pizzaID + ': The pizza with toppings: ' + self.toppings + 'and size: '+ self.size + 'has status ' + self.status + '.'

