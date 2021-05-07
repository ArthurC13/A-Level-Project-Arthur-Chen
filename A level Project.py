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
WATERVEL = 2.5
FRICTION = -0.15
GRAVITY = 0.3
KNOCKBACK = 15

LEVEL = 0
HEALTH = 10

CAMERALAG = 25

# -- Sprites Classes
def collide_hit_rect(a, b):
    return a.hit_rect.colliderect(b.hit_rect)

def load_sprites(paths, magnify):
    sprites = []
    mirrored_sprites = []
    for path in paths:
        temp_list = []
        temp_list2 = []
        for i in sorted(os.listdir(path)):
            if i.endswith('.png'):
                image = pygame.image.load(os.path.join(path, i)).convert_alpha()
                size = tuple(int(magnify*x) for x in image.get_size())
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

def last_enemy(x, y, direction):
    if len(game.enemy_group.sprites()) == 1:
        Key(game, x, y, direction)

#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, health):
        self.groups = game.player_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        paths = ['images/player/idle', 'images/player/run', 'images/player/jump', 'images/player/fall', 'images/player/attack', 'images/player/hurt', 'images/player/death', 'images/player/air_attack']
        self.sprites, self.mirrored_sprites = load_sprites(paths, 2)
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
        self.invincible = False
        self.air = 1000
        self.items = []

    def movement_controls(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)
        ladder = pygame.sprite.spritecollide(self, game.ladder_group, False, collide_hit_rect)
        water = pygame.sprite.spritecollide(self, game.water_group, False, collide_hit_rect)
        keys = pygame.key.get_pressed()
        if ladder:
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
        elif water:
            self.air_check(water[0])
            self.acc.y = 0
            self.vel.y = 2
            if keys[pygame.K_LEFT]:
                self.acc.x = -PLAYERACC/2
                self.face_left = True
            if keys[pygame.K_RIGHT]:
                self.acc.x = PLAYERACC/2
                self.face_left = False
            if keys[pygame.K_UP]:
                self.vel.y = -WATERVEL
            if keys[pygame.K_DOWN]:
                self.vel.y = WATERVEL
        else:
            if self.air <= 1000:
                self.air += 1
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
                if self.current_action not in [4, 5, 6] and now - self.last_attack >= self.attack_cooldown:
                    if on_floor(self):
                        self.last_attack = pygame.time.get_ticks()
                        self.current_action = 4
                        self.current_sprite = -1
                    else:
                        self.last_attack = pygame.time.get_ticks()
                        self.current_action = 7
                        self.current_sprite = -1
                        
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
            Melee_attack(self.game, int(self.hit_rect.center[0])-20, int(self.pos.y)+28, 52, 68, self.game.enemy_group, 'r', 125, False)
        else:
            Melee_attack(self.game, int(self.hit_rect.center[0])+20, int(self.pos.y)+28, 52, 68, self.game.enemy_group, 'l', 125, False)

    def attack2(self):
        if self.face_left:
            Melee_attack(self.game, int(self.hit_rect.center[0])-20, int(self.pos.y)+28, 52, 68, self.game.enemy_group, 'r', 125, False)
            Melee_attack(self.game, int(self.hit_rect.center[0])+26, int(self.pos.y)+46, 40, 32, self.game.enemy_group, 'l', 125, False)
        else:
            Melee_attack(self.game, int(self.hit_rect.center[0])+20, int(self.pos.y)+28, 52, 68, self.game.enemy_group, 'l', 125, False)
            Melee_attack(self.game, int(self.hit_rect.center[0])-26, int(self.pos.y)+46, 40, 32, self.game.enemy_group, 'r', 125, False)

    def air_attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.hit_rect.center[0])-24, int(self.pos.y)+24, 50, 44, self.game.enemy_group, 'r', 125, False)
            Melee_attack(self.game, int(self.hit_rect.center[0])+20, int(self.pos.y)+16, 50, 28, self.game.enemy_group, 'l', 125, False)
        else:
            Melee_attack(self.game, int(self.hit_rect.center[0])+24, int(self.pos.y)+24, 50, 44, self.game.enemy_group, 'l', 125, False)
            Melee_attack(self.game, int(self.hit_rect.center[0])-20, int(self.pos.y)+16, 50, 28, self.game.enemy_group, 'r', 125, False)

    def interact(self):
        hits = pygame.sprite.spritecollide(self, game.item_group, False, collide_hit_rect)
        hits += pygame.sprite.spritecollide(self, game.door_group, False, collide_hit_rect)
        if hits:
            for i in hits:
                i.interact()

    def hurt(self):
        self.current_action = 5
        self.current_sprite = -1
        self.invincible = True

    def air_check(self, water):
        if self.rect.top > water.rect.top:
            self.air -= 1
            if self.air <= 0 and self.current_action != 6:
                self.current_action = 6
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
                    self.invincible = False
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
        if self.pos.y > self.game.map.height + 3000:
            self.kill()
            self.game.game_over()
        self.animations()

