import pygame,sys,time
from settings import *
from sprites import Player, Ball, Block, Upgrade, Projectile
from surface_maker import SurfaceMaker
from random import choice, randint

class Game:
    def __init__(self):
        
        # General Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Breakout")
        
        # Background
        self.bg = self.create_bg()
        
        # Sprite Group Setup
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.upgrade_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()
        
        # Setup
        self.surface_maker = SurfaceMaker()
        self.player = Player(self.all_sprites, self.surface_maker)
        self.create_stage()
        self.ball = Ball(self.all_sprites, self.player, self.block_sprites)
        
        # Hearts
        self.hearts_surface = pygame.image.load('../graphics/other/heart.png').convert_alpha()

        # Projectile
        self.projectile_surface = pygame.image.load('../graphics/other/projectile.png').convert_alpha()
        self.can_shoot = True
        self.shoot_timer = 0
        
        #CRT
        self.crt = CRT()
        
        self.laser_sound = pygame.mixer.Sound('../sounds/laser.wav')
        self.laser_sound.set_volume(0.1)
 
        self.powerup_sound = pygame.mixer.Sound('../sounds/powerup.wav')
        self.powerup_sound.set_volume(0.1)
 
        self.laserhit_sound = pygame.mixer.Sound('../sounds/laser_hit.wav')
        self.laserhit_sound.set_volume(0.02)
 
        self.music = pygame.mixer.Sound('../sounds/music.wav')
        self.music.set_volume(0.1)
        self.music.play(loops = -1)
     
    def create_upgrade(self,pos):
        upgrade_type = choice(UPGRADES)
        Upgrade(pos,upgrade_type,[self.all_sprites,self.upgrade_sprites])
        
    def create_bg(self):
        bg_original = pygame.image.load('../graphics/other/bg.png').convert()
        scale_factor = WINDOW_HEIGHT / bg_original.get_height()
        scaled_width = bg_original.get_width() * scale_factor
        scaled_height = bg_original.get_height() * scale_factor
        scaled_bg = pygame.transform.scale(bg_original, (scaled_width,scaled_height))
        return scaled_bg
    
    def create_stage(self):
        # Cycle through all the rows and columns of the BLOCK MAP
        for row_index,row in enumerate(BLOCK_MAP):
            for col_index, col in enumerate(row):
                if col != ' ':
                    x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
                    y = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
                    Block(col,(x,y),[self.all_sprites, self.block_sprites], self.surface_maker,self.create_upgrade)
        # Find the x and y position
        
    def display_hearts(self):
        for i in range(self.player.hearts):
            x = 2+ i * (self.hearts_surface.get_width() + 2)
            self.display_surface.blit(self.hearts_surface, (x,4))
            
    def upgrade_collision(self):
        overlap_sprites = pygame.sprite.spritecollide(self.player, self.upgrade_sprites, True)
        for sprite in overlap_sprites:
            self.player.upgrade(sprite.upgrade_type)
            self.powerup_sound.play()
    
    def create_projetile(self):
        self.laser_sound.play()
        for projectile in self.player.laser_rects:
            Projectile(
                projectile.midtop - pygame.math.Vector2(0,30),
                self.projectile_surface,
                [self.all_sprites,self.projectile_sprites])
           
    def laser_timer(self):
        if pygame.time.get_ticks() - self.shoot_timer > 750:
            self.can_shoot = True               
  
    def projectile_block_collision(self):
        for projectile in self.projectile_sprites:
            overlap_sprites = pygame.sprite.spritecollide(projectile, self.block_sprites, False)
            if overlap_sprites:
                for sprite in overlap_sprites:
                    sprite.get_damage(1)
                projectile.kill()
                self.laserhit_sound.play()
    
    def run(self):
        last_time = time.time()
        while True:
        
            # Delta Time
            dt = time.time() - last_time
            last_time = time.time()   
            
            # Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT or self.player.hearts <= 0:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.ball.active = True
                        if self.can_shoot:
                            self.create_projetile()  
                            self.can_shoot = False
                            self.shoot_timer = pygame.time.get_ticks()   
                
            # Draw the frame
            self.display_surface.blit(self.bg, (0,0))         
            
            # Update the game
            self.all_sprites.update(dt)        
                    
            # Draw all Sprites
            self.all_sprites.draw(self.display_surface) 
            self.display_hearts()
            self.upgrade_collision()
            self.laser_timer()
            self.projectile_block_collision()
            
            # CRT Style   
            self.crt.draw()
                    
            # Update Window
            pygame.display.update()
     
class CRT:
    def __init__(self):
        vignette = pygame.image.load('../graphics/other/tv.png').convert_alpha()
        self.scaled_vignette = pygame.transform.scale(vignette, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.create_crt_lines()
       
    def create_crt_lines(self):
        line_height = 4
        line_amount = WINDOW_HEIGHT // line_height
        for line in range(line_amount):
            y = line * line_height
            pygame.draw.line(self.scaled_vignette, 'black', (0,y),(WINDOW_WIDTH,y))
       
    def draw(self):
        self.scaled_vignette.set_alpha(randint(70,90))
        self.display_surface.blit(self.scaled_vignette,(0,0))
    
if __name__ == '__main__':
    game = Game()
    game.run() 