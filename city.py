import pygame
import random
from pygame.locals import *

screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

class city:
    def __init__(self,):
        self.image_city = pygame.image.load('city_map.jpg').convert_alpha()
        self.x_city = 0
        self.y_city = 0
        city_Width = SCREEN_WIDTH
        city_Height = SCREEN_HEIGHT
        self.surface_city = pygame.transform.scale(self.image_city, (city_Width, city_Height))
        self.rect_city = self.surface_city.get_rect(topleft=(self.x_city, self.y_city))

        self.image_house = pygame.image.load('house_icon.png').convert_alpha()
        self.x_house = random.randint(25, SCREEN_WIDTH - 25)
        self.y_house = random.randint(25, SCREEN_HEIGHT - 25)
        width_house = 50
        height_house = 50
        self.surface_house = pygame.transform.scale(self.image_house, (width_house, height_house))
        self.rect_house = self.surface_city.get_rect(center = (self.x_house, self.y_house))

        self.image_restaurant_icon = pygame.image.load('italiën_restaurant.png').convert_alpha()# image of restaurant icon
        self.width_icon = 50 # not actual width and height#######################################################################
        self.height_icon = 50
        self.x_restaurant = 400 #position restaurant
        self.y_restaurant = 400
        self.surface_restaurant = pygame.transform.scale(self.image_restaurant_icon, (self.width_icon, self.height_icon))
        self.rect_restaurant_icon = self.image_icon.get_place(center = (self.x_restaurant, self.y_restaurant))
        


    def show_city_image(self):
        return screen.blit(self.surface_city, self.rect_city)
    
    def show_house_icon(self):
        return screen.blit(self.image_house, self.rect_house)
    
    def show_restaurant_icon(self):
        return screen.blit(self.image_restaurant_icon, self.rect_restaurant_icon)

    def open_restaurant_icon(self, mousepoint):
        return self.rect.collidepoint(mousepoint)
    
    
    
    

    

    
    
    

        
