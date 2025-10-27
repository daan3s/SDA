# UI_AI.py

import tkinter as tk
from tkinter import messagebox, scrolledtext, Canvas, Scrollbar, Frame
import random
from enum import Enum
import threading
import queue 
from City_AI import houseCoords 
import time

# Define SystemMode 
class SystemMode(Enum):
    """Defines the current operating mode of the system."""
    SIMULATION = 1
    MANUAL_ORDERING = 2

# =========================================================================
# NEW CLASS: TkinterThread 
# ... (TkinterThread remains the same)
# =========================================================================
class TkinterThread(threading.Thread):
    """
    Runs the main Tkinter root and its event loop in a separate thread
    to prevent GIL conflicts with the Pygame thread.
    """
    def __init__(self, system_reference):
        super().__init__(daemon=True) 
        self.system = system_reference
        self.root = None
        self.manual_ui = None
        self.status_ui = None
        self._is_running = False

    def run(self):
        """Called when the thread starts."""
        self.root = tk.Tk()
        self.root.withdraw() 
        
        self.manual_ui = ManualOrderUI(self.system)
        self.status_ui = OrderStatusUI(self.system, self.root)
        
        self.manual_ui.setup_ui_dependencies() 
        
        self._is_running = True
        
        self.root.title("System UI & Controls")
        
        # Start the Tkinter event loop
        try:
            self.root.mainloop()
        except Exception as e:
            # Handle the case where the main loop is exited unexpectedly
            print(f"[Tkinter Thread] Main loop stopped: {e}")
        finally:
            self.stop()


    def schedule_status_update(self, order_statuses, force_all_active=False):
        """Schedules a status update to run safely on the Tkinter thread."""
        if self._is_running and self.root and self.status_ui.root:
            self.root.after(0, lambda: self.status_ui.update_status(order_statuses, force_all_active))

    def schedule_manual_ui_toggle(self, is_manual_mode):
        """Schedules the toggling of the manual UI window visibility."""
        if self._is_running and self.root and self.manual_ui.root:
            if is_manual_mode:
                self.root.after(0, self.manual_ui.root.deiconify)
            else:
                self.root.after(0, self.manual_ui.root.withdraw)
                
    def schedule_show_restaurant_details(self, rest_name, order_data_list):
        """Schedules the display of single restaurant details on the Tkinter thread."""
        if self._is_running and self.root and self.status_ui.root:
            self.root.after(0, lambda: self.status_ui.show_restaurant_details(rest_name, order_data_list))
    
    def stop(self):
        """Stops the Tkinter event loop gracefully."""
        self._is_running = False
        if self.root:
            self.root.quit()

