import pygame
from pygame.locals import *
import random
import time
import datetime
from Pizza import *
from city_v2 import *
from Pasta import *
from Order import *
import sys


#define constants
FRAMES_PER_SECOND = 30 
N_Restaurants = 3 #define number of restaurants
restList = []
restPos = [(60,315),(500,380),(700,60)]
Eindhoven = city()
running = True
orderBuffer = [[1000, 'pizza', 'medium', 'mushrooms','tuna'],[2000, 'pasta', 'gnocchi', 'pesto', 'chicken']]


def main(): # main loop
    #init world
    pygame.init()
    clock = pygame.time.Clock()

    #load assets

    #init variables
    pizza = Pizza(['tuna'], 'Large', 0)
    pizza.status = 'Done'
    pasta = Pasta(['tuna'], 'Spaghetti', 'Alfredo', 0)
    pasta.status = 'Done'
    orderID = 1000

    #loop forever
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()



        #per frame actions
        if (orderID == 9999):
            orderID = 1000
        


        if (pizza.GetStatus() == 'Done' or pasta.GetStatus() == 'Done'): #if the pizza that is worked on is done:
            if (pizza.GetID() == Order.GetID() or pasta.GetID() == Order.GetID()):
                order.status = 'prepared'
            if (orderBuffer[0][0] == 'pizza'): #if the first item in the buffer is pizza
                toppings = orderBuffer[0][2:]
                pizza = Pizza(toppings, orderBuffer[0][2], orderBuffer[0][0])#make new pizza item
                orderBuffer.pop(0)
                orderID = orderBuffer[0][0] + 1
            elif(orderBuffer[0][0] == 'pasta'):#if the first item in the buffer is pasta
                toppings = orderBuffer[0][3:]
                pasta = Pasta(toppings, orderBuffer[0][2], orderBuffer[0][3], orderBuffer[0][0])#make new pasta item
                orderID = orderBuffer[0][0] + 1
                orderBuffer.pop(0)

        

       # print(pizza.GetDescription())



        #draw window elements
        screen.fill((0,0,0))
        Eindhoven.show_city_image()
        Eindhoven.show_restaurant_icon(restPos)
        Eindhoven.show_house_icon()
        pygame.display.update()

        #update frame 
        clock.tick(FRAMES_PER_SECOND)

main()
