import pygame

screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

class city:
    def __init__(self, x, y):
        self.image_city = pygame.image.load(image.name).convert_alpha
        maxWidth = SCREEN_WIDTH
        maxHeight = SCREEN_HEIGHT
        self.place_city = self.image.get_place(center = (maxWidth, maxHeight))

        self.image_house = pygame.image.load(image.name).convert_alpha
        width_house = 50
        height_house = 50
        self.place_house = self.image.get_place(center = (width_house, height_house))

        self.image_icon = pygame.image.load(image.name).convert_alpha()# image of restaurant icon
        self.place_icon = self.image_icon.get_place(center = (x, y))
        self.width_icon = 50 # not actual width and height#######################################################################
        self.height_icon = 50
        self.x = x #position restaurant
        self.y = y
        self.image_size = (self.width, self.height)
        self.rect = pygame.Rect(self.x, self.y, self.image_size)


    def show_city_image(self):
        return screen.blit(self.image_city, self.place_city)
    
    def show_house_icon(self):
        return screen.blit(self.image_house, self.place_house)
    
    def location_restaurant_icon():
        return (SCREEN_WIDTH - 50, 50)

    def show_restaurant_icon(self, screen):
        return screen.blit(self.image_icon, self.place_icon)

    def open_restaurant_icon(self, mousepoint):
        return self.rect.collidepoint(mousepoint)
    
    
    

        
