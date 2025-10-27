import random


class Customer:
    def __init__(self, customerID, customerAddress):
        self.CustomerID = customerID
        self.CustomerAddress = customerAddress
        self.pizza_id_counter = 1000  # Start pizza IDs at 1000
        self.pasta_id_counter = 2000  # Start pasta IDs at 2000

    def GenerateOrder(self):
        """Generate an order with multiple pizzas and/or pastas"""
        order_id = random.randint(1000, 9999)

        # Decide how many items in this order (1-3 items)
        num_items = random.randint(1, 3)
        order_items = []

        for _ in range(num_items):
            item_type = random.choice(['pizza', 'pasta'])

            if item_type == 'pizza':
                order_items.append(self._generate_pizza_item())
            else:
                order_items.append(self._generate_pasta_item())

        # Combine all items into one order
        order_data = {
            'order_id': order_id,
            'customer_id': self.CustomerID,
            'customer_address': self.CustomerAddress,
            'items': order_items,
            'total_items': num_items
        }

        return order_data

    def ReceiveOrder(self):
        """Receive order - returns bool"""
        return True

    def _generate_pizza_item(self):
        """Generate one pizza item with any combination of toppings"""
        sizes = ['small', 'medium', 'large']
        all_toppings = ['cheese', 'pepperoni', 'mushrooms', 'onions', 'chicken', 'ham', 'pineapple', 'olives',
                        'peppers', 'sausage', 'bacon', 'spinach']

        pizza_id = self.pizza_id_counter
        self.pizza_id_counter += 1

        size = random.choice(sizes)

        # Choose any number of toppings (0 to all toppings)
        num_toppings = random.randint(0, len(all_toppings))
        selected_toppings = random.sample(all_toppings, num_toppings)

        # Format: [pizzaID, 'pizza', size, topping1, topping2, ...]
        pizza_item = [pizza_id, 'pizza', size] + selected_toppings
        return pizza_item

    def _generate_pasta_item(self):
        """Generate one pasta item with any combination of toppings"""
        pastas = ['spaghetti', 'penne', 'fettuccine', 'macaroni', 'gnocchi', 'tagliatelle']
        sauces = ['tomato', 'alfredo', 'pesto', 'bolognese', 'arrabiata', 'carbonara']
        all_toppings = ['chicken', 'mushrooms', 'onions', 'peppers', 'paprika', 'spinach', 'bacon', 'parmesan', 'basil']

        pasta_id = self.pasta_id_counter
        self.pasta_id_counter += 1

        pasta_type = random.choice(pastas)
        sauce = random.choice(sauces)

        # Choose any number of toppings (0 to all toppings)
        num_toppings = random.randint(0, len(all_toppings))
        selected_toppings = random.sample(all_toppings, num_toppings)

        # Format: [pastaID, 'pasta', pasta_type, sauce, topping1, ...]
        pasta_item = [pasta_id, 'pasta', pasta_type, sauce] + selected_toppings
        return pasta_item