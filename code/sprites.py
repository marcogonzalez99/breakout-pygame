import pygame
from settings import *
from random import choice, randint

class Upgrade(pygame.sprite.Sprite):
    def __init__(self,pos,upgrade_type,groups):
        super().__init__(groups)
        self.upgrade_type = upgrade_type
        self.image = pygame.image.load(f'../graphics/upgrades/{upgrade_type}.png')
        self.rect = self.image.get_rect(midtop = pos)
        
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.speed = 300
        
    def update(self,dt):
        self.pos.y += self.speed * dt
        self.rect.y = round(self.pos.y)
        
        if self.rect.top > WINDOW_HEIGHT + 100:
            self.kill()
  
class Projectile (pygame.sprite.Sprite):
    def __init__(self,pos,surface,groups):
        super().__init__(groups)
        
        self.image = surface
        self.rect = self.image.get_rect(midbottom = pos)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.speed = 300
        
    def update(self,dt):
        self.pos.y -= self.speed * dt
        self.rect.y = round(self.pos.y)
        
        if self.rect.bottom <= -100:
            self.kill
        
        
class Player(pygame.sprite.Sprite):
    def __init__(self,groups,surface_maker):
        super().__init__(groups)
        
        # Setup
        self.display_surface = pygame.display.get_surface()
        self.surface_maker = surface_maker
        self.image = surface_maker.get_surface('player',(WINDOW_WIDTH // 10, WINDOW_HEIGHT // 20))
        
        # Position
        self.rect = self.image.get_rect(midbottom = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        # Create old rect
        self.old_rect = self.rect.copy()
        self.direction = pygame.math.Vector2()
        self.speed = 300
        self.pos = pygame.math.Vector2(self.rect.topleft)
        
        self.hearts = 3
        
        # Laser
        self.laser_amount = 0
        self.laser_surface = pygame.image.load('../graphics/other/laser.png').convert_alpha()
        self.laser_rects= []
        
    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0
            
    def screen_constraint(self):
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.pos.x = self.rect.x
        elif self.rect.left < 0:
            self.rect.left = 0      
            self.pos.x = self.rect.x  
            
    def upgrade(self,upgrade_type):
        if upgrade_type == 'speed':
            self.speed += 50
        if upgrade_type == 'heart':
            self.hearts += 1
        if upgrade_type == 'size':
            new_width = self.rect.width * 1.1
            self.image = self.surface_maker.get_surface('player', (new_width, self.rect.height))
            self.rect = self.image.get_rect(center = self.rect.center)
            self.pos.x = self.rect.x
            
        if upgrade_type == 'laser':
            self.laser_amount += 1  
         
    def display_laser(self):
        self.laser_rects = []
        if self.laser_amount > 0:
            divider_length = self.rect.width / (self.laser_amount + 1)
            for i in range(self.laser_amount):
                x = self.rect.left + divider_length * (i + 1)
                laser_rect = self.laser_surface.get_rect(midbottom = (x,self.rect.top))  
                self.laser_rects.append(laser_rect)
                
            for laser_rect in self.laser_rects:
                self.display_surface.blit(self.laser_surface, laser_rect)
            
    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.input()
        
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        
        # Checks for screen constraint
        self.screen_constraint()
        self.display_laser()
        
class Ball(pygame.sprite.Sprite):
    def __init__(self,groups, player, blocks):
        super().__init__(groups)
        
        # Collision Objects
        self.player = player
        self.blocks = blocks
        
        # Graphics Setup
        self.image = pygame.image.load('../graphics/other/ball.png')
        
        # Position Setup
        self.rect = self.image.get_rect(midbottom = player.rect.midtop)
        self.old_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(choice((1,-1)),-1)
        self.speed = 400
        
        # Active
        self.active = False
        
        # Sounds
        self.impact_sound = pygame.mixer.Sound('../sounds/impact.wav')
        self.impact_sound.set_volume(0.1)
        
        self.fail_sound = pygame.mixer.Sound('../sounds/fail.wav')
        self.fail_sound.set_volume(0.1)
    
    def window_collision(self,direction):
        if direction == 'horizontal':
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.direction.x *= -1
                
            if self.rect.right > WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
                self.pos.x = self.rect.x
                self.direction.x *= -1
        if direction == 'vertical':
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direction.y *= -1
                
            if self.rect.bottom > WINDOW_HEIGHT:
                self.active = False
                self.direction.y = -1
                self.player.hearts -= 1
                self.fail_sound.play()
        
    
    def collision(self,direction):
        # Find Overlapping Objects
        overlap_sprites = pygame.sprite.spritecollide(self,self.blocks,False)
        if self.rect.colliderect(self.player.rect):
            overlap_sprites.append(self.player)
            
        if overlap_sprites:
            if direction == 'horizontal':
                for sprite in overlap_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left - 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.impact_sound.play()
 
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right + 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.impact_sound.play()
                
                if getattr(sprite, 'health',None):
                    sprite.get_damage(1)
                        
            if direction == 'vertical':
                for sprite in overlap_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.impact_sound.play()
 
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom + 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.impact_sound.play()
                
                if getattr(sprite, 'health',None):
                    sprite.get_damage(1)
        
    
    def update(self,dt):
        if self.active:
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            
            # Create old rect
            self.old_rect = self.rect.copy()
            
            # Horizontal Movement + Collision
            self.pos.x += self.direction.x * self.speed * dt
            self.rect.x = round(self.pos.x)
            self.collision('horizontal')
            self.window_collision('horizontal')
            
            # Vertical Movement + Collision
            self.pos.y += self.direction.y * self.speed * dt
            self.rect.y = round(self.pos.y)
            self.collision('vertical')
            self.window_collision('vertical')
        else:
            self.rect.midbottom = self.player.rect.midtop
            self.pos = pygame.math.Vector2(self.rect.topleft)
        
class Block(pygame.sprite.Sprite):
    def __init__(self,block_type,pos,groups,surface_maker,create_upgrade):
        super().__init__(groups)
        self.surface_maker = surface_maker
        self.image = self.surface_maker.get_surface(COLOR_LEGEND[block_type],(BLOCK_WIDTH, BLOCK_HEIGHT))
        self.rect = self.image.get_rect(topleft = pos)
        self.old_rect = self.rect.copy()
        
        # Damage information
        self.health = int(block_type)
        
        # Upgrade
        self.create_upgrade = create_upgrade
        
    def get_damage(self,amount):
        self.health -= amount

        if self.health > 0:
            self.image = self.surface_maker.get_surface(COLOR_LEGEND[str(self.health)], (BLOCK_WIDTH,BLOCK_HEIGHT))
        else:
            if randint(0,10) < 9:
                self.create_upgrade(self.rect.center)
            self.kill()
            