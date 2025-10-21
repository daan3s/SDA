import pygame
from pygame.locals import *
import random

statusList = ['Plain', 'Raw', 'Heating up', 'Done']

class Pizza():
    def __init__(self, toppings, pizzaSize, pizzaID):
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
        
    def GetStatus(self):#Determine status of pizza 
        return self.status
    
    def GetID(self):#Determine status of pizza 
        return self.pizzaID
    
    def IsBaking(self, maxTime, InOven): 
        if (self.status == 'Raw'): 
            if (self.bakingTime < maxTime):
                self.bakingTime = self.bakingTime + 1
                self.status = statusList[1]
            else:
                self.status = statusList[2]

    def GetDescription(self):
        self.toppings = ''
        for i in range(0,len(self.toppingsList)):
            self.toppings = self.toppings + self.toppingsList[i] + ', ' 
        self.PizzaDescription = str(self.pizzaID) + ': The pizza with toppings: ' + self.toppings + 'and size: '+ self.size + ' has status ' + self.status + '.'
        return self.PizzaDescription

