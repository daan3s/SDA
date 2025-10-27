# SystemUI_AI.py

import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from enum import Enum
import threading
import queue # For potential future cross-thread communication

# Define SystemMode (kept here for consolidation)
class SystemMode(Enum):
    """Defines the current operating mode of the system."""
    SIMULATION = 1
    MANUAL_ORDERING = 2

# =========================================================================
# NEW CLASS: TkinterThread (The core fix for the GIL error)
# =========================================================================
class TkinterThread(threading.Thread):
    """
    Runs the main Tkinter root and its event loop in a separate thread
    to prevent GIL conflicts with the Pygame thread.
    """
    def __init__(self, system_reference):
        super().__init__(daemon=True) # Daemon ensures the thread closes when the main program exits
        self.system = system_reference
        self.root = None
        self.manual_ui = None
        self.status_ui = None
        self._is_running = False

    def run(self):
        """Called when the thread starts."""
        self.root = tk.Tk()
        self.root.withdraw() # Hidden main Tkinter root
        
        # Instantiate UIs within the Tkinter thread context
        self.manual_ui = ManualOrderUI(self.system)
        self.status_ui = OrderStatusUI(self.system, self.root)
        
        self.manual_ui.setup_ui_dependencies() # Final setup after system is ready
        
        self._is_running = True
        
        # Start the persistent status window immediately
        self.status_ui.start_ui() 
        
        # Start the Tkinter main loop
        self.root.mainloop() 
        self._is_running = False
        print("[TkinterThread] Main loop terminated.")

    def schedule_status_update(self, order_statuses):
        """
        Schedules a status update to run safely on the Tkinter thread.
        This replaces the unsafe self.root.update() calls from the Pygame thread.
        """
        if self._is_running and self.root and self.status_ui.root:
            # Use root.after to schedule the call on the Tkinter thread
            self.root.after(0, lambda: self.status_ui.update_status(order_statuses))
            
    def schedule_manual_ui_toggle(self, is_manual_mode):
        """
        Schedules the manual UI visibility toggle on the Tkinter thread.
        """
        if self._is_running and self.root:
            if is_manual_mode:
                 self.root.after(0, self.manual_ui.start_ui)
            else:
                 self.root.after(0, self.manual_ui.close_ui)

    def stop(self):
        """Stops the Tkinter main loop."""
        if self._is_running and self.root:
            self.root.quit()


# =========================================================================
# OrderStatusUI (Modified to run in the Toplevel)
# =========================================================================
class OrderStatusUI:
    def __init__(self, system_reference, main_tk_root):
        self.system = system_reference
        self.root = None
        self.status_text_area = None
        self.main_tk_root = main_tk_root # Reference to the Tkinter root

    def start_ui(self):
        if self.root:
            self.root.destroy()

        self.root = tk.Toplevel(self.main_tk_root)
        self.root.title("Kitchen Order Status")
        # Ensure geometry is set within the thread
        self.root.geometry("400x500+10+10") 
        self.root.configure(bg='#f0f0f0')
        
        # Prevent manual closing from breaking the main loop
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.withdraw())
        # ... (rest of the setup is the same)
        title_label = tk.Label(self.root, text="Current Orders", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=10)

        self.status_text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=45,
            height=25,
            font=("Courier", 10),
            bg='white',
            fg='black'
        )
        self.status_text_area.pack(padx=10, pady=5, fill='both', expand=True)
        self.status_text_area.insert(tk.END, "Awaiting status updates...")
        self.status_text_area.config(state=tk.DISABLED)

        self.root.lift()
        self.root.deiconify()

    def update_status(self, orders_data):
        """Refreshes the displayed order data. Called safely via root.after()."""
        if self.root and self.status_text_area and self.root.winfo_exists():
            try:
                self.status_text_area.config(state=tk.NORMAL)
                self.status_text_area.delete(1.0, tk.END)

                if not orders_data:
                    self.status_text_area.insert(tk.END, "No active orders in the kitchen queue.")
                else:
                    output = ""
                    for order in orders_data:
                        order_id = order.get('order_id', 'N/A')
                        state = order.get('state', 'Unknown')
                        items_total = order.get('items_total', 0)
                        items_ready = order.get('items_ready', 0)
                        
                        output += f"Order ID: {order_id}\n"
                        output += f"  Status: {state}\n"
                        output += f"  Items: {items_ready}/{items_total} Ready\n"
                        output += "--------------------------------------\n"
                    
                    self.status_text_area.insert(tk.END, output)

                self.status_text_area.config(state=tk.DISABLED)
            except tk.TclError:
                 self.root = None
            
    def close_ui(self):
        if self.root:
            self.root.destroy()
            self.root = None