#Enemies
        
#Slime calss
class Slime(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.enemy_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        paths = ['images/mobs/slime/idle', 'images/mobs/slime/move', 'images/mobs/slime/attack', 'images/mobs/slime/death', 'images/mobs/slime/hurt']
        self.sprites, self.mirrored_sprites = load_sprites(paths, 2)
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
        self.invincible = False

    def movements(self):
        now = pygame.time.get_ticks()
        self.acc = pygame.math.Vector2(0, GRAVITY)
        if self.current_action not in [2, 3, 4] and now - self.last_attack >= self.attack_rate:
            if 40 < abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) < 400 and abs(self.pos.y - game.player.pos.y) < 60:
                if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                    self.acc.x = -0.2
                    self.face_left = False
                else:
                    self.acc.x = 0.2
                    self.face_left = True
            if 40 > abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) and abs(self.pos.y - game.player.pos.y) < 60:
                if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                    self.face_left = False
                else:
                    self.face_left = True
                self.acc.x = 0
                self.current_action = 2
                self.current_sprite = -1
                self.last_attack = pygame.time.get_ticks()

    def attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.hit_rect.center[0])+30, int(self.pos.y)+16, 32, 32, self.game.player_group, 'l', 125, True)
        else:
            Melee_attack(self.game, int(self.hit_rect.center[0])-30, int(self.pos.y)+16, 32, 32, self.game.player_group, 'r', 125, True)

    def hurt(self):
        self.current_action = 4
        self.current_sprite = -1
        self.invincible = True

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
                    last_enemy(self.hit_rect.center[0], self.hit_rect.center[1]-30, self.face_left)
                    self.kill()
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 4:      #hurt
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.invincible = False
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
        if self.pos.y > self.game.map.height + 3000:
            self.kill()
        self.animations()

