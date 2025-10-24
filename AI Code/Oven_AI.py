import pygame
from pygame.locals import *
import random
import time


class Oven():
    def __init__(self, window):
        self.window = window
        self.OvenID = random.randint(2000, 2999)  # Matches diagram attribute name
        self.OvenAvailable = True  # Matches diagram attribute name
        self.BakingTime = 0  # Matches diagram attribute name
        self.BakingTemperature = 0  # Matches diagram attribute name
        self.maxBakingTime = 0
        self.startTime = 0
        self.isBaking = False

    def IsAvailable(self):  # Matches diagram operation name
        return self.OvenAvailable

    def SetTemp(self, temperature):  # Matches diagram operation name
        self.BakingTemperature = temperature
        print(f"Oven {self.OvenID}: Temperature set to {temperature}°C")
        return self.BakingTemperature  # Returns int as per diagram

    def SetTimer(self, minutes):  # Matches diagram operation name
        self.BakingTime = minutes
        self.maxBakingTime = minutes * 60  # Convert to seconds
        print(f"Oven {self.OvenID}: Timer set to {minutes} minutes")
        return self.BakingTime  # Returns int as per diagram

    # Additional methods for functionality
    def startBaking(self):
        if self.OvenAvailable and self.BakingTemperature > 0 and self.BakingTime > 0:
            self.OvenAvailable = False
            self.isBaking = True
            self.startTime = time.time()
            print(f"Oven {self.OvenID}: Started baking at {self.BakingTemperature}°C for {self.BakingTime} minutes")
            return True
        return False

    def update(self):
        if self.isBaking and self.startTime > 0:
            elapsed = time.time() - self.startTime
            remaining = self.maxBakingTime - elapsed

            if remaining <= 0:
                self.finishBaking()
                return "Done"
            elif remaining <= 60:  # 1 minute left
                return "Almost Done"
            else:
                return "Baking"
        return "Not Baking"

    def finishBaking(self):
        self.OvenAvailable = True
        self.isBaking = False
        self.BakingTemperature = 0
        self.BakingTime = 0
        self.startTime = 0
        print(f"Oven {self.OvenID}: Baking completed")

    def getStatus(self):
        if self.OvenAvailable:
            return "Available"
        elif self.isBaking:
            elapsed = time.time() - self.startTime
            if elapsed >= self.maxBakingTime:
                return "Done"
            else:
                return f"Baking ({int(self.maxBakingTime - elapsed)}s remaining)"
        else:
            return "Not Available"

    # Method to check if something is currently baking in the oven
    def IsBaking(self, InOven):
        return InOven and self.isBaking