# =========================================================================
# OrderStatusUI (Collapsible Accordion View)
# =========================================================================
class OrderStatusUI:
    def __init__(self, system_reference, main_tk_root):
        self.system = system_reference
        self.root = None
        self.main_tk_root = main_tk_root
        self.expansion_states = {} 
        self.content_frame = None 
        self.canvas = None
        self.current_view_mode = 'ALL_ACTIVE' 
        self.detailed_rest_name = None
        # --- NEW MEMBER for flicker fix ---
        self.last_active_orders_hash = None
        # ----------------------------------
        
        self.start_ui()

    def start_ui(self):
        # ... (start_ui method remains the same) ...
        """Setup the main status window."""
        self.root = tk.Toplevel(self.main_tk_root)
        self.root.title("Order Status & System View")
        self.root.protocol("WM_DELETE_WINDOW", self.close_ui) 
        self.root.geometry("450x700")
        self.root.withdraw() # Start hidden
        
        # Canvas setup for scrollability
        self.canvas = Canvas(self.root, borderwidth=0, background="#F0F0F0")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame to hold the actual content inside the canvas
        self.content_frame = Frame(self.canvas, background="#F0F0F0")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", 
                                  width=450 - scrollbar.winfo_reqwidth())
        
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        
        # Draw initial content
        self.update_status([])
        self.root.deiconify()
        self.current_view_mode = 'ALL_ACTIVE'


    def toggle_orders_view(self, rest_name, header_button, order_frame_reference):
        """Toggle the expansion state of a restaurant's order list in the ALL_ACTIVE view."""
        
        is_expanded = self.expansion_states.get(rest_name, False)
        
        if is_expanded:
            order_frame_reference.pack_forget()
            header_button.config(text=header_button.cget("text").replace("▼", "►"))
        else:
            order_frame_reference.pack(fill='x', padx=0, pady=(0, 0))
            header_button.config(text=header_button.cget("text").replace("►", "▼"))
            
        self.expansion_states[rest_name] = not is_expanded
        
        self.content_frame.update_idletasks() 
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    # ... (show_restaurant_details and _create_order_section methods remain the same) ...
    def show_restaurant_details(self, rest_name, all_orders):
        """Displays all orders (active and completed) for a single restaurant."""
        if not self.root or not self.content_frame or not self.root.winfo_exists():
            return
            
        self.current_view_mode = 'SINGLE_REST'
        self.detailed_rest_name = rest_name
        self.expansion_states = {} # Reset expansion for this new view

        # 1. Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 2. Header
        header_frame = tk.Frame(self.content_frame, bg='#333333', padx=10, pady=10)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame, text=f"{rest_name} - All Orders & History", 
                 font=("Arial", 14, "bold"), fg='white', bg='#333333').pack(fill='x')
        
        # Separating Active and Completed Orders
        active_orders = [o for o in all_orders if o['type'] == 'ACTIVE']
        completed_orders = [o for o in all_orders if o['type'] == 'COMPLETED']

        # 3. Active Orders Section
        self._create_order_section(
            "Active Orders", 
            active_orders, 
            '#FFD700', 
            self.content_frame
        )

        # 4. Completed Orders Section (History)
        self._create_order_section(
            f"Order History ({len(completed_orders)} Completed)", 
            completed_orders, 
            '#90EE90', 
            self.content_frame
        )
        
        # 5. Back Button
        # Calls the Main System method which will trigger a schedule_status_update with force_all_active=True
        back_button = tk.Button(self.content_frame, text="<< Back to All Active Orders",
                                command=self.system.schedule_status_update_all)
        back_button.pack(pady=10)


        # 6. Final canvas update for scrolling
        self.content_frame.update_idletasks() 
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _create_order_section(self, title, orders, color, parent_frame):
        """Helper to create collapsible or non-collapsible sections for the single restaurant view."""
        
        section_frame = tk.Frame(parent_frame, bg='#F0F0F0', padx=0, pady=0)
        section_frame.pack(fill='x', padx=5, pady=(5, 0))
        
        is_expanded = self.expansion_states.get(title, True)
        button_indicator = "▼" if is_expanded else "►"
        
        # 1. Create the button object without the command argument
        header_button = tk.Button(
            section_frame,
            text=f"{button_indicator} {title}",
            font=("Arial", 11, "bold"),
            bg=color, fg="black",
            activebackground="#D3D3D3",
            anchor='w',
            relief='flat',
            padx=5
        )
        # 2. Assign the command, capturing the necessary arguments
        header_button.config(
            command=lambda name=title, section=section_frame: self.toggle_single_section_view(name, section)
        )
        header_button.pack(fill='x')
        
        details_frame = tk.Frame(section_frame, bg='#FFFFFF', bd=1, relief=tk.SOLID)
        if is_expanded:
            details_frame.pack(fill='x', padx=0, pady=(0, 0)) 
        self.expansion_states[title] = is_expanded

        if not orders:
            tk.Label(details_frame, text="No orders in this category.", bg='white', padx=10).pack(fill='x', pady=5)
            
        for i, order in enumerate(orders):
            # Format display line
            status_line = f"ID: {order['order_id']} | Cust: {order['customer_id']} | Status: {order['state']}"
            
            if order.get('type') == 'ACTIVE':
                status_line += f" | Items: {order.get('items_ready', 0)}/{order.get('items_total', 0)} Ready"
            
            elif order.get('type') == 'COMPLETED':
                try:
                    ts = order.get('completion_time')
                    if ts and isinstance(ts, (int, float)):
                        time_str = time.strftime('%H:%M:%S', time.localtime(ts))
                        status_line += f" | Completed at: {time_str}"
                except:
                    pass

            
            # Order Label
            order_label = tk.Label(
                details_frame, 
                text=status_line, 
                font=("Courier", 10, "bold" if order.get('is_current') else "normal"), 
                bg='white', 
                fg='black', 
                anchor='w', 
                padx=10, 
                pady=5
            )
            order_label.pack(fill='x')
            
            if i < len(orders) - 1:
                tk.Frame(details_frame, height=1, bg='#CCCCCC').pack(fill='x', padx=10) 

    def toggle_single_section_view(self, title, section_frame):
        # ... (toggle_single_section_view method remains the same) ...
        """Specialized toggle for sections within the single restaurant view."""
        
        # Get the header button and details frame based on pack order
        header_button = section_frame.winfo_children()[0]
        details_frame = section_frame.winfo_children()[1]
        
        is_expanded = self.expansion_states.get(title, True)

        if is_expanded:
            details_frame.pack_forget()
            header_button.config(text=header_button.cget("text").replace("▼", "►"))
        else:
            details_frame.pack(fill='x', padx=0, pady=(0, 0))
            header_button.config(text=header_button.cget("text").replace("►", "▼"))
            
        self.expansion_states[title] = not is_expanded
        
        self.content_frame.update_idletasks() 
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    # --- MODIFIED METHOD: Includes caching and comparison ---
    def update_status(self, orders_data, force_all_active=False):
        """Updates the default ALL_ACTIVE view."""
        if not self.root or not self.content_frame or not self.root.winfo_exists():
            return
            
        # Only update if we are in the default mode or explicitly told to switch back
        if self.current_view_mode == 'SINGLE_REST' and not force_all_active:
            return

        self.current_view_mode = 'ALL_ACTIVE'
        
        # --- FIX: Caching and Comparison ---
        # 1. Create a hash of the current order data for comparison
        # Sort the data by order_id and state to ensure the hash is consistent
        # We only care about the elements that determine the layout (not the items_ready count, which updates frequently)
        
        # Extract the elements that define the structure/state for hashing:
        hashable_data = []
        for order in orders_data:
             # Tuple: (restaurant_name, order_id, state)
             hashable_data.append((order.get('restaurant_name'), order.get('order_id'), order.get('state')))
             
        hashable_data.sort()
        
        current_data_hash = hash(tuple(hashable_data))
        
        # 2. Check if the layout/state has changed since the last update
        if current_data_hash == self.last_active_orders_hash and not force_all_active:
             # Data structure and high-level status haven't changed, skip redraw
             return 
             
        self.last_active_orders_hash = current_data_hash
        # --- END FIX ---
        
        # 3. Clear existing content (only if data/view has changed)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Title for All Active View
        tk.Label(self.content_frame, text="Active Orders (System-Wide)", 
                 font=("Arial", 14, "bold"), bg='#F0F0F0').pack(fill='x', padx=5, pady=5)


        if not orders_data:
            tk.Label(self.content_frame, text="No active orders in the kitchen queue.", bg='white', font=("Arial", 10)).pack(pady=20)
            self.content_frame.update_idletasks() 
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            return

        # 4. Group orders by restaurant
        restaurants_orders = {}
        for order in orders_data:
            rest_name = order.get('restaurant_name', 'Unknown Restaurant') 
            if rest_name not in restaurants_orders:
                restaurants_orders[rest_name] = []
            restaurants_orders[rest_name].append(order)

        # 5. Create a collapsible section for each restaurant
        for rest_name, orders in restaurants_orders.items():
            order_count = len(orders)
            # Use the stored expansion state (or default to False)
            is_expanded = self.expansion_states.get(rest_name, False)
            
            rest_frame = tk.Frame(self.content_frame, bg='#E0E0E0', padx=0, pady=0)
            rest_frame.pack(fill='x', padx=5, pady=(5, 0))
            
            order_details_frame = tk.Frame(rest_frame, bg='#FFFFFF', bd=1, relief=tk.SOLID)
            
            button_indicator = "▼" if is_expanded else "►"
            button_text = f"{button_indicator} {rest_name} ({order_count} Orders)"
            
            # 1. Create the button object 
            header_button = tk.Button(
                rest_frame,
                text=button_text,
                font=("Arial", 11, "bold"),
                bg="#A9A9A9", fg="white",
                activebackground="#909090",
                anchor='w',
                relief='flat',
                padx=5,
            )
            
            # 2. Assign the command (Fixing the previous UnboundLocalError)
            header_button.config(
                command=lambda name=rest_name, btn=header_button, details=order_details_frame: self.toggle_orders_view(name, btn, details)
            )
            
            header_button.pack(fill='x')
            
            if is_expanded:
                order_details_frame.pack(fill='x', padx=0, pady=(0, 0)) 
            
            # Populate the order details frame
            for i, order in enumerate(orders):
                order_id = order.get('order_id', 'N/A')
                state = order.get('state', 'Unknown')
                items_total = order.get('items_total', 0)
                items_ready = order.get('items_ready', 0)
                
                status_text = f"ID: {order_id} | Status: {state} | Items: {items_ready}/{items_total} Ready"
                
                order_label = tk.Label(
                    order_details_frame, 
                    text=status_text, 
                    font=("Courier", 10), 
                    bg='white', 
                    fg='black', 
                    anchor='w', 
                    padx=10, 
                    pady=2
                )
                order_label.pack(fill='x')
                
                if i < order_count - 1:
                    tk.Frame(order_details_frame, height=1, bg='#CCCCCC').pack(fill='x', padx=10) 
            
        # 6. Final canvas update for scrolling
        self.content_frame.update_idletasks() 
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def close_ui(self):
        """Called when the user tries to close the status window."""
        self.root.withdraw() # Simply hide it, don't destroy it (could be reopened)

