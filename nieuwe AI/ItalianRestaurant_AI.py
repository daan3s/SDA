# ItalianRestaurant_AI.py

from enum import Enum
import time
import random

# Define the states from the State Diagram
class StoreState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    PREPARING = "PREPARING"
    COOKING = "COOKING"
    BAKING = "BAKING"
    PACKAGING = "PACKAGING"
    DELIVERING = "DELIVERING"

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
        self.current_order = None # The order currently being processed/cooked/packaged
        self.products_ready = [] # Temporary storage for completed items (Pizza/Pasta)
        self.orders_completed_count = 0
        self.is_open = False # For City_AI display
        
        # Reference to the main system for callbacks
        self.system_reference = system_reference 
        self.items_to_package = {} # Tracks items ready for packaging for the current order
        self.delivery_in_progress_order = None # Order data currently out for delivery


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

    def receive_order(self, order_data):
        """Receives a new order from a Customer/System (Sequence Diagram)."""
        self.Orders.append(order_data)
        print(f"[{self.Name}] Received new order {order_data['order_id']} from {order_data['customer_id']}. Queue size: {len(self.Orders)}")
        
        # Transition: OPEN -> PREPARING (if an order is received and queue was empty)
        if self.state == StoreState.OPEN and len(self.Orders) == 1:
             self.state = StoreState.PREPARING
             print(f"[{self.Name}] Transition: OPEN -> PREPARING.")

    # --- Core Order Processing Logic ---
    
    def _start_preparation(self):
        """Transition: PREPARING -> COOKING/BAKING. Chef starts working."""
        if not self.Orders:
            self.state = StoreState.OPEN
            print(f"[{self.Name}] Transition: PREPARING -> OPEN (Queue empty).")
            return

        # Take the next order from the queue
        self.current_order = self.Orders.pop(0)
        order_id = self.current_order['order_id']
        
        # Initialize items_to_package tracker for this order
        self.items_to_package[order_id] = {}
        for item in self.current_order['items']:
            item_id = item[0]
            item_type = item[1]
            # Store the item data initially, mark it as not ready
            self.items_to_package[order_id][item_id] = {'data': item, 'ready': False, 'type': item_type}

        # Find an available chef
        available_chef = next((c for c in self.Chefs if c.ChefAvailable), None)

        if available_chef:
            # Chef handles dispatching all items to Oven/Pan
            available_chef.prepare_order(self, self.current_order)
            self.state = StoreState.COOKING # Change state to indicate active cooking/baking
            print(f"[{self.Name}] Transition: PREPARING -> COOKING/BAKING. Chef {available_chef.Name} started order {order_id}.")
        else:
            # Re-queue the order if no chef is available (simplified)
            self.Orders.insert(0, self.current_order)
            self.current_order = None
            print(f"[{self.Name}] Warning: No available chef. Order {order_id} re-queued.")

    def notify_cooking_status(self, item_id, status: str, item_type: str):
        """
        Receives cooking/baking completion status from Chef/Equipment.
        Transition: COOKING/BAKING -> PACKAGING (when all items are ready).
        """
        order_id = self.current_order['order_id']
        
        if order_id not in self.items_to_package:
            print(f"[{self.Name}] Error: Received status for item {item_id} but order {order_id} is not tracked.")
            return
            
        if status == 'done':
            # Mark the item as ready
            if item_id in self.items_to_package[order_id]:
                self.items_to_package[order_id][item_id]['ready'] = True
                print(f"[{self.Name}] Item {item_id} ({item_type}) ready for order {order_id}.")
            else:
                print(f"[{self.Name}] Error: Unknown item ID {item_id} for order {order_id}.")

        # Check if ALL items in the current order are ready
        all_items_ready = all(item['ready'] for item in self.items_to_package[order_id].values())

        if all_items_ready:
            print(f"[{self.Name}] All items for order {order_id} are ready. Starting packaging.")
            self.state = StoreState.PACKAGING
            
    def _start_packaging(self):
        """Simulate packaging time."""
        if self.state != StoreState.PACKAGING:
            return

        # Simple packaging simulation: Instantaneous (or could use a timer)
        time.sleep(0.01) # Small delay for simulation effect

        print(f"[{self.Name}] Order {self.current_order['order_id']} is packaged. Starting delivery.")
        self.state = StoreState.DELIVERING
        self._start_delivery()


    def _start_delivery(self):
        """Transition: PACKAGING -> DELIVERING. Drone starts delivery."""
        if self.state != StoreState.DELIVERING or not self.current_order:
            return

        available_drone = next((d for d in self.DeliveryDrivers if d.Available), None)

        if available_drone:
            # Find the customer object to get coordinates using the system reference
            customer = self.system_reference.active_customer_orders.get(self.current_order['order_id'])
            if customer:
                customer_x, customer_y = customer.x, customer.y
            else:
                # Fallback: Should not happen if tracking is correct, but safe fallback is necessary
                print(f"[{self.Name}] Warning: Could not find customer coords in system tracking. Using random house.")
                house_index = random.randint(0, len(self.system_reference.city.houseCoords) - 1)
                customer_x, customer_y = self.system_reference.city.houseCoords[house_index]

            # Drone starts delivery
            delivery_successful = available_drone.deliver_order(
                self, 
                self.current_order, 
                customer_x, 
                customer_y
            )

            if delivery_successful:
                self.delivery_in_progress_order = self.current_order
                self.current_order = None # Order is now with the drone
                # Clear item tracking for the packaged order
                del self.items_to_package[self.delivery_in_progress_order['order_id']]
                print(f"[{self.Name}] Delivery started for order {self.delivery_in_progress_order['order_id']}.")
            else:
                # Should not happen if state is handled correctly
                print(f"[{self.Name}] Error: No available drone despite state DELIVERING.")
                
        else:
            # Should enter PACKAGING state and wait for drone
            print(f"[{self.Name}] Waiting for available drone.")
            self.state = StoreState.PACKAGING # Go back to packaging state to wait for drone

    def complete_order(self, completed_order):
        """Called by DeliveryDrone when delivery is finished (Sequence Diagram)."""
        if not self.delivery_in_progress_order or completed_order['order_id'] != self.delivery_in_progress_order['order_id']:
            print(f"[{self.Name}] Warning: complete_order called but order {completed_order['order_id']} was not marked as delivering.")
            return

        self.delivery_in_progress_order = None
        self.orders_completed_count += 1

        # Notify the AutomatedRestaurantSystem that the order is done.
        self.system_reference.handle_completed_order(completed_order)
        
        # State transitions
        if self.Orders:
            self.state = StoreState.PREPARING
            print(f"[{self.Name}] Transition: DELIVERING -> PREPARING (More orders waiting).")
        elif self.current_order:
            # If the next order's preparation was very fast, it might be waiting for packaging
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
            # If a new order arrived while OPEN, transition to PREPARING
            self.state = StoreState.PREPARING
            print(f"[{self.Name}] Transition: OPEN -> PREPARING (New order detected in queue).")

    # --- Utility Methods ---
    def check_and_clear_completed_orders(self):
        """Used by main_automated to update global stats."""
        count = self.orders_completed_count
        self.orders_completed_count = 0
        return count

    def get_restaurant_stats(self):
        return {
            'orders_done': self.orders_completed_count,
            'available_chefs': sum(1 for c in self.Chefs if c.ChefAvailable),
            'total_chefs': len(self.Chefs),
            'available_ovens': sum(1 for o in self.Ovens if o.Available),
            'total_ovens': len(self.Ovens),
            'available_pans': sum(1 for p in self.Pans if p.Available),
            'total_pans': len(self.Pans),
            'state': self.state.value,
            'queue_size': len(self.Orders)
        }
