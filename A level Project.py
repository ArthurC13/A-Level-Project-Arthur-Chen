import pygame
import random
import os
import sys
import pytmx

# -- Global Constants

# -- Colours
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
GREEN = (0, 255, 0)
DARKGREEN = (0, 100, 0)
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
KNOCKBACK = 15

LEVEL = 0
HEALTH = 10

CAMERALAG = 25

# -- Sprites Classes
def collide_hit_rect(a, b):
    return a.hit_rect.colliderect(b.rect)

def load_sprites(paths):
    sprites = []
    mirrored_sprites = []
    for path in paths:
        temp_list = []
        temp_list2 = []
        for i in sorted(os.listdir(path)):
            if i.endswith('.png'):
                image = pygame.image.load(os.path.join(path, i))
                size = tuple(2*x for x in image.get_size())
                image = pygame.transform.scale(image, size)
                temp_list.append(image)
                temp_list2.append(pygame.transform.flip(image, True, False))
        sprites.append(temp_list)
        mirrored_sprites.append(temp_list2)
    return sprites, mirrored_sprites

def wall_collisions(sprite, direction):
    hits = pygame.sprite.spritecollide(sprite, game.wall_group, False, collide_hit_rect)
    if hits:
        if direction == 'x':
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width
            elif sprite.vel.x < 0:
                sprite.pos.x = hits[0].rect.right
            sprite.vel.x = 0
            sprite.hit_rect.x = int(sprite.pos.x)
        if direction == 'y':
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height
            elif sprite.vel.y < 0:
                sprite.pos.y = hits[0].rect.bottom
            sprite.vel.y = 0
            sprite.hit_rect.y = int(sprite.pos.y)

def on_floor(a):
    a.hit_rect.y += 1
    hits = pygame.sprite.spritecollide(a, game.wall_group, False, collide_hit_rect)
    a.hit_rect.y -= 1
    return hits

