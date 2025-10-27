import pygame
import time
import random
import sys
import math
import socket
import json
import threading
from City import City, houseCoords, RESTAURANT_POSITIONS
from Customer import Customer
from DeliveryDrone import DeliveryDrone
from ItalianRestaurant import ItalianRestaurant
from Chef import Chef
from Oven import Oven
from Pan import Pan
from UI import TkinterThread  # NEW: Import the threading class for the UI

# Re-initialize pygame and constants
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
        self.restaurants = []
        self.drones = []
        self.restaurant_positions = RESTAURANT_POSITIONS
        self.customers = []
        self.active_customer_orders = {}
        self.customer_map = {}
        self.city = None

        self.listener_port = 5004
        self.next_manual_order_id = 9000
        self.mock_customer_id = "EXT_CUST_NET"

        # ---  UI Thread Setup ---
        self.tkinter_thread = TkinterThread(self)
        self.tkinter_thread.start()
        # Wait briefly for the thread to initialize the UI objects
        while not self.tkinter_thread.status_ui:
            time.sleep(0.05)
        self.status_ui = self.tkinter_thread.status_ui
        # ----------------------------

        self.setup_system()
        self._start_order_listener()

        # --- UDP Listener methods (_start_order_listener, _listen_for_orders, submit_external_order) remain the same ---

    def _start_order_listener(self):
        """Initializes and starts the UDP listener thread."""
        self.listener_thread = threading.Thread(target=self._listen_for_orders, daemon=True)
        self.listener_thread.start()

    def _listen_for_orders(self):
        """Listens for orders from an external ordering app via UDP."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(('', self.listener_port))
            print("=" * 50)
            print(f"📡 KITCHEN ORDER RECEIVER 📡")
            print(f"Listening for external orders on port {self.listener_port}...")
            print("=" * 50)
        except OSError as e:
            print(f"FATAL: Could not bind to port {self.listener_port}. Is it already in use? Error: {e}")
            self.is_running = False
            return

        while self.is_running:
            try:
                sock.settimeout(0.1)
                data, addr = sock.recvfrom(4096)
                order_data_raw = json.loads(data.decode('utf-8'))

                if "orders" in order_data_raw:
                    self.submit_external_order(order_data_raw.get("orders", []))
                else:
                    print(f"Warning: Received order from {addr} but missing 'orders' key. Payload: {order_data_raw}")

            except socket.timeout:
                continue
            except json.JSONDecodeError:
                print(f"Error: Received malformed JSON from {addr}.")
            except Exception as e:
                if self.is_running:
                    print(f"Error in order listener: {e}")
                else:
                    break

        print("Listener thread shut down.")

    def submit_external_order(self, external_items):
        """Processes and submits an order received from the external network source,
        assigning it to a random customer address."""

        if not external_items:
            print("[SYSTEM] External order rejected: No items provided.")
            return

        order_id = self.next_manual_order_id
        self.next_manual_order_id += 1

        random_customer = random.choice(self.customers)
        customer_address_coords = (random_customer.x, random_customer.y)
        customer_coords = customer_address_coords

        mock_customer = Customer(
            self.mock_customer_id,
            customer_address_coords,
            *customer_address_coords
        )

        target_restaurant, _ = self._find_closest_restaurant(customer_coords)
        if not target_restaurant:
            print("[SYSTEM] ERROR: Could not find any restaurant for external order.")
            return

        order_data = {
            'order_id': order_id,
            'customer_id': self.mock_customer_id,
            'customer_address': customer_address_coords,
            'items': external_items,
            'total_items': len(external_items)
        }

        self.customer_map[self.mock_customer_id] = mock_customer
        self.active_customer_orders[order_id] = mock_customer
        target_restaurant.receive_order(order_data)

        print("=" * 40)
        print(f"🍕 NEW EXTERNAL ORDER {order_id} RECEIVED & ROUTED!")
        print(f"Total Items: {len(external_items)}")
        print(f"Delivery Target: House at {customer_address_coords}")
        print(f"Routed to: {target_restaurant.Name}")
        print("=" * 40)

    def setup_system(self):
        """Initializes city, restaurants, chefs, and customers."""

        # 1. City Setup
        self.city = City("NeoCity", 500000, 100)

        # 2. Multiple Restaurant/Equipment/Staff Setup (Remains the same)
        for i, restaurant_pos in enumerate(self.restaurant_positions):
            restaurant_name = f"Pasta la Vista {i + 1}"
            restaurant = ItalianRestaurant(restaurant_name, f"Restaurant Address {i + 1}", system_reference=self)
            self.restaurants.append(restaurant)
            restaurant.open_for_business()
            self.city.add_restaurant(restaurant, restaurant_pos)

            ovens = [Oven(self.screen), Oven(self.screen)]
            pans = [Pan(self.screen), Pan(self.screen)]
            chef1 = Chef(0, 0, ovens, pans)
            chef2 = Chef(0, 0, ovens, pans)
            chef1.Name = f"Chef Mario {i + 1}"
            chef2.Name = f"Chef Luigi {i + 1}"
            restaurant.add_chef(chef1)
            restaurant.add_chef(chef2)
            for oven in ovens:
                restaurant.add_oven(oven)
            for pan in pans:
                restaurant.add_pan(pan)

            drone = DeliveryDrone(drone_id=i + 1, home_pos=restaurant_pos)
            self.drones.append(drone)
            restaurant.add_delivery_driver(drone)

            # 3. Customer Setup (Remains the same)
        customer_id_counter = 1
        for i, (x, y) in enumerate(self.city.houseCoords):
            customer_id = f"CUST{customer_id_counter}"
            customer = Customer(customer_id, f"House {i + 1}", x, y)
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
            rest_pos = self.city.get_restaurant_position(restaurant)
            if not rest_pos: continue

            distance = math.hypot(cust_x - rest_pos[0], cust_y - rest_pos[1])

            if distance < min_distance:
                min_distance = distance
                closest_restaurant = restaurant
                closest_pos = rest_pos

        return closest_restaurant, closest_pos

    # --- Gathers data for the Order Status UI ---
    def _gather_all_active_orders(self):
        """Gathers all currently active/queued/delivering orders from all restaurants for the status UI."""
        all_active_orders = []

        for rest in self.restaurants:
            # 1. Check the order currently being processed/cooked
            if rest.current_order:
                order_id = rest.current_order['order_id']
                ready_count = sum(1 for item in rest.items_to_package.get(order_id, {}).values() if item['ready'])

                all_active_orders.append({
                    'restaurant_name': rest.Name,
                    'order_id': order_id,
                    'state': rest.state.value,
                    'items_total': len(rest.current_order['items']),
                    'items_ready': ready_count
                })

            # 2. Check orders waiting in the queue
            for order in rest.Orders:
                all_active_orders.append({
                    'restaurant_name': rest.Name,
                    'order_id': order['order_id'],
                    'state': 'QUEUED',
                    'items_total': len(order['items']),
                    'items_ready': 0
                })

            # 3. Check order out for delivery
            if rest.delivery_in_progress_order:
                all_active_orders.append({
                    'restaurant_name': rest.Name,
                    'order_id': rest.delivery_in_progress_order['order_id'],
                    'state': 'DELIVERING',
                    'items_total': len(rest.delivery_in_progress_order['items']),
                    'items_ready': len(rest.delivery_in_progress_order['items'])  # All items ready for delivery
                })

        return all_active_orders

    # ----------------------------------------------------------------

    def _generate_and_place_order(self):
        # Automated orders logic remains the same
        current_time = time.time()
        if current_time - self.last_order_time >= self.order_interval:
            self.last_order_time = current_time
            customer = random.choice(self.customers)
            customer_coords = (customer.x, customer.y)

            target_restaurant, _ = self._find_closest_restaurant(customer_coords)
            if not target_restaurant:
                print("[SYSTEM] ERROR: Could not find any restaurant.")
                return

            order_data = customer.GenerateOrder()
            order_id = order_data['order_id']

            self.active_customer_orders[order_id] = customer
            target_restaurant.receive_order(order_data)

            print(
                f"[SYSTEM] New Automated Order {order_id} placed by {customer.CustomerID}. Routed to {target_restaurant.Name}.")

    def handle_completed_order(self, order_data):
        # Order completion logic remains the same
        order_id = order_data['order_id']

        if order_id in self.active_customer_orders:
            customer = self.active_customer_orders.pop(order_id)
            customer.ReceiveOrder(order_data)
            self.orders_processed += 1
            print(f"[SYSTEM] Order {order_id} completed and removed from active list.")

        if order_data['customer_id'] == self.mock_customer_id:
            if self.mock_customer_id in self.customer_map:
                del self.customer_map[self.mock_customer_id]
            print(f"[System] Temporary external customer (ID {self.mock_customer_id}) cleaned up.")

    def update(self):
        """Main update loop for the simulation logic."""

        # 1. Update the Order Status UI (Scheduled safely on the other thread)
        all_active_orders = self._gather_all_active_orders()
        self.tkinter_thread.schedule_status_update(all_active_orders)

        # 2. Simulation Logic
        self._generate_and_place_order()
        for rest in self.restaurants:
            rest.update()

    def draw(self):
        """Draw all simulation elements on the screen."""
        self.screen.fill((255, 255, 255))

        # Drawing logic remains the same
        self.city.show_city_map(self.screen)

        restaurant_statuses = [f"{rest.Name}: {rest.state.value}" for rest in self.restaurants]
        global font_medium
        self.city.show_restaurant_icon(self.screen, font_medium, restaurant_statuses)

        global font_small
        self.city.draw_customer_houses(self.screen, font_small)

        drone_color = (100, 100, 255)
        drone_radius = 8
        for i, drone in enumerate(self.drones):
            if hasattr(drone, 'x') and hasattr(drone, 'y'):
                drone_x, drone_y = int(drone.x), int(drone.y)
                pygame.draw.circle(self.screen, drone_color, (drone_x, drone_y), drone_radius, 0)
                drone_status_text = f"Drone {drone.DroneID}: {drone.Status}"
                drone_text_surface = font_small.render(drone_status_text, True, (0, 0, 0))
                rest_pos = self.restaurant_positions[i]
                self.screen.blit(drone_text_surface, (rest_pos[0] + 30, rest_pos[1] - 40))

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

        mode_text = "Mode: Pure Simulation (Status Pop-up Active)"
        mode_surface = font_medium.render(mode_text, True, (0, 0, 0))
        self.screen.blit(mode_surface, (10, 120))

        pygame.display.flip()

    def run_simulation(self):
        """The main simulation loop."""
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

            self.update()
            self.draw()
            clock.tick(30)

        pygame.quit()
        
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