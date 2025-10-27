import pygame
import time
import random
import sys
import math
import tkinter as tk # Needed for TclError exception handling
from City_AI import City, houseCoords, RESTAURANT_POSITIONS 
from Customer_AI import Customer
from DeliveryDrone_AI import DeliveryDrone
from ItalianRestaurant_AI import ItalianRestaurant
from Chef_AI import Chef
from Oven_AI import Oven
from Pan_AI import Pan
from UI_AI import ManualOrderUI, OrderStatusUI, SystemMode, TkinterThread 

pygame.init()
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
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
        self.order_interval = 5
        self.orders_processed = 0
        self.restaurant_data = []
        self.restaurants = [] # Now a list
        self.drones = [] # Now a list of all drones
        self.restaurant_positions = RESTAURANT_POSITIONS # Get positions from City_AI
        # --------------------------------------
        self.customers = []
        self.active_customer_orders = {}
        self.customer_map = {}
        self.city = None 

        self.mode = SystemMode.SIMULATION
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
        """Initializes city, restaurants, chefs, and customers."""
        
        # 1. City Setup
        self.city = City("NeoCity", 500000, 100) 
        
        # 2. Multiple Restaurant/Equipment/Staff Setup
        for i, restaurant_pos in enumerate(self.restaurant_positions):
            restaurant_name = f"Papa Gemini's R{i+1}"
            restaurant = ItalianRestaurant(restaurant_name, f"Restaurant Address {i+1}", system_reference=self) 
            self.restaurants.append(restaurant)
            restaurant.open_for_business()
            self.city.add_restaurant(restaurant, restaurant_pos) 

            # Equipment and Staff Setup (2 Chefs, 2 Ovens, 2 Pans per restaurant)
            ovens = [Oven(self.screen), Oven(self.screen)]
            pans = [Pan(self.screen), Pan(self.screen)]
            chef1 = Chef(0, 0, ovens, pans)
            chef2 = Chef(0, 0, ovens, pans)
            chef1.Name = f"Chef Mario {i+1}"
            chef2.Name = f"Chef Luigi {i+1}"
            restaurant.add_chef(chef1)
            restaurant.add_chef(chef2)
            for oven in ovens:
                restaurant.add_oven(oven) 
            for pan in pans:
                restaurant.add_pan(pan)
            
            # Delivery Drone Setup (1 Drone per restaurant)
            drone = DeliveryDrone(drone_id=i+1, home_pos=restaurant_pos)
            self.drones.append(drone)
            restaurant.add_delivery_driver(drone) # Drone is associated with its home restaurant

        # 3. Customer Setup (Same as before)
        customer_id_counter = 1
        for i, (x, y) in enumerate(self.city.houseCoords):
            customer_id = f"CUST{customer_id_counter}"
            customer = Customer(customer_id, f"House {i+1}", x, y)
            self.customers.append(customer)
            self.customer_map[customer_id] = customer
            customer_id_counter += 1
            
        print(f"System Setup Complete: {len(self.customers)} Customers, {len(self.restaurants)} Restaurants.")

    def _find_closest_restaurant(self, customer_coords):
        """Calculates and returns the closest restaurant object and its position."""
        min_distance = float('inf')
        closest_restaurant = None
        closest_pos = None
        
        cust_x, cust_y = customer_coords
        
        for restaurant in self.restaurants:
            # Use the city to get the restaurant's position
            rest_pos = self.city.get_restaurant_position(restaurant)
            if not rest_pos: continue
            
            distance = math.hypot(cust_x - rest_pos[0], cust_y - rest_pos[1])
            
            if distance < min_distance:
                min_distance = distance
                closest_restaurant = restaurant
                closest_pos = rest_pos
                
        return closest_restaurant, closest_pos

    # --- MODIFIED HELPER: Gathers data for the default ALL_ACTIVE view ---
    def _gather_all_active_orders(self):
        """Gathers all currently active/queued orders from all restaurants for the default view."""
        all_active_orders = []
        
        for rest in self.restaurants:
            # Check the order being currently processed
            if rest.current_order:
                order_id = rest.current_order['order_id']
                # Calculate items ready (from items_to_package - simplified for main view)
                ready_count = sum(1 for item in rest.items_to_package.get(order_id, {}).values() if item['ready'])
                
                all_active_orders.append({
                    'restaurant_name': rest.Name,
                    'order_id': order_id,
                    'state': rest.state.value, # PREPARING, COOKING, BAKING, PACKAGING, etc.
                    'items_total': len(rest.current_order['items']),
                    'items_ready': ready_count
                })

            # Check orders waiting in the queue
            for order in rest.Orders:
                all_active_orders.append({
                    'restaurant_name': rest.Name,
                    'order_id': order['order_id'],
                    'state': 'QUEUED',
                    'items_total': len(order['items']),
                    'items_ready': 0
                })
                
            # Check order out for delivery
            if rest.delivery_in_progress_order:
                 all_active_orders.append({
                    'restaurant_name': rest.Name,
                    'order_id': rest.delivery_in_progress_order['order_id'],
                    'state': 'DELIVERING',
                    'items_total': len(rest.delivery_in_progress_order['items']),
                    'items_ready': len(rest.delivery_in_progress_order['items'])
                })
                
        return all_active_orders
    # ----------------------------------------------------------------

    def _generate_and_place_order(self):
        if self.mode != SystemMode.SIMULATION:
            return

        current_time = time.time()
        if current_time - self.last_order_time >= self.order_interval:
            self.last_order_time = current_time
            customer = random.choice(self.customers)
            customer_coords = (customer.x, customer.y)
            
            # --- ROUTING LOGIC ---
            target_restaurant, _ = self._find_closest_restaurant(customer_coords)
            if not target_restaurant:
                print("[SYSTEM] ERROR: Could not find any restaurant.")
                return
            # ---------------------
            
            order_data = customer.GenerateOrder()
            order_id = order_data['order_id']

            self.active_customer_orders[order_id] = customer 
            target_restaurant.receive_order(order_data)
            
            print(f"[SYSTEM] New Automated Order {order_id} placed by {customer.CustomerID}. Routed to {target_restaurant.Name}.")


    def handle_completed_order(self, order_data):
        order_id = order_data['order_id']
        
        # The key logic here is that it removes the order from the *System's* list
        if order_id in self.active_customer_orders:
            customer = self.active_customer_orders.pop(order_id)
            customer.ReceiveOrder(order_data)
            self.orders_processed += 1
            print(f"[SYSTEM] Order {order_id} completed and removed from active list.")
            
            # Clean up temporary manual customer if it exists
            if order_data['customer_id'] == self.manual_ui.customer_id:
                if self.manual_ui.customer_id in self.customer_map:
                    del self.customer_map[self.manual_ui.customer_id]
                print(f"[System] Temporary manual customer (ID {self.manual_ui.customer_id}) cleaned up.")
                

    def submit_manual_order(self, order_data):
        
        # 1. Create Mock Customer and get coords
        mock_customer = Customer(self.manual_ui.customer_id, self.manual_ui.customer_address, *self.manual_ui.customer_address)
        customer_coords = (mock_customer.x, mock_customer.y)
        
        # 2. ROUTING LOGIC
        target_restaurant, _ = self._find_closest_restaurant(customer_coords)
        if not target_restaurant:
            print("[SYSTEM] ERROR: Could not find any restaurant for manual order.")
            return
            
        # 3. Place Order
        self.customer_map[self.manual_ui.customer_id] = mock_customer
        self.active_customer_orders[order_data['order_id']] = mock_customer
        target_restaurant.receive_order(order_data)
        print(f"[SYSTEM] Manual Order {order_data['order_id']} placed. Routed to {target_restaurant.Name}.")
            
    def switch_mode(self, new_mode: SystemMode):
        if self.mode == new_mode: return

        self.mode = new_mode
        print(f"[System] Switched to mode: {self.mode.name}")
        
        # Use the thread-safe scheduler for UI changes
        is_manual = (new_mode == SystemMode.MANUAL_ORDERING)
        self.tkinter_thread.schedule_manual_ui_toggle(is_manual)

    # --- NEW METHOD: Used by UI back button to force return to default view ---
    def schedule_status_update_all(self):
        """Helper for the UI back button to force return to the default ALL_ACTIVE view."""
        # This re-gathers the standard view data and forces the UI thread to switch modes
        status_data = self._gather_all_active_orders()
        self.tkinter_thread.schedule_status_update(status_data, force_all_active=True) 
    # --------------------------------------------------------------------------

    # --- NEW METHOD: Triggers single restaurant detail view ---
    def show_restaurant_status(self, restaurant):
        """Fetches all order data for the clicked restaurant and sends it to the UI."""
        
        # 1. Fetch all order data (active + completed history)
        all_order_data = restaurant.get_all_order_data()
        
        # 2. Get restaurant name
        rest_name = restaurant.Name
        
        # 3. Schedule the custom view on the Tkinter thread
        self.tkinter_thread.schedule_show_restaurant_details(rest_name, all_order_data)
    # ---------------------------------------------------------

    def update(self):
        """Main update loop for the simulation logic."""
            
        # 1. Update the Order Status UI (Scheduled safely on the other thread)
        # Combine status from all restaurants for the default ALL_ACTIVE view
        all_active_orders = self._gather_all_active_orders() 
        self.tkinter_thread.schedule_status_update(all_active_orders) 
            
        # 2. Simulation Logic
        if self.mode == SystemMode.SIMULATION:
            self._generate_and_place_order()
            # Update all restaurants
            for rest in self.restaurants:
                rest.update() 


    def draw(self):
        """Draw all simulation elements on the screen."""
        self.screen.fill((255, 255, 255)) 

        # --- Draw based on Mode ---
        if self.mode == SystemMode.SIMULATION:
            # Draw City Map and Customer Houses
            self.city.show_city_map(self.screen)
            
            # Prepare restaurant statuses and draw icons/status
            restaurant_statuses = [f"{rest.Name}: {rest.state.value}" for rest in self.restaurants] # Name is now included here
            global font_medium # Reference the global font object
            self.city.show_restaurant_icon(self.screen, font_medium, restaurant_statuses) 
            
            global font_small # Need to reference the global font object
            self.city.draw_customer_houses(self.screen, font_small)
            
            # Draw Drones (Loop through all drones)
            drone_color = (100, 100, 255) 
            drone_radius = 8
            for i, drone in enumerate(self.drones):
                if hasattr(drone, 'x') and hasattr(drone, 'y'):
                    drone_x, drone_y = int(drone.x), int(drone.y)
                    # Draw Drone circle
                    pygame.draw.circle(self.screen, drone_color, (drone_x, drone_y), drone_radius, 0)
                    # Draw Drone Status
                    drone_status_text = f"Drone {drone.DroneID}: {drone.Status}"
                    drone_text_surface = font_small.render(drone_status_text, True, (0, 0, 0))
                    # Position the text near its home restaurant
                    rest_pos = self.restaurant_positions[i]
                    # Adjusted Y position to avoid conflict with the new on-map restaurant status text
                    self.screen.blit(drone_text_surface, (rest_pos[0] + 30, rest_pos[1] - 40))

            # Calculate Combined Status Info
            orders_in_queue = sum(len(rest.Orders) for rest in self.restaurants)

            # Draw Simulation Status Info
            status_text = f"Orders Processed: {self.orders_processed}"
            text_surface = font_large.render(status_text, True, (0, 0, 0))
            self.screen.blit(text_surface, (10, 10))
            queue_text = f"Orders In Queue (Total): {orders_in_queue}"
            queue_surface = font_medium.render(queue_text, True, (0, 0, 0))
            self.screen.blit(queue_surface, (10, 50))
            active_text = f"Active Orders (System): {len(self.active_customer_orders)}"
            active_surface = font_medium.render(active_text, True, (0, 0, 0))
            self.screen.blit(active_surface, (10, 80))
            
            # Draw Global Mode Status
            mode_text = f"Mode: {self.mode.name} (Click Rest. to see details)" # Added instruction
            mode_surface = font_medium.render(mode_text, True, (0, 0, 0))
            self.screen.blit(mode_surface, (10, 120))


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
                        
                    # Check for Restaurant Icon Click
                    clicked_restaurant = self.city.open_restaurant_icon(mouse_pos)
                    if clicked_restaurant:
                        # Only show details if in SIMULATION mode
                        if self.mode == SystemMode.SIMULATION:
                            self.show_restaurant_status(clicked_restaurant)
                        else:
                            print("[System] Cannot inspect restaurant in Manual Ordering mode.")


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