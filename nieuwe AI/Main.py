import pygame
import time
import random
import sys
import math
import tkinter as tk # Needed for TclError exception handling
from City_AI import City, houseCoords
from Customer_AI import Customer
from DeliveryDrone_AI import DeliveryDrone
from ItalianRestaurant_AI import ItalianRestaurant
from Chef_AI import Chef
from Oven_AI import Oven
from Pan_AI import Pan
from UI_AI import ManualOrderUI, OrderStatusUI, SystemMode, TkinterThread 
# ----------------------------------

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
        self.order_interval = 8
        self.orders_processed = 0
        self.restaurant = None
        self.drone = None
        self.customers = []
        self.active_customer_orders = {}
        self.customer_map = {}
        self.city = None 

        # --- Threading Setup: Core Fix for GIL Error ---
        self.mode = SystemMode.SIMULATION
        # Create and start the Tkinter thread
        self.tkinter_thread = TkinterThread(self)
        self.tkinter_thread.start()
        
        # Wait briefly for the thread to initialize the UI objects
        while not self.tkinter_thread.manual_ui or not self.tkinter_thread.status_ui:
            time.sleep(0.05) 
            
        # References to the UI objects running in the separate thread
        self.manual_ui = self.tkinter_thread.manual_ui
        self.status_ui = self.tkinter_thread.status_ui
        # -----------------------------------------------

        self.setup_system()
        
    def setup_system(self):
        """Initializes city, restaurant, chefs, and customers."""
        
        # 1. City and Restaurant Setup
        self.city = City("NeoCity", 500000, 100) 
        restaurant_pos = (500, 300) 
        self.restaurant_pos = restaurant_pos
        self.restaurant = ItalianRestaurant("Papa Gemini's", "123 Main St", system_reference=self) 
        self.restaurant.open_for_business()
        self.city.add_restaurant(self.restaurant, restaurant_pos) 

        # 2. Equipment and Staff Setup
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
        if self.mode != SystemMode.SIMULATION:
            return

        current_time = time.time()
        if current_time - self.last_order_time >= self.order_interval:
            self.last_order_time = current_time
            customer = random.choice(self.customers)
            order_data = customer.GenerateOrder()
            order_id = order_data['order_id']

            self.active_customer_orders[order_id] = customer 
            self.restaurant.receive_order(order_data)
            
            print(f"[SYSTEM] New Automated Order {order_id} placed by {customer.CustomerID}.")


    def handle_completed_order(self, order_data):
        order_id = order_data['order_id']
        
        if order_id in self.active_customer_orders:
            customer = self.active_customer_orders.pop(order_id)
            customer.ReceiveOrder(order_data)
            self.orders_processed += 1
            print(f"[SYSTEM] Order {order_id} completed and removed from active list.")
            
            if order_data['customer_id'] == self.manual_ui.customer_id:
                if self.manual_ui.customer_id in self.customer_map:
                    del self.customer_map[self.manual_ui.customer_id]
                print(f"[System] Temporary manual customer (ID {self.manual_ui.customer_id}) cleaned up.")
                

    def submit_manual_order(self, order_data):
        mock_customer = Customer(self.manual_ui.customer_id, self.manual_ui.customer_address, *self.manual_ui.customer_address)
        self.customer_map[self.manual_ui.customer_id] = mock_customer
        self.active_customer_orders[order_data['order_id']] = mock_customer
        self.restaurant.receive_order(order_data)
            
    def switch_mode(self, new_mode: SystemMode):
        if self.mode == new_mode: return

        self.mode = new_mode
        print(f"[System] Switched to mode: {self.mode.name}")
        
        # Use the thread-safe scheduler for UI changes
        is_manual = (new_mode == SystemMode.MANUAL_ORDERING)
        self.tkinter_thread.schedule_manual_ui_toggle(is_manual)


    def update(self):
        """Main update loop for the simulation logic."""
            
        # 1. Update the Order Status UI (Scheduled safely on the other thread)
        order_statuses = self.restaurant.get_active_orders_status()
        self.tkinter_thread.schedule_status_update(order_statuses)
            
        # 2. Simulation Logic
        if self.mode == SystemMode.SIMULATION:
            self._generate_and_place_order()
            self.restaurant.update() 


    def draw(self):
        """Draw all simulation elements on the screen."""
        self.screen.fill((255, 255, 255)) 

        # --- Draw based on Mode ---
        if self.mode == SystemMode.SIMULATION:
            # Draw City Map and Customer Houses
            self.city.show_city_map(self.screen)
            self.city.show_restaurant_icon(self.screen, [self.restaurant_pos]) 
            self.city.draw_customer_houses(self.screen)
            
            # Draw Drone
            drone_color = (100, 100, 255) 
            drone_radius = 8
            if self.drone and hasattr(self.drone, 'x') and hasattr(self.drone, 'y'):
                drone_x, drone_y = int(self.drone.x), int(self.drone.y)
                pygame.draw.circle(self.screen, drone_color, (drone_x, drone_y), drone_radius, 0)
                drone_status_text = f"Drone: {self.drone.Status}"
                drone_text_surface = font_small.render(drone_status_text, True, (0, 0, 0))
                self.screen.blit(drone_text_surface, (self.restaurant_pos[0] + 50, self.restaurant_pos[1] - 40))

            # Draw Simulation Status Info
            status_text = f"Orders Processed: {self.orders_processed}"
            text_surface = font_large.render(status_text, True, (0, 0, 0))
            self.screen.blit(text_surface, (10, 10))
            queue_text = f"Orders In Queue: {len(self.restaurant.Orders)}"
            queue_surface = font_medium.render(queue_text, True, (0, 0, 0))
            self.screen.blit(queue_surface, (10, 50))
            active_text = f"Active Orders: {len(self.active_customer_orders)}"
            active_surface = font_medium.render(active_text, True, (0, 0, 0))
            self.screen.blit(active_surface, (10, 80))
            state_text = f"Restaurant State: {self.restaurant.state.value}"
            state_surface = font_medium.render(state_text, True, (0, 0, 0))
            self.screen.blit(state_surface, (10, 110))

        elif self.mode == SystemMode.MANUAL_ORDERING:
            # Dimmed screen for manual mode (since Tkinter is an external window)
            self.screen.fill((50, 50, 50))
            status_text = "MODE: Manual Ordering (Simulation Paused)"
            status_surface = font_large.render(status_text, True, (255, 255, 255))
            self.screen.blit(status_surface, (SCREEN_WIDTH // 2 - status_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            info_text = "Use the 'Manual Food Ordering' window to place orders."
            info_surface = font_medium.render(info_text, True, (255, 255, 255))
            self.screen.blit(info_surface, (SCREEN_WIDTH // 2 - info_surface.get_width() // 2, SCREEN_HEIGHT // 2))

        # --- Mode Switch Button (Always Visible) ---
        button_rect = pygame.Rect(SCREEN_WIDTH - 220, 10, 210, 40)
        
        if self.mode == SystemMode.SIMULATION:
            button_color = (255, 99, 71)
            button_text = "Switch to Manual Mode"
        else:
            button_color = (60, 179, 113)
            button_text = "Return to Simulation"

        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        text_surface = font_medium.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()

    def run_simulation(self):
        """The main simulation loop."""
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                
                # Handle Button Click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    button_rect = pygame.Rect(SCREEN_WIDTH - 220, 10, 210, 40)
                    
                    if button_rect.collidepoint(mouse_pos):
                        target_mode = SystemMode.MANUAL_ORDERING if self.mode == SystemMode.SIMULATION else SystemMode.SIMULATION
                        self.switch_mode(target_mode)

            self.update()
            self.draw()
            clock.tick(30) 

        pygame.quit()
        # Clean up the Tkinter thread
        self.tkinter_thread.stop()
        sys.exit()

if __name__ == '__main__':
    try:
        game = AutomatedRestaurantSystem(screen)
        game.run_simulation()
    except Exception as e:
        print(f"An error occurred during simulation: {e}")
        pygame.quit()
        sys.exit()