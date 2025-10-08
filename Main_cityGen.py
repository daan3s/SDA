import pygame
from pygame.locals import *
import random
import time
import datetime


from city_v2 import *

import sys

#define constants
FRAMES_PER_SECOND = 30 
N_Restaurants = 3 #define number of restaurants
restList = []
restPos = [(60,315),(500,380),(700,60)]
Eindhoven = city()
running = True



def main(): # main loop
    #init world
    pygame.init()
    clock = pygame.time.Clock()

    #load assets

    #init variables
    #for i in range(0, N_Restaurants):
        #x = random.randint(100,SCREEN_WIDTH-100)
        #y = random.randint(100,SCREEN_HEIGHT-100)
       # restList.append(Italiën_restaurant(x,y,SCREEN_WIDTH,SCREEN_HEIGHT,i))

    #loop forever
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #elif event.type == pygame.MOUSEBUTTONDOWN:###################################################

        #per frame actions

        #draw window elements
        screen.fill((0,0,0))
        Eindhoven.show_city_image()
        Eindhoven.show_restaurant_icon(restPos)
        Eindhoven.show_house_icon()
        pygame.display.update()

        #update frame 
        clock.tick(FRAMES_PER_SECOND)

main()

        #real-time updating
        #current_time = time.time()
        #if current_time - last_real_time_update >= 1.0:
        #    last_real_time_update = current_time
        #    real_time = get_real_world_time()
        #    elapsed = get_elapsed_real_time()
        #    print(f"Real time:  {real_time.strftime('%H:%M:$S')}")
        #    print(f"system running for: {elapsed}")

            #display real time
            #real_time_text = self.font.render(f"real time: {self.get_real_world_time().strftime('%H:%M:%S:')}" True, (255, 255, 255))
                        

            #color of window
            #screen.fill(255, 255, 255)

            # display image
            #screen.blit(image, place)

            #pygame.display.flip()