# Pizza.py
class Pizza:
    def __init__(self, item_data):
        # item_data format: [pizza_id, 'pizza', size, topping1, topping2, ...]
        self.PizzaID = item_data[0]
        self.Type = 'pizza'
        self.Size = item_data[2]
        self.Toppings = item_data[3:] if len(item_data) > 3 else []
        self.Status = "pending"
        self.bakingTime = 5
        self.Price = self.CalculatePrice()

    def CalculatePrice(self):
        """Calculate price compatible with your existing system"""
        base_prices = {'small': 10, 'medium': 15, 'large': 20}
        base_price = base_prices.get(self.Size, 15)
        toppings_price = len(self.Toppings) * 1.5
        return base_price + toppings_price

    def GetPrice(self):
        return self.Price

    def GetStatus(self):
        return self.Status

    def GetDescription(self):
        if not self.Toppings:
            return f"{self.Size.title()} Cheese Pizza - ${self.Price:.2f}"
        else:
            toppings_str = ", ".join(self.Toppings)
            return f"{self.Size.title()} Pizza with {toppings_str} - ${self.Price:.2f}"

    def GetDetailedDescription(self):
        """More detailed description for order display"""
        toppings_str = "Cheese" if not self.Toppings else ", ".join(self.Toppings)
        return f"Pizza #{self.PizzaID}: {self.Size.title()} with {toppings_str} - ${self.Price:.2f}"

    def IsBaking(self):
        return self.Status == "baking"

    def set_status(self, status):
        self.Status = status

    def to_list_format(self):
        """Convert back to your list format for compatibility"""
        return [self.PizzaID, 'pizza', self.Size] + self.Toppings