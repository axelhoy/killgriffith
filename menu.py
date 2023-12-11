import pygame
from data import levels
from tiles import import_folder
from modo import *

class Botones(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path):
        super().__init__()
        self.frame = import_folder(path)
        self.frame_index = 0
        self.image = self.frame[self.frame_index]
        if status == "desbloqueado":
            self.status = "desbloqueado"
        else:
            self.status = "bloqueado"

        self.rect = self.image.get_rect(center = pos)
        self.hitbox_medio = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)
    
    def animate(self):
        self.frame_index += 0.1
        if self.frame_index >= len(self.frame):
            self.frame_index = 0    
        self.image = self.frame[int(self.frame_index)]
        
    def update(self):
        if self.status == "desbloqueado":
            self.animate()
        else:
            tint_surf = pygame.image.load(r"graphics\seleccion_nivel\bloqueado.png").convert_alpha()
            self.image.blit(tint_surf, (0,0))

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos, path):
        super().__init__()
        self.frame = import_folder(path)
        self.frame_index = 0
        self.image = self.frame[self.frame_index]
        self.pos = pos
        self.rect = self.image.get_rect(center = pos)
        
    def animate(self):
        self.frame_index += 0.1
        if self.frame_index >= len(self.frame):
            self.frame_index = 0    
        self.image = self.frame[int(self.frame_index)]
        
    def update(self):
        self.animate()
        