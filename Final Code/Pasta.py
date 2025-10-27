# Pasta.py
class Pasta:
    def __init__(self, item_data):
        # item_data format: [pasta_id, 'pasta', pasta_type, sauce, topping1, topping2, ...]
        self.PastaID = item_data[0]
        self.Type = 'pasta'
        self.PastaType = item_data[2]
        self.Sauce = item_data[3]
        self.Toppings = item_data[4:] if len(item_data) > 4 else []
        self.Status = "pending"
        self.Price = self.CalculatePrice()

    def CalculatePrice(self):
        """Calculate price compatible with your existing system"""
        base_prices = {
            'spaghetti': 12, 'penne': 11, 'fettuccine': 13,
            'macaroni': 10, 'gnocchi': 14, 'tagliatelle': 13
        }
        base_price = base_prices.get(self.PastaType, 12)

        sauce_prices = {'alfredo': 2, 'pesto': 1, 'bolognese': 2, 'carbonara': 3}
        sauce_price = sauce_prices.get(self.Sauce, 0)

        toppings_price = len(self.Toppings) * 1.0

        return base_price + sauce_price + toppings_price

    def GetPrice(self):
        return self.Price

    def GetStatus(self):
        return self.Status

    def GetDescription(self):
        toppings_str = ", ".join(self.Toppings) if self.Toppings else "no extra toppings"
        return f"{self.PastaType.title()} with {self.Sauce} sauce - ${self.Price:.2f}"

    def GetDetailedDescription(self):
        """More detailed description for order display"""
        toppings_str = "no extra toppings" if not self.Toppings else ", ".join(self.Toppings)
        return f"Pasta #{self.PastaID}: {self.PastaType.title()} with {self.Sauce} sauce and {toppings_str} - ${self.Price:.2f}"

    def set_status(self, status):
        self.Status = status

    def to_list_format(self):
        """Convert back to your list format for compatibility"""
        return [self.PastaID, 'pasta', self.PastaType, self.Sauce] + self.Toppings