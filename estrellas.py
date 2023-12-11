import pygame
from configuracion import *
from random import *
from tiles import StaticTile, import_folder

class Estrella:
    def __init__(self, max_y, level_width,cantidad_estrellas):
        lista_estrellas = import_folder(r"graphics\estrellas\stars")
        x_minimo = 0
        x_maximo = level_width
        y_minimo = 0
        y_maximo = max_y
        self.estrellas_sprites = pygame.sprite.Group()

        for estrella in range(cantidad_estrellas):
            estrella = choice(lista_estrellas)
            x = randint(x_minimo, x_maximo)
            y = randint(y_minimo, y_maximo)
            sprite = StaticTile(0, x, y, estrella)
            self.estrellas_sprites.add(sprite)
    def dibujar(self, surface, shift):
        self.estrellas_sprites.update(shift)
        self.estrellas_sprites.draw(surface)