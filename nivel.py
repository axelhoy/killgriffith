import pygame, sqlite3
from csv import reader
from configuracion import *
from tiles import *
from enemy import *
from estrellas import Estrella
from player import Player
from data import levels
from modo import *
from enemy_death import MuerteEnemiga

asset_general = pygame.image.load(r"graphics\terrain\Assets\Tiles.png")

def importar_csv(path):
    '''
    Importa datos de un archivo CSV y retorna una lista.
    '''
    mapa_entero = []
    try:
        with open(path, "r") as map:
            level = reader(map, delimiter=",")
            for row in level:
                mapa_entero.append(list(row))
    except Exception as e:
        print(f"Error al importar el archivo CSV: {e}")
    return mapa_entero

def cortar_tiled():
    '''
    Divide la imagen de las texturas usadas en pequeñas imagenes del tamaño de tiled_tamaño (90). 
    Luego se almacenan en una lista llamada tile_cortado. 
    Se calcula tanto en el eje x como en el eje y, itera sobre estas coordenadas y crea superficies nuevas
    Retorna una lista de superficies que representan los bloques recortados.
    '''

    tile_num_x = asset_general.get_size()[0] // tiled_tamaño
    tile_num_y = asset_general.get_size()[1] // tiled_tamaño

    tile_cortado = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tiled_tamaño
            y = row * tiled_tamaño
            new_surf = pygame.Surface((tiled_tamaño, tiled_tamaño), pygame.SRCALPHA)
            new_surf.blit(asset_general, (0, 0), (x, y, tiled_tamaño, tiled_tamaño))
            tile_cortado.append(new_surf)

    return tile_cortado

