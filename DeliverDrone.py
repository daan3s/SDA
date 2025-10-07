import pygame
import random
import math

StatusList = ['Available', 'Delivering']


class Delivery_Drone():
    def __init__(self, DroneID):
        self.DroneID = DroneID
        self.DroneStatus = StatusList[0]
        self.DroneAvailable = True
        self.Speed = 20

    def IsAvailable(self):  # Check if the drone is available to deliver
        if (self.Dronestatus == 'Available'):
            return True
        else:
            return False

    def DeliveringOrder(self, DeliverySpeed):  # Delivering order to customer
        if self.IsAvailable():
            self.DroneStatus = 'Delivering'
            self.IsAvailable = False

    def CompletingOrder(self):
        self.DroneStatus = 'Available'
        self.IsAvailable = True