# Chef_AI.py
import time
import random

class Chef:
    def __init__(self, x, y, ovens, pans):
        self.x = x
        self.y = y
        self.Name = "Anon Chef"
        self.ChefAvailable = True
        self.current_task = None
        self.task_end_time = 0
        self.ovens = ovens # References to all ovens
        self.pans = pans   # References to all pans

    def prepare_order(self, restaurant, order_data):
        """Restaurant sends order to Chef (Sequence Diagram)."""
        if not self.ChefAvailable:
            return False # Should not happen if called correctly

        self.ChefAvailable = False
        self.current_task = order_data
        print(f"[{self.Name}] Preparing order {order_data['order_id']}. Items: {order_data['total_items']}")
        
        # Chef is now busy coordinating cooking/baking.
        # This state is simplified here; the Chef is 'busy' until all items are launched.
        
        items_to_process = self.current_task['items']
        
        # Assign tasks based on items
        for item in items_to_process:
            item_type = item[1]
            if item_type == 'pizza':
                self._cook_pizza(restaurant, item)
            elif item_type == 'pasta':
                self._cook_pasta(restaurant, item)

        # In this model, the chef becomes free after assigning all tasks,
        # and relies on notifications for task completion.
        self.current_task = None
        self.ChefAvailable = True # Chef is available to take the next order

    def get_available_oven(self):
        for oven in self.ovens:
            if oven.Available:
                return oven
        return None

    def get_available_pan(self):
        for pan in self.pans:
            if pan.Available:
                return pan
        return None

    def _cook_pizza(self, restaurant, pizza_item):
        """Chef sends Pizza to Oven (Sequence Diagram)."""
        oven = self.get_available_oven()
        if oven:
            # Transition: HasPizza / [IsAvailable()] / CookPizza(oven)
            oven.bake_pizza(restaurant, self, pizza_item)
            print(f"[{self.Name}] Sent Pizza to {oven.__class__.__name__}.")
        else:
            print(f"[{self.Name}] Warning: No available Oven for Pizza.")
            # In a real system, the chef would wait or queue the task

    def _cook_pasta(self, restaurant, pasta_item):
        """Chef sends Pasta to Pan (Sequence Diagram)."""
        pan = self.get_available_pan()
        if pan:
            # Transition: HasPasta / [IsAvailable()] / CookPasta(pan)
            pan.cook_pasta(restaurant, self, pasta_item)
            print(f"[{self.Name}] Sent Pasta to {pan.__class__.__name__}.")
        else:
            print(f"[{self.Name}] Warning: No available Pan for Pasta.")
            # In a real system, the chef would wait or queue the task

    # --- Sequence Diagram: Equipment -> Chef Status Update ---

    def receive_cooking_status(self, restaurant, status: str, item_name: str, item_type: str):
        """
        Receives status from Oven/Pan (Sequence Diagram - dashed line).
        Transition: [GetStatus() == 'done'] / AddPizza() or AddPasta()
        """
        if status == 'done':
            print(f"[{self.Name}] Received 'done' status for {item_name} ({item_type}).")
            
            # Chef notifies Restaurant that the item is ready
            restaurant.notify_cooking_status(item_name, 'done', item_type)
        
    def update(self, restaurant):
        """Chef's update loop (simplified) - mainly for visual updates in this model."""
        pass