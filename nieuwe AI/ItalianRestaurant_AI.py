# ItalianRestaurant_AI.py

from enum import Enum
import time
import random
import socket
import json
import threading

# Define the states from the State Diagram
class StoreState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    PREPARING = "PREPARING"
    COOKING = "COOKING"
    BAKING = "BAKING"
    PACKAGING = "PACKAGING"
    DELIVERING = "DELIVERING"

# Network Configuration for Receiving Orders from UI
LISTENING_PORT = 5003 

class ItalianRestaurant:
    def __init__(self, name, address, system_reference):
        self.Name = name
        self.Address = address
        self.state: StoreState = StoreState.CLOSED
        self.Chefs = []
        self.Ovens = []
        self.Pans = []
        self.DeliveryDrivers = []
        self.Orders = []  # Incoming order queue (like a job queue)
        self.current_order = None 
        self.products_ready = [] 
        self.orders_completed_count = 0
        self.completed_orders = []
        self.is_open = False

        self.system_reference = system_reference
        self.items_to_package = {} 
        self.delivery_in_progress_order = None

        # --- NEW: Order Listener Setup ---
        self.listener_thread = None
        self.is_listening = False
        self._start_order_listener()
        # ---------------------------------

    def add_chef(self, chef):
        self.Chefs.append(chef)

    def add_oven(self, oven):
        self.Ovens.append(oven)

    def add_pan(self, pan):
        self.Pans.append(pan)

    def add_delivery_driver(self, driver):
        self.DeliveryDrivers.append(driver)

    def get_current_state(self):
        """Returns the current state for visualization."""
        return self.state.value

    def open_for_business(self):
        self.state = StoreState.OPEN
        self.is_open = True
        print(f"[{self.Name}] is now {self.state.value}.")

    def _start_order_listener(self):
        """Starts a non-blocking thread to listen for UDP orders."""
        if not self.is_listening:
            self.is_listening = True
            # Daemon thread means it won't prevent the main program from exiting
            self.listener_thread = threading.Thread(target=self._listen_for_orders, daemon=True)
            self.listener_thread.start()
            print(f"[{self.Name}] Order listener started on port {LISTENING_PORT}.")
            
    def _listen_for_orders(self):
        """The actual function run by the thread to listen for UDP packets."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Allow reuse of the address
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to all interfaces (0.0.0.0) on the defined port
            sock.bind(('', LISTENING_PORT))
            # Timeout is necessary for clean thread shutdown
            sock.settimeout(0.5)

            while self.is_listening:
                try:
                    data, addr = sock.recvfrom(4096)
                    # When data is received, process it
                    self._handle_received_order(data, addr)
                    
                except socket.timeout:
                    # Expected timeout, loop continues to check 'self.is_listening'
                    continue
                except Exception:
                    # Silent catch for minor socket issues; major ones are caught below
                    pass 

        except Exception as e:
            print(f"[{self.Name}] Fatal Listener setup error: {e}")
            self.is_listening = False 
        finally:
            if 'sock' in locals():
                sock.close()


    def _handle_received_order(self, data, addr):
        """Processes the raw received data and converts it to the internal order format."""
        try:
            order_data_external = json.loads(data.decode('utf-8'))
            
            external_order_items = order_data_external.get("orders", [])
            order_id = order_data_external.get("order_id", random.randint(3000, 4000))
            customer_id = order_data_external.get("customer_id", f"ExternalCustomer-{addr[0]}")
            
            # Convert network-received order data into the internal order format
            internal_order_data = {
                'order_id': order_id,
                'customer_id': customer_id,
                'customer_address': f"NetworkOrder:{addr[0]}",
                'items': external_order_items, # list of [id, type, ...]
                'total_items': len(external_order_items),
                'source': order_data_external.get("source", "Network")
            }
            
            # Add to the order queue
            self.receive_order(internal_order_data)
            
        except json.JSONDecodeError:
            print(f"[{self.Name}] Error: Received malformed JSON from {addr[0]}.")
        except Exception as e:
            print(f"[{self.Name}] Error processing received order: {e}")


    def receive_order(self, order_data):
        """Receives a new order from a Customer/System (Sequence Diagram) or Network."""
        self.Orders.append(order_data)
        print(f"[{self.Name}] Received new order {order_data['order_id']} from {order_data['customer_id']}. Queue size: {len(self.Orders)}")
       
        # Transition: OPEN -> PREPARING (if an order is received and queue was empty)
        if self.state == StoreState.OPEN and len(self.Orders) == 1:
             self.state = StoreState.PREPARING
             print(f"[{self.Name}] Transition: OPEN -> PREPARING.")

    # --- Core Order Processing Logic (Rest of the class methods remain the same) ---
   
    def _start_preparation(self):
        """Transition: PREPARING -> COOKING/BAKING. Chef starts working."""
        # ... (rest of method remains the same)
        if not self.Orders:
            self.state = StoreState.OPEN
            print(f"[{self.Name}] Transition: PREPARING -> OPEN (Queue empty).")
            return

        self.current_order = self.Orders.pop(0)
        order_id = self.current_order['order_id']
       
        self.items_to_package[order_id] = {}
        for item in self.current_order['items']:
            item_id = item[0]
            item_type = item[1]
            self.items_to_package[order_id][item_id] = {'data': item, 'ready': False, 'type': item_type}

        available_chef = next((c for c in self.Chefs if c.ChefAvailable), None)

        if available_chef:
            available_chef.prepare_order(self, self.current_order)
            self.state = StoreState.COOKING 
            print(f"[{self.Name}] Transition: PREPARING -> COOKING/BAKING. Chef {available_chef.Name} started order {order_id}.")
        else:
            self.Orders.insert(0, self.current_order)
            self.current_order = None
            print(f"[{self.Name}] Warning: No available chef. Order {order_id} re-queued.")

    def notify_cooking_status(self, item_id, status: str, item_type: str):
        # ... (rest of method remains the same)
        order_id = self.current_order['order_id']
       
        if order_id not in self.items_to_package:
            print(f"[{self.Name}] Error: Received status for item {item_id} but order {order_id} is not tracked.")
            return
           
        if status == 'done':
            if item_id in self.items_to_package[order_id]:
                self.items_to_package[order_id][item_id]['ready'] = True
                print(f"[{self.Name}] Item {item_id} ({item_type}) ready for order {order_id}.")
            else:
                print(f"[{self.Name}] Error: Unknown item ID {item_id} for order {order_id}.")

        all_items_ready = all(item['ready'] for item in self.items_to_package[order_id].values())

        if all_items_ready:
            print(f"[{self.Name}] All items for order {order_id} are ready. Starting packaging.")
            self.state = StoreState.PACKAGING
           
    def _start_packaging(self):
        # ... (rest of method remains the same)
        if self.state != StoreState.PACKAGING:
            return

        time.sleep(0.01)

        print(f"[{self.Name}] Order {self.current_order['order_id']} is packaged. Starting delivery.")
        self.state = StoreState.DELIVERING
        self._start_delivery()

    def _start_delivery(self):
        # ... (rest of method remains the same)
        if self.state != StoreState.DELIVERING or not self.current_order:
            return

        available_drone = next((d for d in self.DeliveryDrivers if d.Available), None)

        if available_drone:
            customer = self.system_reference.active_customer_orders.get(self.current_order['order_id'])
            # ... (rest of delivery logic remains the same)
            if customer:
                customer_x, customer_y = customer.x, customer.y
            else:
                print(f"[{self.Name}] Warning: Could not find customer coords in system tracking. Using random house.")
                house_index = random.randint(0, len(self.system_reference.city.houseCoords) - 1)
                customer_x, customer_y = self.system_reference.city.houseCoords[house_index]

            delivery_successful = available_drone.deliver_order(self, self.current_order, customer_x, customer_y)

            if delivery_successful:
                self.delivery_in_progress_order = self.current_order
                self.current_order = None
                del self.items_to_package[self.delivery_in_progress_order['order_id']]
                print(f"[{self.Name}] Delivery started for order {self.delivery_in_progress_order['order_id']}.")
            else:
                print(f"[{self.Name}] Warning: No available drone. Waiting.")
                self.state = StoreState.PACKAGING # Go back to packaging state to wait for drone
        else:
            print(f"[{self.Name}] Waiting for available drone.")
            self.state = StoreState.PACKAGING # Wait for a drone

    def complete_order(self, completed_order):
        # ... (rest of method remains the same)
        if not self.delivery_in_progress_order or completed_order['order_id'] != self.delivery_in_progress_order['order_id']:
            print(f"[{self.Name}] Warning: complete_order called but order {completed_order['order_id']} was not marked as delivering.")
            return
        
        self.delivery_in_progress_order = None
        self.orders_completed_count += 1
        self.completed_orders.append(completed_order)
        self.system_reference.handle_completed_order(completed_order)

        if self.Orders:
            self.state = StoreState.PREPARING
            print(f"[{self.Name}] Transition: DELIVERING -> PREPARING (More orders waiting).")
        elif self.current_order:
            next_order_id = self.current_order['order_id']
            if next_order_id in self.items_to_package and all(item['ready'] for item in self.items_to_package.get(next_order_id, {}).values()):
                self.state = StoreState.PACKAGING
            else:
                self.state = StoreState.COOKING
            print(f"[{self.Name}] Transition: DELIVERING -> {self.state.value} (Next order in progress).")
        else:
            self.state = StoreState.OPEN
            print(f"[{self.Name}] Transition: DELIVERING -> OPEN (Queue empty).")

    # --- Update Loop ---
    def update(self):
        """Performs state-based actions and updates all equipment."""
        # 1. Update Equipment
        for oven in self.Ovens:
            oven.update(self)
        for pan in self.Pans:
            pan.update(self)
        for drone in self.DeliveryDrivers:
            drone.update(self)

        # 2. Perform State Actions
        if self.state == StoreState.PREPARING:
            self._start_preparation()
        elif self.state == StoreState.PACKAGING:
            self._start_packaging()
        elif self.state == StoreState.OPEN and self.Orders:
            self.state = StoreState.PREPARING
            print(f"[{self.Name}] Transition: OPEN -> PREPARING (New order detected in queue).")

    # --- Utility Methods ---
    def check_and_clear_completed_orders(self):
        # ... (rest of method remains the same)
        count = self.orders_completed_count
        self.orders_completed_count = 0
        return count

    def get_status_info(self):
        # ... (rest of method remains the same)
        all_orders = []

        # 1. Queued Orders (in self.Orders)
        for order in self.Orders:
            all_orders.append({
                'type': 'QUEUED',
                'order_id': order['order_id'],
                'customer_id': order['customer_id'],
                'state': 'WAITING',
                'items_total': len(order['items']),
                'items_ready': 0,
                'is_current': False,
            })

        # 2. Current Order (in self.current_order)
        if self.current_order:
            ready_count = sum(1 for item in self.items_to_package.get(self.current_order['order_id'], {}).values() if item['ready'])

            all_orders.append({
                'type': 'ACTIVE',
                'order_id': self.current_order['order_id'],
                'customer_id': self.current_order['customer_id'],
                'state': self.state.value, 
                'items_total': len(self.current_order['items']),
                'items_ready': ready_count,
                'is_current': True,
            })

        # 3. Order out for delivery (in self.delivery_in_progress_order)
        if self.delivery_in_progress_order:
             all_orders.append({
                'type': 'ACTIVE',
                'order_id': self.delivery_in_progress_order['order_id'],
                'customer_id': self.delivery_in_progress_order['customer_id'],
                'state': 'DELIVERING',
                'items_total': len(self.delivery_in_progress_order['items']),
                'items_ready': len(self.delivery_in_progress_order['items']),
                'is_current': False
            })

        # 4. Completed Orders (in self.completed_orders)
        for order in self.completed_orders:
            all_orders.append({
                'type': 'COMPLETED',
                'order_id': order['order_id'],
                'customer_id': order['customer_id'],
                'state': order.get('final_status', 'DELIVERED'),
                'items_total': len(order['items']),
                'items_ready': len(order['items']),
                'is_current': False
            })
            
        return all_orders