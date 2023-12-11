import pygame
from configuracion import *
from modo import *
from tiles import *
from class_disparo import Disparo

class Enemy(AnimatedTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, r"graphics\enemy\enemy_helmet\run")
        self.rect.y += size - self.image.get_size()[1]
        self.speed = 2
        
    def move(self):
        self.rect.x += self.speed
    
    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.animar()
        self.move()
        self.reverse_image()

class Enemy_Knight(AnimatedTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, r"graphics\enemy\enemy_knight\run")
        self.rect.y += size - self.image.get_size()[1]
        self.speed = 2
        
    def move(self):
        self.rect.x += self.speed
    
    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.animar()
        self.move()
        self.reverse_image()

class Skull_Knight(AnimatedTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, r"graphics\enemy\skull_knight\run")
        self.rect.y += size / 2.5 - self.image.get_size()[1]
        self.speed = 0
        
    def move(self):
        self.rect.x += self.speed
    
    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.animar()
        self.move()
        self.reverse_image()

class Boss(pygame.sprite.Sprite):
    def __init__(self,x, y,pantalla,check_vida,check_en_rango):
        super().__init__()

        self.reiniciar_animacion = False
        self.check_vida = check_vida
        self.vida = self.check_vida()
        self.vida_anterior = self.vida
        self.display_surface = pantalla

        self.importar_assets_jefe()
        self.indice_frames = 0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["run"][self.indice_frames]
        self.rect = self.image.get_rect(topleft=(x,y))
        self.rectangulo_colision = pygame.Rect(((self.rect.topleft[0]+41),self.rect.topleft[1]),(45,self.rect.height))
       
        self.direccion = pygame.math.Vector2(0,0) 
        self.velocidad = 2
        
        self.invencible = False
        self.duracion_invencible = 600
        self.tiempo_herido = 0

        self.status = 'run'
        self.facing_right = False
        self.piso = False
        self.techo = False
        self.herido = False

        self.check_en_rango = check_en_rango
        self.en_rango = self.check_en_rango()
        self.esta_atacando = False
        self.esta_disparando = False
        self.duracion_atacando = 750
        self.tiempo_atancando = 0
        self.lista_proyectiles = []

    def importar_assets_jefe(self):

        character_path = r'graphics\enemy\boss'
        self.animaciones ={'run':[],'ataca':[],'dañado':[]}

        for animacion in self.animaciones.keys():
            path_completo = character_path +"\\"+ animacion
            self.animaciones[animacion] = import_folder(path_completo)
    
    def animate(self):
        animacion = self.animaciones[self.status]
        if self.reiniciar_animacion:
            self.indice_frames = 0
            self.reiniciar_animacion = False

        self.indice_frames += self.velocidad_animacion
            
        if self.indice_frames >= len(animacion):
            self.indice_frames = 0
            
        image = animacion[int(self.indice_frames)]
        if not self.facing_right:
            self.image = image
            
        else:
            flipped_image = pygame.transform.flip(image,True,False)
            self.image =  flipped_image

    def mover(self):
        self.rect.x += self.velocidad
        if self.rect.x < 0 or self.rect.right > screen_width:
            self.reversa()
            self.cambiar_sentido()

    def reversa(self):
        self.velocidad *= -1

    def get_input(self):
        if self.vida != self.vida_anterior:
                self.recibe_daño()
        elif self.vida == self.vida_anterior and not self.invencible and not self.esta_disparando and not self.esta_atacando and not self.en_rango:
            self.status = "run"
        if self.en_rango and not self.invencible and not self.esta_disparando:
            self.disparo()
        elif not self.invencible and not self.esta_disparando and not self.esta_atacando and not self.en_rango:
            self.mover()
        
    def cambiar_sentido(self):
        self.facing_right = not self.facing_right

    def recibe_daño(self):
        self.status = 'dañado'
        self.vida_anterior = self.vida
        self.invencible = True
        self.tiempo_herido = pygame.time.get_ticks()

    def timer_invencible(self):
        if self.invencible:
            tiempo_actual_invencible = pygame.time.get_ticks()
            if tiempo_actual_invencible - self.tiempo_herido >= self.duracion_invencible:
                self.invencible = False

    def timer_disparo(self):
        if self.esta_disparando:
            tiempo_actual_disparo = pygame.time.get_ticks()
            if tiempo_actual_disparo - self.tiempo_atancando >= self.duracion_atacando:
                self.lanzar_proyectil()
                self.esta_disparando = False
                self.salio_el_proyectil = True
                self.reiniciar_animacion = True

    def disparo(self):
        if not self.esta_disparando and not self.invencible:
            self.status = 'ataca'
            self.esta_disparando = True
            self.tiempo_atancando = pygame.time.get_ticks()

    def lanzar_proyectil(self):
        if not self.invencible:
            x = None
            margen = 47
            y = self.rectangulo_colision.centery
            if  self.facing_right:
                x = self.rectangulo_colision.right - margen
            elif not  self.facing_right:
                x = self.rectangulo_colision.left -100 + margen
            if x is not None:
                path = r"graphics\enemy\boss\disparo"
                self.lista_proyectiles.append(Disparo(x,y,20,self.facing_right,(path),False,10))

    def update(self, shift):
        self.rect.x += shift
        self.en_rango = self.check_en_rango()
        self.get_input()
        self.animate()
        self.vida = self.check_vida()
        self.importar_assets_jefe()
        self.timer_invencible()
        self.timer_disparo()
        self.rectangulo_colision = pygame.Rect(((self.rect.topleft[0]+41),self.rect.topleft[1]),(45,self.rect.height))

