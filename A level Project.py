import pygame
import sys

# -- Global Constants

# -- Colours
BLACK = (0,0,0)
DARKGREY = (40, 40, 40)
WHITE = (255,255,255)
BLUE = (50,50,255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255,255,0)
PURPLE = (103,13,173)
PINK = (255,192,203)
LIGHTPINK = (239, 154, 154)
LIGHTBLUE = (209, 237, 242)
BRIGHTBLUE = (15, 137, 202)

# -- Game settings
WIDTH = 1024
HEIGHT = 768
FPS = 60
GAMETITLE = 'A Level Project'

TILESIZE = 32
GRIDWIDTH = WIDTH/TILESIZE
GRIDHEIGHT = HEIGHT/TILESIZE

# -- Sprites Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

    def move(self, x_speed=0, y_speed=0):
        self.x += x_speed
        self.y += y_speed

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites_group, game.wall_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

# -- Main Game Class
class Game():
    def __init__(self):
        pygame.init()
        size = (WIDTH, HEIGHT)
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(GAMETITLE)
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(100, 50)

    def sprite_group_reset(self):
        self.all_sprites_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

    def new_game(self):
        self.sprite_group_reset()
        self.player = Player(self, 10, 10)
        self.level = 1
        self.load_map(self.level)

    def load_map_file(self, map_path):
        self.maplist = []
        with open(map_path) as f:
            for i in f:
                self.maplist.append(i.strip())

    def load_map(self, level):
        self.load_map_file('maps/map'+str(level)+'.txt')
        x = 0
        y = 0
        for line in self.maplist:
            for item in line:
                if item == '1':
                    Wall(self, x, y)
                x += 1
            x = 0
            y += 1

    def game_loop(self):
        self.done = False
        while not self.done:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        # -- User input and controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
                if event.key == pygame.K_LEFT:
                    self.player.move(x_speed=-1)
                if event.key == pygame.K_RIGHT:
                    self.player.move(x_speed=1)
                if event.key == pygame.K_UP:
                    self.player.move(y_speed=-1)
                if event.key == pygame.K_DOWN:
                    self.player.move(y_speed=1)

    def update(self):
        self.all_sprites_group.update()

    def draw(self):
        self.screen.fill(DARKGREY)
        self.show_grid_lines()
        self.all_sprites_group.draw(self.screen)
        pygame.display.flip()

    def show_grid_lines(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, LIGHTBLUE, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, LIGHTBLUE, (0, y), (WIDTH, y))

    def home_screen(self):
        pass

    def pause_game(self):
        pass
            
    def exit_game(self):
        pygame.quit()
        sys.exit()


### -- Game Loop
game = Game()
game.home_screen()
while True:
    game.new_game()
    game.game_loop()





































