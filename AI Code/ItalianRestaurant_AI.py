import pygame
import time
from datetime import datetime, time as dt_time
import socket
import json


class ItalianRestaurant:
    def __init__(self, name, address):
        # Attributes from class diagram
        self.Name = name  # str
        self.Address = address  # str
        self.OpeningTimes = {  # str 0...* - using dict for better management
            "Monday": "09:00-22:00",
            "Tuesday": "09:00-22:00",
            "Wednesday": "09:00-22:00",
            "Thursday": "09:00-22:00",
            "Friday": "09:00-23:00",
            "Saturday": "10:00-23:00",
            "Sunday": "10:00-21:00"
        }
        self.OrdersDone = 0  # int
        self.Ovens = []  # list
        self.Pans = []  # list
        self.DeliveryDrivers = []  # list
        self.Chefs = []  # list
        self.Orders = []  # list

        # Additional attributes for functionality
        self.is_open = False
        self.start_time = time.time()
        self.order_counter = 0

        # Network settings for receiving orders
        self.order_port = 5000
        self.setup_order_receiver()

    def setup_order_receiver(self):
        """Setup UDP socket for receiving orders"""
        try:
            self.order_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.order_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.order_socket.bind(('', self.order_port))
            self.order_socket.setblocking(False)  # Non-blocking
            print(f"Restaurant order receiver setup on port {self.order_port}")
        except Exception as e:
            print(f"Error setting up order receiver: {e}")

    # Operations from class diagram
    def Check_opening_hours(self):
        """Check if restaurant is currently open based on opening hours"""
        current_time = self.Get_real_world_time()
        current_day = current_time.strftime("%A")
        current_hour = current_time.hour
        current_minute = current_time.minute

        if current_day in self.OpeningTimes:
            opening_hours = self.OpeningTimes[current_day]
            try:
                open_time_str, close_time_str = opening_hours.split("-")
                open_time = datetime.strptime(open_time_str, "%H:%M").time()
                close_time = datetime.strptime(close_time_str, "%H:%M").time()

                current_time_obj = dt_time(current_hour, current_minute)
                self.is_open = open_time <= current_time_obj <= close_time
                return self.is_open
            except ValueError:
                print(f"Error parsing opening hours for {current_day}: {opening_hours}")
                return False
        return False

    def Show_opening_hours(self):
        """Display all opening hours"""
        print(f"\n=== {self.Name} Opening Hours ===")
        for day, hours in self.OpeningTimes.items():
            print(f"{day}: {hours}")
        print("================================")
        return self.OpeningTimes

    def Get_real_world_time(self):
        """Get current real world time"""
        return datetime.now()

    def Get_elapsed_time(self):
        """Get elapsed time since restaurant started"""
        return time.time() - self.start_time

    def Show_open_status(self):
        """Show whether restaurant is currently open or closed"""
        is_open = self.Check_opening_hours()
        status = "OPEN" if is_open else "CLOSED"
        current_time = self.Get_real_world_time().strftime("%H:%M:%S")

        status_info = {
            "restaurant": self.Name,
            "status": status,
            "current_time": current_time,
            "is_open": is_open
        }

        print(f"\n{self.Name} Status: {status}")
        print(f"Current Time: {current_time}")
        return status_info

    def Receive_order(self):
        """Receive orders from customers via UDP"""
        if not self.is_open:
            print("Restaurant is closed. Cannot receive orders.")
            return None

        try:
            data, addr = self.order_socket.recvfrom(1024)
            order_data = json.loads(data.decode('utf-8'))

            print(f"Received order from {addr}")
            print(f"Order data: {order_data}")

            # Add restaurant processing info
            order_data['restaurant_name'] = self.Name
            order_data['received_time'] = self.Get_real_world_time().isoformat()
            order_data['restaurant_order_id'] = self.order_counter
            self.order_counter += 1

            self.Orders.append(order_data)
            return order_data

        except BlockingIOError:
            # No data available, which is fine
            pass
        except Exception as e:
            print(f"Error receiving order: {e}")

        return None

    def Process_order(self, order_index=None):
        """Process a specific order or the next order in queue"""
        if not self.Orders:
            print("No orders to process")
            return None

        if order_index is None:
            # Process the oldest order
            order_to_process = self.Orders.pop(0)
        else:
            if 0 <= order_index < len(self.Orders):
                order_to_process = self.Orders.pop(order_index)
            else:
                print(f"Invalid order index: {order_index}")
                return None

        # Process the order
        print(f"Processing order: {order_to_process}")

        # Assign to available chef
        chef_assigned = self.assign_order_to_chef(order_to_process)
        if chef_assigned:
            print(f"Order assigned to chef: {chef_assigned.Name}")
        else:
            print("No available chefs, order queued")
            # Put back in queue if no chefs available
            self.Orders.insert(0, order_to_process)
            return None

        self.OrdersDone += 1
        return order_to_process

    # Additional helper methods for restaurant operations
    def assign_order_to_chef(self, order):
        """Assign order to an available chef"""
        for chef in self.Chefs:
            if chef.ChefAvailable:
                chef.current_order = order
                chef.ChefAvailable = False
                chef.ChefStatus = "Processing Order"
                return chef
        return None

    def add_chef(self, chef):
        """Add a chef to the restaurant"""
        self.Chefs.append(chef)
        print(f"Added chef: {chef.Name}")

    def add_oven(self, oven):
        """Add an oven to the restaurant"""
        self.Ovens.append(oven)
        print(f"Added oven: {oven.OvenID}")

    def add_pan(self, pan):
        """Add a pan to the restaurant"""
        self.Pans.append(pan)
        print(f"Added pan: {pan.panID}")

    def add_delivery_driver(self, driver):
        """Add a delivery driver to the restaurant"""
        self.DeliveryDrivers.append(driver)
        print(f"Added delivery driver: {driver.DroneID}")

    def get_available_ovens(self):
        """Get list of available ovens"""
        return [oven for oven in self.Ovens if oven.OvenAvailable]

    def get_available_pans(self):
        """Get list of available pans"""
        return [pan for pan in self.Pans if pan.panavailable]

    def get_available_chefs(self):
        """Get list of available chefs"""
        return [chef for chef in self.Chefs if chef.ChefAvailable]

    def get_available_drivers(self):
        """Get list of available delivery drivers"""
        return [driver for driver in self.DeliveryDrivers if driver.DroneAvailable]

    def get_restaurant_stats(self):
        """Get comprehensive restaurant statistics"""
        return {
            "name": self.Name,
            "address": self.Address,
            "is_open": self.is_open,
            "orders_done": self.OrdersDone,
            "orders_queued": len(self.Orders),
            "total_chefs": len(self.Chefs),
            "available_chefs": len(self.get_available_chefs()),
            "total_ovens": len(self.Ovens),
            "available_ovens": len(self.get_available_ovens()),
            "total_pans": len(self.Pans),
            "available_pans": len(self.get_available_pans()),
            "total_drivers": len(self.DeliveryDrivers),
            "available_drivers": len(self.get_available_drivers()),
            "elapsed_time": self.Get_elapsed_time()
        }

    def update(self):
        """Update restaurant state - call this regularly"""
        # Check opening hours
        self.Check_opening_hours()

        # Receive new orders
        if self.is_open:
            self.Receive_order()

        # Process orders if we have available chefs
        if self.Orders and self.get_available_chefs():
            self.Process_order()

    def close_restaurant(self):
        """Close the restaurant and cleanup"""
        print(f"Closing {self.Name}")
        try:
            self.order_socket.close()
        except:
            pass
        self.is_open = False


# Example usage
if __name__ == "__main__":
    # Create restaurant
    restaurant = ItalianRestaurant("Mario's Italian Kitchen", "123 Pizza Street, Italy")

    # Show opening hours
    restaurant.Show_opening_hours()

    # Check current status
    status = restaurant.Show_open_status()
    print(f"Restaurant is {'OPEN' if status['is_open'] else 'CLOSED'}")

    # Display statistics
    stats = restaurant.get_restaurant_stats()
    print(f"\nRestaurant Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")