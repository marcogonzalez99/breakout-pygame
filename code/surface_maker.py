import pygame
from settings import *
from os import walk

class SurfaceMaker:
    # Import all the graphics
    def __init__(self):
        for index,info in enumerate(walk('../graphics/blocks')):
            if index == 0:
                self.assets = {color: {} for color in info[1]}
            else:
                for image_name in info[2]:
                    color_type = list(self.assets.keys())[index-1]
                    full_path = '../graphics/blocks' + f'/{color_type}/' + image_name
                    surface = pygame.image.load(full_path).convert_alpha()
                    self.assets[color_type][image_name.split('.')[0]] = surface
    
    def get_surface(self,block_type,size):
        
        # Create one surface with the graphics at any size
        image = pygame.Surface(size)
        image.set_colorkey((0,0,0))
        sides = self.assets[block_type]
        
        
        # 4 Corners
        image.blit(sides['topleft'],(0,0))
        image.blit(sides['topright'],(size[0] - sides['topright'].get_width(),0))
        image.blit(sides['bottomleft'],(0,size[1] - sides['bottomleft'].get_height()))
        image.blit(sides['bottomright'],(size[0] - sides['topright'].get_width(),size[1] - sides['bottomleft'].get_height()))
        
        # Top Side
        top_width = size[0] - (sides['topleft'].get_width() + sides['topright'].get_width())
        scaled_top_surface = pygame.transform.scale(sides['top'], (top_width, sides['top'].get_height()))
        image.blit(scaled_top_surface, (sides['topleft'].get_width(),0))
        
        # Left Side
        left_height = size[1] - (sides['topleft'].get_height() + sides['bottomleft'].get_height())
        scaled_left_surface = pygame.transform.scale(sides['left'],(sides['left'].get_width(),left_height))
        image.blit(scaled_left_surface, (0,sides['topleft'].get_height()))
        
        # Right Side
        right_height = size[1] - (sides['topright'].get_height() + sides['bottomright'].get_height())
        scaled_right_surface = pygame.transform.scale(sides['right'],(sides['right'].get_width(),right_height))
        image.blit(scaled_right_surface, (size[0] - sides['right'].get_width(),sides['topright'].get_height()))
        
        # Bottom Side
        bottom_width = size[0] - (sides['bottomleft'].get_width() + sides['bottomright'].get_width())
        scaled_bottom_surface = pygame.transform.scale(sides['bottom'], (bottom_width, sides['bottom'].get_height()))
        image.blit(scaled_bottom_surface, (sides['topleft'].get_width(), size[1] - sides['bottom'].get_height()))
        
        # Center Color
        center_height = size[1] - (sides['top'].get_height() + sides['bottom'].get_height())
        center_width = size[0] - (sides['left'].get_width() + sides['right'].get_width())
        scaled_center = pygame.transform.scale(sides['center'], (center_width, center_height))
        image.blit(scaled_center,sides['topleft'].get_size())
        
        
        return image