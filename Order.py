import pygame
import random
import math

StatusList = ['Processing', 'Preparing', 'Baking', 'Packaging', 'Delivering']
DeliveryCosts = Distance * (0.50)
class Order():
    def __init__(self, OrderID, CustomerData, Products, Status, Restaurant):
        self.OrderID = OrderID
        self.CustomerData = CustomerData
        self.Products = Products
        self.Status = StatusList[0]
        self.Restaurant = Restaurant

def Add_Pizza(self, pizza):  #Add pizza from pizza class
    self.pizzas.append(pizza)

def Add_Pasta(self, pasta):  #Add pasta from pasta class
    self.pastas.append(pasta)

def Calculate_Total(self, price):  #Calculate the total for the order
    total = pizza.price + pasta.price + DeliveryCosts

def Get_Status(self, OrderStatus):  #Get the current status of the order
    self.Status = StatusList[OrderStatus]
    return self.Status

def Make_Description(self):
    self.OrderDescription = self.OrderID + 'Products : ' + self.Products + 'Status: ' + self.Status + 'Restaurant: ' + self.Restaurant
