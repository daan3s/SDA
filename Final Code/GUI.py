import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import json

# Global variables to track ingredient states
ingredient_states = {}
selected_size = None
size_buttons = {}  # Dictionary to track size buttons
basket = []  # List to store orders

# Pasta selection variables
selected_pasta_type = None
selected_sauce = None
pasta_ingredient_states = {}
pasta_type_buttons = {}  # Dictionary to track pasta type buttons
sauce_buttons = {}  # Dictionary to track sauce buttons

# Counter for generating unique IDs
pizza_id_counter = 1000
pasta_id_counter = 2000

# Network settings - Default to broadcast, but can be changed to specific IP
TARGET_PORT = 5004
TARGET_IP = "145.93.93.128"  # Default: broadcast to all





def order_pizza():
    # Clear main screen
    for widget in root.winfo_children():
        widget.destroy()

    # Create pizza customization screen
    create_pizza_screen()


def order_pasta():
    # Clear main screen
    for widget in root.winfo_children():
        widget.destroy()

    # Create pasta customization screen
    create_pasta_screen()


def toggle_ingredient(ingredient, button):
    # Toggle the state
    ingredient_states[ingredient] = not ingredient_states.get(ingredient, False)

    # Update button appearance
    if ingredient_states[ingredient]:
        button.config(bg="#4CAF50", relief="sunken")  # Green when selected
    else:
        button.config(bg="#f0f0f0", relief="raised")  # Normal when not selected


def toggle_pasta_ingredient(ingredient, button):
    # Toggle the state
    pasta_ingredient_states[ingredient] = not pasta_ingredient_states.get(ingredient, False)

    # Update button appearance
    if pasta_ingredient_states[ingredient]:
        button.config(bg="#4CAF50", relief="sunken")  # Green when selected
    else:
        button.config(bg="#f0f0f0", relief="raised")  # Normal when not selected


def select_size(size, button):
    global selected_size

    # If clicking the same size, deselect it
    if selected_size == size:
        # Deselect current size
        selected_size = None
        button.config(bg="#f0f0f0", relief="raised")
    else:
        # Deselect previously selected size if any
        if selected_size and selected_size in size_buttons:
            size_buttons[selected_size].config(bg="#f0f0f0", relief="raised")

        # Select new size
        selected_size = size
        button.config(bg="#2196F3", relief="sunken")  # Blue when selected


def select_pasta_type(pasta_type, button):
    global selected_pasta_type

    # If clicking the same pasta type, deselect it
    if selected_pasta_type == pasta_type:
        # Deselect current pasta type
        selected_pasta_type = None
        button.config(bg="#f0f0f0", relief="raised")
    else:
        # Deselect previously selected pasta type if any
        if selected_pasta_type and selected_pasta_type in pasta_type_buttons:
            pasta_type_buttons[selected_pasta_type].config(bg="#f0f0f0", relief="raised")

        # Select new pasta type
        selected_pasta_type = pasta_type
        button.config(bg="#2196F3", relief="sunken")  # Blue when selected


def select_sauce(sauce, button):
    global selected_sauce

    # If clicking the same sauce, deselect it
    if selected_sauce == sauce:
        # Deselect current sauce
        selected_sauce = None
        button.config(bg="#f0f0f0", relief="raised")
    else:
        # Deselect previously selected sauce if any
        if selected_sauce and selected_sauce in sauce_buttons:
            sauce_buttons[selected_sauce].config(bg="#f0f0f0", relief="raised")

        # Select new sauce
        selected_sauce = sauce
        button.config(bg="#2196F3", relief="sunken")  # Blue when selected


def add_pasta_to_basket():
    global selected_pasta_type, selected_sauce, pasta_ingredient_states, pasta_id_counter

    # Check if pasta type is selected
    if not selected_pasta_type:
        messagebox.showwarning("No Pasta Type Selected", "Please select a pasta type!")
        return

    # Check if sauce is selected
    if not selected_sauce:
        messagebox.showwarning("No Sauce Selected", "Please select a sauce!")
        return

    # Get selected pasta ingredients
    selected_pasta_ingredients = [ingredient for ingredient, selected in pasta_ingredient_states.items() if selected]

    # Calculate extra cost for toppings
    topping_cost = len(selected_pasta_ingredients) * 0.75

    # Generate unique pasta ID
    pasta_id = pasta_id_counter
    pasta_id_counter += 1

    # Create order dictionary
    order = {
        "id": pasta_id,
        "type": "Pasta",
        "pasta_type": selected_pasta_type,
        "sauce": selected_sauce,
        "ingredients": selected_pasta_ingredients,
        "topping_cost": topping_cost
    }

    # Add to basket
    basket.append(order)

    # Return to main screen (no confirmation message)
    create_main_screen()


