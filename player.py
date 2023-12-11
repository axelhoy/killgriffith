import pygame
from tiles import import_folder
from modo import *
import random
from class_disparo import Disparo

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, cambiar_vida, cambiar_balas, cantidad_balas):
        super().__init__()
        self.importar_assets()
        self.disparo_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\disparo.wav")
        self.sound_volume = 100
        self.music_volume = 100
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations["idle"][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        self.golpe_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\sword.wav")


        self.salto_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\salto.ogg")
        self.hit_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\hit.ogg")

        self.cambiar_balas = cambiar_balas
        self.cambiar_vida = cambiar_vida
        self.cantidad_balas = cantidad_balas
        self.balas_actuales = self.cantidad_balas()

        self.invencible = False
        self.duracion_invencible = 500
        self.tiempo_dañado = 0

        self.attacking = False 
        self.attack_cooldown = 0 
        
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 20
        self.gravity = 0.8
        self.salto_speed = -20
        self.colission_rect = pygame.Rect(self.rect.topleft, (100, self.rect.height))
        
        self.estado_jugador = "idle"
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False

        self.esta_disparando = False
        self.duracion_atacando = 600
        self.tiempo_atacando = 0
        self.reiniciar_ataque = True
        self.lista_proyectiles = []

    def importar_assets(self):
        '''
        Carga imagenes, las organiza en categorías de animación y las redimensiona a un tamaño específico. 
        '''
        character_path = "graphics\\character\\"
        self.animations = {"idle":[], "run":[], "jump":[], "fall":[], "invencible":[], "hit":[], "animacion_disparo":[]}
        for animation in self.animations:
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
        
        reescalar_imagenes(self.animations, 150,75 )

    def animar(self):
        '''
        Utiliza imágenes almacenadas en self.animations
        Se actualiza el índice de fotogramas a una velocidad específica y se ajusta la imagen según la dirección del personaje. 
        La posición del rectángulo se actualiza en consecuencia.
        '''
        animation = self.animations[self.estado_jugador]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        image = animation[int(self.frame_index)]

        if self.facing_right:
            self.image = image
            self.rect.bottomleft = self.colission_rect.bottomleft
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image
            self.rect.bottomright = self.colission_rect.bottomright

        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)


    def get_input(self):
        '''
        Detecta las teclas presionadas, ajusta la dirección, orientación y/o acciones del personaje en consecuencia. 
        '''
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        elif keys[pygame.K_TAB]:
            cambiar_modo()
        elif keys[pygame.K_e]:
            self.golpea()
        elif keys[pygame.K_q] and not self.esta_disparando and self.balas_actuales > 0:
            self.disparo()
            self.cambiar_balas(-1)
            self.lanzar_proyectil()
        else:
            self.direction.x = 0
        if keys[pygame.K_SPACE] and self.on_ground:
            self.salto_sound.set_volume(self.sound_volume / 200.0)
            self.salto_sound.play()
            self.salto()
    
    def get_estado_jugador(self):
        '''
        Cambia el estado del jugador dependiendo de las variantes dadas
        '''
        if not self.attacking:
            if self.direction.y < 0:
                self.estado_jugador = "jump"
            elif self.direction.y > 1:
                self.estado_jugador = "fall"
            else:
                if self.direction.x != 0:
                    self.estado_jugador = "run"
                else:
                    self.estado_jugador = "idle"
        
        if self.invencible:
            self.estado_jugador = "invencible"
        if self.attacking:
            self.estado_jugador = "hit"
        if self.esta_disparando:
            self.estado_jugador = "animacion_disparo"

    def gravedad(self):
        self.direction.y += self.gravity
        self.colission_rect.y += self.direction.y

    def disparo(self):
        if not self.esta_disparando:
            self.disparo_sound.play()
            self.esta_disparando = True
            self.tiempo_atacando = pygame.time.get_ticks()

    def lanzar_proyectil(self):
        x = None
        margen = 47
        y = self.colission_rect.centery - 20
        if self.facing_right:
            x = self.colission_rect.right - margen
        elif not  self.facing_right:
            x = self.colission_rect.left -100 + margen
        if x is not None:
            self.lista_proyectiles.append(Disparo(x,y,20,self.facing_right,(r"graphics\character\disparo")))
            
    def salto(self):
        self.direction.y = self.salto_speed 
    def recibe_daño(self):
        if not self.invencible:
            self.hit_sound.set_volume(self.sound_volume / 200.0)
            self.hit_sound.play()
            self.cambiar_vida(-10)
            self.invencible = True
            self.tiempo_dañado = pygame.time.get_ticks()
    def timer_invencible(self):
        if self.invencible:
            if self.facing_right:
                self.direction.y = -3
            else:
                self.direction.y = -3
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_dañado >= self.duracion_invencible:
                self.invencible = False

    def golpea(self):
        if not self.attacking and self.attack_cooldown == 0:
            self.golpe_sound.play()
            self.attacking = True
            self.attack_cooldown = 40
    def timer_golpe(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        elif self.attacking:
            self.attacking = False
    def timer_disparo(self):
        if self.esta_disparando:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_atacando >= self.duracion_atacando:
                self.esta_disparando = False
                self.reiniciar_ataque = True

    def update(self):
        self.balas_actuales = self.cantidad_balas()
        self.get_input()
        self.get_estado_jugador()
        self.animar()
        self.timer_invencible()
        self.timer_golpe()
        self.timer_disparo()

