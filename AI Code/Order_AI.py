import pygame
import random
import math

StatusList = ['Processing', 'Preparing', 'Baking', 'Packaging', 'Delivering']


class Order():
    def __init__(self, OrderID, CustomerData, Restaurant):
        self.OrderID = OrderID
        self.CustomerData = CustomerData
        self.Products = []  # Initialize as empty list
        self.Status = StatusList[0]  # Start with 'Processing'
        self.Restaurant = Restaurant
        self.pizzas = []  # Specific list for pizzas
        self.pastas = []  # Specific list for pastas

    def AddPizza(self, pizza):  # Matches diagram operation name
        self.pizzas.append(pizza)
        self.Products.append(pizza)
        print(f"Pizza {pizza.GetID()} added to order {self.OrderID}")
        return pizza  # Returns pizza as per diagram

    def AddPasta(self, pasta):  # Matches diagram operation name
        self.pastas.append(pasta)
        self.Products.append(pasta)
        print(f"Pasta {pasta.GetID()} added to order {self.OrderID}")
        return pasta  # Returns pasta as per diagram

    def CalculateTotal(self):  # Matches diagram operation name - returns int
        total = 0

        # Calculate pizza prices
        for pizza in self.pizzas:
            total += pizza.GetPrice()  # Use GetPrice() method from Pizza class

        # Calculate pasta prices
        for pasta in self.pastas:
            total += pasta.CalculatePrice()  # Use CalculatePrice() method from Pasta class

        # Add delivery cost based on customer distance
        if hasattr(self.CustomerData, 'distance'):
            delivery_cost = self.CustomerData.distance * 0.50
            total += delivery_cost

        return int(total)  # Return int as per diagram

    def GetStatus(self):  # Matches diagram operation name - returns str
        return self.Status

    def SetStatus(self, status_index):
        """Set the order status based on index"""
        if 0 <= status_index < len(StatusList):
            self.Status = StatusList[status_index]
            print(f"Order {self.OrderID} status changed to: {self.Status}")

    def MakeDescription(self):  # Matches diagram operation name - returns str
        # Build products description
        products_desc = ""
        for product in self.Products:
            if hasattr(product, 'GetDescription'):
                products_desc += product.GetDescription() + "; "
            else:
                products_desc += f"Product {getattr(product, 'pizzaID', getattr(product, 'pastaID', 'Unknown'))}, "

        # Remove trailing separator
        if products_desc.endswith("; "):
            products_desc = products_desc[:-2]

        description = f"Order {self.OrderID}: Products: {products_desc} | Status: {self.Status} | Restaurant: {self.Restaurant} | Total: ${self.CalculateTotal()}"
        return description

    def GetOrderSummary(self):
        """Additional helper method to get order summary"""
        return {
            'order_id': self.OrderID,
            'customer': self.CustomerData,
            'pizza_count': len(self.pizzas),
            'pasta_count': len(self.pastas),
            'total_products': len(self.Products),
            'status': self.Status,
            'total_price': self.CalculateTotal(),
            'restaurant': self.Restaurant
        }