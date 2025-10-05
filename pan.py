import pygame
import random
import time


class pan:
    def __init__(self, window):
        self.panID = random.randint(9900, 9999)
        self.window = window
        self.isAvailable = True
        self.maxBakingTime = 30
        self.currentBakingTIme = 0
        self.isBaking = False
        self.pastaReady = False
        self.startTime = 0



    def startBaking(self):
        if self.isAvailable and not self.isBaking:
            self.isAvailable = False
            self.isBaking = True
            self.pastaReady = False
            self.currentBakingTIme = 0
            self.startTime = time.time()
            print(f"pan {self.panID} : Started baking pasta")
            return True
        return False
    
    def update(self):
        if self.isBaking and not self.pastaReady:
            elapsed = time.time() - self.startTime
            self.currentBakingTime = elapsed 
            
            if elapsed >= self.maxBakingTime:
                self.finishBaking()

    def finshBaking(self):
        self.isBaking = False
        self.pastaReady = True
        print(f"Pan {self.panID}: pasta is ready for delivery" )

    def 