def add_to_basket():
    global selected_size, ingredient_states, pizza_id_counter

    # Check if a size is selected
    if not selected_size:
        messagebox.showwarning("No Size Selected", "Please select a pizza size!")
        return

    # Get selected ingredients
    selected_ingredients = [ingredient for ingredient, selected in ingredient_states.items() if selected]

    # Calculate extra cost for toppings
    topping_cost = len(selected_ingredients) * 0.75

    # Generate unique pizza ID
    pizza_id = pizza_id_counter
    pizza_id_counter += 1

    # Create order dictionary
    order = {
        "id": pizza_id,
        "type": "Pizza",
        "size": selected_size,
        "ingredients": selected_ingredients,
        "topping_cost": topping_cost
    }

    # Add to basket
    basket.append(order)

    # Return to main screen (no confirmation message)
    create_main_screen()


def view_basket():
    # Clear screen
    for widget in root.winfo_children():
        widget.destroy()

    # Create basket screen
    create_basket_screen()


def format_order_data():
    """Format the basket data as requested"""
    formatted_orders = []

    for item in basket:
        if item['type'] == 'Pizza':
            # Format: [pizzaID, 'pizza', size, ingredient1, ingredient2, ...]
            order_data = [item['id'], 'pizza', item['size'].lower()]
            # Add all ingredients
            order_data.extend([ingredient.lower() for ingredient in item['ingredients']])
            formatted_orders.append(order_data)
        else:  # Pasta
            # Format: [pastaID, 'pasta', pasta_type, sauce, ingredient1, ingredient2, ...]
            order_data = [item['id'], 'pasta', item['pasta_type'].lower(), item['sauce'].lower()]
            # Add all ingredients
            order_data.extend([ingredient.lower() for ingredient in item['ingredients']])
            formatted_orders.append(order_data)

    return formatted_orders


def configure_target_ip():
    """Allow user to set specific target IP"""
    global TARGET_IP

    new_ip = simpledialog.askstring(
        "Configure Target IP",
        "Enter the kitchen laptop's IP address:",
        initialvalue=TARGET_IP
    )

    if new_ip:
        TARGET_IP = new_ip
        messagebox.showinfo("Success", f"Target IP set to: {TARGET_IP}")


def send_order():
    """Send order to target IP (specific or broadcast)"""
    if not basket:
        messagebox.showwarning("Empty Basket", "Your basket is empty. Please add items before sending.")
        return

    # Format the order data
    formatted_orders = format_order_data()

    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # If using broadcast address, enable broadcast option
        if TARGET_IP == "255.255.255.255":
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Prepare data to send
        data_to_send = {
            "orders": formatted_orders,
            "total_items": len(basket),
            "source": "FoodOrderingApp"
        }

        # Convert to JSON and send
        json_data = json.dumps(data_to_send)
        sock.sendto(json_data.encode('utf-8'), (TARGET_IP, TARGET_PORT))
        sock.close()

        if TARGET_IP == "255.255.255.255":
            message = f"Order broadcasted to all devices on port {TARGET_PORT}!"
        else:
            message = f"Order sent to {TARGET_IP}:{TARGET_PORT}!"

        messagebox.showinfo("Success", f"{message}\n\nOrder data:\n{formatted_orders}")

        # Clear basket after successful payment
        basket.clear()

        # Return to main screen
        create_main_screen()

    except Exception as e:
        messagebox.showerror("Send Error", f"Failed to send order: {str(e)}\n\nTarget: {TARGET_IP}:{TARGET_PORT}")


def process_payment():
    """Process payment and send order directly"""
    if not basket:
        messagebox.showwarning("Empty Basket", "Your basket is empty. Please add items before paying.")
        return

    # Format the order data
    formatted_orders = format_order_data()

    target_info = "all devices on network" if TARGET_IP == "255.255.255.255" else TARGET_IP

    # Ask for confirmation before sending
    confirm = messagebox.askyesno(
        "Confirm Payment",
        f"Ready to send order to kitchen?\n\n"
        f"Target: {target_info}\n"
        f"Total items: {len(basket)}\n\n"
        f"Send order now?"
    )

    if confirm:
        send_order()