#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, health):
        self.groups = game.player_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        paths = ['images/player/idle', 'images/player/run', 'images/player/jump', 'images/player/fall', 'images/player/attack', 'images/player/hurt', 'images/player/death', 'images/player/air_attack']
        self.sprites, self.mirrored_sprites = load_sprites(paths)
        self.current_action = 0
        '''
        Player actions:
        0. idle
        1. run
        2. jump
        3. fall
        4. attack
        5. hurt
        6. death
        7. air attack
        '''
        self.current_sprite = 0
        self.face_left = False
        self.image = self.sprites[self.current_action][self.current_sprite]
        self.last_sprite_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 30, 60)
        self.hit_rect.center = self.rect.center
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.health = health
        self.last_attack = pygame.time.get_ticks()
        self.attack_cooldown = 1000

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
            if keys[pygame.K_z]:
                now = pygame.time.get_ticks()
                if now - self.last_attack >= self.attack_cooldown:
                    if on_floor(self):
                        self.last_attack = pygame.time.get_ticks()
                        self.current_action = 4
                        self.current_sprite = -1
                    else:
                        self.last_attack = pygame.time.get_ticks()
                        self.current_action = 7
                        self.current_sprite = -1
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
        hits = on_floor(self)
        self.hit_rect.y -= 1
        hits2 = pygame.sprite.spritecollide(self, game.wall_group, False, collide_hit_rect)
        self.hit_rect.y += 1
        if hits and not hits2:
            self.vel.y = JUMPVEL
            self.current_sprite = -1

    def attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.pos.x)-20, int(self.pos.y)+14, 52, 68, self.game.enemy_group, 'r')
        else:
            Melee_attack(self.game, int(self.pos.x)+20, int(self.pos.y)+14, 52, 68, self.game.enemy_group, 'l')

    def attack2(self):
        if self.face_left:
            Melee_attack(self.game, int(self.pos.x)-20, int(self.pos.y)+14, 52, 68, self.game.enemy_group, 'r')
            Melee_attack(self.game, int(self.pos.x)+26, int(self.pos.y)+32, 40, 32, self.game.enemy_group, 'l')
        else:
            Melee_attack(self.game, int(self.pos.x)+20, int(self.pos.y)+14, 52, 68, self.game.enemy_group, 'l')
            Melee_attack(self.game, int(self.pos.x)-26, int(self.pos.y)+32, 40, 32, self.game.enemy_group, 'r')

    def air_attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.pos.x)-24, int(self.pos.y)+16, 50, 44, self.game.enemy_group, 'r')
            Melee_attack(self.game, int(self.pos.x)+20, int(self.pos.y)+8, 50, 28, self.game.enemy_group, 'l')
        else:
            Melee_attack(self.game, int(self.pos.x)+24, int(self.pos.y)+16, 50, 44, self.game.enemy_group, 'l')
            Melee_attack(self.game, int(self.pos.x)-20, int(self.pos.y)+8, 50, 28, self.game.enemy_group, 'r')

    def interact(self):
        hits = pygame.sprite.spritecollide(self, game.door_group, False, collide_hit_rect)
        if hits:
            if hits[0].open:
                self.game.next_level()

    def hurt(self):
        self.current_action = 5
        self.current_sprite = -1

    def enemy_contact(self):
        hits = pygame.sprite.spritecollide(self, game.enemy_group, False, collide_hit_rect)
        if hits:
            if self.vel.y > 0.3 and self.rect.bottom > hits[0].rect.center[1]:
                self.vel.y = -9.5

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
            if now - self.last_sprite_time >= 80:
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
        elif self.current_action == 4:      #attacking
            if now - self.last_sprite_time >= 50:
                self.current_sprite += 1
                if self.current_sprite == 2:
                    self.attack()
                if self.current_sprite == 5 and self.vel not in [(0, 0), (0, 0.3)]:
                    self.current_sprite = 0
                    self.current_action = 0
                if self.current_sprite == 8:
                    self.attack2()
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                    self.current_action = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 5:      #hurt
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_action = 0
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 6:      #dying
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = len(sprites_list[self.current_action])-1
                    self.kill()
                    self.game.game_over()
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 7:      #air attacking
            if now - self.last_sprite_time >= 50:
                self.current_sprite += 1
                if self.current_sprite == 1:
                    self.air_attack()
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    if self.vel.y > 0:
                        self.current_action = 3
                        self.current_sprite = 1
                    else:
                        self.current_action = 2
                        self.current_sprite = 3
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()

    def update(self):
        self.movement_controls()
        #self.enemy_contact()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #terminal velocity
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.x = int(self.pos.x)
        wall_collisions(self, 'x')
        self.hit_rect.y = int(self.pos.y)
        wall_collisions(self, 'y')
        self.rect.center = self.hit_rect.center
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        if self.current_action not in [4, 5, 6, 7]:
            if self.vel in [(0, 0), (0, 0.3)]:
                self.current_action = 0
            elif self.vel.y not in [0, 0.3]:
                if self.vel.y < 0:
                    self.current_action = 2
                else:
                    self.current_action = 3
            else:
                self.current_action = 1
        if self.health <= 0 and self.current_action != 6:
            self.current_action = 6
            self.current_sprite = -1
        self.animations()

#Enemies
        
