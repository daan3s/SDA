import pygame
import time


class Chef:
    def __init__(self, x, y):
        # Attributes from class diagram
        self.Name = "Chef"  # str - default name
        self.ChefAvailable = True  # bool - matches diagram
        self.ChefStatus = "Available"  # str - matches diagram (fixed typo from CheftStatus)

        # Visual properties
        self.x = x
        self.y = y
        self.image_chef = pygame.image.load("chef.png").convert_alpha()
        self.chef_width = 100
        self.chef_height = 100
        self.surface_chef = pygame.transform.scale(self.image_chef, (self.chef_width, self.chef_height))
        self.rect_chef = self.surface_chef.get_rect(center=(self.x, self.y))

        # State management
        self.state = "waiting"
        self.holding = None
        self.duration = 0
        self.speed = 1

        # Order management
        self.current_order = []
        self.current_item = None

        # Available options
        self.toppings_Pizza = ["extra cheese", "pepperoni", "mushrooms", "onions", "tuna", "ham", "pepper", "chicken",
                               "pineapple", "paprika"]
        self.pizza_size = ["small", "medium", "large"]
        self.toppings_Pasta = ["chicken", "paprika", "mushrooms", "pepper", "onion"]
        self.pasta_type = ["spaghetti", "gnocchi", "macaroni", "tagliatelle", "penne"]
        self.pasta_sauce = ["pesto", "tomato", "bolognese", "alfredo", "arrabiata"]

        # Base prices
        self.base_price = {
            'pizza': {'small': 8, 'medium': 12, 'large': 16},
            'pasta': {'spaghetti': 10, 'gnocchi': 12, 'macaroni': 9, 'tagliatelle': 11, 'penne': 10}
        }

    # Public operations from class diagram
    def prepare_pizza(self, size_index=1):
        """Prepare a pizza - matches diagram operation"""
        if not self.ChefAvailable:
            print("Chef is not available")
            return None

        self.ChefAvailable = False
        self.ChefStatus = "Preparing Pizza"

        size = self.pizza_size[size_index]
        pizza = {
            'type': 'pizza',
            'size': size,
            'toppings': [],
            'base_price': self.base_price['pizza'][size],
            'cooking_method': None,
            'is_cooked': False
        }
        self.current_item = pizza
        self.current_order.append(pizza)
        self.state = "preparing pizza"
        print(f"Preparing {size} pizza")
        return pizza

    def prepare_pasta(self, pasta_type_index=0, sauce_index=0):
        """Prepare pasta - matches diagram operation"""
        if not self.ChefAvailable:
            print("Chef is not available")
            return None

        self.ChefAvailable = False
        self.ChefStatus = "Preparing Pasta"

        pasta_type = self.pasta_type[pasta_type_index]
        sauce_type = self.pasta_sauce[sauce_index]

        pasta = {
            'type': 'pasta',
            'pasta_type': pasta_type,
            'sauce_type': sauce_type,
            'toppings': [],
            'base_price': self.base_price['pasta'][pasta_type],
            'cooking_method': None,
            'is_cooked': False
        }
        self.current_item = pasta
        self.current_order.append(pasta)
        self.state = "preparing pasta"
        print(f"Preparing {pasta_type} with {sauce_type} sauce")
        return pasta

    def get_order_description(self, order):
        """Get order description - matches diagram operation"""
        if order['type'] == 'pizza':
            toppings = ', '.join(order['toppings']) if order['toppings'] else 'no toppings'
            return f"{order['size']} Pizza with {toppings}"
        else:
            toppings = ', '.join(order['toppings']) if order['toppings'] else 'no toppings'
            return f"{order['pasta_type']} Pasta with {order['sauce_type']} sauce and {toppings}"

    def add_pizza_topping(self, topping_index):
        """Add pizza topping - matches diagram operation"""
        if self.current_item and self.current_item['type'] == 'pizza':
            if 0 <= topping_index < len(self.toppings_Pizza):
                topping = self.toppings_Pizza[topping_index]
                self.current_item['toppings'].append(topping)
                print(f"Added {topping} to pizza")
                return True
        return False

    def add_pasta_topping(self, topping_index):
        """Add pasta topping - additional method for pasta"""
        if self.current_item and self.current_item['type'] == 'pasta':
            if 0 <= topping_index < len(self.toppings_Pasta):
                topping = self.toppings_Pasta[topping_index]
                self.current_item['toppings'].append(topping)
                print(f"Added {topping} to pasta")
                return True
        return False

    # Private operations from class diagram
    def _prepare_keys(self, key):
        """Handle keyboard input - private method from diagram"""
        # Pizza sizes
        if key == pygame.K_1:
            self.prepare_pizza(0)  # small
        elif key == pygame.K_2:
            self.prepare_pizza(1)  # Medium
        elif key == pygame.K_3:
            self.prepare_pizza(2)  # Large

        # Pasta types
        elif key == pygame.K_5:
            self.prepare_pasta(0)  # Spaghetti
        elif key == pygame.K_6:
            self.prepare_pasta(1)  # Gnocchi
        elif key == pygame.K_7:
            self.prepare_pasta(2)  # Macaroni
        elif key == pygame.K_8:
            self.prepare_pasta(3)  # Tagliatelle
        elif key == pygame.K_9:
            self.prepare_pasta(4)  # Penne

        # Pizza toppings
        elif key == pygame.K_q:
            self.add_pizza_topping(0)  # extra cheese
        elif key == pygame.K_w:
            self.add_pizza_topping(1)  # Pepperoni
        elif key == pygame.K_e:
            self.add_pizza_topping(2)  # Mushrooms
        elif key == pygame.K_r:
            self.add_pizza_topping(3)  # onions
        elif key == pygame.K_t:
            self.add_pizza_topping(4)  # tuna
        elif key == pygame.K_y:
            self.add_pizza_topping(5)  # ham
        elif key == pygame.K_u:
            self.add_pizza_topping(6)  # pepper
        elif key == pygame.K_i:
            self.add_pizza_topping(7)  # chicken
        elif key == pygame.K_o:
            self.add_pizza_topping(8)  # pineapple
        elif key == pygame.K_p:
            self.add_pizza_topping(9)  # paprika

        # Pasta toppings
        elif key == pygame.K_a:
            self.add_pasta_topping(0)  # chicken
        elif key == pygame.K_s:
            self.add_pasta_topping(1)  # paprika
        elif key == pygame.K_d:
            self.add_pasta_topping(2)  # mushrooms
        elif key == pygame.K_f:
            self.add_pasta_topping(3)  # pepper
        elif key == pygame.K_g:
            self.add_pasta_topping(4)  # onions

        # Pasta sauce selection
        elif key == pygame.K_z:
            if self.current_item and self.current_item['type'] == 'pasta':
                self.current_item['sauce_type'] = self.pasta_sauce[0]  # pesto
        elif key == pygame.K_x:
            if self.current_item and self.current_item['type'] == 'pasta':
                self.current_item['sauce_type'] = self.pasta_sauce[1]  # tomato
        elif key == pygame.K_c:
            if self.current_item and self.current_item['type'] == 'pasta':
                self.current_item['sauce_type'] = self.pasta_sauce[2]  # bolognese
        elif key == pygame.K_v:
            if self.current_item and self.current_item['type'] == 'pasta':
                self.current_item['sauce_type'] = self.pasta_sauce[3]  # alfredo
        elif key == pygame.K_b:
            if self.current_item and self.current_item['type'] == 'pasta':
                self.current_item['sauce_type'] = self.pasta_sauce[4]  # arrabiata

    # Public operations from class diagram
    def set_oven_cooking(self):
        """Set oven cooking - matches diagram operation"""
        if self.current_item:
            self.current_item['cooking_method'] = 'oven'
            self.state = "cooking"
            self.ChefStatus = "Cooking in Oven"
            print(f"Set to cook in oven")
            return True
        return False

    def set_pan_cooking(self):
        """Set pan cooking - matches diagram operation"""
        if self.current_item:
            self.current_item['cooking_method'] = 'pan'
            self.state = "cooking"
            self.ChefStatus = "Cooking in Pan"
            print(f"Set to cook in pan")
            return True
        return False

    # Private operations from class diagram
    def _update_cooking(self):
        """Update cooking progress - private method from diagram"""
        if self.state == "cooking" and self.current_item:
            self.duration += self.speed
            if self.duration >= 100:
                self.current_item['is_cooked'] = True
                self.state = "waiting"
                self.ChefStatus = "Available"
                self.ChefAvailable = True
                self.duration = 0
                item_name = self.get_item_description(self.current_item)
                print(f"Finished cooking {item_name}!")
                self.current_item = None

    def get_item_description(self, item):
        """Get item description - matches diagram operation"""
        if item['type'] == 'pizza':
            toppings = ', '.join(item['toppings']) if item['toppings'] else 'no toppings'
            return f"{item['size']} pizza with {toppings}"
        else:
            toppings = ', '.join(item['toppings']) if item['toppings'] else 'no toppings'
            return f"{item['pasta_type']} with {item['sauce_type']} sauce and {toppings}"

    # Additional helper methods
    def update(self):
        """Update chef state"""
        self._update_cooking()

    def show_chef(self, screen):
        """Display chef on screen"""
        screen.blit(self.surface_chef, self.rect_chef)

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self._prepare_keys(event.key)

    def get_status(self):
        """Get current chef status"""
        return {
            'name': self.Name,
            'available': self.ChefAvailable,
            'status': self.ChefStatus,
            'current_item': self.current_item,
            'state': self.state
        }

    def complete_order(self):
        """Complete the current order and reset chef"""
        self.current_order = []
        self.current_item = None
        self.state = "waiting"
        self.ChefAvailable = True
        self.ChefStatus = "Available"
        print("Order completed, chef is available")


# Example usage in main loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    chef = Chef(400, 300)
    last_real_time_update = time.time()

    running = True
    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            chef.handle_event(event)

        # Real-time updating
        if current_time - last_real_time_update >= 1.0:
            last_real_time_update = current_time
            real_time = time.strftime('%H:%M:%S')
            print(f"Real time: {real_time}")

        # Update chef
        chef.update()

        # Draw everything
        screen.fill((255, 255, 255))
        chef.show_chef(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()