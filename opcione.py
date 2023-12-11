import pygame, json, re


pygame.mixer.init()
sonido_moverse = pygame.mixer.Sound(r"graphics\sfx\seleccion_menu\buttonrollover.wav")
sonido_seleccion = pygame.mixer.Sound(r"graphics\sfx\seleccion_menu\juego.wav")
def draw_pause_menu(screen, screen_width, screen_height, pause_selection, paused, options_menu_active):
    fondo_pausa = pygame.image.load(r"graphics\seleccion_nivel\pausa.png")
    screen.blit(fondo_pausa, (0,0))
    font = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 10)

    if paused:
        resume_text = font.render("resumir", True, (255, 255, 255))
        options_text = font.render("opciones", True, (255, 255, 255))
        quit_text = font.render("salir", True, (255, 255, 255))

        selected_color = (255, 0, 0)
        if pause_selection == 0:
            resume_text = font.render("resumir", True, selected_color)
        elif pause_selection == 1:
            options_text = font.render("opciones", True, selected_color)
        elif pause_selection == 2:
            quit_text = font.render("salir", True, selected_color)

        screen.blit(resume_text, (screen_width // 2.9, screen_height // 2 - 200))
        screen.blit(options_text, (screen_width // 3.15, screen_height // 2))
        screen.blit(quit_text, (screen_width // 2.6, screen_height // 2 + 200))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            sonido_seleccion.play()
            if pause_selection == 0:
                paused = not paused
            elif pause_selection == 1:
                paused = not paused
                options_menu_active = not options_menu_active
            elif pause_selection == 2:
                pygame.quit()

        if keys[pygame.K_w]:
            sonido_moverse.play()
            pause_selection = (pause_selection - 1) % 3
        elif keys[pygame.K_s]:
            sonido_moverse.play()
            pause_selection = (pause_selection + 1) % 3

    return pause_selection, paused, options_menu_active


def draw_options_menu(screen, screen_width, screen_height, options_selection, options_menu_active, paused, music_volume, sound_volume, configuracion):
    fondo_audio = pygame.image.load(r"graphics\seleccion_nivel\audio.png")
    screen.blit(fondo_audio, (0, 0))
    font = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 10)


    if options_menu_active:
        music_volume_text = font.render(f"musica: {music_volume}", True, (255, 255, 255))
        sound_volume_text = font.render(f"sonido: {sound_volume}", True, (255, 255, 255))
        sali = font.render("guardar cambios", True, (255, 255, 255))

        kolor = (255, 0, 0)
        if options_selection == 0:
            music_volume_text = font.render(f"musica: {music_volume}", True, kolor)
        elif options_selection == 1:
            sound_volume_text = font.render(f"sonido: {sound_volume}", True, kolor)
        elif options_selection == 2:
            sali = font.render("guardar cambios", True, kolor)

        screen.blit(music_volume_text, (screen_width // 3.8, screen_height // 2 - 200))
        screen.blit(sound_volume_text, (screen_width // 3.8, screen_height // 2 ))
        screen.blit(sali, (screen_width // 6.5, screen_height // 2 + 200))

        keys = pygame.key.get_pressed()
        if options_selection == 0:
            keys_a = keys[pygame.K_a]
            keys_d = keys[pygame.K_d]
            if keys_a or keys_d:
                change = 10 if keys_d else -10
                music_volume = max(0, min(100, music_volume + change))
        elif options_selection == 1:
            keys_a = keys[pygame.K_a]
            keys_d = keys[pygame.K_d]
            if keys_a or keys_d:
                change = 10 if keys_d else -10
                sound_volume = max(0, min(100, sound_volume + change))

        if keys[pygame.K_RETURN]:
            sonido_seleccion.play()
            if options_selection == 2:
                options_menu_active = not options_menu_active
                paused = not paused

        if keys[pygame.K_w]:
            sonido_moverse.play()
            options_selection = (options_selection - 1) % 3
        elif keys[pygame.K_s]:
            sonido_moverse.play()
            options_selection = (options_selection + 1) % 3
    cambios = {
        'music_volume': music_volume,
        'sound_volume': sound_volume
    }
    configuracion.update(cambios)
    with open('niveles_desbloqueados.json', 'w') as json_file:
        json.dump(configuracion, json_file)

    return options_selection, paused, options_menu_active, music_volume, sound_volume

def draw_mainn_menu(screen, screen_width, screen_height, status, menu_selection):
    fondo_pausa = pygame.image.load(r"graphics\seleccion_nivel\main_menu.jpg")
    screen.blit(fondo_pausa, (0,0))
    font = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 10)
    resume_text = font.render("Jugar", True, (255, 255, 255))
    options_text = font.render("ranking", True, (255, 255, 255))
    quit_text = font.render("salir", True, (255, 255, 255))
    selected_color = (255, 0, 0)
    if menu_selection == 0:
        resume_text = font.render("Jugar", True, selected_color)
    elif menu_selection == 1:
        options_text = font.render("ranking", True, selected_color)
    elif menu_selection == 2:
        quit_text = font.render("salir", True, selected_color)

    screen.blit(resume_text, (screen_width // 2.8, screen_height // 2 - 150))
    screen.blit(options_text, (screen_width // 3.05, screen_height // 2 + 50))
    screen.blit(quit_text, (screen_width // 2.55, screen_height // 2 + 250))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        sonido_seleccion.play()
        if menu_selection == 0:
            pygame.time.wait(500)
            status = "seleccion_mapa"
        elif menu_selection == 1:
            status = "ranking"
        elif menu_selection == 2:
            pygame.quit()
    

    if keys[pygame.K_w]:
        sonido_moverse.play()
        menu_selection = (menu_selection - 1) % 3

    elif keys[pygame.K_s]:
        sonido_moverse.play()
        menu_selection = (menu_selection + 1) % 3



    return status, menu_selection 

def draw_nombre(screen, screen_width, screen_height, status, nombre):
    fondo_pausa = pygame.image.load(r"graphics\seleccion_nivel\main_menu.jpg")
    screen.blit(fondo_pausa, (0, 0))

    font = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 15)
    font2 = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 30)
    input_font = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 15)

    resume_text = font.render("Ingrese su nombre:", True, "black")
    user_input = input_font.render(nombre, True, "white")
    error_message = font.render("", True, "white")

    screen.blit(resume_text, (screen_width // 4, screen_height // 2 - 150))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        if validar_nombre(nombre):
            print(f"Bienvenido, {nombre}")
            sonido_seleccion.play()
            pygame.time.wait(500)
            status = "menu"
        else:
            error_message = font2.render("Nombre no válido. Solo letras y números.", True, (255, 0, 0))


    user_input = input_font.render(nombre, True, "white")
    screen.blit(user_input, (screen_width // 2.75, screen_height // 2 + 50))
    screen.blit(error_message, (screen_width // 4.3, screen_height // 2 + 250))
    return status, nombre

def validar_nombre(name):
    return re.match("^[a-zA-Z0-9]+$", name) is not None

def mostrar_pantalla_ranking(screen, screen_width, status, ranking):
    fondo_pausa = pygame.image.load(r"graphics\seleccion_nivel\main_menu.jpg")
    screen.blit(fondo_pausa, (0, 0))
    font = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 15)
    font2 = pygame.font.Font(r"graphics\Greek-Freak.ttf", screen_width // 20)



    header_text = font.render("Ranking - Top 3", True, "#910101")
    screen.blit(header_text, (screen_width // 3.3, screen.get_height() // 3.2))
    keys = pygame.key.get_pressed()

    y = 500
    for i, jugador in enumerate(ranking, 1):
        nombre, puntaje, id = jugador
        jugador_text = font2.render(f"{i}. {nombre}#{id}: {puntaje}", True, "white")
        screen.blit(jugador_text, (screen_width // 3, y))
        y += 120
    if keys[pygame.K_ESCAPE]:
        sonido_seleccion.play()

        status = "menu"
    
    pygame.display.flip()  
    return status