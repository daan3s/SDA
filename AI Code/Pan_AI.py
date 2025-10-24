import pygame
import random
import time


class Pan:
    def __init__(self, window):
        self.panID = random.randint(9900, 9999)
        self.window = window
        self.panavailable = True  # Matches diagram attribute name
        self.CookingTime = 0  # Matches diagram attribute name
        self.CookingTemperature = 0  # Matches diagram attribute name
        self.maxBakingTime = 30  # Additional for functionality
        self.startTime = 0  # Additional for functionality

    def IsAvailable(self):  # Matches diagram operation name
        return self.panavailable

    def SetTemp(self, temperature):  # Matches diagram operation name
        self.CookingTemperature = temperature
        print(f"Pan {self.panID}: Temperature set to {temperature}°C")
        return self.CookingTemperature  # Returns int as per diagram

    def SetTimer(self, minutes):  # Matches diagram operation name
        self.CookingTime = minutes
        self.maxBakingTime = minutes * 60  # Convert to seconds
        print(f"Pan {self.panID}: Timer set to {minutes} minutes")
        return self.CookingTime  # Returns int as per diagram

    # Additional methods for functionality (not in diagram but needed)
    def startBaking(self):
        if self.panavailable and self.CookingTemperature > 0 and self.CookingTime > 0:
            self.panavailable = False
            self.startTime = time.time()
            print(f"Pan {self.panID}: Started baking at {self.CookingTemperature}°C for {self.CookingTime} minutes")
            return True
        return False

    def update(self):
        if not self.panavailable and self.startTime > 0:
            elapsed = time.time() - self.startTime
            remaining = self.maxBakingTime - elapsed

            if remaining <= 0:
                self.finishBaking()
                return "Done"
            elif remaining <= 60:  # 1 minute left
                return "Almost Done"
            else:
                return "Baking"

    def finishBaking(self):
        self.panavailable = True
        self.CookingTemperature = 0
        self.CookingTime = 0
        self.startTime = 0
        print(f"Pan {self.panID}: Cooking completed")

    def getStatus(self):
        if self.panavailable:
            return "Available"
        elif self.startTime > 0:
            elapsed = time.time() - self.startTime
            if elapsed >= self.maxBakingTime:
                return "Done"
            else:
                return f"Baking ({int(self.maxBakingTime - elapsed)}s remaining)"
        else:
            return "Not Available"