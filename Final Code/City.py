# City.py
import pygame
import random
import math

pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720

# Global house coordinates for customers
houseCoords = [(400,630),(200,420),(620,465),(830,385),(690,245),(300,240),(85,195),(450,75),(1090,552),(1050,140)]

# --- NEW: Defined Restaurant Positions ---
RESTAURANT_POSITIONS = [(870, 548), (200, 560), (570, 190)] 
# ---------------------------------------

# House visualization parameters
HOUSE_ICON_SIZE = (30, 30) 

class City:
    def __init__(self, name, population, size):
        self.Name = name
        self.Population = population
        self.Size = size
        self.Restaurant = []
        self.restaurant_positions = []
        self.MinimumDistance = 100
        self.houseCoords = houseCoords

        # Visual properties
        try:
            self.image_city = pygame.image.load('city_map_new.jpeg')
            self.image_city = pygame.transform.scale(self.image_city, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            print("City map image not found, creating blank background")
            self.image_city = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image_city.fill((200, 200, 200))

        # --- Load Icons ---
        try:
            self.image_house = pygame.image.load('house_icon.png').convert_alpha()
            self.image_house = pygame.transform.scale(self.image_house, HOUSE_ICON_SIZE)
        except pygame.error:
            self.image_house = None
        self.REST_ICON_SIZE = (50, 50)
        self.width_icon, self.height_icon = self.REST_ICON_SIZE
        try:
            self.image_restaurant = pygame.image.load('italiën_restaurant.png').convert_alpha()
            self.image_restaurant = pygame.transform.scale(self.image_restaurant, self.REST_ICON_SIZE)
        except pygame.error:
            self.image_restaurant = None

    def get_restaurant_position(self, restaurant):
        """Returns the map position (x, y) of a given restaurant object."""
        try:
            index = self.Restaurant.index(restaurant)
            return self.restaurant_positions[index]
        except ValueError:
            return None

    def show_city_map(self, screen):
        """Draw the city map background."""
        screen.blit(self.image_city, (0, 0))

    def add_restaurant(self, restaurant, position):
        """Adds a restaurant and its map position."""
        self.Restaurant.append(restaurant)
        self.restaurant_positions.append(position)

    # --- MODIFIED METHOD: Now accepts font object to draw numbers ---
    def draw_customer_houses(self, screen, font_small): 
        """Draw customer houses on the map, using the icon if available, and add numbers."""
        half_w, half_h = HOUSE_ICON_SIZE[0] // 2, HOUSE_ICON_SIZE[1] // 2
        for i, (x, y) in enumerate(self.houseCoords):
            house_num = i + 1
            
            # 1. Draw House Icon
            if self.image_house:
                screen.blit(self.image_house, (x - half_w, y - half_h))
            else:
                HOUSE_COLOR = (255, 0, 0)
                HOUSE_RADIUS = 5
                pygame.draw.circle(screen, HOUSE_COLOR, (x, y), HOUSE_RADIUS, 0)
            
            # 2. Draw House Number (NEW)
            text_surface = font_small.render(str(house_num), True, (0, 0, 0)) # Black text
            # Position the text 10 pixels above the house icon's top edge
            text_rect = text_surface.get_rect(center=(x, y - half_h - 10)) 
            screen.blit(text_surface, text_rect)
    # -------------------------------------------------------------

    # --- MODIFIED: Added restaurant_statuses and font_medium parameters ---
    def show_restaurant_icon(self, screen, font_medium, restaurant_statuses, restPos=None):
        """Show restaurant icons and their status on the map, using the icon if available."""
        if restPos is None:
            restPos = self.restaurant_positions

        half_w, half_h = self.REST_ICON_SIZE[0] // 2, self.REST_ICON_SIZE[1] // 2
        
        for i, (xi, yi) in enumerate(restPos):
            # 1. Draw Icon
            if self.image_restaurant:
                screen.blit(self.image_restaurant, (xi - half_w, yi - half_h))
            else:
                pygame.draw.circle(screen, (0, 150, 0), (xi, yi), self.width_icon // 2, 0) 
                pygame.draw.circle(screen, (255, 255, 255), (xi, yi), self.width_icon // 3, 0)
                
            # 2. Draw Status Text (NEW)
            if i < len(restaurant_statuses):
                status_text = restaurant_statuses[i]
                # Render text (Black text on a small white rectangle for map visibility)
                text_surface = font_medium.render(status_text, True, (0, 0, 0), (255, 255, 255)) 
                
                # Position the text slightly to the right of the icon and centered vertically
                text_x = xi + half_w + 5 
                text_y = yi - (text_surface.get_height() // 2)
                screen.blit(text_surface, (text_x, text_y))
    # --------------------------------------------------------------------

    def open_restaurant_icon(self, mousepoint):
        """Check if mouse is over a restaurant icon"""
        for i, pos in enumerate(self.restaurant_positions):
            rect = pygame.Rect(pos[0] - self.width_icon // 2, pos[1] - self.height_icon // 2, self.width_icon, self.height_icon)
            if rect.collidepoint(mousepoint):
                return self.Restaurant[i] if i < len(self.Restaurant) else None
        return None

    def get_city_info(self):
        """Get comprehensive city information"""
        return {
            "name": self.Name,
            "population": self.Population,
            "size": self.Size,
            "restaurant_count": len(self.Restaurant),
            "minimum_distance": self.MinimumDistance
        }