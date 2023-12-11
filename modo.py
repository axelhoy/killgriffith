import pygame
DEBUG = False

def cambiar_modo():
    global DEBUG
    DEBUG = not DEBUG

def obtener_modo():
    return DEBUG

def reescalar_imagenes(diccionario_animaciones, ancho, alto):
    for clave in diccionario_animaciones:
        for i in range(len(diccionario_animaciones[clave])):
            img = diccionario_animaciones[clave][i]
            diccionario_animaciones[clave][i] = pygame.transform.scale(img, (ancho, alto))