#demon class
class Demon(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.enemy_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        paths = ['images/mobs/demon/idle', 'images/mobs/demon/attack', 'images/mobs/demon/hurt', 'images/mobs/demon/death']
        self.sprites, self.mirrored_sprites = load_sprites(paths, 2)
        self.berserk_sprites, self.mirrored_berserk_sprites = load_sprites(['images/mobs/demon/berserk'], 2)
        self.current_action = 0
        '''
        Demon actions:
        0. idle
        1. attack
        2. hurt
        3. death
        '''
        self.current_sprite = 0
        self.face_left = False
        self.image = self.sprites[self.current_action][self.current_sprite]
        self.last_sprite_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 128, 192)
        self.hit_rect.center = self.rect.center
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.last_attack = pygame.time.get_ticks()
        self.attack_rate = 4000
        self.health = 50
        self.attack_speed = 125
        self.movement_speed = 0.4
        self.vision = 500
        self.invincible = False
        self.berserking = False

    def movements(self):
        now = pygame.time.get_ticks()
        self.acc = pygame.math.Vector2(0, GRAVITY)
        if self.current_action not in [1, 2, 3] and now - self.last_attack >= self.attack_rate:
            if 150 < abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) < self.vision and abs(self.pos.y - game.player.pos.y) < 300:
                if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                    self.acc.x = -self.movement_speed
                    self.face_left = False
                else:
                    self.acc.x = self.movement_speed
                    self.face_left = True
            if 150 > abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) and abs(self.pos.y - game.player.pos.y) < 200:
                if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                    self.face_left = False
                else:
                    self.face_left = True
                self.acc.x = 0
                self.current_action = 1
                self.current_sprite = -1
                self.last_attack = pygame.time.get_ticks()
        elif self.berserking and self.current_action != 3:
            if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                self.acc.x = -self.movement_speed/3
                self.face_left = False
            else:
                self.acc.x = self.movement_speed/3
                self.face_left = True

    def attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.hit_rect.center[0])+90, int(self.pos.y)+130, 250, 120, self.game.player_group, 'l', 125, False)
        else:
            Melee_attack(self.game, int(self.hit_rect.center[0])-90, int(self.pos.y)+130, 250, 120, self.game.player_group, 'r', 125, False)

    def hurt(self):
        self.invincible = True
        self.current_action = 2
        self.current_sprite = -1

    def berserk(self):
        if not self.berserking:
            self.sprites[1] = self.berserk_sprites[0]
            self.mirrored_sprites[1] = self.mirrored_berserk_sprites[0]
            self.berserking = True
        self.movement_speed = 0.3+(50-self.health)*0.01
        self.attack_speed = 100-(50-self.health)*1.3
        self.attack_rate = 4000-(50-self.health)*50
        self.vision = 500+(50-self.health)*2.5
        
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
        elif self.current_action == 1:      #attacking
            if now - self.last_sprite_time >= self.attack_speed:
                self.current_sprite += 1
                if self.current_sprite >= 7 and self.current_sprite <= 14:
                    self.attack()
                if self.current_sprite == 15 and 150 > abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) and abs(self.pos.y - game.player.pos.y) < 200:
                    if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                        self.face_left = False
                    else:
                        self.face_left = True
                    self.current_sprite = 7
                    self.attack()
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                    self.current_action = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 2:      #hurt
            if now - self.last_sprite_time >= 75:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.invincible = False
                    self.current_sprite = 0
                    self.current_action = 0
                    self.last_attack = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 3:      #dying
            if now - self.last_sprite_time >= 125:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_action = 3
                    self.current_sprite = 0
                    last_enemy(self.hit_rect.center[0], self.hit_rect.center[1]-30, self.face_left)
                    self.kill()
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.image.set_alpha(255*((16-self.current_sprite)/16))
                self.last_sprite_time = pygame.time.get_ticks()

    def update(self):
        self.movements()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.x = int(self.pos.x)
        wall_collisions(self, 'x')
        self.hit_rect.y = int(self.pos.y)
        wall_collisions(self, 'y')
        self.rect.center = (self.hit_rect.center[0], self.hit_rect.center[1]-70)
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        if self.current_action not in [1, 2, 3]:
            self.current_action = 0
        if self.health <= 25:
            self.berserk()
        if self.health <= 0 and self.current_action != 3:
            self.current_action = 3
            self.current_sprite = -1
        if self.pos.y > self.game.map.height + 3000:
            self.kill()
        self.animations()

