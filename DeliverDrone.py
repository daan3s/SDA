import pygame
import random
import math

StatusList = ['Available', 'Delivering']


class Delivery_Drone():
    def __init__(self, DroneID):
        self.DroneID = DroneID
        self.DriverStatus = StatusList[0]

    def IsAvailable(self):  # Check if the drone is available to deliver
        if (self.Driverstatus == 'Available'):
            return
        else:
            return

    def DeliveringOrder(self, DeliverySpeed):  # Delivering order to customer

