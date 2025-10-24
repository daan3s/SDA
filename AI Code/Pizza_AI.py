statusList = ['Plain', 'Raw', 'Heating up', 'Done']


class Pizza():
    def __init__(self, toppings, pizzaSize, pizzaID):
        self.pizzaID = pizzaID
        self.toppingsList = toppings  # get the toppings of the pizza
        self.price = len(toppings) * 0.75  # set a price based on toppings
        self.status = statusList[0]
        self.size = pizzaSize
        self.bakingTime = 0

    def GetPrice(self): #Define the prize of the pizza
        base_price = self.price
        if (self.size == 'Large'):
            return base_price + 5
        if (self.size == 'Medium'):
            return base_price + 3
        if (self.size == 'Small'):
            return base_price + 1
        return base_price  # default case

    def GetStatus(self):  # Determine status of pizza
        return self.status

    def GetID(self):  # Get pizza ID
        return self.pizzaID

    def IsBaking(self, maxTime, InOven):
        if InOven:
            if self.status == 'Plain':
                self.status = 'Raw'  # Start baking

            if self.status in ['Raw', 'Heating up']:
                self.bakingTime += 1

                # Progress through baking stages
                if self.bakingTime >= maxTime:
                    self.status = 'Done'
                elif self.bakingTime >= maxTime * 0.7:  # 70% baked
                    self.status = 'Heating up'
                else:
                    self.status = 'Raw'

        return self.status in ['Raw', 'Heating up']  # Return True if still baking

    def GetDescription(self):
        toppings_str = ', '.join(self.toppingsList) if self.toppingsList else 'no toppings'
        return f"{self.pizzaID}: The pizza with toppings: {toppings_str} and size: {self.size} has status {self.status}."