def create_basket_screen():
    # Title
    title_label = tk.Label(
        root,
        text="Your Basket",
        font=("Arial", 20, "bold"),
        bg='white',
        fg='black'
    )
    title_label.pack(pady=20)

    if not basket:
        # Empty basket message
        empty_label = tk.Label(
            root,
            text="Your basket is empty",
            font=("Arial", 14),
            bg='white',
            fg='black'
        )
        empty_label.pack(pady=50)
    else:
        # Basket items frame
        basket_frame = tk.Frame(root, bg='white')
        basket_frame.pack(pady=20, fill='both', expand=True)

        # Display each item in basket
        for i, item in enumerate(basket):
            item_frame = tk.Frame(basket_frame, bg='white', relief='solid', bd=1)
            item_frame.pack(fill='x', padx=20, pady=5)

            # Item details - different format for pizza vs pasta
            if item['type'] == 'Pizza':
                ingredients_text = ", ".join(item['ingredients']) if item['ingredients'] else "No extra ingredients"
                item_text = f"Item {i + 1}: {item['type']} (ID: {item['id']}) - {item['size']}\nIngredients: {ingredients_text}\nToppings cost: €{item['topping_cost']:.2f}"
            else:  # Pasta
                ingredients_text = ", ".join(item['ingredients']) if item['ingredients'] else "No extra ingredients"
                item_text = f"Item {i + 1}: {item['type']} (ID: {item['id']})\nPasta: {item['pasta_type']}\nSauce: {item['sauce']}\nIngredients: {ingredients_text}\nToppings cost: €{item['topping_cost']:.2f}"

            item_label = tk.Label(
                item_frame,
                text=item_text,
                font=("Arial", 10),
                bg='white',
                fg='black',
                justify='left',
                anchor='w'
            )
            item_label.pack(padx=10, pady=10, fill='x')

    # Buttons frame
    buttons_frame = tk.Frame(root, bg='white')
    buttons_frame.pack(pady=20)

    # Pay & Send button
    pay_button = tk.Button(
        buttons_frame,
        text="Pay & Send to Kitchen",
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        width=20,
        height=2,
        command=process_payment
    )
    pay_button.grid(row=0, column=0, padx=10, pady=5)

    # Configure IP button
    config_button = tk.Button(
        buttons_frame,
        text="Set Target IP",
        font=("Arial", 10),
        bg="#2196F3",
        fg="white",
        width=12,
        height=1,
        command=configure_target_ip
    )
    config_button.grid(row=1, column=0, padx=10, pady=5)

    # Back button
    back_button = tk.Button(
        buttons_frame,
        text="Back to Main Menu",
        font=("Arial", 12),
        bg="#cccccc",
        fg="black",
        width=15,
        height=2,
        command=create_main_screen
    )
    back_button.grid(row=0, column=1, padx=10, pady=5)


