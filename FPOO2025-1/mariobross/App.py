import pygame
import random
import os

# Inicialización
pygame.init()
pygame.font.init()

# Constantes
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
LIMITE_INFERIOR = 450
FPS = 60

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")

# Colores y fuente
COLOR_FONDO = (135, 206, 250)
COLOR_TEXTO = (255, 255, 255)
FUENTE = pygame.font.SysFont('Arial', 24)

# -------- CLASES --------

class Jugador:
    def __init__(self):
        self.x = 100
        self.ancho = 40
        self.alto = 50
        self.y = LIMITE_INFERIOR - self.alto
        self.vidas = 3
        self.estado = 'pequeño'
        self.inmunidad = False
        self.tiempo_inmunidad = 0
        self.velocidad = 5
        self.salto = False
        self.velocidad_salto = 12  # salto más natural
        self.gravedad = 0.8
        self.velocidad_y = 0
        self.recogidas_monedas = 0

    def mover(self, direccion):
        if direccion == "izquierda":
            self.x = max(self.x - self.velocidad, 0)
        elif direccion == "derecha":
            self.x = min(self.x + self.velocidad, ANCHO_VENTANA - self.ancho)

    def actualizar_salto(self):
        if self.salto:
            self.velocidad_y += self.gravedad
            self.y += self.velocidad_y
            if self.y >= LIMITE_INFERIOR - self.alto:
                self.y = LIMITE_INFERIOR - self.alto
                self.salto = False
                self.velocidad_y = 0

    def iniciar_salto(self):
        if not self.salto:
            self.salto = True
            self.velocidad_y = -self.velocidad_salto

    def dibujar(self, pantalla, imagen_pequeno, imagen_grande):
        imagen = imagen_pequeno if self.estado == 'pequeño' else imagen_grande
        pantalla.blit(imagen, (self.x, self.y))

    def actualizar_estado(self):
        if self.inmunidad:
            self.tiempo_inmunidad -= 1 / FPS
            if self.tiempo_inmunidad <= 0:
                self.inmunidad = False

    def colisionar_con_goomba(self):
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


class Goomba:
    def __init__(self):
        self.tipo = random.choice(['café', 'negro'])
        self.ancho = 40
        self.alto = 50
        self.x = ANCHO_VENTANA
        self.y = LIMITE_INFERIOR - self.alto
        self.velocidad = 3
        self.activo = True

    def mover(self):
        self.x -= self.velocidad
        if self.x + self.ancho < 0:
            self.activo = False

    def dibujar(self, pantalla, imagen_cafe, imagen_negro):
        imagen = imagen_cafe if self.tipo == 'café' else imagen_negro
        pantalla.blit(imagen, (self.x, self.y))

    def colisiona_con(self, jugador):
        rect_goomba = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        rect_jugador = pygame.Rect(jugador.x, jugador.y, jugador.ancho, jugador.alto)
        return rect_goomba.colliderect(rect_jugador)


