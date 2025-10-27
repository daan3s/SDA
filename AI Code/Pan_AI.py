# Pan_AI.py
import time
import random

class Pan:
    def __init__(self, screen):
        self.screen = screen # For visualization
        self.Available = True
        self.cooking_item = None
        self.chef_reference = None
        self.cook_end_time = 0
        self.cook_time = 4 # seconds

    def cook_pasta(self, restaurant, chef, pasta_item):
        """Receives Pasta from Chef (Sequence Diagram)."""
        self.Available = False
        self.chef_reference = chef
        self.cooking_item = pasta_item
        self.cook_end_time = time.time() + self.cook_time
        print(f"[Pan] Started cooking Pasta {pasta_item[0]}. Ready in {self.cook_time}s.")

    def update(self, restaurant):
        if not self.Available and time.time() >= self.cook_end_time:
            # Update Pasta Status (Sequence Diagram - dashed line to Chef)
            item_name = self.cooking_item[0]
            self.chef_reference.receive_cooking_status(restaurant, 'done', item_name, 'pasta')

            print(f"[Pan] Finished cooking Pasta {item_name}.")
            self.Available = True
            self.cooking_item = None
            self.chef_reference = None