#Nightmare class
class Hell_hound(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.enemy_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        paths = ['images/mobs/hell_hound/idle', 'images/mobs/hell_hound/walk', 'images/mobs/hell_hound/run', 'images/mobs/hell_hound/jump']
        self.sprites, self.mirrored_sprites = load_sprites(paths, 2)
        self.current_action = 0
        '''
        Nightmare actions:
        0. idle
        1. walk
        2. run
        3. jump
        '''
        self.current_sprite = 0
        self.face_left = False
        self.image = self.sprites[self.current_action][self.current_sprite]
        self.last_sprite_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 70, 42)
        self.hit_rect.midtop = self.rect.midtop
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.last_attack = pygame.time.get_ticks()
        self.image_offset = 10
        self.attack_rate = 2000
        self.health = 10
        self.attack_speed = 90
        self.movement_speed = 0.8
        self.vision = 500
        self.invincible = False

    def movements(self):
        now = pygame.time.get_ticks()
        self.acc = pygame.math.Vector2(0, GRAVITY)
        if now - self.last_attack >= self.attack_rate:
            if 80 < abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) < self.vision and abs(self.pos.y - game.player.pos.y) < 150:
                self.current_action = 2
                if self.hit_rect.center[0] > game.player.hit_rect.center[0]:
                    self.acc.x = -self.movement_speed
                    self.face_left = False
                else:
                    self.acc.x = self.movement_speed
                    self.face_left = True
            elif 80 > abs(self.hit_rect.center[0] - game.player.hit_rect.center[0]) and abs(self.pos.y - game.player.pos.y) < 150 and self.current_action != 3:
                self.current_action = 3
                self.current_sprite = -1

    def attack(self):
        if self.face_left:
            Melee_attack(self.game, int(self.hit_rect.center[0])+90, int(self.pos.y)+130, 250, 120, self.game.player_group, 'l', 125, False)
        else:
            Melee_attack(self.game, int(self.hit_rect.center[0])-90, int(self.pos.y)+130, 250, 120, self.game.player_group, 'r', 125, False)

    def hurt(self):
        #self.invincible = True
        self.current_action = 0
        self.current_sprite = -1
        
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
        elif self.current_action == 1:      #walking
            if now - self.last_sprite_time >= self.attack_speed:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 2:      #running
            if now - self.last_sprite_time >= self.attack_speed:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
        elif self.current_action == 3:      #jumping
            if now - self.last_sprite_time >= self.attack_speed:
                self.current_sprite += 1
                if self.current_sprite < 4:
                    self.vel.y = -2.5
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                    self.current_action = 0
                    self.last_attack = pygame.time.get_ticks()
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()

    def update(self):
        self.movements()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.x = int(self.pos.x)
        wall_collisions(self, 'x')
        self.hit_rect.y = int(self.pos.y)
        wall_collisions(self, 'y')
        if self.current_action == 3:
            self.image_offset = 40
        else:
            self.image_offset = 10
        self.rect.center = (self.hit_rect.center[0], self.hit_rect.center[1]-self.image_offset)
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        if self.current_action not in [1, 2, 3]:
            self.current_action = 0
        if self.health <= 0:
            self.kill()
        if self.pos.y > self.game.map.height + 3000:
            self.kill()
        self.animations()
        