def create_pasta_screen():
    global pasta_type_buttons, sauce_buttons

    # Create a main frame to control positioning
    main_frame = tk.Frame(root, bg='white')
    main_frame.pack(fill='both', expand=True)

    # Title
    title_label = tk.Label(
        main_frame,
        text="Customize Your Pasta",
        font=("Arial", 18, "bold"),
        bg='white',
        fg='black'
    )
    title_label.pack(pady=15)

    # Pasta Type selection section
    pasta_type_label = tk.Label(
        main_frame,
        text="Select Pasta Type (choose 1):",
        font=("Arial", 12, "bold"),
        bg='white',
        fg='black'
    )
    pasta_type_label.pack(pady=8)

    # Pasta Type buttons frame
    pasta_type_frame = tk.Frame(main_frame, bg='white')
    pasta_type_frame.pack(pady=5)

    # Pasta Type buttons - 2 rows to fit better
    pasta_types = ["Spaghetti", "Gnocchi", "Macaroni", "Tagliatelle", "Penne"]
    pasta_type_buttons = {}  # Reset the dictionary

    for i, pasta_type in enumerate(pasta_types):
        row = i // 3  # 3 buttons per row
        col = i % 3

        pasta_type_button = tk.Button(
            pasta_type_frame,
            text=pasta_type,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="black",
            width=12,
            height=2,
            relief="raised"
        )

        pasta_type_button.config(
            command=lambda pt=pasta_type, btn=pasta_type_button: select_pasta_type(pt, btn)
        )

        pasta_type_button.grid(row=row, column=col, padx=3, pady=3)
        pasta_type_buttons[pasta_type] = pasta_type_button  # Store button reference

    # Sauce selection section
    sauce_label = tk.Label(
        main_frame,
        text="Select Sauce (choose 1):",
        font=("Arial", 12, "bold"),
        bg='white',
        fg='black'
    )
    sauce_label.pack(pady=15)

    # Sauce buttons frame
    sauce_frame = tk.Frame(main_frame, bg='white')
    sauce_frame.pack(pady=5)

    # Sauce buttons - 2 rows to fit better
    sauces = ["Pesto", "Tomato", "Bolognese", "Alfredo", "Arrabiata"]
    sauce_buttons = {}  # Reset the dictionary

    for i, sauce in enumerate(sauces):
        row = i // 3  # 3 buttons per row
        col = i % 3

        sauce_button = tk.Button(
            sauce_frame,
            text=sauce,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="black",
            width=12,
            height=2,
            relief="raised"
        )

        sauce_button.config(
            command=lambda s=sauce, btn=sauce_button: select_sauce(s, btn)
        )

        sauce_button.grid(row=row, column=col, padx=3, pady=3)
        sauce_buttons[sauce] = sauce_button  # Store button reference

    # Ingredients section
    ingredient_label = tk.Label(
        main_frame,
        text="Select Toppings (€0.75 each):",
        font=("Arial", 12, "bold"),
        bg='white',
        fg='black'
    )
    ingredient_label.pack(pady=15)

    # Pasta ingredients
    pasta_ingredients = ["Chicken", "Paprika", "Mushroom", "Pepper", "Onion"]

    # Create ingredient buttons frame
    ingredient_frame = tk.Frame(main_frame, bg='white')
    ingredient_frame.pack(pady=5)

    # Create buttons in a grid (3 columns) - same format as others
    for i, ingredient in enumerate(pasta_ingredients):
        row = i // 3
        col = i % 3

        # Create button with initial state
        ingredient_button = tk.Button(
            ingredient_frame,
            text=ingredient,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="black",
            width=12,
            height=2,
            relief="raised"
        )

        # Set command to toggle function
        ingredient_button.config(
            command=lambda ing=ingredient, btn=ingredient_button: toggle_pasta_ingredient(ing, btn)
        )

        ingredient_button.grid(row=row, column=col, padx=3, pady=3)

    # Spacer to push buttons to bottom
    spacer = tk.Frame(main_frame, bg='white', height=10)
    spacer.pack(fill='x', expand=True)

    # Buttons frame for Add to Basket and Back
    action_frame = tk.Frame(main_frame, bg='white')
    action_frame.pack(pady=15)

    # Add to Basket button
    add_to_basket_button = tk.Button(
        action_frame,
        text="Add to Basket",
        font=("Arial", 12, "bold"),
        bg="#FF9800",
        fg="white",
        width=15,
        height=2,
        command=add_pasta_to_basket
    )
    add_to_basket_button.grid(row=0, column=0, padx=8, pady=5)

    # Back button
    back_button = tk.Button(
        action_frame,
        text="Back to Main Menu",
        font=("Arial", 12),
        bg="#cccccc",
        fg="black",
        width=15,
        height=2,
        command=create_main_screen
    )
    back_button.grid(row=0, column=1, padx=8, pady=5)


