import os
import pygame
import random

# Inicialización
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constantes
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
LIMITE_INFERIOR = 500
FPS = 60
COLOR_FONDO = (135, 206, 250)
COLOR_TEXTO = (255, 255, 255)
FUENTE = pygame.font.SysFont('Arial', 24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")

# Clases
class Jugador:
    def __init__(self):
        self.ancho = 40
        self.alto = 50
        self.x = 100
        self.y = LIMITE_INFERIOR - self.alto
        self.velocidad = 5
        self.salto = False
        self.velocidad_salto = 15
        self.contador_salto = self.velocidad_salto

        self.estado = 'pequeño'
        self.vidas = 3
        self.inmunidad = False
        self.tiempo_inmunidad = 0
        self.recogidas_monedas = 0

    def mover(self, direccion):
        if direccion == "izquierda":
            self.x = max(self.x - self.velocidad, 0)
        elif direccion == "derecha":
            self.x = min(self.x + self.velocidad, ANCHO_VENTANA - self.ancho)

    def actualizar_salto(self):
        if self.salto:
            if self.contador_salto >= -self.velocidad_salto:
                if self.contador_salto > 0:
                    self.y -= self.contador_salto * 0.7
                else:
                    self.y += abs(self.contador_salto * 0.6)
                self.contador_salto -= 1
            else:
                self.salto = False
                self.contador_salto = self.velocidad_salto
                self.y = LIMITE_INFERIOR - self.alto

    def actualizar_estado(self):
        if self.inmunidad:
            self.tiempo_inmunidad -= 1 / FPS
            if self.tiempo_inmunidad <= 0:
                self.inmunidad = False

    def dibujar(self, pantalla, img_pequeno, img_grande):
        if self.estado == 'pequeño':
            pantalla.blit(img_pequeno, (self.x, self.y))
        else:
            pantalla.blit(img_grande, (self.x, self.y))

    def colisionar_con_enemigo(self):
        if self.inmunidad:
            return
        if self.estado == 'grande':
            self.estado = 'pequeño'
            self.alto = 50
            self.y = LIMITE_INFERIOR - self.alto
        else:
            self.vidas = max(0, self.vidas - 1)

    def crecer(self):
        self.estado = 'grande'
        self.alto = 80
        self.y = LIMITE_INFERIOR - self.alto

    def vida_extra(self):
        self.vidas += 1

    def activar_inmunidad(self):
        self.inmunidad = True
        self.tiempo_inmunidad = 8

    def esta_saltando_sobre(self, enemigo):
        """Verifica si el jugador está saltando sobre un enemigo"""
        return (self.salto and 
                self.y + self.alto <= enemigo.y + 10 and
                self.x < enemigo.x + enemigo.ancho and
                self.x + self.ancho > enemigo.x)


class Goomba:
    def __init__(self):
        self.tipo = random.choice(['café', 'negro'])
        self.ancho = 40
        self.alto = 40
        self.x = ANCHO_VENTANA
        self.y = LIMITE_INFERIOR - self.alto
        self.velocidad = 3
        self.activo = True

    def mover(self):
        self.x -= self.velocidad
        if self.x + self.ancho < 0:
            self.activo = False

    def dibujar(self, pantalla, img_cafe, img_negro):
        img = img_cafe if self.tipo == 'café' else img_negro
        pantalla.blit(img, (self.x, self.y))

    def colisiona_con(self, jugador):
        rect1 = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        rect2 = pygame.Rect(jugador.x, jugador.y, jugador.ancho, jugador.alto)
        return rect1.colliderect(rect2)


class Tortuga:
    def __init__(self):
        self.ancho = 40
        self.alto = 40
        self.x = ANCHO_VENTANA
        self.y = LIMITE_INFERIOR - self.alto
        self.velocidad = 2
        self.activo = True
        self.estado = 'normal'  # 'normal', 'caparazon' o 'disparada'
        self.velocidad_caparazon = 8  # ✅ Velocidad más rápida para caparazón disparado
        self.direccion = -1

    def mover(self):
        if self.estado == 'normal':
            self.x -= self.velocidad
        elif self.estado == 'disparada':  # ✅ NUEVO ESTADO
            # Se mueve muy rápido y desaparece al salir de pantalla
            self.x += self.velocidad_caparazon * self.direccion
        
        # ✅ Desactivar si sale de la pantalla en cualquier dirección
        if (self.x + self.ancho < 0) or (self.x > ANCHO_VENTANA):
            self.activo = False

    def ser_pisada(self, jugador):
        """✅ MODIFICADO: La tortuga es pisada y se convierte en caparazón disparado"""
        if self.estado == 'normal':
            self.estado = 'disparada'  # ✅ Cambio: directamente a 'disparada'
            self.alto = 30
            self.y = LIMITE_INFERIOR - self.alto
            
            # Determinar dirección basada en la posición del jugador
            if jugador.x < self.x:
                self.direccion = 1  # Jugador a la izquierda, caparazón va a la derecha
            else:
                self.direccion = -1  # Jugador a la derecha, caparazón va a la izquierda
            
            print(f"🐢 ¡Tortuga pisada! Caparazón disparado hacia {'derecha' if self.direccion == 1 else 'izquierda'}")
            return True
        
        return False

    def dibujar(self, pantalla, img_normal, img_caparazon):
        if self.estado == 'normal':
            pantalla.blit(img_normal, (self.x, self.y))
        else:  # ✅ Tanto 'caparazon' como 'disparada' usan la misma imagen
            pantalla.blit(img_caparazon, (self.x, self.y))

    def colisiona_con(self, jugador):
        rect1 = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        rect2 = pygame.Rect(jugador.x, jugador.y, jugador.ancho, jugador.alto)
        return rect1.colliderect(rect2)


class ObjetoBeneficioso:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.activo = True

    def colisiona_con(self, jugador):
        if not self.activo:
            return False
        rect1 = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        rect2 = pygame.Rect(jugador.x, jugador.y, jugador.ancho, jugador.alto)
        return rect1.colliderect(rect2)


class Moneda(ObjetoBeneficioso):
    def __init__(self, x=None, y=None):
        x = x or random.randint(20, ANCHO_VENTANA - 20)
        min_altura = LIMITE_INFERIOR - 60
        max_altura = LIMITE_INFERIOR - 20
        y = y or random.randint(min_altura, max_altura)
        super().__init__(x, y)
        self.ya_recogida = False

    def dibujar(self, pantalla, img):
        if self.activo and not self.ya_recogida:
            pantalla.blit(img, (self.x - 15, self.y - 15))

    def colisiona_con(self, jugador):
        if not self.activo or self.ya_recogida:
            return False
        rect1 = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        rect2 = pygame.Rect(jugador.x, jugador.y, jugador.ancho, jugador.alto)
        return rect1.colliderect(rect2)


class Hongo(ObjetoBeneficioso):
    def __init__(self, tipo, posicion):
        super().__init__(*posicion)
        self.tipo = tipo
        self.radio = 15
        self.activo = False
        self.tiempo_visible = 0

    def dibujar(self, pantalla, img_crecimiento, img_vida):
        if self.activo:
            img = img_crecimiento if self.tipo == 'crecimiento' else img_vida
            pantalla.blit(img, (self.x - self.radio, self.y - self.radio))

    def activar(self, duracion):
        self.activo = True
        self.tiempo_visible = duracion

    def actualizar(self):
        if self.activo:
            self.tiempo_visible -= 1 / FPS
            if self.tiempo_visible <= 0:
                self.activo = False


class Estrella(ObjetoBeneficioso):
    def __init__(self, posicion):
        super().__init__(*posicion)
        self.radio = 15

    def dibujar(self, pantalla, img):
        if self.activo:
            pantalla.blit(img, (self.x - self.radio, self.y - self.radio))


class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        
        self.cargar_audio()
        
        pygame.display.set_caption("Mario Mosquera Game")
        self.clock = pygame.time.Clock()
        self.jugador = Jugador()
        
        def load_img(name, size):
            return pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, name)), size)

        self.imgs = {
            "fondo": load_img("fondo.png", (ANCHO_VENTANA, ALTO_VENTANA)),
            "jugador_pequeno": load_img("1.png", (40, 50)),
            "jugador_grande": load_img("1.png", (40, 80)),
            "goomba_cafe": load_img("goomba.png", (40, 40)),
            "goomba_negro": load_img("goomba_muerte.png", (40, 30)),
            "tortuga_normal": load_img("normal.png", (40, 40)),
            "tortuga_caparazon": load_img("aplasta.png", (40, 30)),
            "moneda": load_img("moneda.png", (30, 30)),
            "hongo_crecimiento": load_img("hongoRojo.png", (40, 40)),
            "hongo_vida": load_img("hongoVerde.png", (40, 40)),
            "estrella": load_img("estrella.png", (30, 30))
        }

        self.monedas = []
        self.generar_monedas()
        self.hongo_crecimiento = Hongo("crecimiento", (600, LIMITE_INFERIOR - 60))
        self.hongo_vida = Hongo("vida", (700, LIMITE_INFERIOR - 60))
        self.estrella = Estrella((650, LIMITE_INFERIOR - 60))

        self.goombas = []
        self.tortugas = []
        self.enemigos_creados_total = 0
        self.max_enemigos_total = 15
        self.max_enemigos_simultaneos = 3
        self.tiempo_desde_ultimo_enemigo = 0
        self.tiempo_minimo_entre_enemigos = 2
        self.juego_terminado = False

        self.musica_pausada = False
        
        # ✅ CONTROL DE SONIDO MEJORADO
        self.puede_reproducir_sonido_moneda = True
        self.tiempo_ultimo_sonido_moneda = 0
        self.cooldown_sonido_moneda = 0.3  # 300ms entre sonidos
        
        self.iniciar_musica_fondo()

    def cargar_audio(self):
        """✅ FUNCIÓN MEJORADA: Mejor control de volúmenes"""
        try:
            SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
            
            # ✅ Cargar sonido de moneda con volumen reducido
            sound_path = os.path.join(SOUNDS_DIR, "Moneda.wav")
            if os.path.exists(sound_path):
                self.sonido_moneda = pygame.mixer.Sound(sound_path)
                self.sonido_moneda.set_volume(0.15)  # ✅ Volumen muy bajo (15%)
                print("✅ Sonido de moneda cargado con volumen reducido")
            else:
                print(f"⚠️ Archivo de sonido no encontrado: {sound_path}")
                self.sonido_moneda = None
            
            # ✅ Cargar música de fondo
            self.musica_fondo = None
            formatos_musica = ["Tono.wav", "fondo.mp3", "fondo.wav", "fondo.ogg", "background.mp3", "background.wav", "music.mp3"]
            
            for nombre_archivo in formatos_musica:
                music_path = os.path.join(SOUNDS_DIR, nombre_archivo)
                if os.path.exists(music_path):
                    self.musica_fondo = music_path
                    print(f"🎵 Música de fondo encontrada: {nombre_archivo}")
                    break
            
            if not self.musica_fondo:
                print("⚠️ No se encontró música de fondo")
                    
        except Exception as e:
            print(f"⚠️ Error al cargar audio: {e}")
            self.sonido_moneda = None
            self.musica_fondo = None

    def iniciar_musica_fondo(self):
        """✅ FUNCIÓN MEJORADA: Volumen balanceado"""
        if self.musica_fondo:
            try:
                pygame.mixer.music.load(self.musica_fondo)
                pygame.mixer.music.set_volume(0.3)  # ✅ Volumen reducido (30%)
                pygame.mixer.music.play(-1)
                print("🎵 Música de fondo iniciada con volumen balanceado")
            except Exception as e:
                print(f"⚠️ Error al reproducir música de fondo: {e}")

    def reproducir_sonido_moneda(self):
        """✅ NUEVA FUNCIÓN: Control inteligente del sonido de moneda"""
        tiempo_actual = pygame.time.get_ticks() / 1000.0  # Convertir a segundos
        
        if (self.sonido_moneda and 
            tiempo_actual - self.tiempo_ultimo_sonido_moneda > self.cooldown_sonido_moneda):
            
            try:
                # ✅ Detener cualquier sonido de moneda anterior
                self.sonido_moneda.stop()
                # ✅ Reproducir nuevo sonido
                self.sonido_moneda.play()
                self.tiempo_ultimo_sonido_moneda = tiempo_actual
                print("🪙 Sonido de moneda reproducido")
                return True
            except Exception as e:
                print(f"⚠️ Error al reproducir sonido: {e}")
                return False
        else:
            print("⏳ Sonido de moneda en cooldown")
            return False

    def alternar_musica(self):
        try:
            if self.musica_pausada:
                pygame.mixer.music.unpause()
                self.musica_pausada = False
                print("▶️ Música reanudada")
            else:
                pygame.mixer.music.pause()
                self.musica_pausada = True
                print("⏸️ Música pausada")
        except Exception as e:
            print(f"⚠️ Error al alternar música: {e}")

    def detener_musica(self):
        try:
            pygame.mixer.music.stop()
            print("⏹️ Música detenida")
        except:
            pass

    def generar_monedas(self):
        self.monedas = []
        jugador_rect = pygame.Rect(self.jugador.x, self.jugador.y, self.jugador.ancho, self.jugador.alto)
        
        for _ in range(10):
            intentos = 0
            while intentos < 100:
                x = random.randint(200, ANCHO_VENTANA - 20)
                min_altura = LIMITE_INFERIOR - 60
                max_altura = LIMITE_INFERIOR - 20
                y = random.randint(min_altura, max_altura)
                
                moneda_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                if not moneda_rect.colliderect(jugador_rect):
                    self.monedas.append(Moneda(x, y))
                    break
                intentos += 1
            
            if intentos >= 100:
                x = 300 + len(self.monedas) * 50
                y = LIMITE_INFERIOR - 40
                self.monedas.append(Moneda(x, y))
        
        print(f"Generadas {len(self.monedas)} monedas nuevas")

    def generar_enemigo(self):
        total_enemigos = len(self.goombas) + len(self.tortugas)
        
        if total_enemigos < self.max_enemigos_simultaneos and self.enemigos_creados_total < self.max_enemigos_total:
            if random.random() < 0.7:
                self.goombas.append(Goomba())
                print("🟫 Goomba generado")
            else:
                self.tortugas.append(Tortuga())
                print("🐢 Tortuga generada")
            
            self.enemigos_creados_total += 1

    def manejar_eventos(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.jugador.mover("izquierda")
        if keys[pygame.K_RIGHT]:
            self.jugador.mover("derecha")
        if keys[pygame.K_SPACE]:
            if not self.jugador.salto:
                self.jugador.salto = True
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.detener_musica()
                return False
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    self.alternar_musica()
        
        return True

    def actualizar(self):
        if self.juego_terminado:
            return

        self.tiempo_desde_ultimo_enemigo += 1 / FPS
        if self.tiempo_desde_ultimo_enemigo >= self.tiempo_minimo_entre_enemigos:
            self.generar_enemigo()
            self.tiempo_desde_ultimo_enemigo = 0

        # Actualizar goombas
        for g in self.goombas:
            g.mover()
        self.goombas = [g for g in self.goombas if g.activo]

        # Actualizar tortugas
        for t in self.tortugas:
            t.mover()
        self.tortugas = [t for t in self.tortugas if t.activo]

        # Colisiones con goombas
        for g in self.goombas[:]:
            if g.colisiona_con(self.jugador):
                self.jugador.colisionar_con_enemigo()
                g.activo = False
                if self.jugador.vidas <= 0:
                    self.juego_terminado = True
                    self.detener_musica()

        # ✅ COLISIONES CON TORTUGAS MEJORADAS
        for t in self.tortugas[:]:
            if t.colisiona_con(self.jugador):
                if self.jugador.esta_saltando_sobre(t):
                    if t.ser_pisada(self.jugador):
                        # ✅ Dar rebote al jugador
                        self.jugador.contador_salto = self.jugador.velocidad_salto // 2
                else:
                    # ✅ Solo recibir daño si la tortuga está en estado normal
                    if t.estado == 'normal' and not self.jugador.inmunidad:
                        self.jugador.colisionar_con_enemigo()
                        if self.jugador.vidas <= 0:
                            self.juego_terminado = True
                            self.detener_musica()

        # ✅ COLISIONES ENTRE CAPARAZONES DISPARADOS Y GOOMBAS
        for t in self.tortugas:
            if t.estado == 'disparada':
                for g in self.goombas[:]:
                    if g.colisiona_con(t):
                        g.activo = False
                        print("💥 ¡Caparazón disparado destruyó un Goomba!")

        # ✅ SISTEMA DE MONEDAS MEJORADO
        for moneda in self.monedas[:]:  
            if not moneda.ya_recogida and moneda.colisiona_con(self.jugador):
                # ✅ Marcar inmediatamente como recogida
                moneda.ya_recogida = True
                moneda.activo = False
                
                # ✅ Incrementar contador
                self.jugador.recogidas_monedas += 1
                
                # ✅ Reproducir sonido con control mejorado
                self.reproducir_sonido_moneda()
                
                print(f"🪙 Moneda recogida! Total: {self.jugador.recogidas_monedas}")
                
                # ✅ Verificar vida extra
                if self.jugador.recogidas_monedas >= 10:
                    self.jugador.vida_extra()
                    self.jugador.recogidas_monedas = 0
                    print("¡Vida extra obtenida!")
                    self.generar_monedas()
                    break
        
        # ✅ Limpiar monedas recogidas
        self.monedas = [m for m in self.monedas if not m.ya_recogida]

        # Lógica para hongos
        for h in [self.hongo_crecimiento, self.hongo_vida]:
            if h.colisiona_con(self.jugador) and h.activo:
                if h.tipo == 'crecimiento':
                    self.jugador.crecer()
                else:
                    self.jugador.vida_extra()
                h.activo = False
            h.actualizar()

        if not self.hongo_crecimiento.activo and random.random() < 1 / (FPS * 20):
            self.hongo_crecimiento.activar(10)
        if not self.hongo_vida.activo and random.random() < 1 / (FPS * 20):
            self.hongo_vida.activar(10)

        if self.estrella.colisiona_con(self.jugador) and self.estrella.activo:
            self.jugador.activar_inmunidad()
            self.estrella.activo = False

        self.jugador.actualizar_salto()
        self.jugador.actualizar_estado()

    def dibujar(self):
        self.pantalla.blit(self.imgs["fondo"], (0, 0))
        
        # Dibujar monedas
        for m in self.monedas:
            m.dibujar(self.pantalla, self.imgs["moneda"])
        
        self.hongo_crecimiento.dibujar(self.pantalla, self.imgs["hongo_crecimiento"], self.imgs["hongo_vida"])
        self.hongo_vida.dibujar(self.pantalla, self.imgs["hongo_crecimiento"], self.imgs["hongo_vida"])
        self.estrella.dibujar(self.pantalla, self.imgs["estrella"])

        # Dibujar goombas
        for g in self.goombas:
            g.dibujar(self.pantalla, self.imgs["goomba_cafe"], self.imgs["goomba_negro"])

        # Dibujar tortugas
        for t in self.tortugas:
            t.dibujar(self.pantalla, self.imgs["tortuga_normal"], self.imgs["tortuga_caparazon"])

        self.jugador.dibujar(self.pantalla, self.imgs["jugador_pequeno"], self.imgs["jugador_grande"])

        texto_vidas = FUENTE.render(f"Vidas: {self.jugador.vidas}", True, COLOR_TEXTO)
        texto_monedas = FUENTE.render(f"Monedas: {self.jugador.recogidas_monedas}", True, COLOR_TEXTO)
        
        self.pantalla.blit(texto_vidas, (10, 10))
        self.pantalla.blit(texto_monedas, (10, 40))

        if self.juego_terminado:
            texto_fin = FUENTE.render("Game over", True, (255, 0, 0))
            self.pantalla.blit(texto_fin, (ANCHO_VENTANA // 2 - texto_fin.get_width() // 2, ALTO_VENTANA // 2))

        pygame.display.flip()

    def ejecutar(self):
        corriendo = True
        while corriendo:
            self.clock.tick(FPS)
            corriendo = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
        
        pygame.quit()


if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
