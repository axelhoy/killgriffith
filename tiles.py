import pygame
from os import path, walk

def import_folder(folder_path):
    '''
    Carga las imágenes de un directorio dado y las devuelve como una lista de superficies
    Walk se usa para obtener la lista de archivos en el directorio, (carpeta/subcarpeta/archivo)
    Las imágenes se convierten (.convert_alpha()) para manejar transparencias, y la lista resultante se devuelve como salida de la función.
    '''
    surface_list = []
    for _, __, image_files in walk(folder_path):
        for image in image_files:
            full_path = path.join(folder_path, image)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        '''
        Tile basico, crea una surface y una rectaa
        '''
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.rect = self.image.get_rect(topleft = (x,y))
    
    def update(self, shift):
        self.rect.x += shift

class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface

class AnimatedTile(Tile):
    def __init__(self, size, x, y, path):
        '''
        Utilizando la logica para animar, anima los Tile con secuencia de imagenes
        '''
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
    
    def animar(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0    
        self.image = self.frames[int(self.frame_index)]
    
    def update(self, shift):
        self.animar()
        self.rect.x += shift

class Coin(AnimatedTile):
    def __init__(self, size, x, y, path):
        '''
        Creado ya que la moneda quedaba flotando en el topleft.
        Con esto se fixea y se mueve al centro de su posicion
        '''
        super().__init__(size, x, y, path)
        self.rect = self.image.get_rect(center = ((x + size // 2), (y + size // 2)))