#Slime calss
class Slime(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.enemy_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.sprites, self.mirrored_sprites = load_sprites(['images/mobs/slime/idle', 'images/mobs/slime/move', 'images/mobs/slime/attack', 'images/mobs/slime/death', 'images/mobs/slime/hurt'])
        self.current_action = 0
        '''
        Slime actions:
        0. idle
        1. move
        2. attack
        3. death
        4. hurt
        '''
        self.current_sprite = 0
        self.face_left = False
        self.image = self.sprites[self.current_action][self.current_sprite]
        self.last_sprite_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 32, 32)
        self.hit_rect.center = self.rect.center
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.last_attack = pygame.time.get_ticks()
        self.attack_rate = 2000
        self.health = 5

    def movements(self):
        now = pygame.time.get_ticks()
        self.acc = pygame.math.Vector2(0, GRAVITY)
        if self.current_action != 2 and now - self.last_attack >= self.attack_rate:
            if 40 < abs(self.pos.x - game.player.pos.x) < 400 and abs(self.pos.y - game.player.pos.y) < 125:
                if self.pos.x > game.player.pos.x:
                    self.acc.x = -0.2
                    self.face_left = False
                else:
                    self.acc.x = 0.2
                    self.face_left = True
            if 40 > abs(self.pos.x - game.player.pos.x) and abs(self.pos.y - game.player.pos.y) < 60:
                self.acc.x = 0
                self.current_action = 2
                self.current_sprite = -1
                self.last_attack = pygame.time.get_ticks()

    def attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.pos.x)+32, int(self.pos.y), 24, 32, self.game.player_group, 'l')
        else:
            Melee_attack(self.game, int(self.pos.x)-32, int(self.pos.y), 24, 32, self.game.player_group, 'r')

    def hurt(self):
        self.current_action = 4
        self.current_sprite = -1

    def avoid_stack(self):
        for i in self.game.enemy_group:
            if i != self:
                distance = self.pos.x - i.pos.x
                if abs(distance) < 30 and abs(self.pos.y - i.pos.y) < 30:
                    if on_floor(i):
                        if distance < 0:
                            self.acc.x -= 1
                        else:
                            self.acc.x += 1

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
        elif self.current_action == 1:      #moving
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 2:      #attacking
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite == 2:
                    self.attack()
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_action = 0
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 3:      #dying
            if now - self.last_sprite_time >= 100:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_action = 0
                    self.current_sprite = 0
                    self.kill()
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 4:      #hurt
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_action = 0
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()

    def update(self):
        self.movements()
        if self.current_action != 4:
            self.avoid_stack()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.x = int(self.pos.x)
        wall_collisions(self, 'x')
        self.hit_rect.y = int(self.pos.y)
        wall_collisions(self, 'y')
        self.rect.center = self.hit_rect.center
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        if self.current_action not in [2, 3, 4]:
            if self.vel in [(0, 0), (0, 0.3)]:
                self.current_action = 0
            else:
                self.current_action = 1
        if self.health <= 0 and self.current_action != 3:
            self.current_action = 3
            self.current_sprite = -1
        self.animations()
        
        

#Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.wall_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        x, y, w, h = int(x), int(y), int(w), int(h)
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

