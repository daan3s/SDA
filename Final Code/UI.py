# UI.py

import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame
import threading
import time
from enum import Enum


# Define SystemMode (Kept for conceptual completeness, though not strictly used for mode switching anymore)
class SystemMode(Enum):
    """Defines the current operating mode of the system."""
    SIMULATION = 1
    MANUAL_ORDERING = 2


# =========================================================================
# TkinterThread
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
        self.status_ui = None
        self._is_running = False

    def run(self):
        """Called when the thread starts."""
        self.root = tk.Tk()
        self.root.withdraw()

        self.status_ui = OrderStatusUI(self.system, self.root)

        self._is_running = True

        self.root.title("System UI & Controls")

        # Start the Tkinter event loop
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"[Tkinter Thread] Main loop stopped: {e}")
        finally:
            self.stop()

    def schedule_status_update(self, order_statuses):
        """Schedules a status update to run safely on the Tkinter thread."""
        if self._is_running and self.root and self.status_ui.root:
            self.root.after(0, lambda: self.status_ui.update_status(order_statuses))

    def stop(self):
        """Stops the Tkinter event loop gracefully."""
        self._is_running = False
        if self.root:
            # We must use quit() here to stop the mainloop
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
        # NEW: Member for flicker fix (data comparison)
        self.last_active_orders_hash = None

        self.start_ui()

    def start_ui(self):
        """Setup the main status window."""
        self.root = tk.Toplevel(self.main_tk_root)
        self.root.title("Order Status - All Active Orders")
        # Hide the main root window close button if possible, but keep Toplevel closable
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
        self.root.geometry("450x700")

        # Canvas setup for scrollability
        self.canvas = Canvas(self.root, borderwidth=0, background="#F0F0F0")
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Frame to hold the actual content inside the canvas
        self.content_frame = Frame(self.canvas, background="#F0F0F0")
        # Ensure the content frame fills the width
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw",
                                  width=450 - scrollbar.winfo_reqwidth())

        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Draw initial content
        self.update_status([])
        self.root.deiconify()

    def toggle_orders_view(self, rest_name, header_button, order_frame_reference):
        """Toggle the expansion state of a restaurant's order list."""

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

    def update_status(self, orders_data):
        """Updates the default ALL_ACTIVE view."""
        if not self.root or not self.content_frame or not self.root.winfo_exists():
            return

        # 1. Create a hash of the current order data for comparison (Flicker Fix)
        hashable_data = []
        for order in orders_data:
            # Tuple: (restaurant_name, order_id, state)
            hashable_data.append((order.get('restaurant_name'), order.get('order_id'), order.get('state')))

        hashable_data.sort()
        current_data_hash = hash(tuple(hashable_data))

        # 2. Check if the layout/state has changed since the last update
        if current_data_hash == self.last_active_orders_hash:
            # Only data inside the expanded frames (items_ready) would change.
            # We rely on Pygame's update loop to schedule the next full status update.
            return

        self.last_active_orders_hash = current_data_hash

        # 3. Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Title for All Active View
        tk.Label(self.content_frame, text="Active Orders (System-Wide)",
                 font=("Arial", 14, "bold"), bg='#F0F0F0').pack(fill='x', padx=5, pady=5)

        if not orders_data:
            tk.Label(self.content_frame, text="No active orders in the kitchen queue or in transit.", bg='white',
                     font=("Arial", 10)).pack(pady=20)
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
            is_expanded = self.expansion_states.get(rest_name, False)

            rest_frame = tk.Frame(self.content_frame, bg='#E0E0E0', padx=0, pady=0)
            rest_frame.pack(fill='x', padx=5, pady=(5, 0))

            order_details_frame = tk.Frame(rest_frame, bg='#FFFFFF', bd=1, relief=tk.SOLID)

            button_indicator = "▼" if is_expanded else "►"
            button_text = f"{button_indicator} {rest_name} ({order_count} Orders)"

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

            # Use lambda to assign the command safely
            header_button.config(
                command=lambda name=rest_name, btn=header_button, details=order_details_frame: self.toggle_orders_view(
                    name, btn, details)
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