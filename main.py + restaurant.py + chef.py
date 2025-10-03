import pygame
import math
import time
import datetime





#initialize game
pygame.init()
clock = pygame.time.Clock()

# set window to full screen 
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)


# define constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Italiën_restaurant:
    def __init__(self, x, y):
         self.clock = pygame.time.Clock()
         self.game_start_time = datetime.datetime.now()
         self.last_real_time_update = time.time()
         self.openingTime = datetime.time(15, 0)
         self.closingTime = datetime.time(23, 0)
         self.restaurant_open = False

         self.image_restaurant = pygame.image.load(image.name).convert_alpha # image whole restaurant
         maxWidth = SCREEN_WIDTH 
         maxHeight = SCREEN_HEIGHT
         self.place_restaurant = self.image.get_place(center = (maxWidth, maxHeight))


         
         
                  
         
    def check_opening_hours(self):
         current_time = datetime.datetime.now().time()
         self.restaurant_open = self.openingTime <= current_time <= self.closingTime
         return self.restaurant_open
    
    def show_opening_hours(self):
        return f"open: {self.openingTime.strftime('%H:%M')} - {self.closingTime.strftime('%H:%M')}"
    
    def show_openStatus(self):
        if self.restaurant_open == True:
            return "OPEN"
        else: 
            return "CLOSED"
        
    def get_real_world_time(self):
        return datetime.datetime.now()
    
    def get_elaspsed_real_time(self):
        return datetime.datetime.now() - self.game_start_time
    
    
    
    def receive_order():
        return##################################################################


        