#Ladder class
class Ladder(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.ladder_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        x, y, w, h = int(x), int(y), int(w), int(h)
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Door(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites_group, game.door_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.closed = pygame.image.load('images/door/closed.png')
        self.opened = pygame.image.load('images/door/open.png')
        self.image = self.closed
        self.rect = self.image.get_rect()
        x, y = int(x), int(y)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.open = False
        
    def update(self):
        if len(game.enemy_group.sprites()) == 0 and not self.open:
            self.open = True
            self.image = self.opened

# -- Utility classes

#Melee attack class
class Melee_attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, target, direction):
        self.groups = game.all_sprites_group, game.melee_attack_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((w, h))
        if self.game.show_hit_rect:
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(x, y, 32, 32)
        self.rect.center = self.hit_rect.center
        self.target = target
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 125
        self.pos = pygame.math.Vector2(x, y)
        self.direction = direction

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time >= self.life_time:
            self.kill()
        hits = pygame.sprite.spritecollide(self, self.target, False, collide_hit_rect)
        if hits:
            for i in hits:
                if i.health > 0:
                    i.health -= 1
                    if self.direction == 'l':
                        i.vel.x = KNOCKBACK
                        i.hurt()
                    else:
                        i.vel.x = -KNOCKBACK
                        i.hurt()
            self.kill()
        
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

class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface
        
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
        self.myfont = pygame.font.Font('fonts/m5x7.ttf', 40)
        self.tools_reset()

    def sprite_group_reset(self):
        self.all_sprites_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.ladder_group = pygame.sprite.Group()
        self.door_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.melee_attack_group = pygame.sprite.Group()

    def tools_reset(self):
        self.show_grid = False
        self.show_stats = False
        self.show_hit_rect = False

    def new_game(self):
        self.level = LEVEL
        self.player_health = HEALTH
        self.next_level()
        
    def next_level(self):
        self.sprite_group_reset()
        self.level += 1
        try:
            self.load_map(self.level)
        except:
            self.level = LEVEL + 1
            self.load_map(self.level)
        self.camera = Camera(self.map.width, self.map.height)

    def load_map(self, level):
        self.map = TiledMap('maps/map'+str(level)+'.tmx')
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y, self.player_health)
            if tile_object.name == 'slime':
                Slime(self, tile_object.x, tile_object.y)
            if tile_object.name == 'ladder':
                Ladder(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'wall':
                Wall(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'door':
                Door(self, tile_object.x, tile_object.y)

    def game_loop(self):
        self.done = False
        self.mode = 'in game'
        while not self.done:
            self.dt = self.clock.tick(FPS)/1000
            self.events()
            self.update()
            self.draw()
            
    def wait_loop(self):
        self.wait = True
        if self.mode == 'pause':
            while self.wait:
                self.dt = self.clock.tick(FPS)/1000
                self.events()
                self.draw()
        elif self.mode == 'death screen':
            while self.wait:
                self.dt = self.clock.tick(FPS)/1000
                self.events()
                self.draw()
            self.new_game()
        elif self.mode == 'home screen':
            while self.wait:
                self.dt = self.clock.tick(FPS)/1000
                self.events()
            self.new_game()

    def events(self):
        # -- User input and controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_0:
                    self.tools_reset()
                if event.key == pygame.K_1:
                    self.show_grid = not self.show_grid
                if event.key == pygame.K_2:
                    self.show_stats = not self.show_stats
                if event.key == pygame.K_3:
                    self.show_hit_rect = not self.show_hit_rect
                if self.mode == 'in game':
                    if event.key == pygame.K_n:
                        self.next_level()
                    if event.key == pygame.K_r:
                        self.level -= 1
                        self.next_level()
                    if event.key == pygame.K_ESCAPE:
                        self.pause_game()
                elif self.mode == 'pause':
                    if event.key == pygame.K_ESCAPE:
                        self.pause_game()
                elif self.mode == 'death screen':
                    self.wait = False
                elif self.mode == 'home screen':
                    self.wait = False

    def update(self):
        self.all_sprites_group.update()
        self.enemy_group.update()
        self.player_group.update()
        self.camera.update(self.player)
        self.player_health = self.player.health

    def blit_texts(self, texts, colour, x, y, y_intervals, font):
        textlist = texts.split('\n')
        counter = 0
        for line in textlist:
            self.screen.blit(font.render(line, False, colour), (x, y + (y_intervals*counter)))
            counter += 1

    def draw_texts(self):
        string = 'Player health:' + str(self.player.health)
        self.blit_texts(string, WHITE, 384, 32, 32, self.myfont)
        if self.show_stats:
            string = 'Camera Offset x: ' + str(self.camera.x) + '\nCamera Offset y: ' + str(self.camera.y)
            string += '\nPlayer x: ' + str(self.player.rect.x) + '\nPlayer y: ' + str(self.player.rect.y)
            string += '\nPlayer Acc: ' + str(self.player.acc) + '\nPlayer Vel: ' + str(self.player.vel)
            string += '\nFPS: ' + "{:.2f}".format(self.clock.get_fps())
            self.blit_texts(string, WHITE, 640, 32, 32, self.myfont)

    def draw(self):
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        if self.show_grid:
            self.show_grid_lines()
        for i in self.all_sprites_group:
            self.screen.blit(i.image, self.camera.apply(i))
        for i in self.enemy_group:
            self.screen.blit(i.image, self.camera.apply(i))
        self.screen.blit(self.player.image, self.camera.apply(self.player))
        if self.show_hit_rect:
            pygame.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(self.player.hit_rect), 2)
            for i in self.enemy_group:
                pygame.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(i.hit_rect), 2)
        self.draw_texts()
        pygame.display.flip()

    def show_grid_lines(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, LIGHTBLUE, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, LIGHTBLUE, (0, y), (WIDTH, y))

    def home_screen(self):
        self.mode = 'home screen'
        string = 'Press any key to start'
        self.blit_texts(string, WHITE, 380, 384, 32, self.myfont)
        pygame.display.flip()
        self.wait_loop()

    def game_over(self):
        self.done = True
        self.mode = 'death screen'

    def pause_game(self):
        self.done = not self.done
        self.wait = False
        self.mode = 'pause'
            
    def exit_game(self):
        pygame.quit()
        sys.exit()


### -- Game Loop
run = True
game = Game()
game.home_screen()
while run:
    game.game_loop()
    game.wait_loop()