class Nivel:
    def __init__(self, current_level, surface, crear_seleccion_nivel, cambiar_monedas, cambiar_vida, vida_actual, perder_vida, sound_volume, music_volume, cambiar_puntaje, puntaje, nombre, paused, cambiar_balas, balas, cambiar_vida_boss):
        self.display_surface = surface
        self.movimiento_camara = 0
        self.nombre = nombre
        self.paused = paused
        self.sound_volume = sound_volume
        self.music_volume = music_volume
        self.bandera_caida = 0

        self.balas = balas
        self.balas_actuales = self.balas()

        self.crear_seleccion_nivel = crear_seleccion_nivel
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data["desbloquea"]
        self.music_track = pygame.mixer.music.load(level_data["music_track"])
        pygame.mixer.music.set_volume(.3)

        self.vida_actual = vida_actual
        self.perder_vida = perder_vida
        self.cambiar_monedas = cambiar_monedas
        self.cambiar_vida = cambiar_vida
        self.cambiar_vida_boss = cambiar_vida_boss
        self.fuente = pygame.font.Font(r"graphics\Greek-Freak.ttf", 20)
        self.skull_knight_box = pygame.image.load(r"graphics\ui\skull_knight.png")

        self.casco_hitsound = pygame.mixer.Sound(r"graphics\sfx\jugador\salto_en_casco.ogg")
        self.coin_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\coin.ogg")
        self.heart_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\heart.wav")
        self.enemy_hitsound = pygame.mixer.Sound(r"graphics/enemy/hurt.ogg")
        self.skull_knight_sound = pygame.mixer.Sound(r"graphics\sfx\jugador\skull_knight.mp3")
        self.enemy_death = pygame.mixer.Sound(r"graphics/enemy/death.ogg")
        self.muerte_sprite =  pygame.sprite.Group()
        self.enemy_knight_hit = 0
        self.enemy_helmet_hit = 0

        self.puntaje = puntaje
        self.cambiar_puntaje = cambiar_puntaje
        self.enemigos_derrotados = 0
        self.niveles_completados = 0

        player_layout = importar_csv(level_data["player"])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, cambiar_vida, cambiar_balas)


        self.conn = sqlite3.connect('db1.db')
        terrain_layout = importar_csv(level_data["terrain"])
        sprite_types = ["terrain", "grass", "coins", "enemie_helmet", "limite", "enemie_knight", "health", "skull_knight", "guardar", "boss"]

        for sprite_type in sprite_types:
            layout = importar_csv(level_data[sprite_type])
            sprites_group = self.create_tile_group(layout, sprite_type)
            setattr(self, f"{sprite_type}_sprite", sprites_group)

        self.level_width = len(terrain_layout[0]) * tiled_tamaño
        self.top = pygame.image.load(r"graphics\estrellas\sky_top.png").convert()
        self.bottom = pygame.image.load(r"graphics\estrellas\sky_bottom.png").convert()
        self.top = pygame.transform.scale(self.top,(screen_width, tiled_tamaño))
        self.bottom = pygame.transform.scale(self.bottom,(screen_width, tiled_tamaño))
        self.estrellas = Estrella(screen_height//2, self.level_width, 25)

        self.en_rango = False
        self.choco_proyectil = False
        self.vida_maxima_boss = 20
        self.vida_boss = 20
        boss_layout = importar_csv(level_data["boss"])
        self.boss = pygame.sprite.GroupSingle()
        self.boss_setup(boss_layout)

        self.tiempo_limite = 50
        self.cronometro = pygame.image.load(r"graphics\ui\cronometer.png")
        self.start_time = pygame.time.get_ticks() 
        self.toco_knight = False



        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS "Jugadores" (
                "id"	INTEGER,
                "nombre"	TEXT,
                "puntaje"	INTEGER,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
        ''')
        self.conn.commit()

    def create_tile_group(self, layout, type):
        '''
        Función lambda toma tres argumentos (x, y, y/o surface) y devuelve un objeto Tile (StaticTile, Tile, Coin o Enemy) con esos argumentos.
        En Tiled, cuando un valor esta vacio (No se asigno ninguna imagen al cuadrado) este vale -1
        Si este es diferente a -1 (Existe una imagen en esa posicion), y el tipo existe en la lista, recorta la imagen en la columna dada por fila
        '''
        sprite_group = pygame.sprite.Group()

        create_sprite = {
            "terrain": lambda x, y, surface: StaticTile(tiled_tamaño, x, y, surface),
            "grass": lambda x, y, surface: StaticTile(tiled_tamaño, x, y, surface),
            "coins": lambda x, y, surface: Coin(tiled_tamaño, x, y, r"graphics\coins\coins"),
            "enemie_helmet": lambda x, y, surface: Enemy(tiled_tamaño, x, y),
            "limite": lambda x, y, surface: Tile(tiled_tamaño, x, y),
            "enemie_knight": lambda x, y, surface: Enemy_Knight(tiled_tamaño, x, y),
            "health": lambda x, y, surface: Coin(tiled_tamaño, x, y, r"graphics\health\healthanimated"),
            "skull_knight": lambda x, y, surface: Skull_Knight(tiled_tamaño*2.5, x, y),
            "guardar": lambda x, y, surface: Coin(tiled_tamaño, x, y, r"graphics\guardar\guardar"),
        }

        for indice_fila, fila in enumerate(layout):
            for indice_columna, columna in enumerate(fila):
                if columna != "-1":
                    x = indice_columna * tiled_tamaño
                    y = indice_fila * tiled_tamaño
                    if type in create_sprite:
                        sprite_surface = cortar_tiled()[int(columna)]
                        sprite = create_sprite[type](x, y, sprite_surface)
                        sprite_group.add(sprite)

        return sprite_group
    
    def check_en_rango(self):
        return self.en_rango
    
    def check_vida(self):
        return self.vida_boss

    def jugador_en_rango(self):
        top_boss = self.boss.sprite.rect.top
        left_boss = self.boss.sprite.rectangulo_colision.left
        right_boss = self.boss.sprite.rectangulo_colision.right
        bottom_jugador = self.player.sprite.colission_rect.bottom
        right_jugador = self.player.sprite.colission_rect.right
        left_jugador = self.player.sprite.colission_rect.left
        if top_boss <= bottom_jugador:
            if left_jugador > left_boss and left_jugador > right_boss and right_jugador > left_boss and right_jugador > right_boss:
                self.boss.sprite.facing_right = True
                self.en_rango = True
            elif left_jugador < left_boss and left_jugador < right_boss and right_jugador < left_boss and right_jugador < right_boss:
                self.boss.sprite.facing_right = False
                self.en_rango = True
        else:
            self.en_rango = False
    def balass(self, balas):
        self.balas = balas
    
    def player_setup(self, layout, cambiar_vida, cambiar_balas):
        for indice_fila, fila in enumerate(layout):
            for indice_columna, columna in enumerate(fila):
                x = indice_columna * tiled_tamaño
                y = indice_fila * tiled_tamaño
                if columna == "0":
                    sprite = Player((x,y),self.display_surface, cambiar_vida, cambiar_balas, self.balas)
                    self.player.add(sprite)
                    if sprite.facing_right:
                        self.facing_right = True
                if columna == "1":
                    final = pygame.image.load(r"graphics\character\puck.png").convert_alpha()
                    sprite = StaticTile(tiled_tamaño, x, y, final)
                    self.goal.add(sprite)

    def boss_setup(self,layout):
        for indice_fila, fila in enumerate(layout):
            for indice_columna, columna in enumerate(fila):
                x = indice_columna * tiled_tamaño
                y = indice_fila * tiled_tamaño
                if columna == "0":
                    sprite = Boss(x,y,self.display_surface,self.check_vida,self.check_en_rango)
                    self.boss.add(sprite)


    def voltear_enemigo(self):
        for enemy in self.enemie_helmet_sprite.sprites():
            if pygame.sprite.spritecollide(enemy, self.limite_sprite, False):
                enemy.reverse()
        for enemy in self.enemie_knight_sprite.sprites():
            if pygame.sprite.spritecollide(enemy, self.limite_sprite, False):
                enemy.reverse()
        for enemy in self.boss.sprites():
            if pygame.sprite.spritecollide(enemy, self.limite_sprite, False):
                enemy.reversa()
                enemy.cambiar_sentido()

                

    def drawcielo(self, surface):
        for columna in range(tiled_vertical):
            y = columna * tiled_tamaño
            if columna < 8:
                surface.blit(self.top,(0,y))
            else:
                surface.blit(self.bottom,(0,y))

    def colision_horizontal(self):
        player = self.player.sprite
        player.colission_rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprite.sprites():
            if sprite.rect.colliderect(player.colission_rect):
                if player.direction.x < 0:
                    player.colission_rect.left = sprite.rect.right
                    player.on_left = True
                elif player.direction.x > 0:
                    player.colission_rect.right = sprite.rect.left
                    player.on_right = True

    def colision_vertical(self):
        player = self.player.sprite
        player.gravedad()
        for sprite in self.terrain_sprite.sprites():
            if sprite.rect.colliderect(player.colission_rect):
                if player.direction.y > 0:
                    player.colission_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.colission_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def camara(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        
        if player_x < screen_width//7 and direction_x < 0:
            self.movimiento_camara = 8
            player.speed = 0
        elif player_x > screen_width// 1.3 and direction_x > 0:
            self.movimiento_camara = -8
            player.speed = 0
        else:
            self.movimiento_camara = 0
            player.speed = 8
            
    def dibujar_y_actualizar(self, nombre):
        nombre.update(self.movimiento_camara)
        nombre.draw(self.display_surface)

    def muerte(self):
        if self.player.sprite.rect.top > screen_height:
            self.bandera_caida += 1
            self.player.sprite.direction.y = -30
            if self.bandera_caida in {2, 4, 6}:
                self.perder_vida(-1)

    def siguiente_nivel(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal,False) or self.vida_boss <= 0 or self.vida_maxima_boss <= 0:
            self.cambiar_puntaje(500)
            self.tiempo_limite = 50
            self.crear_seleccion_nivel(self.current_level, self.new_max_level)
        
    def agarrar_monedas(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.coins_sprite, True):
            self.coin_sound.set_volume(self.sound_volume / 200.0)
            self.coin_sound.play()
            self.cambiar_monedas(1)
            self.cambiar_puntaje(20)

    def guardar_partida(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.guardar_sprite, True):
            player_name = self.nombre

            puntaje_int = self.puntaje()

            self.cursor.execute('''
                INSERT INTO Jugadores (nombre, puntaje)
                VALUES (?, ?)
            ''', (player_name, puntaje_int))
            self.conn.commit()

            print("Partida guardada en la base de datos.")

    def agarrar_vida(self, vida_actual):
        if pygame.sprite.spritecollide(self.player.sprite, self.health_sprite, True):
            self.heart_sound.set_volume(self.sound_volume / 200.0)
            self.heart_sound.play()
            if vida_actual < 100:
                self.cambiar_vida(20)
                if vida_actual > 100:
                    vida_actual = 100

    def colision_enemiga(self):
        player = self.player.sprite
        boss = self.boss.sprite
        
        ## Enemigo con casco
        for enemy in self.enemie_helmet_sprite.sprites():
            if enemy.rect.colliderect(player.rect) and self.player.sprite.attacking and player.attack_cooldown == 15:  
                self.enemy_hitsound.set_volume(self.sound_volume / 200)
                self.enemy_hitsound.play()
                self.enemy_helmet_hit += 1
                if self.enemy_helmet_hit == 1:
                    enemy.rect.x += 50 if self.player.sprite.facing_right else -50
                if self.enemy_helmet_hit == 2:
                    self.enemy_death.set_volume(self.sound_volume / 200)
                    self.enemy_death.play()
                    self.cambiar_puntaje(200)
                    muerte_sprite = MuerteEnemiga(enemy.rect.midtop, "muerte")
                    self.muerte_sprite.add(muerte_sprite)
                    enemy.kill()
                    self.enemy_helmet_hit = 0
            if enemy.rect.colliderect(player.colission_rect):
                enemy_top = enemy.rect.top
                player_bottom = player.colission_rect.bottom
                enemy_center = enemy.rect.centery
                if enemy_top < player_bottom < enemy_center and player.direction.y >= 0:
                    self.casco_hitsound.set_volume(self.sound_volume / 200)
                    self.casco_hitsound.play()
                    player.direction.y = -15
                else:
                    if not player.attacking:
                        player.recibe_daño()
                        enemy.reverse()

        ## Enemigo sin casco
        for enemy_knight in self.enemie_knight_sprite.sprites():
            if enemy_knight.rect.colliderect(player.colission_rect):
                enemy_knight_top = enemy_knight.rect.top
                player_bottom = player.colission_rect.bottom
                enemy_knight_center = enemy_knight.rect.centery
                if enemy_knight_top < player_bottom < enemy_knight_center and self.player.sprite.direction.y >= 0:
                    self.enemy_hitsound.set_volume(self.sound_volume / 200)
                    self.enemy_hitsound.play()
                    self.player.sprite.direction.y = -15
                    self.enemy_knight_hit += 1
                    if self.enemy_knight_hit == 2:
                        self.enemy_death.set_volume(self.sound_volume / 200)
                        self.enemy_death.play()
                        self.cambiar_puntaje(200)
                        muerte_sprite = MuerteEnemiga(enemy_knight.rect.midtop, "muerte")
                        self.muerte_sprite.add(muerte_sprite)
                        enemy_knight.kill()
                        self.enemy_knight_hit = 0
                else:
                    self.player.sprite.recibe_daño()
                    enemy_knight.reverse()

        ## Skull knight
        for enemy in self.skull_knight_sprite.sprites():
            if enemy.rect.colliderect(player.rect):
                if not self.toco_knight:
                    self.skull_knight_sound.set_volume(self.sound_volume / 200)
                    self.skull_knight_sound.play()
                    self.toco_knight = True
                texto_knight = self.fuente.render(f"Bien hecho {self.nombre}, su puntaje es de {self.puntaje()}", True, "white")
                texto_knight2 = self.fuente.render(f"Adelante, ve y guarda tu progreso!", True, "white")
                self.display_surface.blit(self.skull_knight_box, (550,150))
                self.display_surface.blit(texto_knight,(780,210))
                self.display_surface.blit(texto_knight2,(780,260))

        ## Boss
        if self.current_level == 2:
            if boss.rect.colliderect(player.rect) and self.player.sprite.attacking and player.attack_cooldown == 15:  
                self.enemy_death.set_volume(self.sound_volume / 200)
                self.enemy_death.play()
                self.vida_boss -=1
                self.cambiar_vida_boss(-1)

    def chequear_colision_disparo(self):
        i = 0 
        
        while i < len(self.player.sprite.lista_proyectiles):
            p = self.player.sprite.lista_proyectiles[i]
            self.display_surface.blit(p.image,p.rect)
            p.update()
            enemie_helmet = pygame.sprite.spritecollide(p,self.enemie_helmet_sprite,True)
            terreno_colisionado = pygame.sprite.spritecollide(p,self.terrain_sprite,False)
            enemie_knight = pygame.sprite.spritecollide(p,self.enemie_knight_sprite,False)

            boss = self.boss.sprite
            if p.rect.centerx < 0 or p.rect.centerx > screen_width:
                self.player.sprite.lista_proyectiles.pop(i)
                i -=1
            elif enemie_helmet:
                    for enemigo in enemie_helmet:
                        self.player.sprite.lista_proyectiles.pop(i)
                        i-=1
                        self.enemy_death.set_volume(self.sound_volume / 200)
                        self.enemy_death.play()
                        self.cambiar_puntaje(200)
                        muerte_sprite = MuerteEnemiga(enemigo.rect.midtop, "muerte")
                        self.muerte_sprite.add(muerte_sprite)
                        enemigo.kill()
            elif enemie_knight:
                for enemigo in enemie_knight:
                    self.casco_hitsound.set_volume(self.sound_volume / 200)
                    self.casco_hitsound.play()
                    self.player.sprite.lista_proyectiles.pop(i)
            elif terreno_colisionado:
                for terreno in terreno_colisionado:
                    self.player.sprite.lista_proyectiles.pop(i)
                    i-=1
            if self.current_level == 2:
                if p.rect.colliderect(boss.rect) and not boss.invencible:
                    self.vida_boss -=5
                    self.cambiar_vida_boss(-5)
                    self.player.sprite.lista_proyectiles.pop(i)
                    i-=1
                    self.enemy_death.set_volume(self.sound_volume / 200)
                    self.enemy_death.play()
            i +=1

    def chequear_colision_disparo_boss(self):
            i = 0 
            while i < len(self.boss.sprite.lista_proyectiles):
                p = self.boss.sprite.lista_proyectiles[i]
                self.display_surface.blit(p.image,p.rect)
                p.update()
                jugador = self.player.sprite
                boss = self.boss.sprite
                if p.rect.centerx < 0 or p.rect.centerx > screen_width:
                    self.boss.sprite.lista_proyectiles.pop(i)
                    i -=1
                    self.choco_proyectil = True
            
                if p.rect.colliderect(jugador.rect):
                    self.player.sprite.recibe_daño()
                    self.boss.sprite.lista_proyectiles.pop(i)
                    i-=1
                i +=1

    def update_sound_volume(self, sound_volume, music_volume):
        self.sound_volume = sound_volume
        self.music_volume = music_volume
        self.player.sprite.sound_volume = sound_volume
        self.player.sprite.music_volume = music_volume
        pygame.mixer.music.set_volume(music_volume / 200)

    def mostrar_cronometro(self, surface):
        tiempo_transcurrido = pygame.time.get_ticks() - self.start_time 
        fps = pygame.time.get_ticks() // 16
        if fps % 60 == 0: 
            self.cambiar_puntaje(-10)
        segundos_restantes = self.tiempo_limite - tiempo_transcurrido // 1000
        texto_cronometro = self.fuente.render(f"{segundos_restantes:02d}", True, "white")
        surface.blit(self.cronometro, (1500, 20))
        surface.blit(texto_cronometro, (1570, 70))
        if segundos_restantes <= 0:
            self.tiempo_limite = 50
            self.start_time = pygame.time.get_ticks()
            self.perder_vida(-1)


    def run(self):
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()

            if not self.paused:


                self.balas_actuales = self.balas()
                self.drawcielo(self.display_surface)
                self.chequear_colision_disparo()
                self.estrellas.dibujar(self.display_surface, self.movimiento_camara)

                self.skull_knight_sprite.update(self.movimiento_camara)
                self.enemie_helmet_sprite.update(self.movimiento_camara)
                self.enemie_knight_sprite.update(self.movimiento_camara)
                self.limite_sprite.update(self.movimiento_camara)
                self.voltear_enemigo()
                self.enemie_helmet_sprite.draw(self.display_surface)
                self.enemie_knight_sprite.draw(self.display_surface)
                self.skull_knight_sprite.draw(self.display_surface)
                self.dibujar_y_actualizar(self.muerte_sprite)


                self.player.update()
                self.player.draw(self.display_surface)
                self.boss.update(self.movimiento_camara)

                self.dibujar_y_actualizar(self.terrain_sprite)
                self.dibujar_y_actualizar(self.grass_sprite)
                self.boss.draw(self.display_surface)


                self.dibujar_y_actualizar(self.health_sprite)
                self.dibujar_y_actualizar(self.coins_sprite)
                self.dibujar_y_actualizar(self.guardar_sprite)
                self.colision_horizontal()
                self.colision_vertical()
                self.camara()

                self.dibujar_y_actualizar(self.goal)

                self.agarrar_monedas()
                self.guardar_partida()
                self.colision_enemiga()
                self.muerte()
                self.siguiente_nivel()
                if self.current_level == 2:
                    self.jugador_en_rango()
                    self.chequear_colision_disparo_boss()
                
                if obtener_modo():
                    pygame.draw.rect(self.display_surface, "blue", self.player.sprite.rect,3)
                    pygame.draw.rect(self.display_surface, "yellow", self.player.sprite.colission_rect,3)
                    for enemy in self.skull_knight_sprite.sprites():
                        pygame.draw.rect(self.display_surface, "red", enemy.rect, 3)
                    for sprite in self.terrain_sprite.sprites():
                        pygame.draw.rect(self.display_surface, "red", sprite.rect, 3)
                    for sprite in self.boss_sprite.sprites():
                        pygame.draw.rect(self.display_surface, "red", sprite.rect, 3)