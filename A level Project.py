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
FRICTION = -0.15
GRAVITY = 0.3

CAMERALAG = 30

# -- Sprites Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x * TILESIZE, y * TILESIZE)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

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

    def movement_controls(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYERACC
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYERACC
        if keys[pygame.K_UP]:
            self.jump()

    def jump(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, game.wall_group, False)
        self.rect.y -= 1
        if hits:
            self.vel.y = JUMPVEL

    def update(self):
        self.movement_controls()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.rect.x = int(self.pos.x)
        self.wall_collisions('x')
        self.rect.y = int(self.pos.y)
        self.wall_collisions('y')

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

# -- Map and Camera
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
#CameraV1
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

    def sprite_group_reset(self):
        self.all_sprites_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

    def new_game(self):
        self.sprite_group_reset()
        self.level = 2
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
                if event.key == pygame.K_p:
                    print(self.player.pos, -self.player.rect.x - int(self.player.rect.width / 2) + int(WIDTH / 2))

    def update(self):
        self.all_sprites_group.update()
        self.camera.update(self.player)

    def blit_texts(self, texts, colour, x, y, y_intervals, font):
        textlist = texts.split('\n')
        counter = 0
        for line in textlist:
            self.screen.blit(font.render(line, False, colour), (x, y + (y_intervals*counter)))
            counter += 1

    def draw_texts(self):
        string = 'Camera Offset x: ' + str(self.camera.x) + '\nCamera Offset y: ' + str(self.camera.y) + '\nPlayer x: ' + str(self.player.rect.x) + '\nPlayer y: ' + str(self.player.rect.y)
        self.blit_texts(string, WHITE, 32, 32, 32, self.myfont)

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.show_grid_lines()
        for i in self.all_sprites_group:
            self.screen.blit(i.image, self.camera.apply(i))
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
        self.done = True
            
    def exit_game(self):
        pygame.quit()
        sys.exit()


### -- Game Loop
game = Game()
game.home_screen()
while True:
    game.new_game()
    game.game_loop()





































