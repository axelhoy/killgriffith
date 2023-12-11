import pygame, sys, json, sqlite3
from pygame.locals import *
from configuracion import *
from nivel import Nivel
from data import *
from mainmenu import SeleccionMenu
from ui import UI
from opcione import *
from pyvidplayer import Video

class Game:
    def __init__(self):
        self.conn = sqlite3.connect('db1.db')
        self.cursor = self.conn.cursor()
        self.nombre = ""
        self.event = ""
        self.max_level = self.load_unlocked_levels()
        self.vida_maxima = 100
        self.vida_actual = 100
        self.vida_maxima_boss = 20
        self.vida_actual_boss = 20
        self.monedas = 0
        self.cantidad_vidas = 3

        self.sound_volume = self.load_sonido()
        self.music_volume = self.load_volumen()
        
        self.life_loss_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\life_loss.wav")
        self.menu = SeleccionMenu(0, self.max_level, screen, self.crear_level)
        self.status = "video"
        self.ui = UI(screen, self.perder_vida)

        self.vid = Video(r"graphics\opening.mp4")
        self.vid.set_size((screen_width,screen_height))

        self.paused = False 
        self.pause_selection = 0
        self.menu_selection = 0

        self.options_menu_active = False
        self.options_selection = 0
        self.puntaje_global = 1000
        self.total_balas = 10
        self.balas_actuales = 10

        self.ranking = self.obtener_ranking()

    def crear_level(self, current_level):
        self.level = Nivel(current_level, screen, self.crear_seleccion_menu, self.cambiar_monedas, self.cambiar_vida, self.vida_actual, self.perder_vida, self.sound_volume, self.music_volume, self.cambiar_puntaje, self.retornar_puntaje, self.nombre, self.paused, self.cambiar_balas, self.actualizar_balas, self.cambiar_vida_boss)
        self.status = "nivel"

    def load_unlocked_levels(self):
        try:
            with open('niveles_desbloqueados.json', 'r') as json_file:
                unlocked_levels = json.load(json_file)
                return unlocked_levels.get('max_level')
        except FileNotFoundError:
            default_unlocked_levels = {'max_level': 0,
                    'music_volume': 100,
                    'sound_volume': 100
                }
            with open('niveles_desbloqueados.json', 'w') as json_file:
                json.dump(default_unlocked_levels, json_file)
            return 0
        
    def load_volumen(self):
        with open('niveles_desbloqueados.json', 'r') as json_file:
            unlocked_levels = json.load(json_file)
            return unlocked_levels.get('music_volume')



    def load_sonido(self):
        with open('niveles_desbloqueados.json', 'r') as json_file:
            unlocked_levels = json.load(json_file)
            return unlocked_levels.get('sound_volume')

    def crear_seleccion_menu(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level

            unlocked_levels = {'max_level': self.max_level,
                'music_volume': self.music_volume,
                'sound_volume': self.sound_volume}
            with open('niveles_desbloqueados.json', 'w') as json_file:
                json.dump(unlocked_levels, json_file)

        self.menu = SeleccionMenu(current_level, self.max_level, screen, self.crear_level)
        self.status = "seleccion_mapa"
        
    def cambiar_monedas(self, cantidad):
        self.monedas += cantidad

    def cambiar_vida(self, cantidad):
        self.vida_actual += cantidad
    
    def cambiar_vida_boss(self, cantidad):
        self.vida_actual_boss += cantidad
    
    def cambiar_puntaje(self, cantidad):
        self.puntaje_global += cantidad
    
    def cambiar_balas(self, cantidad):
        self.balas_actuales += cantidad
    
    def actualizar_balas(self):
        return self.balas_actuales
    
    def retornar_puntaje(self):
        self.puntaje_global = self.puntaje_global
        return self.puntaje_global

    def perder_vida(self, cantidad):
        self.cantidad_vidas += cantidad

    def cleanup(self):
        self.puntaje_global = 1000
        self.max_level = 0
        self.save_game_state()

    def save_game_state(self):
        unlocked_levels = {'max_level': self.max_level,
                           'music_volume': self.music_volume,
                           'sound_volume': self.sound_volume}
        with open('niveles_desbloqueados.json', 'w') as json_file:
            json.dump(unlocked_levels, json_file)
    
    def juego_terminado(self):
        if self.vida_actual <= 0:
            self.life_loss_sound.set_volume(self.sound_volume / 200.0)
            self.life_loss_sound.play()
            self.vida_actual = 100
            self.cantidad_vidas -=1
        if self.cantidad_vidas <= 0:
            self.cantidad_vidas = 3
            self.menu = SeleccionMenu(0, self.max_level, screen, self.crear_level)
            self.status = "seleccion_mapa" 

    def obtener_ranking(self):
        try:
            self.cursor.execute('''
                SELECT nombre, puntaje, id FROM Jugadores
                ORDER BY puntaje DESC 
                LIMIT 3
            ''')
            ranking = self.cursor.fetchall()
            return ranking
        except Exception as e:
            print("Error al obtener ranking:", e)
            return []
        
    def run(self):
        self.sound_volume = self.load_sonido()
        self.music_volume = self.load_volumen()
        keys = pygame.key.get_pressed()
        clock = pygame.time.Clock()

        if self.status == "video":
            self.vid.set_volume(0)
            self.vid.draw(screen, (0,0))
            if keys[pygame.K_SPACE]:
                self.status = "nombre"
                self.vid.close()
        elif self.status == "nombre":
            self.status, self.nombre = draw_nombre(screen, screen_width, screen_height, self.status, self.nombre)
        elif self.status == "ranking":
            self.status = mostrar_pantalla_ranking(screen, screen_width, self.status,self.ranking)
        elif self.status == "menu":
            clock.tick(20)
            self.status, self.menu_selection = draw_mainn_menu(screen, screen_width, screen_height, self.status, self.menu_selection)
        elif self.status == "seleccion_mapa":
            self.menu.run()
        elif self.status == "nivel":
            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE]:
                self.paused = not self.paused
                self.options_menu_active = False 

            if self.paused:
                clock.tick(10)
                self.pause_selection, self.paused, self.options_menu_active = draw_pause_menu(
                    screen, screen_width, screen_height, 
                    self.pause_selection, self.paused, self.options_menu_active
                )

            elif self.options_menu_active:
                clock.tick(10)
                configuracion = {
                'max_level': self.max_level,
                'music_volume': self.music_volume,
                'sound_volume': self.sound_volume
                }
                self.options_selection, self.paused, self.options_menu_active, self.music_volume, self.sound_volume = draw_options_menu(
                    screen, screen_width, screen_height, 
                    self.options_selection, self.options_menu_active, self.paused,
                    self.music_volume, self.sound_volume, configuracion
                )
                self.level.update_sound_volume(self.sound_volume, self.music_volume)

            else:
                self.level.run()
                self.level.agarrar_vida(self.vida_actual)
                self.level.mostrar_cronometro(screen)
                self.ui.mostrar_vida(self.vida_actual, self.vida_maxima)
                self.ui.mostrar_monedas(self.monedas)
                self.ui.mostrar_cantidad_vidas(self.cantidad_vidas)
                self.ui.mostrar_puntaje(self.puntaje_global)
                self.ui.mostrar_balas(self.balas_actuales)
                self.ui.barra_boss(self.max_level, self.vida_actual_boss, self.vida_maxima_boss)
                self.juego_terminado()


pygame.init()

screen =  pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("KILL GRIFFITH")
clock = pygame.time.Clock()
game = Game()
estado = ""
maximo = 8
key_sound = pygame.mixer.Sound(r"graphics\sfx\seleccion_menu\keypressed.mp3")
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.cleanup()  
            pygame.quit()
            sys.exit()

        keys = pygame.key.get_pressed()

        if game.status == "nombre":
            if keys[pygame.K_BACKSPACE]:
                key_sound.play()
                game.nombre = game.nombre[:-1]
            else:
                if len(game.nombre) < maximo:
                    if event.type == pygame.KEYDOWN:
                        if event.key != pygame.K_RETURN:
                            key_sound.play()
                            key_name = pygame.key.name(event.key)
                            if len(key_name) == 1 and key_name.isprintable():
                                game.nombre += key_name
    game.run()
    pygame.display.update()
 