class ObjetoBeneficioso:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.activo = True

    def colisiona_con(self, jugador):
        if not self.activo:
            return False
        distancia = ((self.x - (jugador.x + jugador.ancho // 2)) ** 2 + (self.y - (jugador.y + jugador.alto // 2)) ** 2) ** 0.5
        return distancia < self.radio + max(jugador.ancho, jugador.alto) / 4


class Moneda(ObjetoBeneficioso):
    def __init__(self):
        x = random.randint(50, ANCHO_VENTANA - 50)
        y = LIMITE_INFERIOR - 20  # en el suelo
        super().__init__(x, y)
        self.radio = 10

    def dibujar(self, pantalla, imagen):
        if self.activo:
            pantalla.blit(imagen, (self.x - self.radio, self.y - self.radio))


class Hongo(ObjetoBeneficioso):
    def __init__(self, tipo, posicion_fija):
        x, _ = posicion_fija
        y = LIMITE_INFERIOR - 30  # en el suelo
        super().__init__(x, y)
        self.tipo = tipo
        self.radio = 15
        self.activo = False
        self.tiempo_visible = 0

    def dibujar(self, pantalla, img_crecimiento, img_vida):
        if self.activo:
            imagen = img_crecimiento if self.tipo == 'crecimiento' else img_vida
            pantalla.blit(imagen, (self.x - self.radio, self.y - self.radio))

            pantalla.blit(imagen, (self.x - self.radio, self.y - self.radio))

    def activar(self, tiempo):
        self.activo = True
        self.tiempo_visible = tiempo

    def actualizar(self):
        if self.activo:
            self.tiempo_visible -= 1 / FPS
            if self.tiempo_visible <= 0:
                self.activo = False


class Estrella(ObjetoBeneficioso):
    def __init__(self, posicion_fija):
        super().__init__(*posicion_fija)
        self.radio = 15

    def dibujar(self, pantalla, imagen):
        if self.activo:
            pantalla.blit(imagen, (self.x - self.radio, self.y - self.radio))


class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Mario Mosquera Game")
        self.clock = pygame.time.Clock()
        self.jugador = Jugador()
        self.imgs = {}

        def load_img(name, size):
            path = os.path.join(ASSETS_DIR, name)
            return pygame.transform.scale(pygame.image.load(path), size)

        fondo_original = pygame.image.load(os.path.join(ASSETS_DIR, "fondo.png"))
        self.imgs["fondo"] = pygame.transform.scale(fondo_original, (ANCHO_VENTANA, ALTO_VENTANA))
        self.imgs["inicial"] = load_img("1.png", (40, 50))
        self.imgs["inicialGrande"] = load_img("1.png", (40, 80))
        self.imgs["goomba"] = load_img("goomba.png", (40, 50))
        self.imgs["goombaNegro"] = load_img("goomba_muerte.png", (40, 50))
        self.imgs["moneda"] = load_img("moneda.png", (30, 30))
        self.imgs["hongoRojo"] = load_img("hongoRojo.png", (40, 40))
        self.imgs["hongoVerde"] = load_img("hongoVerde.png", (40, 40))
        self.imgs["estrella"] = load_img("estrella.png", (40, 40))

        self.monedas = []
        self.generar_monedas()

        self.hongo_crecimiento = Hongo('crecimiento', (600, LIMITE_INFERIOR - 30))
        self.hongo_vida = Hongo('vida', (70, LIMITE_INFERIOR - 20))
        self.estrella = Estrella((550, LIMITE_INFERIOR - 20))

        self.goombas = []
        self.goombas_creados_total = 0
        self.max_goombas_simultaneos = 2
        self.max_goombas_total = 10
        self.tiempo_desde_ultimo_goomba = 0
        self.tiempo_minimo_entre_goombas = 2

        self.juego_terminado = False

    def generar_monedas(self):
        self.monedas = [Moneda() for _ in range(10)]

    def generar_goomba(self):
        if len(self.goombas) < self.max_goombas_simultaneos and self.goombas_creados_total < self.max_goombas_total:
            self.goombas.append(Goomba())
            self.goombas_creados_total += 1

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not self.jugador.salto:
                    self.jugador.salto = True

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.jugador.mover("izquierda")
        if teclas[pygame.K_RIGHT]:
            self.jugador.mover("derecha")

        return True

    def actualizar(self):
        if self.juego_terminado:
            return

        self.tiempo_desde_ultimo_goomba += 1 / FPS
        if self.tiempo_desde_ultimo_goomba >= self.tiempo_minimo_entre_goombas:
            self.generar_goomba()
            self.tiempo_desde_ultimo_goomba = 0

        for g in self.goombas:
            g.mover()
        self.goombas = [g for g in self.goombas if g.activo]

        for g in self.goombas:
            if g.colisiona_con(self.jugador):
                self.jugador.colisionar_con_goomba()
                g.activo = False
                if self.jugador.vidas <= 0:
                    self.juego_terminado = True

        for m in self.monedas:
            if m.colisiona_con(self.jugador):
                m.activo = False
                self.jugador.recogidas_monedas += 1
                if self.jugador.recogidas_monedas == 10:
                    self.jugador.vida_extra()
                    self.jugador.recogidas_monedas = 0
                    self.generar_monedas()

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
        for m in self.monedas:
            m.dibujar(self.pantalla, self.imgs["moneda"])
        self.hongo_crecimiento.dibujar(self.pantalla, self.imgs["hongoRojo"], self.imgs["hongoVerde"])
        self.hongo_vida.dibujar(self.pantalla, self.imgs["hongoRojo"], self.imgs["hongoVerde"])
        self.estrella.dibujar(self.pantalla, self.imgs["estrella"])

        for g in self.goombas:
            g.dibujar(self.pantalla, self.imgs["goomba"], self.imgs["goombaNegro"])

        self.jugador.dibujar(self.pantalla, self.imgs["inicial"], self.imgs["inicialGrande"])

        texto_vidas = FUENTE.render(f"Vidas: {self.jugador.vidas}", True, COLOR_TEXTO)
        texto_monedas = FUENTE.render(f"Monedas: {self.jugador.recogidas_monedas}", True, COLOR_TEXTO)
        self.pantalla.blit(texto_vidas, (10, 10))
        self.pantalla.blit(texto_monedas, (10, 70))

        if self.juego_terminado:
            texto_fin = FUENTE.render("\u2022 Game over!", True, (255, 0, 0))
            self.pantalla.blit(texto_fin, (ANCHO_VENTANA // 2 - texto_fin.get_width() // 2, ALTO_VENTANA // 2))

        pygame.display.flip()

    def correr(self):
        ejecutando = True
        while ejecutando:
            self.clock.tick(FPS)
            ejecutando = self.manejar_eventos()
            if not self.juego_terminado:
                self.actualizar()
            self.dibujar()


if __name__ == "__main__":
    juego = Juego()
    juego.correr()
    pygame.quit()
