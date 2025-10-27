# Oven.py
import time
import random

class Oven:
    def __init__(self, screen):
        self.screen = screen # For visualization
        self.Available = True
        self.cooking_item = None
        self.chef_reference = None
        self.bake_end_time = 0
        self.bake_time = 5 # seconds

    def bake_pizza(self, restaurant, chef, pizza_item):
        """Receives Pizza from Chef (Sequence Diagram)."""
        self.Available = False
        self.chef_reference = chef
        self.cooking_item = pizza_item
        self.bake_end_time = time.time() + self.bake_time
        print(f"[Oven] Started baking Pizza {pizza_item[0]}. Ready in {self.bake_time}s.")

    def update(self, restaurant):
        if not self.Available and time.time() >= self.bake_end_time:
            # Update Pizza Status (Sequence Diagram - dashed line to Chef)
            item_name = self.cooking_item[0]
            self.chef_reference.receive_cooking_status(restaurant, 'done', item_name, 'pizza')
            
            print(f"[Oven] Finished baking Pizza {item_name}.")
            self.Available = True
            self.cooking_item = None
            self.chef_reference = None