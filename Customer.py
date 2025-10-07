import pygame
import random
import math

class Customer():
    def __init__(self, ID, address):
        self.customerID = ID
        self.customerAddress = address

    def GenerateOrder(self):
