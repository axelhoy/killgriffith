import pygame
from configuracion import *
class UI:
    def __init__(self, surface, perder_vida):
        self.display_surface = surface
        self.vida_100 = pygame.image.load(r"graphics\ui\barra_vida\100.png")
        self.vida_75 = pygame.image.load(r"graphics\ui\barra_vida\75.png")
        self.vida_50 = pygame.image.load(r"graphics\ui\barra_vida\50.png")
        self.vida_25 = pygame.image.load(r"graphics\ui\barra_vida\25.png")
        self.thom_yorke = pygame.image.load(r"graphics\unnamed.jpg")
        self.easter_egg = pygame.transform.scale(self.thom_yorke, (15,15))
        self.vida_boss = pygame.image.load(r"graphics\ui\barra_vida\boss.png")

        self.barra_ancho = 320
        self.barra_alto = 20
        self.perder_vida = perder_vida

        self.coin = pygame.image.load(r"graphics\ui\coin.png")
        self.bala = pygame.image.load(r"graphics\ui\bala.png")
        self.fuente = pygame.font.Font(r"graphics\Greek-Freak.ttf", 20)

        self.cantidad_vidas = pygame.image.load(r"graphics\ui\MC_Heart.png")
        self.score_board = pygame.image.load(r"graphics\ui\scoreboard.png")
        self.score_board = pygame.transform.scale(self.score_board, (100,100))
    def mostrar_vida(self, actual, llena):
        if actual < 26:
            self.display_surface.blit(self.vida_25, (25, 25))
        elif actual < 51:
            self.display_surface.blit(self.vida_50, (25, 25))
        elif actual < 76:
            self.display_surface.blit(self.vida_75, (25, 25))
        else:
            self.display_surface.blit(self.vida_100, (25, 25))
        porcentaje_vida = actual / llena
        barra_ancha_actual = self.barra_ancho * porcentaje_vida
        barra_vida_rect = pygame.Rect((107,65), (barra_ancha_actual, self.barra_alto))
        pygame.draw.rect(self.display_surface, "#A70000", barra_vida_rect)

    def mostrar_monedas(self, cantidad):
        self.display_surface.blit(self.easter_egg, (1740, 10))
        self.display_surface.blit(self.coin, (100, 100))
        cantidad_monedas = self.fuente.render(str(cantidad), False, "white")
        self.display_surface.blit(cantidad_monedas, (150,114))
    
    def mostrar_cantidad_vidas(self, cantidad):
        self.display_surface.blit(self.cantidad_vidas, (500, 50))
        str_vidas = self.fuente.render(str(cantidad), False, "white")
        self.display_surface.blit(str_vidas, (570,60))

    def mostrar_puntaje(self, puntaje_global):
        texto_puntaje = self.fuente.render(f"{puntaje_global:02d}", True, "white")
        self.display_surface.blit(self.score_board, (870, 33))
        self.display_surface.blit(texto_puntaje, (900, 70))

    def mostrar_balas(self, balas):
        self.display_surface.blit(self.bala, (350, 100))
        cantidad_monedas = self.fuente.render(str(balas), False, "white")
        self.display_surface.blit(cantidad_monedas, (400,114))

    def barra_boss(self, max_level, actual, llena):
        if max_level == 2:
            self.display_surface.blit(self.vida_boss, (screen_width // 2.5, screen_height // 1.2))
            porcentaje_vida = actual / llena
            barra_ancha_actual = self.barra_ancho * porcentaje_vida
            barra_vida_rect = pygame.Rect((screen_width // 2.24, screen_height // 1.14), (barra_ancha_actual, self.barra_alto))
            pygame.draw.rect(self.display_surface, "#A70000", barra_vida_rect)