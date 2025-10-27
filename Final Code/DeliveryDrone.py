# DeliveryDrone.py
import time
import random
import math

class DeliveryDrone:
    def __init__(self, drone_id, home_pos):
        self.DroneID = drone_id
        self.Available = True
        self.delivery_task = None
        self.delivery_end_time = 0
        
        # Position tracking for visualization
        self.HomePos = home_pos # (x, y) of the restaurant
        self.x = home_pos[0]
        self.y = home_pos[1]
        self.target_x = home_pos[0]
        self.target_y = home_pos[1]
        self.speed = 40 # Pixels per second (for visualization)
        self.Status = "IDLE"

    def deliver_order(self, restaurant, order_data, customer_x, customer_y):
        """Receives Completed order from Restaurant (Sequence Diagram)."""
        if not self.Available:
            return False

        self.Available = False
        self.Status = "DELIVERING"
        
        # Store full order data and customer coordinates
        self.delivery_task = order_data
        self.target_x = customer_x
        self.target_y = customer_y
        
        # Calculate distance and actual delivery time for realism
        # Note: Using straight line distance (Pythagorean theorem)
        distance = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        
        # Time to travel one way + return trip + 1s dropoff
        travel_time = distance / self.speed
        self.delivery_time_seconds = travel_time * 2 + 1 
        self.delivery_end_time = time.time() + self.delivery_time_seconds
        
        print(f"[Drone {self.DroneID}] Started delivery of order {order_data['order_id']} to {order_data['customer_address']}. ETA {self.delivery_time_seconds:.1f}s.")
        return True

    def update(self, restaurant):
        if not self.Available:
            if time.time() < self.delivery_end_time:
                # Update position based on time elapsed
                time_elapsed = time.time() - (self.delivery_end_time - self.delivery_time_seconds)
                
                # Simplified movement: directly towards target during first half, directly back during second half
                half_time = self.delivery_time_seconds / 2
                
                if time_elapsed < half_time:
                    # Going to customer
                    t = time_elapsed / half_time
                    self.x = self.HomePos[0] + t * (self.target_x - self.HomePos[0])
                    self.y = self.HomePos[1] + t * (self.target_y - self.HomePos[1])
                    self.Status = f"TRAVELING ({self.delivery_task['order_id']})"
                else:
                    # Returning to base
                    t = (time_elapsed - half_time) / half_time
                    self.x = self.target_x + t * (self.HomePos[0] - self.target_x)
                    self.y = self.target_y + t * (self.HomePos[1] - self.target_y)
                    self.Status = "RETURNING"
                
            else:
                # Delivery complete
                completed_order = self.delivery_task
                
                # Delivered() / CompleteOrder(order_data) -> calls Restaurant to complete
                restaurant.complete_order(completed_order) 

                print(f"[Drone {self.DroneID}] Delivery complete and returned to base.")
                self.Available = True
                self.delivery_task = None
                self.x = self.HomePos[0]
                self.y = self.HomePos[1]
                self.Status = "IDLE"
