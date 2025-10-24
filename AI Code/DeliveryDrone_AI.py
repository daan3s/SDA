import pygame
import random
import math

StatusList = ['Available', 'Delivering']


class DeliveryDrone():  # Fixed class name (underscore removed for consistency)
    def __init__(self, DroneID, Dronespeed=20):
        self.DroneID = DroneID
        self.DroneAvailable = True  # Matches diagram attribute name
        self.DroneStatus = StatusList[0]  # Matches diagram attribute name
        self.DroneSpeed = Dronespeed  # Matches diagram attribute name
        self.CurrentOrder = None  # Additional for functionality

    def IsAvailable(self):  # Matches diagram operation name - returns bool
        return self.DroneAvailable  # Directly return the boolean attribute

    def DeliveringOrder(self):  # Matches diagram operation name - returns bool
        # Start delivering an order
        if self.DroneAvailable:
            self.DroneAvailable = False
            self.DroneStatus = 'Delivering'
            print(f"Drone {self.DroneID}: Started delivering order")
            return True  # Successfully started delivery
        else:
            print(f"Drone {self.DroneID}: Not available for delivery")
            return False  # Failed to start delivery

    # Additional methods for functionality (not in diagram but needed)
    def CompleteDelivery(self):
        """Complete the current delivery and make drone available again"""
        self.DroneAvailable = True
        self.DroneStatus = 'Available'
        self.CurrentOrder = None
        print(f"Drone {self.DroneID}: Delivery completed")
        return True

    def GetStatus(self):
        """Get current drone status"""
        return self.DroneStatus

    def UpdatePosition(self, current_pos, destination_pos):
        """Update drone position during delivery (additional functionality)"""
        if self.DroneStatus == 'Delivering':
            # Calculate distance and movement
            dx = destination_pos[0] - current_pos[0]
            dy = destination_pos[1] - current_pos[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance <= self.DroneSpeed:
                # Reached destination
                return destination_pos, True  # Position, delivery_complete
            else:
                # Move towards destination
                ratio = self.DroneSpeed / distance
                new_x = current_pos[0] + dx * ratio
                new_y = current_pos[1] + dy * ratio
                return (new_x, new_y), False  # Position, delivery_complete
        return current_pos, False