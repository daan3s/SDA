import pygame
from pygame.locals import *
import random

pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
houseCoords = [(400,510),(200,420),(620,465),(810,385),(690,235),(300,240),(65,90),(450,70)]

class city:
    def __init__(self):
        self.image_city = pygame.image.load('images\city_map.jpg')
        self.maxWidth = 0
        self.maxHeight = 0

        self.image_house = pygame.image.load('images\house_icon.png')
        pygame.transform.smoothscale_by(self.image_house,(50,50))
        i = random.randint(0,len(houseCoords)-1)
        width_house = houseCoords[i][0]
        height_house = houseCoords[i][1]
        self.place_house = (width_house, height_house)

        self.image_icon = pygame.image.load('images\italiën_restaurant.png')# image of restaurant icon
        self.width_icon = 50 # not actual width and height#######################################################################
        self.height_icon = 50
        self.image_size = (self.width_icon, self.height_icon)   

    def show_city_image(self):
        screen.blit(self.image_city, (self.maxWidth,self.maxHeight))
    
    def show_house_icon(self):
        screen.blit(self.image_house, self.place_house)
    
    def location_restaurant_icon():
        return (SCREEN_WIDTH - 50, 50)

    def show_restaurant_icon(self, restPos):
        for i in range(0,len(restPos)): #get restaurant coords from list
            self.xi = restPos[i][0]
            self.yi = restPos[i][1]
            self.place_icon = (self.xi, self.yi)
            screen.blit(self.image_icon, self.place_icon)

    def open_restaurant_icon(self, mousepoint):
        return self.rect.collidepoint(mousepoint)
    
    
    

        
