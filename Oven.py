import pygame
from pygame.locals import *
import random

class Oven():
    def __init__(self, window):
        self.window = window
        self.ovenID = random.randint(2000,2999)
        self.isAvailable = True
        self.temperature = random.randint(150,200)
        self.maxBakingTime = -1*self.temperature + 200
    
    def IsBaking(self, InOven):
        if (InOven):
            