def create_pizza_screen():
    global size_buttons

    # Title
    title_label = tk.Label(
        root,
        text="Customize Your Pizza",
        font=("Arial", 20, "bold"),
        bg='white',
        fg='black'
    )
    title_label.pack(pady=20)

    # Size selection section
    size_label = tk.Label(
        root,
        text="Select Size:",
        font=("Arial", 14, "bold"),
        bg='white',
        fg='black'
    )
    size_label.pack(pady=10)

    # Size buttons frame
    size_frame = tk.Frame(root, bg='white')
    size_frame.pack(pady=10)

    # Size buttons
    sizes = ["Small", "Medium", "Large"]
    size_buttons = {}  # Reset the dictionary

    for i, size in enumerate(sizes):
        size_button = tk.Button(
            size_frame,
            text=size,
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="black",
            width=12,
            height=2,
            relief="raised"
        )

        size_button.config(
            command=lambda s=size, btn=size_button: select_size(s, btn)
        )

        size_button.grid(row=0, column=i, padx=10, pady=5)
        size_buttons[size] = size_button  # Store button reference

    # Ingredients section
    ingredient_label = tk.Label(
        root,
        text="Select Toppings (€0.75 each):",
        font=("Arial", 14, "bold"),
        bg='white',
        fg='black'
    )
    ingredient_label.pack(pady=20)

    # Pizza ingredients - updated names
    ingredients = [
        "Extra Cheese", "Paprika", "Chicken", "Pepperoni", "Tuna",
        "Onions", "Mushrooms", "Ham", "Pineapple", "Pepper"
    ]

    # Create ingredient buttons
    button_frame = tk.Frame(root, bg='white')
    button_frame.pack(pady=10)

    # Create buttons in a grid (3 columns)
    for i, ingredient in enumerate(ingredients):
        row = i // 3
        col = i % 3

        # Create button with initial state
        ingredient_button = tk.Button(
            button_frame,
            text=ingredient,
            font=("Arial", 10),  # Slightly smaller font to fit longer names
            bg="#f0f0f0",
            fg="black",
            width=15,
            height=2,
            relief="raised",
            wraplength=100  # Allow text to wrap if needed
        )

        # Set command to toggle function
        ingredient_button.config(
            command=lambda ing=ingredient, btn=ingredient_button: toggle_ingredient(ing, btn)
        )

        ingredient_button.grid(row=row, column=col, padx=8, pady=8)

    # Buttons frame for Add to Basket and Back
    action_frame = tk.Frame(root, bg='white')
    action_frame.pack(pady=20)

    # Add to Basket button
    add_to_basket_button = tk.Button(
        action_frame,
        text="Add to Basket",
        font=("Arial", 14, "bold"),
        bg="#FF9800",
        fg="white",
        width=15,
        height=2,
        command=add_to_basket
    )
    add_to_basket_button.grid(row=0, column=0, padx=10, pady=10)

    # Back button
    back_button = tk.Button(
        action_frame,
        text="Back to Main Menu",
        font=("Arial", 12),
        bg="#cccccc",
        fg="black",
        width=15,
        height=2,
        command=create_main_screen
    )
    back_button.grid(row=0, column=1, padx=10, pady=10)


def create_main_screen():
    # Clear screen
    for widget in root.winfo_children():
        widget.destroy()

    # Reset ingredient states when returning to main screen
    global ingredient_states, selected_size, size_buttons, selected_pasta_type, selected_sauce, pasta_ingredient_states, pasta_type_buttons, sauce_buttons
    ingredient_states = {}
    selected_size = None
    size_buttons = {}
    selected_pasta_type = None
    selected_sauce = None
    pasta_ingredient_states = {}
    pasta_type_buttons = {}
    sauce_buttons = {}

    # Title
    title_label = tk.Label(
        root,
        text="Welcome to Food Ordering",
        font=("Arial", 20, "bold"),
        bg='white',
        fg='black'
    )
    title_label.pack(pady=30)

    # Basket info
    basket_count = len(basket)
    basket_label = tk.Label(
        root,
        text=f"Items in basket: {basket_count}",
        font=("Arial", 12),
        bg='white',
        fg='black'
    )
    basket_label.pack(pady=10)

    # Target info
    target_info = "All devices" if TARGET_IP == "255.255.255.255" else TARGET_IP
    target_label = tk.Label(
        root,
        text=f"Target: {target_info}:{TARGET_PORT}",
        font=("Arial", 10),
        bg='white',
        fg='gray'
    )
    target_label.pack(pady=5)

    # Configure IP button
    config_button = tk.Button(
        root,
        text="Set Target IP",
        font=("Arial", 10),
        bg="#2196F3",
        fg="white",
        width=12,
        height=1,
        command=configure_target_ip
    )
    config_button.pack(pady=5)

    # View Basket Button
    view_basket_button = tk.Button(
        root,
        text="View Basket",
        font=("Arial", 12, "bold"),
        bg="#9C27B0",
        fg="white",
        width=15,
        height=2,
        command=view_basket
    )
    view_basket_button.pack(pady=10)

    # Subtitle
    subtitle_label = tk.Label(
        root,
        text="What would you like to order?",
        font=("Arial", 14),
        bg='white',
        fg='black'
    )
    subtitle_label.pack(pady=20)

    # Pizza Button
    pizza_button = tk.Button(
        root,
        text="Pizza",
        font=("Arial", 16, "bold"),
        bg="#ff6b6b",
        fg="white",
        width=20,
        height=3,
        command=order_pizza
    )
    pizza_button.pack(pady=15)

    # Pasta Button
    pasta_button = tk.Button(
        root,
        text="Pasta",
        font=("Arial", 16, "bold"),
        bg="#4ecdc4",
        fg="white",
        width=20,
        height=3,
        command=order_pasta
    )
    pasta_button.pack(pady=15)


# Create main window
root = tk.Tk()
root.title("Food Ordering App")
root.geometry("500x800")
root.configure(bg='white')

# Start with main screen
create_main_screen()

# Start the application
root.mainloop()