import pygame
from tiles import import_folder

class MuerteEnemiga(pygame.sprite.Sprite):
    def __init__(self, pos, tipo):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.15
        if tipo == "muerte":
            self.frames = import_folder("graphics\enemy\enemy_knight\death")
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midtop = pos)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
    
    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift