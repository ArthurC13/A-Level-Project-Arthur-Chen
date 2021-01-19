import pygame

# -- Global Constants


# -- Colours
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255,255,0)

# -- Initialise Pygame
pygame.init()

# -- Black Screen
size = (640,480)
screen = pygame.display.set_mode(size)

# -- Title of new window/screen
pygame.display.set_caption('My Window')

# -- Classes

# -- Exit game flag set to false
done = False

# -- Manages how fast screen refreshes
clock = pygame.time.Clock()

### -- Game Loop

while not done:
    # -- User input and controls
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        #End If
    #Next event

    # -- game logic goes after this comment

    # -- Screen background is BLACK
    screen.fill(BLACK)

    # -- Draw here
    pygame.draw.rect(screen, BLUE, (220,165,200,150))
    pygame.draw.circle(screen, YELLOW, (40,100),40,0)

    # -- flip display to reveal new position of objects
    pygame.display.flip()

    # - The clock ticks over
    clock.tick(60)

#End While - End of game loop

pygame.quit()
