import pygame
import random
import math

StatusList = ['Available', 'Delivering']
VehicleList = ['Car', 'Bike']


class Delivery_Driver():
    def __init__(self, name):
        self.Name = name
        self.Vehicle = VehicleList[0]
        self.DriverStatus = StatusList[0]

    def IsAvailable(self):  # Check if the driver is available to deliver
        if (self.Driverstatus == 'Available'):
            return
        else:
            return

    def DeliveringOrder(self, DeliverySpeed):  # Delivering order to customer
        if (distance >= 5):
            self.Vehicle = 'Car'
            set.speed = 20

else
self.Vehicle = 'Bike'
set.speed = 10
