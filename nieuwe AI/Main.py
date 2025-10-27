import pygame
import time
import random
import sys
import math
from City_AI import City, houseCoords
from Customer_AI import Customer
from DeliveryDrone_AI import DeliveryDrone
from ItalianRestaurant_AI import ItalianRestaurant
from Chef_AI import Chef
from Oven_AI import Oven
from Pan_AI import Pan

pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Automated Restaurant Delivery Simulation")
font_large = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 18)
clock = pygame.time.Clock()

class AutomatedRestaurantSystem:
    def __init__(self, screen):
        self.screen = screen
        self.is_running = True
        self.current_time = time.time()
        self.last_order_time = self.current_time
        self.order_interval = 8 # seconds between new automated orders
        self.orders_processed = 0
        self.restaurant = None
        self.drone = None
        self.customers = []
        
        # FIX: Initialize the missing attribute
        self.active_customer_orders = {}  # {order_id: Customer object} 
        self.customer_map = {} # {customer_id: Customer object}

        self.setup_system()

    def setup_system(self):
        """Initializes city, restaurant, chefs, and customers."""
        
        # 1. City and Restaurant Setup
        self.city = City("NeoCity", 500000, 100)
        
        # Restaurant position for the map icon and drone home
        restaurant_pos = (500, 300) # Centrally located
        self.restaurant_pos = restaurant_pos
        
        # Pass self reference to the restaurant for callback on order completion
        self.restaurant = ItalianRestaurant("Papa Gemini's", "123 Main St", system_reference=self) 
        self.restaurant.open_for_business()
        self.city.add_restaurant(self.restaurant, restaurant_pos)

        # 2. Equipment and Staff Setup (2 Chefs, 2 Ovens, 2 Pans, 1 Drone)
        ovens = [Oven(self.screen), Oven(self.screen)]
        pans = [Pan(self.screen), Pan(self.screen)]
        chef1 = Chef(0, 0, ovens, pans)
        chef2 = Chef(0, 0, ovens, pans)
        chef1.Name = "Chef Mario"
        chef2.Name = "Chef Luigi"
        self.restaurant.add_chef(chef1)
        self.restaurant.add_chef(chef2)
        for oven in ovens:
            self.restaurant.add_oven(oven)
        for pan in pans:
            self.restaurant.add_pan(pan)
        
        # 3. Delivery Drone Setup
        self.drone = DeliveryDrone(drone_id=1, home_pos=restaurant_pos)
        self.restaurant.add_delivery_driver(self.drone)

        # 4. Customer Setup
        customer_id_counter = 1
        for i, (x, y) in enumerate(self.city.houseCoords):
            customer_id = f"CUST{customer_id_counter}"
            customer = Customer(customer_id, f"House {i+1}", x, y)
            self.customers.append(customer)
            self.customer_map[customer_id] = customer
            customer_id_counter += 1
            
        print(f"System Setup Complete: {len(self.customers)} Customers, {len(self.restaurant.Chefs)} Chefs, 1 Restaurant.")


    def _generate_and_place_order(self):
        """Generates a new order and sends it to the restaurant."""
        customer = random.choice(self.customers)
        order_data = customer.GenerateOrder()
        order_id = order_data['order_id']

        # 1. Track the order
        self.active_customer_orders[order_id] = customer 

        # 2. Place the order with the restaurant
        self.restaurant.receive_order(order_data)
        
        print(f"[SYSTEM] New Order {order_id} placed by {customer.CustomerID} at {customer.CustomerAddress}.")


    def handle_completed_order(self, order_data):
        """
        Called by ItalianRestaurant when an order is completed (delivered).
        This updates the system's tracking and notifies the customer.
        """
        order_id = order_data['order_id']
        
        if order_id in self.active_customer_orders:
            customer = self.active_customer_orders.pop(order_id)
            
            # Notify the customer (Sequence Diagram: Customer.ReceiveOrder)
            customer.ReceiveOrder(order_data)
            
            self.orders_processed += 1
            print(f"[SYSTEM] Order {order_id} completed and removed from active list.")
        else:
            print(f"[SYSTEM] Error: Completed order {order_id} not found in active list.")


    def update(self):
        """Main update loop for the simulation logic."""
        self.current_time = time.time()
        
        # 1. Automated Order Generation
        if self.current_time - self.last_order_time >= self.order_interval:
            self._generate_and_place_order()
            self.last_order_time = self.current_time
            
        # 2. Update Restaurant, Equipment, and Drone
        self.restaurant.update()

    def draw(self):
        """Draw all simulation elements on the screen."""
        self.screen.fill((255, 255, 255)) # White background

        # 1. Draw City Map and Customer Houses
        self.city.show_city_map(self.screen)
        self.city.show_restaurant_icon(self.screen, [self.restaurant_pos]) 
        self.city.draw_customer_houses(self.screen)
        
        # 2. Draw Drone
        drone_color = (100, 100, 255) # Blue
        drone_radius = 8
        
        if self.drone and hasattr(self.drone, 'x') and hasattr(self.drone, 'y'):
            drone_x, drone_y = int(self.drone.x), int(self.drone.y)
            
            # Draw the drone circle
            pygame.draw.circle(self.screen, drone_color, (drone_x, drone_y), drone_radius, 0)
            
            # Draw drone status text near the restaurant
            drone_status_text = f"Drone: {self.drone.Status}"
            drone_text_surface = font_small.render(drone_status_text, True, (0, 0, 0))
            self.screen.blit(drone_text_surface, (self.restaurant_pos[0] + 50, self.restaurant_pos[1] - 40))

        # 3. Draw Simulation Status Info
        status_text = f"Orders Processed: {self.orders_processed}"
        text_surface = font_large.render(status_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (10, 10))
        
        # Draw Queue Status (Actual count)
        queue_text = f"Orders In Queue: {len(self.restaurant.Orders)}"
        queue_surface = font_medium.render(queue_text, True, (0, 0, 0))
        self.screen.blit(queue_surface, (10, 50))

        # Draw Active Orders Count
        active_text = f"Active Orders: {len(self.active_customer_orders)}"
        active_surface = font_medium.render(active_text, True, (0, 0, 0))
        self.screen.blit(active_surface, (10, 80))

        # Draw Restaurant State
        state_text = f"Restaurant State: {self.restaurant.state.value}"
        state_surface = font_medium.render(state_text, True, (0, 0, 0))
        self.screen.blit(state_surface, (10, 110))

        pygame.display.flip()

    def run_simulation(self):
        """The main simulation loop."""
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

            self.update()
            self.draw()
            clock.tick(30) # Maintain 30 FPS

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    try:
        game = AutomatedRestaurantSystem(screen)
        game.run_simulation()
    except Exception as e:
        print(f"An error occurred during simulation: {e}")
        pygame.quit()
        sys.exit()