# =========================================================================
# ManualOrderUI (Modified to run in the Toplevel)
# =========================================================================
class ManualOrderUI:
    # ... (all existing __init__ and utility methods remain the same)
    def __init__(self, system_reference):
        self.system = system_reference
        self.root = None
        self.ingredient_states = {}
        self.selected_size = None
        self.size_buttons = {}
        self.basket = []
        self.selected_pasta_type = None
        self.selected_sauce = None
        self.pasta_ingredient_states = {}
        self.pasta_type_buttons = {}
        self.sauce_buttons = {}
        self.pizza_id_counter = 10000
        self.pasta_id_counter = 20000
        self.customer_address = None 
        self.customer_id = 9999
        self.main_tk_root = None # Will be set by the TkinterThread

    def setup_ui_dependencies(self):
        """Called by the TkinterThread AFTER the city is initialized."""
        if self.system.city and self.system.city.houseCoords:
            self.customer_address = (self.system.city.houseCoords[0][0], self.system.city.houseCoords[0][1])
        else:
            self.customer_address = (100, 100) 
            print("[ManualUI] Warning: Could not find city coordinates; using fallback address (100, 100).")

    def start_ui(self):
        # Retrieve the Tkinter root from the system's TkinterThread object
        self.main_tk_root = self.system.tkinter_thread.root 
        
        if self.root:
             self.root.destroy()

        self.root = tk.Toplevel(self.main_tk_root)
        self.root.title("Manual Food Ordering")
        self.root.geometry("500x800")
        self.root.configure(bg='white')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_main_screen()

        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
    def close_ui(self):
        if self.root:
            self.root.destroy()
            self.root = None
            
    # ... (all other methods like on_closing, toggle_ingredient, create_main_screen, etc., remain the same)
    def on_closing(self):
        # Must schedule the mode switch back to Pygame thread
        if messagebox.askokcancel("Quit", "Are you sure you want to exit manual ordering?"):
            self.system.switch_mode(SystemMode.SIMULATION)
            if self.root:
                self.root.destroy()
            self.root = None
            
    # --- Other methods for item selection, creation, and sending order are unchanged ---
    def toggle_ingredient(self, ingredient, button):
        if not self.root or not self.root.winfo_exists(): return
        self.ingredient_states[ingredient] = not self.ingredient_states.get(ingredient, False)
        if self.ingredient_states[ingredient]:
            button.config(bg="#4CAF50", relief="sunken")
        else:
            button.config(bg="#f0f0f0", relief="raised")
            
    def toggle_pasta_ingredient(self, ingredient, button):
        if not self.root or not self.root.winfo_exists(): return
        self.pasta_ingredient_states[ingredient] = not self.pasta_ingredient_states.get(ingredient, False)
        if self.pasta_ingredient_states[ingredient]:
            button.config(bg="#4CAF50", relief="sunken")
        else:
            button.config(bg="#f0f0f0", relief="raised")

    def select_size(self, size, button):
        if not self.root or not self.root.winfo_exists(): return
        if self.selected_size and self.selected_size in self.size_buttons:
            self.size_buttons[self.selected_size].config(bg="#f0f0f0", relief="raised")
        self.selected_size = size
        button.config(bg="#2196F3", relief="sunken")

    def select_pasta_type(self, pasta_type, button):
        if not self.root or not self.root.winfo_exists(): return
        if self.selected_pasta_type and self.selected_pasta_type in self.pasta_type_buttons:
            self.pasta_type_buttons[self.selected_pasta_type].config(bg="#f0f0f0", relief="raised")
        self.selected_pasta_type = pasta_type
        button.config(bg="#2196F3", relief="sunken")

    def select_sauce(self, sauce, button):
        if not self.root or not self.root.winfo_exists(): return
        if self.selected_sauce and self.selected_sauce in self.sauce_buttons:
            self.sauce_buttons[self.selected_sauce].config(bg="#f0f0f0", relief="raised")
        self.selected_sauce = sauce
        button.config(bg="#2196F3", relief="sunken")
        
    def add_to_basket(self, item_type):
        if not self.root or not self.root.winfo_exists(): return
        selected_ingredients = []
        order = {}

        if item_type == 'pizza':
            if not self.selected_size:
                messagebox.showwarning("No Size Selected", "Please select a pizza size!")
                return
            selected_ingredients = [ing for ing, sel in self.ingredient_states.items() if sel]
            pizza_id = self.pizza_id_counter
            self.pizza_id_counter += 1
            order = {"id": pizza_id, "type": "Pizza", "size": self.selected_size, "ingredients": selected_ingredients}

        elif item_type == 'pasta':
            if not self.selected_pasta_type or not self.selected_sauce:
                messagebox.showwarning("Incomplete Selection", "Please select a pasta type and a sauce!")
                return
            selected_ingredients = [ing for ing, sel in self.pasta_ingredient_states.items() if sel]
            pasta_id = self.pasta_id_counter
            self.pasta_id_counter += 1
            order = {"id": pasta_id, "type": "Pasta", "pasta_type": self.selected_pasta_type, "sauce": self.selected_sauce, "ingredients": selected_ingredients}

        self.basket.append(order)
        self.create_main_screen()

    def format_order_data(self):
        formatted_orders = []
        for item in self.basket:
            if item['type'] == 'Pizza':
                order_data = [item['id'], 'pizza', item['size'].lower()]
                order_data.extend([ingredient.lower() for ingredient in item['ingredients']])
                formatted_orders.append(order_data)
            else:
                order_data = [item['id'], 'pasta', item['pasta_type'].lower(), item['sauce'].lower()]
                order_data.extend([ingredient.lower() for ingredient in item['ingredients']])
                formatted_orders.append(order_data)
        return formatted_orders

    def send_order(self):
        if not self.root or not self.root.winfo_exists(): return
        if not self.basket or not self.customer_address:
            messagebox.showerror("Order Error", "System not fully initialized or basket is empty.")
            return

        formatted_orders = self.format_order_data()
        order_id = random.randint(30000, 39999)

        order_data = {
            'order_id': order_id,
            'customer_id': self.customer_id,
            'customer_address': self.customer_address,
            'items': formatted_orders,
            'total_items': len(self.basket)
        }

        try:
            self.system.submit_manual_order(order_data)
            messagebox.showinfo("Order Sent", f"Order {order_id} submitted to the kitchen! The simulation will now process it.")
            self.basket.clear()
            self.create_main_screen()
        except Exception as e:
            messagebox.showerror("Order Error", f"Failed to submit order: {str(e)}")

    def process_payment(self):
        if not self.root or not self.root.winfo_exists(): return
        if not self.basket:
            messagebox.showwarning("Empty Basket", "Your basket is empty. Please add items before submitting.")
            return

        confirm = messagebox.askyesno(
            "Confirm Order",
            f"Ready to submit order to the kitchen?\n"
            f"Total items: {len(self.basket)}\n\n"
            f"Submit order now?"
        )

        if confirm:
            self.send_order()
            
    # --- Screen Navigation & Creation ---
    def clear_screen(self):
        if self.root:
            for widget in self.root.winfo_children():
                widget.destroy()

    def order_pizza(self):
        self.clear_screen()
        self.create_pizza_screen()

    def order_pasta(self):
        self.clear_screen()
        self.create_pasta_screen()

    def view_basket(self):
        self.clear_screen()
        self.create_basket_screen()

    def create_main_screen(self):
        if not self.root or not self.root.winfo_exists(): return
        self.clear_screen()
        self.ingredient_states = {}
        self.selected_size = None
        self.size_buttons = {}
        self.selected_pasta_type = None
        self.selected_sauce = None
        self.pasta_ingredient_states = {}
        self.pasta_type_buttons = {}
        self.sauce_buttons = {}

        title_label = tk.Label(self.root, text="Manual Food Ordering", font=("Arial", 20, "bold"), bg='white', fg='black')
        title_label.pack(pady=30)

        switch_button = tk.Button(
            self.root,
            text="Switch to Simulation",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            width=20,
            height=1,
            command=self.on_closing
        )
        switch_button.pack(pady=5)

        basket_count = len(self.basket)
        basket_label = tk.Label(self.root, text=f"Items in basket: {basket_count}", font=("Arial", 12), bg='white', fg='black')
        basket_label.pack(pady=10)

        view_basket_button = tk.Button(
            self.root,
            text="View Basket",
            font=("Arial", 12, "bold"),
            bg="#9C27B0",
            fg="white",
            width=15,
            height=2,
            command=self.view_basket
        )
        view_basket_button.pack(pady=10)

        subtitle_label = tk.Label(self.root, text="What would you like to order?", font=("Arial", 14), bg='white', fg='black')
        subtitle_label.pack(pady=20)

        pizza_button = tk.Button(
            self.root,
            text="Pizza",
            font=("Arial", 16, "bold"),
            bg="#ff6b6b",
            fg="white",
            width=20,
            height=3,
            command=self.order_pizza
        )
        pizza_button.pack(pady=15)

        pasta_button = tk.Button(
            self.root,
            text="Pasta",
            font=("Arial", 16, "bold"),
            bg="#4ecdc4",
            fg="white",
            width=20,
            height=3,
            command=self.order_pasta
        )
        pasta_button.pack(pady=15)

        tk.Frame(self.root, bg='white').pack(expand=True, fill='both')

    def create_basket_screen(self):
        if not self.root or not self.root.winfo_exists(): return
        self.clear_screen()
        title_label = tk.Label(self.root, text="Your Basket", font=("Arial", 20, "bold"), bg='white', fg='black')
        title_label.pack(pady=20)

        if not self.basket:
            empty_label = tk.Label(self.root, text="Your basket is empty", font=("Arial", 14), bg='white', fg='black')
            empty_label.pack(pady=50)
        else:
            basket_frame = tk.Frame(self.root, bg='white')
            basket_frame.pack(pady=20, fill='both', expand=True)

            for i, item in enumerate(self.basket):
                item_frame = tk.Frame(basket_frame, bg='white', relief='solid', bd=1)
                item_frame.pack(fill='x', padx=20, pady=5)

                if item['type'] == 'Pizza':
                    ingredients_text = ", ".join(item['ingredients']) if item['ingredients'] else "No extra ingredients"
                    item_text = f"Item {i + 1}: {item['type']} (ID: {item['id']}) - {item['size']}\nIngredients: {ingredients_text}"
                else:
                    ingredients_text = ", ".join(item['ingredients']) if item['ingredients'] else "No extra ingredients"
                    item_text = f"Item {i + 1}: {item['type']} (ID: {item['id']})\nPasta: {item['pasta_type']}\nSauce: {item['sauce']}\nIngredients: {ingredients_text}"

                item_label = tk.Label(item_frame, text=item_text, font=("Arial", 10), bg='white', fg='black', justify='left', anchor='w')
                item_label.pack(padx=10, pady=10, fill='x')

        buttons_frame = tk.Frame(self.root, bg='white')
        buttons_frame.pack(pady=20)

        pay_button = tk.Button(buttons_frame, text="Submit Order to Kitchen", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=20, height=2, command=self.process_payment)
        pay_button.grid(row=0, column=0, padx=10, pady=5)

        back_button = tk.Button(buttons_frame, text="Back to Main Menu", font=("Arial", 12), bg="#cccccc", fg="black", width=15, height=2, command=self.create_main_screen)
        back_button.grid(row=0, column=1, padx=10, pady=5)


    def create_pasta_screen(self):
        if not self.root or not self.root.winfo_exists(): return
        self.clear_screen()
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill='both', expand=True)

        title_label = tk.Label(main_frame, text="Customize Your Pasta", font=("Arial", 18, "bold"), bg='white', fg='black')
        title_label.pack(pady=15)

        pasta_type_label = tk.Label(main_frame, text="Select Pasta Type (choose 1):", font=("Arial", 12, "bold"), bg='white', fg='black')
        pasta_type_label.pack(pady=8)
        pasta_type_frame = tk.Frame(main_frame, bg='white')
        pasta_type_frame.pack(pady=5)
        pasta_types = ["Spaghetti", "Gnocchi", "Macaroni", "Tagliatelle", "Penne"]
        self.pasta_type_buttons = {}

        for i, pasta_type in enumerate(pasta_types):
            row = i // 3; col = i % 3
            pasta_type_button = tk.Button(pasta_type_frame, text=pasta_type, font=("Arial", 10), bg="#f0f0f0", fg="black", width=12, height=2, relief="raised")
            pasta_type_button.config(command=lambda pt=pasta_type, btn=pasta_type_button: self.select_pasta_type(pt, btn))
            pasta_type_button.grid(row=row, column=col, padx=3, pady=3)
            self.pasta_type_buttons[pasta_type] = pasta_type_button

        sauce_label = tk.Label(main_frame, text="Select Sauce (choose 1):", font=("Arial", 12, "bold"), bg='white', fg='black')
        sauce_label.pack(pady=15)
        sauce_frame = tk.Frame(main_frame, bg='white')
        sauce_frame.pack(pady=5)
        sauces = ["Pesto", "Tomato", "Bolognese", "Alfredo", "Arrabiata"]
        self.sauce_buttons = {}

        for i, sauce in enumerate(sauces):
            row = i // 3; col = i % 3
            sauce_button = tk.Button(sauce_frame, text=sauce, font=("Arial", 10), bg="#f0f0f0", fg="black", width=12, height=2, relief="raised")
            sauce_button.config(command=lambda s=sauce, btn=sauce_button: self.select_sauce(s, btn))
            sauce_button.grid(row=row, column=col, padx=3, pady=3)
            self.sauce_buttons[sauce] = sauce_button

        ingredient_label = tk.Label(main_frame, text="Select Toppings (optional):", font=("Arial", 12, "bold"), bg='white', fg='black')
        ingredient_label.pack(pady=15)
        pasta_ingredients = ["Chicken", "Paprika", "Mushroom", "Pepper", "Onion"]
        ingredient_frame = tk.Frame(main_frame, bg='white')
        ingredient_frame.pack(pady=5)

        for i, ingredient in enumerate(pasta_ingredients):
            row = i // 3; col = i % 3
            ingredient_button = tk.Button(ingredient_frame, text=ingredient, font=("Arial", 10), bg="#f0f0f0", fg="black", width=12, height=2, relief="raised")
            ingredient_button.config(command=lambda ing=ingredient, btn=ingredient_button: self.toggle_pasta_ingredient(ing, btn))
            ingredient_button.grid(row=row, column=col, padx=3, pady=3)

        spacer = tk.Frame(main_frame, bg='white', height=10)
        spacer.pack(fill='x', expand=True)

        action_frame = tk.Frame(main_frame, bg='white')
        action_frame.pack(pady=15)

        add_to_basket_button = tk.Button(action_frame, text="Add to Basket", font=("Arial", 12, "bold"), bg="#FF9800", fg="white", width=15, height=2, command=lambda: self.add_to_basket('pasta'))
        add_to_basket_button.grid(row=0, column=0, padx=8, pady=5)
        back_button = tk.Button(action_frame, text="Back to Main Menu", font=("Arial", 12), bg="#cccccc", fg="black", width=15, height=2, command=self.create_main_screen)
        back_button.grid(row=0, column=1, padx=8, pady=5)


    def create_pizza_screen(self):
        if not self.root or not self.root.winfo_exists(): return
        self.clear_screen()
        title_label = tk.Label(self.root, text="Customize Your Pizza", font=("Arial", 20, "bold"), bg='white', fg='black')
        title_label.pack(pady=20)

        size_label = tk.Label(self.root, text="Select Size:", font=("Arial", 14, "bold"), bg='white', fg='black')
        size_label.pack(pady=10)
        size_frame = tk.Frame(self.root, bg='white')
        size_frame.pack(pady=10)
        sizes = ["Small", "Medium", "Large"]
        self.size_buttons = {}

        for i, size in enumerate(sizes):
            size_button = tk.Button(size_frame, text=size, font=("Arial", 12), bg="#f0f0f0", fg="black", width=12, height=2, relief="raised")
            size_button.config(command=lambda s=size, btn=size_button: self.select_size(s, btn))
            size_button.grid(row=0, column=i, padx=10, pady=5)
            self.size_buttons[size] = size_button

        ingredient_label = tk.Label(self.root, text="Select Toppings (optional):", font=("Arial", 14, "bold"), bg='white', fg='black')
        ingredient_label.pack(pady=20)
        ingredients = ["Extra Cheese", "Paprika", "Chicken", "Pepperoni", "Tuna", "Onions", "Mushrooms", "Ham", "Pineapple", "Pepper"]
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=10)

        for i, ingredient in enumerate(ingredients):
            row = i // 3; col = i % 3
            ingredient_button = tk.Button(button_frame, text=ingredient, font=("Arial", 10), bg="#f0f0f0", fg="black", width=15, height=2, relief="raised", wraplength=100)
            ingredient_button.config(command=lambda ing=ingredient, btn=ingredient_button: self.toggle_ingredient(ing, btn))
            ingredient_button.grid(row=row, column=col, padx=8, pady=8)

        action_frame = tk.Frame(self.root, bg='white')
        action_frame.pack(pady=20)

        add_to_basket_button = tk.Button(action_frame, text="Add to Basket", font=("Arial", 14, "bold"), bg="#FF9800", fg="white", width=15, height=2, command=lambda: self.add_to_basket('pizza'))
        add_to_basket_button.grid(row=0, column=0, padx=10, pady=10)
        back_button = tk.Button(action_frame, text="Back to Main Menu", font=("Arial", 12), bg="#cccccc", fg="black", width=15, height=2, command=self.create_main_screen)
        back_button.grid(row=0, column=1, padx=10, pady=10)