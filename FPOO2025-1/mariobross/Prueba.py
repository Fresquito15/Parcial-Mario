import os
import pygame
import random

# Inicialización
pygame.init()
pygame.font.init()

# Constantes
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
LIMITE_INFERIOR = 500  # Ajustado para que los personajes estén en el suelo
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

    def dibujar(self, pantalla, img):
        if self.activo:
            pantalla.blit(img, (self.x - 15, self.y - 15))


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
        self.goombas_creados_total = 0
        self.max_goombas_total = 10
        self.max_goombas_simultaneos = 2
        self.tiempo_desde_ultimo_goomba = 0
        self.tiempo_minimo_entre_goombas = 2
        self.juego_terminado = False

    def generar_monedas(self):
        self.monedas = []
        while len(self.monedas) < 10:
            self.monedas.append(Moneda())

    def generar_goomba(self):
        if len(self.goombas) < self.max_goombas_simultaneos and self.goombas_creados_total < self.max_goombas_total:
            self.goombas.append(Goomba())
            self.goombas_creados_total += 1

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
                return False
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
        self.hongo_crecimiento.dibujar(self.pantalla, self.imgs["hongo_crecimiento"], self.imgs["hongo_vida"])
        self.hongo_vida.dibujar(self.pantalla, self.imgs["hongo_crecimiento"], self.imgs["hongo_vida"])
        self.estrella.dibujar(self.pantalla, self.imgs["estrella"])

        for g in self.goombas:
            g.dibujar(self.pantalla, self.imgs["goomba_cafe"], self.imgs["goomba_negro"])

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
