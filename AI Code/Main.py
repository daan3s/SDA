# main_automated.py
import pygame
import time
import random
import sys
import os

# Import all classes from their individual _AI files
from Customer_AI import Customer
from ItalianRestaurant_AI import ItalianRestaurant
from City_AI import City
from Chef_AI import Chef
from Oven_AI import Oven
from Pan_AI import Pan
from DeliveryDrone_AI import DeliveryDrone
from Pizza_AI import Pizza
from Pasta_AI import Pasta
from Order_AI import Order


class AutomatedRestaurantSystem:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption("Automated Restaurant System")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize all components
        self.setup_system()

    def setup_system(self):
        """Setup all the components of the restaurant system"""
        print("=== Setting Up Automated Restaurant System ===")

        # 1. Create City
        self.city = City("Pizza Ville", 50000, 1000)
        print(f"Created city: {self.city.Name}")

        # 2. Create Restaurant
        self.restaurant = ItalianRestaurant("Mario's Italian Kitchen", "123 Pizza Street")
        print(f"Created restaurant: {self.restaurant.Name}")

        # 3. Add restaurant to city
        self.city.AddRestaurant(self.restaurant)

        # 4. Setup restaurant equipment and staff
        self.setup_restaurant_staff()

        # 5. Create automated customers
        self.setup_customers()

        # 6. Order tracking
        self.orders_processed = 0
        self.start_time = time.time()

        print("=== System Setup Complete ===\n")

    def setup_restaurant_staff(self):
        """Setup chefs, ovens, pans, and delivery drones"""
        # Add chefs
        chef1 = Chef(200, 300)
        chef1.Name = "Chef Mario"
        self.restaurant.add_chef(chef1)

        chef2 = Chef(300, 300)
        chef2.Name = "Chef Luigi"
        self.restaurant.add_chef(chef2)

        # Add ovens
        oven1 = Oven(self.screen)
        oven2 = Oven(self.screen)
        self.restaurant.add_oven(oven1)
        self.restaurant.add_oven(oven2)

        # Add pans
        pan1 = Pan(self.screen)
        pan2 = Pan(self.screen)
        self.restaurant.add_pan(pan1)
        self.restaurant.add_pan(pan2)

        # Add delivery drones
        drone1 = DeliveryDrone(5001)
        drone2 = DeliveryDrone(5002)
        self.restaurant.add_delivery_driver(drone1)
        self.restaurant.add_delivery_driver(drone2)

        print(f"Added {len(self.restaurant.Chefs)} chefs, {len(self.restaurant.Ovens)} ovens, "
              f"{len(self.restaurant.Pans)} pans, {len(self.restaurant.DeliveryDrivers)} drones")

    def setup_customers(self):
        """Create automated customers"""
        self.customers = []
        addresses = [
            "123 Main Street", "456 Oak Avenue", "789 Pine Road",
            "321 Elm Boulevard", "654 Maple Lane", "987 Cedar Street",
            "111 Pizza Lane", "222 Pasta Street", "333 Tomato Road"
        ]

        for i, address in enumerate(addresses):
            customer = Customer(1000 + i, address)
            self.customers.append(customer)
            print(f"Created customer: ID={customer.CustomerID}, Address={address}")

        print(f"Created {len(self.customers)} customers")

    def generate_automated_order(self):
        """Generate an order from a random customer"""
        if not self.customers:
            return None

        customer = random.choice(self.customers)
        order_data = customer.GenerateOrder()

        print(f"\n=== New Automated Order ===")
        print(f"Customer: {customer.CustomerID} - {customer.CustomerAddress}")
        print(f"Order ID: {order_data['order_id']}")
        print(f"Items: {order_data['total_items']}")

        for item in order_data['items']:
            if item[1] == 'pizza':
                print(f"  - Pizza {item[0]}: {item[2]} with {', '.join(item[3:]) if len(item) > 3 else 'no toppings'}")
            else:
                print(
                    f"  - Pasta {item[0]}: {item[2]} with {item[3]} sauce and {', '.join(item[4:]) if len(item) > 4 else 'no toppings'}")

        return order_data

    def process_automated_order(self, order_data):
        """Process an automated order through the system"""
        print(f"\n--- Processing Order {order_data['order_id']} ---")

        # 1. Assign order to restaurant
        restaurant = self.city.AssignOrderToRestaurant(order_data)
        if not restaurant:
            print("No restaurant available for order")
            return False

        # 2. Restaurant receives order (simulate without network for now)
        print(f"Restaurant received order {order_data['order_id']}")

        # 3. Add order directly to restaurant's order queue
        if hasattr(restaurant, 'Orders'):
            restaurant.Orders.append(order_data)
            print(f"Order {order_data['order_id']} added to restaurant queue")

        # 4. Process order in restaurant
        if hasattr(restaurant, 'Process_order'):
            success = restaurant.Process_order()
        else:
            # Simple simulation if Process_order doesn't exist
            success = True

        if success:
            print(f"Order {order_data['order_id']} processed successfully")
            self.orders_processed += 1

            # 5. Simulate customer receiving order
            customer_id = order_data['customer_id']
            customer = next((c for c in self.customers if c.CustomerID == customer_id), None)
            if customer:
                customer.ReceiveOrder()
                print(f"Customer {customer_id} received order")

            return True
        else:
            print(f"Failed to process order {order_data['order_id']}")
            return False

    def update_system(self):
        """Update all system components"""
        # Update restaurant state
        if hasattr(self.restaurant, 'update'):
            self.restaurant.update()

        # Update chefs
        for chef in self.restaurant.Chefs:
            if hasattr(chef, 'update'):
                chef.update()

        # Update ovens and pans
        for oven in self.restaurant.Ovens:
            if hasattr(oven, 'update'):
                oven.update()

        for pan in self.restaurant.Pans:
            if hasattr(pan, 'update'):
                pan.update()

    def draw_system(self):
        """Draw the entire system visualization"""
        self.screen.fill((255, 255, 255))

        # Draw city background
        if hasattr(self.city, 'show_city_image'):
            self.city.show_city_image(self.screen)

        # Draw restaurants
        if hasattr(self.city, 'show_restaurant_icon'):
            self.city.show_restaurant_icon(self.screen)

        # Draw houses
        if hasattr(self.city, 'show_house_icon'):
            self.city.show_house_icon(self.screen)

        # Draw chefs (simplified representation)
        for i, chef in enumerate(self.restaurant.Chefs):
            color = (0, 255, 0) if hasattr(chef, 'ChefAvailable') and chef.ChefAvailable else (255, 0, 0)
            pygame.draw.circle(self.screen, color, (100 + i * 50, 100), 20)

            # Draw chef name
            font = pygame.font.Font(None, 24)
            name = chef.Name if hasattr(chef, 'Name') else f"Chef {i}"
            name_surface = font.render(name, True, (0, 0, 0))
            self.screen.blit(name_surface, (80 + i * 50, 130))

        # Draw status information
        font = pygame.font.Font(None, 36)
        status_text = f"Orders Processed: {self.orders_processed}"
        text_surface = font.render(status_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (10, 10))

        elapsed_time = time.time() - self.start_time
        time_text = f"Time: {int(elapsed_time)}s"
        time_surface = font.render(time_text, True, (0, 0, 0))
        self.screen.blit(time_surface, (10, 50))

        # Draw restaurant status
        if hasattr(self.restaurant, 'is_open'):
            status = "OPEN" if self.restaurant.is_open else "CLOSED"
            status_color = (0, 255, 0) if self.restaurant.is_open else (255, 0, 0)
            status_surface = font.render(f"Restaurant: {status}", True, status_color)
            self.screen.blit(status_surface, (10, 90))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        last_order_time = time.time()
        order_interval = 5  # Generate order every 5 seconds

        print("=== Starting Automated Order Processing ===")
        print("Generating orders every 5 seconds...\n")
        print("Press SPACE to generate manual order")
        print("Press ESC to exit\n")

        while self.running:
            current_time = time.time()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        # Manual order generation
                        order_data = self.generate_automated_order()
                        if order_data:
                            self.process_automated_order(order_data)

            # Generate automated orders periodically
            if current_time - last_order_time >= order_interval:
                order_data = self.generate_automated_order()
                if order_data:
                    self.process_automated_order(order_data)
                last_order_time = current_time

            # Update system
            self.update_system()

            # Draw everything
            self.draw_system()

            self.clock.tick(60)

        pygame.quit()
        self.print_final_stats()

    def print_final_stats(self):
        """Print final statistics when system closes"""
        elapsed_time = time.time() - self.start_time
        print(f"\n=== System Shutdown ===")
        print(f"Total runtime: {int(elapsed_time)} seconds")
        print(f"Total orders processed: {self.orders_processed}")
        print(f"Orders per minute: {self.orders_processed / (elapsed_time / 60):.1f}")

        # Restaurant stats
        if hasattr(self.restaurant, 'get_restaurant_stats'):
            stats = self.restaurant.get_restaurant_stats()
            print(f"\nRestaurant Statistics:")
            print(f"  Orders completed: {stats['orders_done']}")
            print(f"  Chefs: {stats['available_chefs']}/{stats['total_chefs']} available")
            print(f"  Ovens: {stats['available_ovens']}/{stats['total_ovens']} available")
            print(f"  Pans: {stats['available_pans']}/{stats['total_pans']} available")
            print(f"  Drones: {stats['available_drivers']}/{stats['total_drivers']} available")


# Run the system
if __name__ == "__main__":
    system = AutomatedRestaurantSystem()
    system.run()