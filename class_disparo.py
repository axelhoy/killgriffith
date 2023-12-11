import pygame
from tiles import import_folder
class Disparo:
    def __init__(self, x, y,tamanio, direccion,path,valor=True, velocidad = 8):
        self.image = pygame.Surface((tamanio,tamanio))
        self.rect = self.image.get_rect()
        self.rectangulo_colision = pygame.Rect(self.rect.center,(20,20))
        self.rect.x = x
        self.rectangulo_colision.x = self.rect.x +20
        self.rect.centery = y
        self.rectangulo_colision.centery = y +20
        self.direccion = direccion
        self.velocidad_proyectil = velocidad
        self.invertir = valor

        self.frames = import_folder(path)
        self.indice_frames = 0
        self.image = self.frames[self.indice_frames]

    def animar(self):
        self.indice_frames += 0.1
        if self.indice_frames >=len(self.frames):
            self.indice_frames = 0
        self.image = self.frames[int(self.indice_frames)]
        if not self.direccion and  self.invertir:
            self.image = pygame.transform.flip(self.image,True,False)

    def update(self):
        if self.direccion:
            nueva_x = lambda x,v:(x+v)
            self.rect.x = nueva_x(self.rect.x,self.velocidad_proyectil)
            self.rectangulo_colision.x =nueva_x(self.rect.x,self.velocidad_proyectil)
        elif not self.direccion:
            nueva_x = lambda x,v:(x-v)
            self.rect.x = nueva_x(self.rect.x,self.velocidad_proyectil)
            self.rectangulo_colision.x = self.rect.x + 25
        self.animar()