class chef:
    def __init__(self, x, y):
        self.x = 500 #location chef
        self.y = 500
        self.image_chef = pygame.image.load("chef.png").convert_alpha() #making image of chef
        self.chef_width = 100
        self.chef_height = 100
        self.surface_chef = pygame.transform.scale(self.image_chef, (self.chef_width, self.chef_height))
        self.rect_chef = self.image_chef.get_place(center = (self.x, self.y))

        self.state =  "waiting"
        self.holding = None

        self.duration = 0  
        self.speed = 1

        self.current_order = []
        self.current_item = None
        self.toppings_Pizza = ["extra cheese", "pepperoni", "mushrooms", "onions", "tuna", "ham", "pepper", "chicken", "pineapple", "paprika"]
        self.pizza_size = ["small", "medium", "large"]
        self.toppings_Pasta = ["chicken", "paprika", "mushrooms", "pepper", "onion"]
        self.pasta_type = ["spaghetti", "gnocchi", "macaroni", "tagliatelle", "penne"]
        self.pasta_sauce = ["pesto", "tomato", "bolognese", "alfredo", "arrabiata"]


    
    def prepare_pizza(self, size_index=1):
        size = self.pizza_size[size_index]

        pizza = {
            'type': 'pizza', 
            'size': size,
            'toppings': [],
            'base price': self.base_price['pizza'][size],
            'cooking_method': None, 
            'is_cooked': False
        }
        self.current_item = pizza
        self.current_order.append(pizza)
        self.state = "preparing pizza"
        return pizza
    
    def prepare_pasta(self, pasta_type_index=0, sauce_index=0):
        pasta_type = self.pasta_type[pasta_type_index]
        sauce_type = self.pasta_sauce[sauce_index]
        
        pasta = {
            'type' : 'pasta',
            'pasta type' : pasta_type,
            'sauce type' : sauce_type,
            'toppings': [],
            'base price': self.base_price['pasta'][pasta_type],
            'cooking_method' : None,
            'is_cooked' : False
        }
        self.current_item = pasta
        self.current_order.append(pasta)
        self.state = "preparing pasta"
        return pasta
    
    
       
    def get_order_description(self, order):
        if order['type'] == 'pizza':
            toppings = ', '.join(order['toppings'])
            return f"{order['size']} {order['crust']} Pizza with {toppings}"
        else:
            toppings = ', '.join(order['toppings'])
            return f"{order['pasta_type']} Pasta with {order['sauce']} sauce and {toppings}"
        

    # Add topping methods
    def add_pizza_topping(self, topping_index):
        if self.current_item and self.current_item['type'] == 'pizza':
            if 0 <= topping_index < len(self.toppings_Pizza):
                topping = self.toppings_Pizza[topping_index]
                self.current_item['toppings'].append(topping)
                print(f"Added {topping} to pizza")

    def add_pasta_topping(self, topping_index):
        if self.current_item and self.current_item['type'] == 'pasta':
            if 0 <= topping_index < len(self.toppings_Pasta):
                topping = self.toppings_Pasta[topping_index]
                self.current_item['toppings'].append(topping)
                print(f"Added {topping} to pasta")   

 

    def prepare_keys(self, key):
        #pizza
        if key == pygame.k_1:
            self.chef_pizza(0)  # small
        elif key == pygame.k_2:
            self.chef_pizza(1)  # Medium  
        elif key == pygame.K_3:
            self.chef_pizza(2)  # Large

        # pasta
        elif key == pygame.K_5:
            self.chef_pasta(0)  # Spaghetti
        elif key == pygame.K_6:
            self.chef_pasta(1)  # Gnocchi
        elif key == pygame.K_7:
            self.chef_pasta(2)  # macaroni
        elif key == pygame.K_8:
            self.chef_pasta(3)  # tagliatelle
        elif key == pygame.K_9:
            self.chef_pasta(4)  # penne

            # Pizza toppings 
        elif key == pygame.K_q:
            self.chef_add_pizza_topping(0)  #  extra cheese
        elif key == pygame.K_w:
            self.chef_add_pizza_topping(1)  # Pepperoni
        elif key == pygame.K_e:
            self.chef_add_pizza_topping(2)  # Mushrooms
        elif key == pygame.K_r:
            self.chef_add_pizza_topping(3)  # onions
        elif key == pygame.K_t:
            self.chef_add_pizza_topping(4)  # tuna
        elif key == pygame.K_y:
            self.chef_add_pizza_topping(5)  # ham
        elif key == pygame.K_u:
            self.chef_add_pizza_topping(6)  # pepper
        elif key == pygame.K_i:
            self.chef_add_pizza_topping(7)  # chicken
        elif key == pygame.K_o:
            self.chef_add_pizza_topping(8)  # pinapple
        elif key == pygame.K_p:
            self.chef_add_pizza_topping(9)  # paprika  


        # Pasta toppings
        elif key == pygame.K_a:
            self.chef_add_pasta_topping(0)  # chicken
        elif key == pygame.K_s:
            self.chef_add_pasta_topping(1)  # paprika
        elif key == pygame.K_d:
            self.chef_add_pasta_topping(2)  # mushrooms
        elif key == pygame.K_f:
            self.chef_add_pasta_topping(3)  # pepper
        elif key == pygame.K_g:
            self.chef_add_pasta_topping(4)  # onions

        # pasta sauce
        elif key == pygame.K_z:
            self.chef_add_pasta_topping(0)  # pesto
        elif key == pygame.K_x:
            self.chef_add_pasta_topping(1)  # tomato
        elif key == pygame.K_c:
            self.chef_add_pasta_topping(2)  # bolognese
        elif key == pygame.K_v:
            self.chef_add_pasta_topping(3)  # alfredo
        elif key == pygame.K_b:
            self.chef_add_pasta_topping(4)  # arrabiata


    # Cooking methods
    def set_oven_cooking(self):
        if self.current_item:
            self.current_item['cooking_method'] = 'oven'
            self.state = "cooking pizza" if self.current_item['type'] == 'pizza' else "cooking pasta"
            print(f"Set to cook in oven")

    def set_pan_cooking(self):
        if self.current_item:
            self.current_item['cooking_method'] = 'pan' 
            self.state = "cooking pizza" if self.current_item['type'] == 'pizza' else "cooking pasta"
            print(f"Set to cook in pan") 

    # Cooking state methods
    def update_cooking(self):
        if self.state in ["cooking pizza", "cooking pasta"] and self.current_item:
            self.duration += self.speed
            if self.duration >= 100:
                self.current_item['is_cooked'] = True
                self.state = "waiting"
                self.duration = 0
                item_name = self.get_item_description(self.current_item)
                print(f"Finished cooking {item_name}!")
                self.current_item = None

    def get_item_description(self, item):
        if item['type'] == 'pizza':
            toppings = ', '.join(item['toppings']) if item['toppings'] else 'no toppings'
            return f"{item['size']} pizza with {toppings}"
        else:
            toppings = ', '.join(item['toppings']) if item['toppings'] else 'no toppings'
            return f"{item['pasta type']} with {item['sauce type']} sauce and {toppings}"

    def update(self):
        self.update_cooking()

    def show_chef(self):
        screen.blit(self.image_chef, self.rect_chef)
    

        # main loop
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == quit :
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:###################################################

            #real-time updating
            current_time = time.time()
            if current_time - self.last_real_time_update >= 1.0:
                self.last_real_time_update = current_time
                real_time = self.get_real_world_time()
                elapsed = self.get_elapsed_real_time()
                print(f"Real time:  {real_time.strftime('%H:%M:$S')}")
                print(f"system running for: {elapsed}")

                #display real time
                real_time_text = self.font.render(f"real time: {self.get_real_world_time().strftime('%H:%M:%S:')}" True, (255, 255, 255))
                        
                


            #color of window
            screen.fill(255, 255, 255)

            # display image
            screen.blit(self.image, self.place)

            pygame.display.flip()
            clock.tick(60)