#Key class
class Key(pygame.sprite.Sprite):
    def __init__(self, game, x, y, face_left):
        self.groups = game.item_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        paths = ['images/items/key/spinning']
        self.sprites, self.mirrored_sprites = load_sprites(paths, 0.3)
        self.current_action = 0
        '''
        Key actions:
        0. spinning
        '''
        self.current_sprite = 0
        self.face_left = False
        self.image = self.sprites[self.current_action][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.pos = pygame.math.Vector2(int(x), int(y))
        self.vel = pygame.math.Vector2(0, -7)
        self.acc = pygame.math.Vector2(0, 0)
        self.hit_rect = pygame.Rect(0, 0, 16, 40)
        self.hit_rect.center = self.rect.center
        self.last_sprite_time = pygame.time.get_ticks()
        self.health = 100
        self.invincible = False

    def movements(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)

    def hurt(self):
        self.vel.y = -3

    def interact(self):
        game.player.items.append('key')
        self.kill()

    def animations(self):
        now = pygame.time.get_ticks()
        sprites_list = self.sprites
        if self.face_left:
            sprites_list = self.mirrored_sprites
        if self.current_action == 0:        #spinning
            if now - self.last_sprite_time >= 200:
                self.current_sprite += 1
                if self.current_sprite > len(sprites_list[self.current_action])-1:
                    self.current_sprite = 0
                self.image = sprites_list[self.current_action][self.current_sprite]
                self.last_sprite_time = pygame.time.get_ticks()
    
    def update(self):
        self.movements()
        self.acc.x += self.vel.x*FRICTION
        self.vel += self.acc
        self.vel.y = min(self.vel.y, 15)        #termial velocity
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.x = int(self.pos.x)
        wall_collisions(self, 'x')
        self.hit_rect.y = int(self.pos.y)
        wall_collisions(self, 'y')
        self.rect.center = (self.hit_rect.center[0], self.hit_rect.center[1])
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
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

#Water class
class Water(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.water_group
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
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

#Door class
class Door(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites_group, game.door_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.closed = pygame.image.load('images/door/closed.png')
        self.opened = pygame.image.load('images/door/open.png')
        self.image = self.closed
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        x, y = int(x), int(y)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.open = False

    def interact(self):
        if self.open:
            self.game.next_level()
        if 'key' in game.player.items and not self.open:
            self.open = True
            self.image = self.opened
        

# -- Utility classes

#Melee attack class
class Melee_attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, target, direction, life_time, single_attack):
        self.groups = game.all_sprites_group, game.melee_attack_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((w, h))
        if self.game.show_hit_rect:
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, w, h)
        self.hit_rect.center = (x, y)
        self.rect.center = self.hit_rect.center
        self.target = target
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = life_time
        self.single_attack = single_attack
        self.direction = direction

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time >= self.life_time:
            self.kill()
        hits = pygame.sprite.spritecollide(self, self.target, False, collide_hit_rect)
        hits += pygame.sprite.spritecollide(self, game.item_group, False, collide_hit_rect)
        if hits:
            for i in hits:
                if i.health > 0 and not i.invincible:
                    i.health -= 1
                    if self.direction == 'l':
                        i.vel.x = KNOCKBACK
                        i.hurt()
                    else:
                        i.vel.x = -KNOCKBACK
                        i.hurt()
            if self.single_attack:
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
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = int(x)
        self.y = int(y)

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
        self.water_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.item_group = pygame.sprite.Group()
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

    def load_map(self, level):
        self.map = TiledMap('maps/map'+str(level)+'.tmx')
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y, self.player_health)
            if tile_object.name == 'slime':
                Slime(self, tile_object.x, tile_object.y)
            if tile_object.name == 'demon':
                self.demon = Demon(self, tile_object.x, tile_object.y)
            if tile_object.name == 'hell_hound':
                Hell_hound(self, tile_object.x, tile_object.y)
            if tile_object.name == 'ladder':
                Ladder(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'water':
                Water(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'wall':
                Wall(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'door':
                Door(self, tile_object.x, tile_object.y)
        self.camera = Camera(self.map.width, self.map.height, self.player.pos.x, self.player.pos.y)

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
                self.update()
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
        self.item_group.update()
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
        string = 'Player health:' + str(self.player.health) + '\nPlayer Air:' + str(self.player.air//10)
        try:
            string += '\nDemon health: ' + str(self.demon.health)
            string += '\nKey speed: ' + str(self.key.x_speed)
        except:
            pass
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
        for i in self.item_group:
            self.screen.blit(i.image, self.camera.apply(i))
        if self.show_hit_rect:
            pygame.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(self.player.hit_rect), 2)
            for i in self.enemy_group:
                pygame.draw.rect(self.screen, LIGHTBLUE, self.camera.apply_rect(i.hit_rect), 2)
            for i in self.item_group:
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














