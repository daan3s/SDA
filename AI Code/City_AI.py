# City_AI.py
import pygame
import random
import math

pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
houseCoords = [(400, 510), (200, 420), (620, 465), (810, 385), (690, 235), (300, 240), (65, 90), (450, 70)]


class City:
    def __init__(self, name, population, size):
        # Attributes from class diagram
        self.Name = name  # str
        self.Population = population  # int
        self.Size = size  # int
        self.Restaurant = []  # list of ItalianRestaurant objects
        self.MinimumDistance = 100  # int - minimum distance between restaurants

        # Visual properties with error handling
        try:
            self.image_city = pygame.image.load('city_map.jpg')
            self.image_city = pygame.transform.scale(self.image_city, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("City map image not found, creating blank background")
            self.image_city = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image_city.fill((200, 200, 200))  # Gray background

        self.maxWidth = 0
        self.maxHeight = 0

        try:
            self.image_house = pygame.image.load('house_icon.png')
            self.image_house = pygame.transform.scale(self.image_house, (50, 50))
        except:
            print("House icon not found, creating placeholder")
            self.image_house = pygame.Surface((50, 50))
            self.image_house.fill((0, 0, 255))  # Blue square

        i = random.randint(0, len(houseCoords) - 1)
        width_house = houseCoords[i][0]
        height_house = houseCoords[i][1]
        self.place_house = (width_house, height_house)

        try:
            self.image_icon = pygame.image.load('italian_restaurant.png')
            self.image_icon = pygame.transform.scale(self.image_icon, (50, 50))
        except:
            print("Restaurant icon not found, creating placeholder")
            self.image_icon = pygame.Surface((50, 50))
            self.image_icon.fill((255, 0, 0))  # Red square

        self.width_icon = 50
        self.height_icon = 50
        self.image_size = (self.width_icon, self.height_icon)

        # Restaurant positions for visual representation
        self.restaurant_positions = []

    # Operations from class diagram
    def AddRestaurant(self, restaurant):
        """Add a restaurant to the city - matches diagram operation"""
        # Check if location is available (minimum distance from other restaurants)
        if not self.IsLocationAvailable(restaurant):
            print(f"Cannot add restaurant {restaurant.Name} - location too close to existing restaurants")
            return False

        self.Restaurant.append(restaurant)

        # Generate a random position for the new restaurant
        pos = self.generate_restaurant_position()
        self.restaurant_positions.append(pos)

        print(f"Added restaurant: {restaurant.Name} at position {pos}")
        return True

    def AssignOrderToRestaurant(self, order):
        """Assign order to the most appropriate restaurant - matches diagram operation"""
        if not self.Restaurant:
            print("No restaurants available in the city")
            return None

        # Simple strategy: assign to first available restaurant
        for restaurant in self.Restaurant:
            if hasattr(restaurant, 'is_open') and restaurant.is_open:
                print(f"Order assigned to: {restaurant.Name}")
                return restaurant

        print("No open restaurants available")
        return None

    def IsLocationAvailable(self, new_restaurant, position=None):
        """Check if a location is available for a new restaurant - matches diagram operation"""
        if not self.Restaurant:
            return True

        # If no specific position provided, assume it's available for now
        if position is None:
            return True

        # Check distance from existing restaurants
        for i, existing_pos in enumerate(self.restaurant_positions):
            distance = self.CalculateDistance(position, existing_pos)
            if distance < self.MinimumDistance:
                print(f"Location too close to {self.Restaurant[i].Name} (distance: {distance})")
                return False

        return True

    def CalculateDistance(self, pos1, pos2):
        """Calculate distance between two points - matches diagram operation"""
        x1, y1 = pos1
        x2, y2 = pos2
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return int(distance)  # Return int as per diagram

    # Helper methods for restaurant positioning
    def generate_restaurant_position(self):
        """Generate a random position for a restaurant"""
        max_attempts = 50
        for attempt in range(max_attempts):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            position = (x, y)

            if self.IsLocationAvailable(None, position):
                return position

        # If no good position found, return a default one
        return (SCREEN_WIDTH - 100, 100)

    # Existing visual methods
    def show_city_image(self, screen):
        screen.blit(self.image_city, (self.maxWidth, self.maxHeight))

    def show_house_icon(self, screen):
        screen.blit(self.image_house, self.place_house)

    def location_restaurant_icon(self):
        return (SCREEN_WIDTH - 50, 50)

    def show_restaurant_icon(self, screen, restPos=None):
        """Show restaurant icons on the map"""
        if restPos is None:
            restPos = self.restaurant_positions

        for i in range(len(restPos)):
            xi = restPos[i][0]
            yi = restPos[i][1]
            place_icon = (xi, yi)
            screen.blit(self.image_icon, place_icon)

    def open_restaurant_icon(self, mousepoint):
        """Check if mouse is over a restaurant icon"""
        for i, pos in enumerate(self.restaurant_positions):
            rect = pygame.Rect(pos[0], pos[1], self.width_icon, self.height_icon)
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
        """Update the open/closed status of all restaurants"""
        for restaurant in self.Restaurant:
            if hasattr(restaurant, 'Check_opening_hours'):
                restaurant.Check_opening_hours()