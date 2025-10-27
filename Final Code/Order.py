# Order.py

class Order:
    def __init__(self, order_data, pizza_class, pasta_class):
        self.OrderID = order_data['order_id']
        self.CustomerData = {
            'customer_id': order_data['customer_id'],
            'customer_address': order_data['customer_address']
        }
        self.PizzaClass = pizza_class
        self.PastaClass = pasta_class
        self.Products = self._create_products(order_data['items'])
        self.Status = "received"
        self.Restaurant = None

    def _create_products(self, items_list):
        """Convert your list items to Pizza/Pasta objects"""
        products = []
        for item in items_list:
            if item[1] == 'pizza':
                products.append(self.PizzaClass(item))
            elif item[1] == 'pasta':
                products.append(self.PastaClass(item))
        return products

    def AddPizza(self, pizza_data):
        """Add pizza using your list format"""
        pizza = self.PizzaClass(pizza_data)
        self.Products.append(pizza)
        return pizza

    def AddPasta(self, pasta_data):
        """Add pasta using your list format"""
        pasta = self.PastaClass(pasta_data)
        self.Products.append(pasta)
        return pasta

    def CalculateTotal(self):
        return sum(product.GetPrice() for product in self.Products)

    def GetStatus(self):
        return self.Status

    def MakeDescription(self):
        products_desc = [product.GetDescription() for product in self.Products]
        products_str = "\n  - ".join(products_desc)
        return f"Order #{self.OrderID} - Total: ${self.CalculateTotal():.2f}\n  - {products_str}"

    def DisplayFullOrderDetails(self):
        """Display complete order details in terminal"""
        print("\n" + "=" * 60)
        print(f"📦 ORDER #{self.OrderID} DETAILS")
        print("=" * 60)
        print(f"Customer: {self.CustomerData['customer_id']}")
        print(f"Address: {self.CustomerData['customer_address']}")
        print(f"Status: {self.Status}")
        print("-" * 40)

        # Combine and display all products together
        all_products = self.get_all_products()
        total = 0

        for i, product in enumerate(all_products, 1):
            print(f"{i}. {product.GetDetailedDescription()}")
            total += product.GetPrice()

        print("-" * 40)
        print(f"TOTAL: ${total:.2f}")
        print("=" * 60 + "\n")

    def get_all_products(self):
        """Get all products combined (both pizzas and pastas)"""
        return self.Products

    def get_pizzas(self):
        """Get only pizza products"""
        return [product for product in self.Products if hasattr(product, 'Type') and product.Type == 'pizza']

    def get_pastas(self):
        """Get only pasta products"""
        return [product for product in self.Products if hasattr(product, 'Type') and product.Type == 'pasta']

    def get_items_by_type(self, item_type):
        """Get items by type ('pizza' or 'pasta')"""
        return [product for product in self.Products if hasattr(product, 'Type') and product.Type == item_type]

    def set_status(self, status):
        self.Status = status

    def to_dict_format(self):
        """Convert back to your dictionary format for compatibility"""
        return {
            'order_id': self.OrderID,
            'customer_id': self.CustomerData['customer_id'],
            'customer_address': self.CustomerData['customer_address'],
            'items': [product.to_list_format() for product in self.Products],
            'total_items': len(self.Products)
        }

    def get_order_summary(self):
        """Get a quick summary of the order"""
        pizzas = self.get_pizzas()
        pastas = self.get_pastas()
        return {
            'order_id': self.OrderID,
            'total_items': len(self.Products),
            'pizza_count': len(pizzas),
            'pasta_count': len(pastas),
            'total_price': self.CalculateTotal()
        }