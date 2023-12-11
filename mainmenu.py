import pygame
from menu import Icon, Botones
from data import levels

class SeleccionMenu:
    def __init__(self, start_level, max_level, surface, create_level):
        self.create_level = create_level
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.fondo = pygame.image.load(r"graphics\seleccion_nivel\fondo.jpg").convert_alpha()
        self.setup_botones()
        self.sprite_icono()
        self.moving = False
        self.move_direction = pygame.math.Vector2(0,0)
        self.speed = 15


        self.music_track = pygame.mixer.music.load(r"graphics\sfx\niveles\menu.mp3")
        pygame.mixer.music.set_volume(.1)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        self.sonido_moverse = pygame.mixer.Sound(r"graphics\sfx\seleccion_menu\buttonrollover.wav")
        self.sonido_seleccion = pygame.mixer.Sound(r"graphics\sfx\seleccion_menu\juego.wav")


    def setup_botones(self):
        self.botones = pygame.sprite.Group()
        for indice, valor in enumerate(levels.values()):
            if indice == self.max_level:
                node_sprite = Botones(valor["posicion_menu"], "desbloqueado", 15, valor["boton"])
            else:
                node_sprite = Botones(valor["posicion_menu"], "bloqueado", 15, valor["boton"])
            self.botones.add(node_sprite)

    
    def input(self):
        
        keys =  pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.sonido_seleccion.play()
            self.pantalla_carga()

    def pantalla_carga(self):
        imagen_cargando = pygame.image.load(r"graphics\seleccion_nivel\carga.jpg").convert_alpha()
        self.display_surface.blit(imagen_cargando, ((0,0)))
        pygame.display.flip()
        pygame.time.delay(50)
        self.create_level(self.max_level)

    def sprite_icono(self):
        initial_pos = self.botones.sprites()[self.max_level].rect.center
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(initial_pos, r"graphics\seleccion_nivel\icon")
        self.icon.add(icon_sprite)

    def actualizar(self):
        if self.moving and self.move_direction:
            self.icon.sprite.rect.center += self.move_direction * self.speed
            target_node = self.botones.sprites()[self.current_level]
            if target_node.hitbox_medio.collidepoint(self.icon.sprite.rect.center):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def run(self):
        # self.musica()
        self.display_surface.blit(self.fondo, (0, 0))
        self.input()
        self.actualizar()
        self.icon.update()
        self.botones.update()

        self.botones.draw(self.display_surface)
        self.icon.draw(self.display_surface)
        