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
def collide_hit_rect(a, b):
    return a.hit_rect.colliderect(b.rect)

#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.player_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_sprites()
        self.current_action = 0
        '''
        Player actions:
        0. idle
        1. run
        2. jump
        3. fall
        '''
        self.current_sprite = 0
        self.face_left = False
        self.image = self.sprites[self.current_action][self.current_sprite]
        self.last_sprite_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 32, 64)
        self.hit_rect.center = self.rect.center
        self.pos = pygame.math.Vector2(x * TILESIZE, y * TILESIZE)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

    def load_sprites(self):
        paths = ['images/player/idle', 'images/player/run', 'images/player/jump', 'images/player/fall']
        self.sprites = []
        self.mirrored_sprites = []
        for path in paths:
            temp_list = []
            temp_list2 = []
            for i in sorted(os.listdir(path)):
                image = pygame.image.load(os.path.join(path, i))
                size = tuple(2*x for x in image.get_size())
                image = pygame.transform.scale(image, size)
                temp_list.append(image)
                temp_list2.append(pygame.transform.flip(image, True, False))
            self.sprites.append(temp_list)
            self.mirrored_sprites.append(temp_list2)

    def wall_collisions(self, direction):
        hits = pygame.sprite.spritecollide(self, game.wall_group, False, collide_hit_rect)
        if hits:
            if direction == 'x':
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.hit_rect.width
                elif self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.hit_rect.x = int(self.pos.x)
            if direction == 'y':
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.hit_rect.height
                elif self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.hit_rect.y = int(self.pos.y)

    def on_ladder(self):
        hits = pygame.sprite.spritecollide(self, game.ladder_group, False, collide_hit_rect)
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
                self.face_left = True
            if keys[pygame.K_RIGHT]:
                self.acc.x = PLAYERACC
                self.face_left = False
            if keys[pygame.K_UP]:
                self.jump()
            if keys[pygame.K_DOWN]:
                self.interact()
        else:
            self.acc.y = 0
            self.vel.y = 0
            if keys[pygame.K_LEFT]:
                self.acc.x = -PLAYERACC
                self.face_left = True
            if keys[pygame.K_RIGHT]:
                self.acc.x = PLAYERACC
                self.face_left = False
            if keys[pygame.K_UP]:
                self.vel.y = -LADDERVEL
            if keys[pygame.K_DOWN]:
                self.vel.y = LADDERVEL

    def jump(self):
        self.hit_rect.y += 1
        hits = pygame.sprite.spritecollide(self, game.wall_group, False, collide_hit_rect)
        self.hit_rect.y -= 1
        if hits:
            self.vel.y = JUMPVEL
            self.current_sprite = 0

    def interact(self):
        pass

    def animations(self):
        now = pygame.time.get_ticks()
        sprites_list = self.sprites
        if self.face_left:
            sprites_list = self.mirrored_sprites
        if self.current_action == 0:        #idle
            if now - self.last_sprite_time >= 200:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 1:      #running
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 2:      #jumping
            if now - self.last_sprite_time >= 100:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = len(sprites_list[self.current_action])-1
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 3:      #falling
            if now - self.last_sprite_time >= 150:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()

    def update(self):
        self.movement_controls()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.x = int(self.pos.x)
        self.wall_collisions('x')
        self.hit_rect.y = int(self.pos.y)
        self.wall_collisions('y')
        self.rect.center = self.hit_rect.center
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        if self.vel in [(0, 0), (0, 0.3)]:
            self.current_action = 0
        elif self.vel.y not in [0, 0.3]:
            if self.vel.y < 0:
                self.current_action = 2
            else:
                self.current_action = 3
        else:
            self.current_action = 1
        self.animations()
        

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

    def apply_rect(self, rect):
        return rect.move(-self.x, -self.y)

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
        self.show_stats = False
        self.show_hit_rect = False

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
                    self.show_stats = not self.show_stats
                if event.key == pygame.K_3:
                    self.show_hit_rect = not self.show_hit_rect

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
        if self.show_stats:
            string = 'Camera Offset x: ' + str(self.camera.x) + '\nCamera Offset y: ' + str(self.camera.y)
            string += '\nPlayer x: ' + str(self.player.rect.x) + '\nPlayer y: ' + str(self.player.rect.y)
            string += '\nPlayer Acc: ' + str(self.player.acc) + '\nPlayer Vel: ' + str(self.player.vel)
            string += '\nPlayer action:' + str(self.player.current_action) + '\nPlayer sprite: ' + str(self.player.current_sprite)
            string += '\nFPS: ' + "{:.2f}".format(self.clock.get_fps())
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
        if self.show_hit_rect:
            pygame.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(self.player.hit_rect), 2)
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





