# ... (ManualOrderUI class remains the same) ...
class ManualOrderUI:
    def __init__(self, system_reference):
        self.system = system_reference
        self.root = None
        self.selected_items = []
        self.pizza_id_counter = 5000
        self.pasta_id_counter = 6000
        self.order_id_counter = 9000
        
        # Customer Mock Data
        self.customer_id = "MANUAL_CUST_1"
        # Set a default coordinate (e.g., house 1 from houseCoords)
        self.customer_address = houseCoords[0]
        
    def setup_ui_dependencies(self):
        """Called by the thread after the main root is created."""
        self._initialize_main_window()
        self._setup_content_frames()
        self.root.withdraw() # Start hidden

    def _initialize_main_window(self):
        self.root = tk.Toplevel()
        self.root.title("Manual Food Ordering")
        self.root.geometry("600x800")
        # Ensure it doesn't close the whole app, but just hides itself
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw) 
        self.root.configure(bg='white')
        
    def _setup_content_frames(self):
        # Header
        tk.Label(self.root, text="Place a Custom Order", font=("Arial", 16, "bold"), fg="white", bg="#FF5722", pady=10).pack(fill='x')

        # Menu Selection
        menu_frame = tk.Frame(self.root, bg='white', padx=20, pady=10)
        menu_frame.pack(fill='x')
        
        tk.Label(menu_frame, text="Menu Items:", font=("Arial", 14, "bold"), bg='white', anchor='w').pack(fill='x', pady=5)
        
        # Pizza Button
        tk.Button(menu_frame, text="Add Pizza 🍕", font=("Arial", 12), bg="#4CAF50", fg="white", 
                  command=lambda: self._show_pizza_dialog()).pack(side='left', padx=10, pady=5)
        # Pasta Button
        tk.Button(menu_frame, text="Add Pasta 🍝", font=("Arial", 12), bg="#2196F3", fg="white", 
                  command=lambda: self._show_pasta_dialog()).pack(side='left', padx=10, pady=5)
        
        # Order Basket Display
        self.basket_frame = tk.Frame(self.root, bg='#F5F5F5', padx=10, pady=10, bd=2, relief=tk.GROOVE)
        self.basket_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(self.basket_frame, text="Order Basket:", font=("Arial", 14, "bold"), bg='#F5F5F5', anchor='w').pack(fill='x', pady=5)
        
        # Scrollable area for items
        self.basket_canvas = Canvas(self.basket_frame, bg='#F5F5F5', borderwidth=0)
        self.basket_canvas.pack(side="left", fill="both", expand=True)
        
        basket_scrollbar = Scrollbar(self.basket_frame, orient="vertical", command=self.basket_canvas.yview)
        basket_scrollbar.pack(side="right", fill="y")
        
        self.basket_canvas.configure(yscrollcommand=basket_scrollbar.set)
        
        self.basket_content_frame = Frame(self.basket_canvas, bg='#F5F5F5')
        self.basket_canvas.create_window((0, 0), window=self.basket_content_frame, anchor="nw", width=550)
        
        self.basket_content_frame.bind("<Configure>", lambda e: self.basket_canvas.configure(scrollregion = self.basket_canvas.bbox("all")))

        # Action Buttons
        self._update_basket_display()
        
    def _show_pizza_dialog(self):
        # Constants from Customer_AI logic
        sizes = ['small', 'medium', 'large', 'family']
        all_toppings = ['cheese', 'mushrooms', 'onions', 'peppers', 'sausage', 'bacon', 'spinach', 'extra cheese']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Customize Pizza")
        dialog.geometry("300x400")
        dialog.transient(self.root) 
        dialog.grab_set() 
        
        selected_size = tk.StringVar(dialog, sizes[1]) # Default to medium
        selected_toppings = {topping: tk.BooleanVar(dialog) for topping in all_toppings}

        tk.Label(dialog, text="Size:").pack(pady=5)
        size_menu = tk.OptionMenu(dialog, selected_size, *sizes)
        size_menu.pack()
        
        tk.Label(dialog, text="Toppings:").pack(pady=10)
        
        # Scrollable area for toppings
        topping_canvas = Canvas(dialog)
        topping_frame = Frame(topping_canvas)
        v_scrollbar = Scrollbar(dialog, orient="vertical", command=topping_canvas.yview)
        topping_canvas.configure(yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.pack(side="right", fill="y")
        topping_canvas.pack(fill="both", expand=True)
        topping_canvas.create_window((0, 0), window=topping_frame, anchor="nw", width=250)

        for topping, var in selected_toppings.items():
            tk.Checkbutton(topping_frame, text=topping, variable=var).pack(anchor='w')

        topping_frame.update_idletasks()
        topping_canvas.config(scrollregion=topping_canvas.bbox("all"))

        def add_pizza():
            pizza_toppings = [t for t, v in selected_toppings.items() if v.get()]
            
            item = {
                'type': 'Pizza',
                'item_id': self.pizza_id_counter,
                'size': selected_size.get(),
                'ingredients': pizza_toppings
            }
            self.pizza_id_counter += 1
            self.selected_items.append(item)
            self._update_basket_display()
            dialog.destroy()

        tk.Button(dialog, text="Add to Order", command=add_pizza).pack(pady=10)
        self.root.wait_window(dialog)


    def _show_pasta_dialog(self):
        # Constants from Customer_AI logic
        pastas = ['spaghetti', 'penne', 'fettuccine', 'macaroni', 'gnocchi', 'tagliatelle']
        sauces = ['tomato', 'alfredo', 'pesto', 'bolognese', 'arrabiata', 'carbonara']
        all_toppings = ['chicken', 'mushrooms', 'onions', 'peppers', 'paprika', 'spinach', 'bacon', 'parmesan', 'basil']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Customize Pasta")
        dialog.geometry("300x450")
        dialog.transient(self.root) 
        dialog.grab_set() 
        
        selected_pasta = tk.StringVar(dialog, pastas[0]) 
        selected_sauce = tk.StringVar(dialog, sauces[0]) 
        selected_toppings = {topping: tk.BooleanVar(dialog) for topping in all_toppings}

        tk.Label(dialog, text="Pasta Type:").pack(pady=5)
        pasta_menu = tk.OptionMenu(dialog, selected_pasta, *pastas)
        pasta_menu.pack()
        
        tk.Label(dialog, text="Sauce:").pack(pady=5)
        sauce_menu = tk.OptionMenu(dialog, selected_sauce, *sauces)
        sauce_menu.pack()
        
        tk.Label(dialog, text="Toppings:").pack(pady=10)
        
        # Scrollable area for toppings
        topping_canvas = Canvas(dialog)
        topping_frame = Frame(topping_canvas)
        v_scrollbar = Scrollbar(dialog, orient="vertical", command=topping_canvas.yview)
        topping_canvas.configure(yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.pack(side="right", fill="y")
        topping_canvas.pack(fill="both", expand=True)
        topping_canvas.create_window((0, 0), window=topping_frame, anchor="nw", width=250)

        for topping, var in selected_toppings.items():
            tk.Checkbutton(topping_frame, text=topping, variable=var).pack(anchor='w')
            
        topping_frame.update_idletasks()
        topping_canvas.config(scrollregion=topping_canvas.bbox("all"))

        def add_pasta():
            pasta_toppings = [t for t, v in selected_toppings.items() if v.get()]
            
            item = {
                'type': 'Pasta',
                'item_id': self.pasta_id_counter,
                'pasta_type': selected_pasta.get(),
                'sauce': selected_sauce.get(),
                'ingredients': pasta_toppings
            }
            self.pasta_id_counter += 1
            self.selected_items.append(item)
            self._update_basket_display()
            dialog.destroy()

        tk.Button(dialog, text="Add to Order", command=add_pasta).pack(pady=10)
        self.root.wait_window(dialog)
        
    def _remove_item(self, item_id_to_remove):
        self.selected_items = [item for item in self.selected_items if item['item_id'] != item_id_to_remove]
        self._update_basket_display()

    def _update_basket_display(self):
        # Clear basket content frame
        for widget in self.basket_content_frame.winfo_children():
            widget.destroy()
            
        if not self.selected_items:
            tk.Label(self.basket_content_frame, text="Your basket is empty. Add items to order.", bg='#F5F5F5', pady=20).pack()
        else:
            for i, item in enumerate(self.selected_items):
                item_type = item['type']
                
                if item_type == "Pizza":
                    item_details = f"{item['size'].capitalize()} Pizza"
                elif item_type == "Pasta":
                    item_details = f"{item['pasta_type'].capitalize()} with {item['sauce'].capitalize()} Sauce"
                
                ingredients_text = ", ".join(item.get('ingredients', [])).capitalize()
                
                item_display = tk.Frame(self.basket_content_frame, bd=1, relief=tk.SOLID, padx=10, pady=5, bg='white')
                item_display.pack(fill='x', padx=5, pady=5)
                
                # Item Description
                desc_frame = tk.Frame(item_display, bg='white')
                desc_frame.pack(fill='x')
                
                tk.Label(desc_frame, text=f"{i+1}. {item_details}", font=("Arial", 12, "bold"), bg='white', anchor='w').pack(side='left', fill='x', expand=True)
                
                # Remove Button
                remove_button = tk.Button(desc_frame, text="X", fg="red", bg='white', relief='flat', 
                                          command=lambda item_id=item['item_id']: self._remove_item(item_id))
                remove_button.pack(side='right')

                if ingredients_text:
                    tk.Label(item_display, text=f"  Toppings: {ingredients_text}", font=("Arial", 10), bg='white', anchor='w').pack(fill='x')

        # Update scrollable region
        self.basket_content_frame.update_idletasks()
        self.basket_canvas.config(scrollregion=self.basket_canvas.bbox("all"))

        # Re-draw submit button area
        for widget in self.root.winfo_children():
            # Find the action frame (the one with the submit button)
            if widget.winfo_class() == 'Frame':
                # Check for the frame that contains the submit button (heuristic based on previous layout)
                children = widget.winfo_children()
                if children and children[0].winfo_class() == 'Button' and children[0].cget('text') == 'Submit Order':
                     widget.destroy()
                     break


        action_frame = tk.Frame(self.root, bg='white')
        action_frame.pack(pady=20)

        submit_button = tk.Button(action_frame, text="Submit Order", font=("Arial", 14, "bold"), bg="#FF5722", fg="white", width=15, height=2, command=self.process_payment, 
                                  state=tk.NORMAL if self.selected_items else tk.DISABLED)
        submit_button.pack()
        
    def process_payment(self):
        if not self.selected_items:
            messagebox.showerror("Error", "Your order basket is empty.")
            return

        order_id = self.order_id_counter
        self.order_id_counter += 1
        
        # Format items for the system (match the format generated by Customer_AI)
        formatted_items = []
        for item in self.selected_items:
            item_list = [item['item_id'], item['type'].lower()]
            if item['type'] == 'Pizza':
                item_list.append(item['size'])
            elif item['type'] == 'Pasta':
                item_list.extend([item['pasta_type'], item['sauce']])
            
            item_list.extend(item['ingredients'])
            formatted_items.append(item_list)
            
        order_data = {
            'order_id': order_id,
            'customer_id': self.customer_id,
            'customer_address': self.customer_address, # Coordinates as the 'address' for routing
            'items': formatted_items
        }
        
        # Submit to the main system thread
        self.system.submit_manual_order(order_data)

        # Clear UI
        self.selected_items = []
        self._update_basket_display()
        messagebox.showinfo("Order Placed", f"Order {order_id} submitted! A drone will be dispatched soon.")