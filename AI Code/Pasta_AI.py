statusList = ['Plain', 'Raw', 'Heating up', 'Done']


class Pasta():
    def __init__(self, toppings, pastaType, pastaSauce, pastaID, size):
        self.pastaID = pastaID
        self.toppingsList = toppings
        self.price = len(toppings) * 0.75
        self.status = statusList[0]
        self.type = pastaType
        self.sauce = pastaSauce
        self.size = size
        self.bakingTime = 0

    def CalculatePrice(self):
        price = self.price

        # Calculate price based on pasta type
        if (self.type == 'Spaghetti' or self.type == 'Macaroni' or self.type == 'Penne'):
            price += 1
        elif (self.type == 'Tagliatelle' or self.type == 'Gnocchi'):
            price += 2

        # Calculate price based on sauce
        if (self.sauce == 'Alfredo' or self.sauce == 'Bolognese' or self.sauce == 'Arrabiata'):
            price += 2
        elif (self.sauce == 'Tomato' or self.sauce == 'Pesto'):
            price += 1

        # Calculate price based on size
        if (self.size == 'Large'):
            price += 5
        elif (self.size == 'Medium'):
            price += 3
        elif (self.size == 'Small'):
            price += 1

        return price

    def GetStatus(self):
        return self.status

    def GetID(self):
        return self.pastaID

    def IsBaking(self, maxTime, InOven):
        if InOven:
            if self.status == 'Plain':
                self.status = 'Raw'

            if self.status in ['Raw', 'Heating up']:
                self.bakingTime += 1

                if self.bakingTime >= maxTime:
                    self.status = 'Done'
                elif self.bakingTime >= maxTime * 0.7:
                    self.status = 'Heating up'
                else:
                    self.status = 'Raw'

        return self.status in ['Raw', 'Heating up']

    def GetDescription(self):
        toppings_str = ', '.join(self.toppingsList) if self.toppingsList else 'no toppings'

        pasta_description = f"{self.pastaID}: The {self.type} pasta with sauce: {self.sauce}, toppings: {toppings_str}, and size: {self.size} has status {self.status}."

        return pasta_description  # Fixed: return instead of print