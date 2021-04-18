import pygame
import random
import os
import sys

# -- Global Constants

# -- Colours
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255,255,0)
PURPLE = (103,13,173)
PINK = (255,192,203)
LIGHTBLUE = (209, 237, 242)
BRIGHTBLUE = (15, 137, 202)
NIGHTBLUE = (34, 36, 64)

# -- Game settings
WIDTH = 1024        #32*32
HEIGHT = 768        #24*32
FPS = 60
GAMETITLE = 'A Level Project'

BGCOLOUR = NIGHTBLUE

TILESIZE = 32
GRIDWIDTH = WIDTH/TILESIZE
GRIDHEIGHT = HEIGHT/TILESIZE

PLAYERACC = 0.9
JUMPVEL = -9.5
LADDERVEL = 4
FRICTION = -0.15
GRAVITY = 0.3

LEVEL = 0

CAMERALAG = 25

# -- Sprites Classes

#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.player_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_sprites()
        print(self.sprites)
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.last_sprite_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x * TILESIZE, y * TILESIZE)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

    def load_sprites(self):
        path = 'images/player/idle'
        self.sprites = []
        for i in sorted(os.listdir(path)):
            image = pygame.image.load(os.path.join(path, i))
            size = tuple(2*x for x in image.get_size())
            image = pygame.transform.scale(image, size)
            self.sprites.append(image)

    def wall_collisions(self, direction):
        hits = pygame.sprite.spritecollide(self, game.wall_group, False)
        if hits:
            if direction == 'x':
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                elif self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = int(self.pos.x)
            if direction == 'y':
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                elif self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = int(self.pos.y)

    def on_ladder(self):
        hits = pygame.sprite.spritecollide(self, game.ladder_group, False)
        if hits:
            return [True, hits[0].rect.left]
        return [False]

    def movement_controls(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)
        ladder = self.on_ladder()
        keys = pygame.key.get_pressed()
        if not ladder[0]:
            if keys[pygame.K_LEFT]:
                self.acc.x = -PLAYERACC
            if keys[pygame.K_RIGHT]:
                self.acc.x = PLAYERACC
            if keys[pygame.K_UP]:
                self.jump()
            if keys[pygame.K_DOWN]:
                self.interact()
        else:
            self.acc.y = 0
            self.vel.y = 0
            if keys[pygame.K_LEFT]:
                self.acc.x = -PLAYERACC
            if keys[pygame.K_RIGHT]:
                self.acc.x = PLAYERACC
            if keys[pygame.K_UP]:
                self.vel.y = -LADDERVEL
            if keys[pygame.K_DOWN]:
                self.vel.y = LADDERVEL

    def jump(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, game.wall_group, False)
        self.rect.y -= 1
        if hits:
            self.vel.y = JUMPVEL

    def interact(self):
        pass

    def update(self):
        now = pygame.time.get_ticks()
        self.movement_controls()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.rect.x = int(self.pos.x)
        self.wall_collisions('x')
        self.rect.y = int(self.pos.y)
        self.wall_collisions('y')
        if now - self.last_sprite_time >= 200:
            self.current_sprite += 1
            if self.current_sprite > len(self.sprites)-1:
                self.current_sprite = 0
            self.image = self.sprites[self.current_sprite]
            self.last_sprite_time = pygame.time.get_ticks()

#Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y, colour):
        self.groups = game.all_sprites_group, game.wall_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

#Ladder class
class Ladder(pygame.sprite.Sprite):
    def __init__(self, game, x, y, colour):
        self.groups = game.all_sprites_group, game.ladder_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        
# -- Map and Camera

#Map class
class Map():
    def __init__(self, map_path):
        self.maplist = []
        with open(map_path) as f:
            for i in f:
                self.maplist.append(i.strip())
        self.tilewidth = len(self.maplist[0])
        self.tileheight = len(self.maplist)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE
        
#Camera V1 - no lag
'''
class Camera():
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x - int(target.rect.width / 2) + int(WIDTH / 2)
        y = -target.rect.y + int(HEIGHT / 4*3)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)
'''
#Camera class
class Camera():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(-self.x, -self.y)

    def update(self, target):
        self.x += (target.rect.x - self.x + target.rect.width // 2 - WIDTH//2)//CAMERALAG
        self.y += (target.rect.y - self.y + target.rect.height // 2 - HEIGHT//2)//CAMERALAG

        self.x = max(0, self.x)
        self.y = max(0, self.y)
        self.x = min(self.width - WIDTH, self.x)
        self.y = min(self.height - HEIGHT, self.y)


# -- Main Game Class
class Game():
    def __init__(self):
        pygame.init()
        size = (WIDTH, HEIGHT)
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(GAMETITLE)
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(100, 50)
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.level = LEVEL
        self.tools_reset()

    def sprite_group_reset(self):
        self.all_sprites_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.ladder_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

    def tools_reset(self):
        self.show_grid = False
        self.show_pos = False

    def new_level(self):
        self.sprite_group_reset()
        self.level += 1
        try:
            self.load_map(self.level)
        except:
            self.level = LEVEL + 1
            self.load_map(self.level)
        self.camera = Camera(self.map.width, self.map.height)

    def load_map(self, level):
        self.map = Map('maps/map'+str(level)+'.txt')
        x = 0
        y = 0
        for line in self.map.maplist:
            for item in line:
                if item == '1':
                    Wall(self, x, y, PURPLE)
                if item == '2':
                    Wall(self, x, y, BRIGHTBLUE)
                if item == '3':
                    Ladder(self, x, y, YELLOW)
                if item == 'p':
                    self.player = Player(self, x, y)
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
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_n:
                    self.new_level()
                if event.key == pygame.K_r:
                    self.level -= 1
                    self.new_level()
                if event.key == pygame.K_0:
                    self.tools_reset()
                if event.key == pygame.K_1:
                    self.show_grid = not self.show_grid
                if event.key == pygame.K_2:
                    self.show_pos = not self.show_pos

    def update(self):
        self.all_sprites_group.update()
        self.player_group.update()
        self.camera.update(self.player)

    def blit_texts(self, texts, colour, x, y, y_intervals, font):
        textlist = texts.split('\n')
        counter = 0
        for line in textlist:
            self.screen.blit(font.render(line, False, colour), (x, y + (y_intervals*counter)))
            counter += 1

    def draw_texts(self):
        if self.show_pos:
            string = 'Camera Offset x: ' + str(self.camera.x) + '\nCamera Offset y: ' + str(self.camera.y) + '\nPlayer x: ' + str(self.player.rect.x) + '\nPlayer y: ' + str(self.player.rect.y)
            self.blit_texts(string, WHITE, 32, 32, 32, self.myfont)

    def draw(self):
        self.screen.fill(BGCOLOUR)
        if self.show_grid:
            self.show_grid_lines()
        #self.all_sprites_group.draw(self.screen)
        #self.player_group.draw(self.screen)
        #all sprites draw replaced with for loop blitting individual sprites on to the screen - doing the same thing but alow camera to be applied
        for i in self.all_sprites_group:
            self.screen.blit(i.image, self.camera.apply(i))
        self.screen.blit(self.player.image, self.camera.apply(self.player))
        self.draw_texts()
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
    game.new_level()
    game.game_loop()





































