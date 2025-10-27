# City_AI.py
import pygame
import random
import math

pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Global house coordinates for customers
houseCoords = [
    (400, 510), (200, 420), (620, 465), (810, 385), 
    (690, 235), (300, 240), (65, 90), (450, 70), 
    (750, 550), (100, 500)
]
# House visualization parameters
HOUSE_RADIUS = 5
HOUSE_COLOR = (255, 0, 0) # Red


class City:
    def __init__(self, name, population, size):
        # Attributes from class diagram
        self.Name = name  # str
        self.Population = population  # int
        self.Size = size  # int
        self.Restaurant = []  # list of ItalianRestaurant objects
        self.restaurant_positions = [] # list of (x, y) tuples for restaurants
        self.MinimumDistance = 100  # int - minimum distance between restaurants
        self.houseCoords = houseCoords # Make houseCoords accessible via the instance

        # Visual properties with error handling
        try:
            # Note: Assuming 'city_map.jpg' is available for the original user context.
            self.image_city = pygame.image.load('city_map.jpg')
            self.image_city = pygame.transform.scale(self.image_city, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            print("City map image not found, creating blank background")
            self.image_city = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image_city.fill((200, 200, 200))  # Gray background
        
        # Icon for restaurants (a simple circle)
        self.width_icon, self.height_icon = 30, 30
        try:
            self.image_icon = pygame.Surface((self.width_icon, self.height_icon))
            self.image_icon.fill((0, 255, 0)) # Green square for restaurant
        except:
            self.image_icon = pygame.Surface((self.width_icon, self.height_icon))
            self.image_icon.fill((0, 255, 0))


    def show_city_map(self, screen):
        """Draw the city map background."""
        screen.blit(self.image_city, (0, 0))

    def add_restaurant(self, restaurant, position):
        """Adds a restaurant and its map position."""
        self.Restaurant.append(restaurant)
        self.restaurant_positions.append(position)
        print(f"Added restaurant {restaurant.Name} at {position}")


    def draw_customer_houses(self, screen):
        """Draw customer houses on the map."""
        for x, y in self.houseCoords:
            pygame.draw.circle(screen, HOUSE_COLOR, (x, y), HOUSE_RADIUS, 0)

    def show_restaurant_icon(self, screen, restPos=None):
        """Show restaurant icons on the map"""
        if restPos is None:
            restPos = self.restaurant_positions

        for i in range(len(restPos)):
            xi = restPos[i][0]
            yi = restPos[i][1]
            # Draw a green circle for the restaurant icon
            pygame.draw.circle(screen, (0, 150, 0), (xi, yi), self.width_icon // 2, 0) 
            pygame.draw.circle(screen, (255, 255, 255), (xi, yi), self.width_icon // 3, 0) # White center
            
    # ... (rest of City class methods)
    def open_restaurant_icon(self, mousepoint):
        """Check if mouse is over a restaurant icon"""
        for i, pos in enumerate(self.restaurant_positions):
            # Adjusted rect to check for collision based on circle center
            rect = pygame.Rect(pos[0] - self.width_icon // 2, pos[1] - self.height_icon // 2, self.width_icon, self.height_icon)
            if rect.collidepoint(mousepoint):
                return self.Restaurant[i] if i < len(self.Restaurant) else None
        return None

    # Additional helper methods
    def get_city_info(self):
        """Get comprehensive city information"""
        return {
            "name": self.Name,
            "population": self.Population,
            "size": self.Size,
            "restaurant_count": len(self.Restaurant),
            "open_restaurants": len([r for r in self.Restaurant if hasattr(r, 'is_open') and r.is_open]),
            "minimum_distance": self.MinimumDistance
        }

    def update_restaurant_status(self):
        """Update the open/closed status..."""
        pass
