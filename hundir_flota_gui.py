"""
Hundir la flota - Interfaz visual con pygame-ce (2 jugadores en el mismo equipo).

Requisitos:  pip install pygame-ce numpy
Uso:         colocar este archivo junto a utils.py y ejecutar:  python hundir_flota_gui.py

Controles:
  - Clic en el tablero derecho ("Tus disparos") para disparar.
  - Clic / ESPACIO / ENTER para avanzar entre pantallas.
  - R para reiniciar al terminar la partida. ESC para salir.

Animaciones: mar ondulante, barco navegando, mira que apunta, salpicadura (agua),
explosiones con humo (tocado / hundido), temblor de pantalla, destello del barco
hundido, fundidos entre pantallas y confeti en la victoria.

Diseño de la pantalla (cada zona tiene su propio hueco, así los textos no se pisan):
  y   0-  90  cabecera (jugador + info)
  y  90- 145  banner de mensajes (Agua / Tocado / Hundido / avisos)
  y 160- 195  títulos de los tableros
  y 225- 625  tableros
  y 655- 690  pie con las instrucciones
"""
import math
import random
import sys
import pygame
from utils import Tablero

# ---------------------------------------------------------------- Constantes
TAM = 10
CELDA = 40
ANCHO, ALTO = 1020, 720
FPS = 60

X_IZQ, X_DER = 60, 560
Y_TABLERO = 225
Y_TITULO_TABLERO = 168
Y_BANNER = 118
Y_PIE = 672

T_APUNTAR = 0.5  # segundos que tarda la mira en fijar el objetivo

COLOR_FONDO = (15, 23, 42)
COLOR_AGUA = (37, 99, 235)
COLOR_AGUA_HOVER = (96, 165, 250)
COLOR_BARCO = (148, 163, 184)
COLOR_TOCADO = (220, 38, 38)
COLOR_HUNDIDO = (127, 29, 29)
COLOR_LINEA = (15, 23, 42)
COLOR_TEXTO = (241, 245, 249)
COLOR_TEXTO_SUAVE = (148, 163, 184)
COLOR_ACENTO = (250, 204, 21)

FUEGO = [(255, 240, 150), (255, 200, 60), (255, 140, 30), (240, 80, 20)]
COLORES_CONFETI = [(250, 204, 21), (220, 38, 38), (96, 165, 250), (52, 211, 153), (244, 114, 182)]

LETRAS = "ABCDEFGHIJ"


def mezclar(c1, c2, k):
    """Mezcla dos colores RGB (k=0 -> c1, k=1 -> c2)."""
    k = max(0.0, min(1.0, k))
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


# ------------------------------------------------------------------- Lógica
class Partida:
    """Envuelve dos Tablero (de utils.py) y gestiona disparos y victoria."""

    def __init__(self):
        self.tableros = [Tablero(), Tablero()]
        for t in self.tableros:
            t.colocar_barco(0)
        self.barcos = [self._extraer_barcos(t) for t in self.tableros]
        # disparos[i] = {(fila, col): "X" tocado | "A" agua} realizados por el jugador i
        self.disparos = [{}, {}]
        self.turno = 0
        self.ganador = None
        self.mensaje = ""
        self.oculta = None            # casilla recién disparada cuya animación aún no ha terminado
        self.ultimo_hundido = set()   # casillas del último barco hundido

    @staticmethod
    def _extraer_barcos(tablero):
        """Devuelve una lista de conjuntos de casillas, una por barco.

        Se calculan a partir de la longitud y el punto de inicio, sin fiarse
        del extremo final guardado en posiciones_barcos (en sentido 'derecha'
        ese extremo está desplazado una casilla en utils.py).
        """
        barcos = []
        for filas, cols, longitud, sentido in tablero.posiciones_barcos:
            if sentido < 2:  # horizontal
                fila, col0 = filas[0], min(cols)
                celdas = {(fila, col0 + k) for k in range(longitud)}
            else:  # vertical
                col, fila0 = cols[0], min(filas)
                celdas = {(fila0 + k, col) for k in range(longitud)}
            barcos.append(celdas)
        return barcos

    def disparos_visibles(self, jugador):
        """Disparos de `jugador`, sin contar el que aún se está animando."""
        d = self.disparos[jugador]
        if self.oculta is not None and jugador == self.turno:
            d = {k: v for k, v in d.items() if k != self.oculta}
        return d

    def barcos_hundidos_por(self, jugador):
        """Casillas de los barcos enemigos ya hundidos por `jugador`."""
        rival = 1 - jugador
        vis = self.disparos_visibles(jugador)
        hundidas = set()
        for celdas in self.barcos[rival]:
            if all(vis.get(c) == "X" for c in celdas):
                hundidas |= celdas
        return hundidas

    def barcos_restantes(self, jugador):
        """Barcos de `jugador` que aún no han sido hundidos por el rival."""
        rival = 1 - jugador
        vis = self.disparos_visibles(rival)
        return sum(
            1 for celdas in self.barcos[jugador]
            if not all(vis.get(c) == "X" for c in celdas)
        )

    def disparar(self, celda):
        """Devuelve el mensaje del disparo, o None si la casilla ya se había disparado."""
        jugador, rival = self.turno, 1 - self.turno
        if celda in self.disparos[jugador]:
            return None

        fila, col = celda
        self.ultimo_hundido = set()
        for celdas in self.barcos[rival]:
            if celda in celdas:
                self.disparos[jugador][celda] = "X"
                self.tableros[jugador].matriz_juego[fila, col] = "X"
                hundido = all(self.disparos[jugador].get(c) == "X" for c in celdas)
                if hundido:
                    self.ultimo_hundido = set(celdas)
                if all(
                    all(self.disparos[jugador].get(c) == "X" for c in b)
                    for b in self.barcos[rival]
                ):
                    self.ganador = jugador
                return "¡Hundido!" if hundido else "¡Tocado!"

        self.disparos[jugador][celda] = "A"
        self.tableros[jugador].matriz_juego[fila, col] = "A"
        return "¡Agua!"

    def siguiente_turno(self):
        self.turno = 1 - self.turno


# ----------------------------------------------------------------- Efectos
class Particula:
    def __init__(self, x, y, vx, vy, vida, color, radio, gravedad=0.0, arrastre=1.0):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.vida, self.color, self.radio = vida, color, radio
        self.gravedad, self.arrastre = gravedad, arrastre
        self.edad = 0.0

    @property
    def viva(self):
        return self.edad < self.vida

    def actualizar(self, dt):
        self.edad += dt
        self.vy += self.gravedad * dt
        k = self.arrastre ** (dt * 60)
        self.vx *= k
        self.vy *= k
        self.x += self.vx * dt
        self.y += self.vy * dt

    def dibujar(self, capa):
        f = max(0.0, 1 - self.edad / self.vida)
        r = max(1, int(self.radio * (0.4 + 0.6 * f)))
        pygame.draw.circle(capa, (*self.color, int(255 * f)), (int(self.x), int(self.y)), r)


class Onda:
    """Círculo que se expande y se desvanece (ondas de agua, destellos, anillos)."""

    def __init__(self, x, y, radio_max, vida, color, retraso=0.0, relleno=False, grosor=3):
        self.x, self.y = x, y
        self.radio_max, self.vida, self.color = radio_max, vida, color
        self.edad = -retraso
        self.relleno, self.grosor = relleno, grosor

    @property
    def viva(self):
        return self.edad < self.vida

    def actualizar(self, dt):
        self.edad += dt

    def dibujar(self, capa):
        if self.edad < 0:
            return
        f = min(1.0, self.edad / self.vida)
        r = max(2, int(self.radio_max * (1 - (1 - f) ** 2)))
        a = int(255 * (1 - f) * (0.7 if self.relleno else 1.0))
        ancho = 0 if self.relleno else min(self.grosor, r)
        pygame.draw.circle(capa, (*self.color, a), (int(self.x), int(self.y)), r, ancho)


class Confeti:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vy = random.uniform(80, 220)
        self.deriva = random.uniform(-30, 30)
        self.fase = random.uniform(0, math.tau)
        self.w = random.randint(6, 11)
        self.h = random.randint(4, 8)
        self.color = random.choice(COLORES_CONFETI)

    def actualizar(self, dt, t):
        self.y += self.vy * dt
        self.x += (self.deriva + 40 * math.sin(t * 3 + self.fase)) * dt

    def dibujar(self, surf, t):
        ancho = max(2, int(self.w * abs(math.cos(t * 4 + self.fase))))
        pygame.draw.rect(surf, self.color, pygame.Rect(int(self.x), int(self.y), ancho, self.h))


# ------------------------------------------------------------------- Interfaz
class Interfaz:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hundir la flota")
        self.ventana = pygame.display.set_mode((ANCHO, ALTO))
        self.pantalla = pygame.Surface((ANCHO, ALTO))  # lienzo (permite el temblor)

        # los efectos y la mira sólo se dibujan dentro del tablero de ataque,
        # así nunca invaden los textos
        self.zona_ataque = pygame.Rect(X_DER, Y_TABLERO, TAM * CELDA, TAM * CELDA)
        self.capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.capa.set_clip(self.zona_ataque)
        self.velo = pygame.Surface((ANCHO, ALTO))
        self.velo.fill((0, 0, 0))
        self.velo_blanco = pygame.Surface((ANCHO, ALTO))
        self.velo_blanco.fill((255, 255, 255))

        self.f_titulo = pygame.font.SysFont("arial", 56, bold=True)
        self.f_banner = pygame.font.SysFont("arial", 44, bold=True)
        self.f_grande = pygame.font.SysFont("arial", 32, bold=True)
        self.f_normal = pygame.font.SysFont("arial", 22)
        self.f_pequena = pygame.font.SysFont("arial", 18)

        self.reloj = pygame.time.Clock()
        self.ahora = 0.0
        self.t_fade = 0.0
        self.estado = "titulo"  # titulo | pase | juego | animando | resultado | fin
        self.partida = Partida()
        self.reiniciar_animaciones()

    def reiniciar_animaciones(self):
        self.particulas = []
        self.ondas = []
        self.programados = []   # explosiones retardadas (barco hundido)
        self.confeti = []
        self.disparo_celda = None
        self.resultado_pend = ""
        self.t_disparo = 0.0
        self.t_impacto = -10.0
        self.t_mensaje = -10.0
        self.t_flash_blanco = -10.0
        self.shake_amp = 0.0
        self.shake_dur = 1.0
        self.shake_fin = 0.0
        self.bloqueo_hasta = 0.0
        self.invalida = None    # (casilla, instante) para parpadear si ya estaba disparada

    def cambiar_estado(self, nuevo, fundido=True):
        self.estado = nuevo
        if fundido:
            self.t_fade = self.ahora

    # ---- utilidades
    def pulso(self, minimo, maximo, vel=3.0):
        return int(minimo + (maximo - minimo) * (0.5 + 0.5 * math.sin(self.ahora * vel)))

    def texto(self, txt, fuente, color, centro=None, izq=None, alpha=255, ancho_max=None):
        img = fuente.render(txt, True, color)
        if ancho_max and img.get_width() > ancho_max:  # nunca se sale de su hueco
            k = ancho_max / img.get_width()
            img = pygame.transform.smoothscale(
                img, (int(img.get_width() * k), int(img.get_height() * k)))
        if alpha < 255:
            img.set_alpha(alpha)
        rect = img.get_rect()
        if centro:
            rect.center = centro
        elif izq:
            rect.topleft = izq
        self.pantalla.blit(img, rect)

    def rect_celda(self, x0, fila, col):
        return pygame.Rect(x0 + col * CELDA, Y_TABLERO + fila * CELDA, CELDA, CELDA)

    def centro_celda(self, x0, fila, col):
        return self.rect_celda(x0, fila, col).center

    def celda_bajo_raton(self, x0):
        mx, my = pygame.mouse.get_pos()
        col, fila = (mx - x0) // CELDA, (my - Y_TABLERO) // CELDA
        if 0 <= fila < TAM and 0 <= col < TAM:
            return (fila, col)
        return None

    def color_agua(self, f, c):
        d = int(14 * math.sin(self.ahora * 2 + f * 0.7 + c * 0.7))
        return (37 + d // 2, 99 + d, min(255, 235 + d))

    def escala_marca(self, celda):
        """Las marcas 'aparecen' creciendo justo después del impacto."""
        if celda == self.disparo_celda:
            s = min(1.0, (self.ahora - self.t_impacto) / 0.3)
            return s * s * (3 - 2 * s)
        return 1.0

    # ---- marcas
    def dibujar_marca_tocado(self, rect, color=COLOR_TEXTO, escala=1.0):
        h = int(10 * escala)
        if h < 1:
            return
        cx, cy = rect.center
        pygame.draw.line(self.pantalla, color, (cx - h, cy - h), (cx + h, cy + h), 4)
        pygame.draw.line(self.pantalla, color, (cx + h, cy - h), (cx - h, cy + h), 4)

    def dibujar_marca_agua(self, rect, escala=1.0):
        r = int(6 * escala)
        if r > 0:
            pygame.draw.circle(self.pantalla, COLOR_TEXTO, rect.center, r)

    # ---- tableros
    def dibujar_etiquetas(self, x0):
        for i in range(TAM):
            self.texto(str(i), self.f_pequena, COLOR_TEXTO_SUAVE,
                       centro=(x0 + i * CELDA + CELDA // 2, Y_TABLERO - 16))
            self.texto(LETRAS[i], self.f_pequena, COLOR_TEXTO_SUAVE,
                       centro=(x0 - 16, Y_TABLERO + i * CELDA + CELDA // 2))

    def dibujar_tablero_propio(self, x0, jugador, titulo):
        """Tablero con los barcos de `jugador` y los disparos recibidos."""
        p = self.partida
        self.texto(titulo, self.f_normal, COLOR_TEXTO, izq=(x0, Y_TITULO_TABLERO))
        self.dibujar_etiquetas(x0)
        recibidos = p.disparos[1 - jugador]
        hundidos = p.barcos_hundidos_por(1 - jugador)
        ocupadas = set().union(*p.barcos[jugador])

        for f in range(TAM):
            for c in range(TAM):
                r = self.rect_celda(x0, f, c)
                if (f, c) in hundidos:
                    color = COLOR_HUNDIDO
                elif (f, c) in ocupadas:
                    color = COLOR_BARCO
                else:
                    color = self.color_agua(f, c)
                pygame.draw.rect(self.pantalla, color, r)
                pygame.draw.rect(self.pantalla, COLOR_LINEA, r, 1)
                marca = recibidos.get((f, c))
                if marca == "X":
                    self.dibujar_marca_tocado(r, COLOR_TEXTO if (f, c) in hundidos else COLOR_TOCADO)
                elif marca == "A":
                    self.dibujar_marca_agua(r)

    def dibujar_tablero_ataque(self, x0, jugador, titulo, interactivo):
        """Tablero enemigo oculto: sólo se ven los disparos de `jugador`."""
        p = self.partida
        self.texto(titulo, self.f_normal, COLOR_TEXTO, izq=(x0, Y_TITULO_TABLERO))
        self.dibujar_etiquetas(x0)
        vis = p.disparos_visibles(jugador)
        hundidos = p.barcos_hundidos_por(jugador)
        hover = self.celda_bajo_raton(x0) if interactivo else None

        t_flash = self.ahora - self.t_impacto
        flash = self.estado == "resultado" and t_flash < 1.2 and bool(p.ultimo_hundido)

        for f in range(TAM):
            for c in range(TAM):
                r = self.rect_celda(x0, f, c)
                marca = vis.get((f, c))
                if (f, c) in hundidos:
                    color = COLOR_HUNDIDO
                elif marca == "X":
                    color = COLOR_TOCADO
                elif (f, c) == hover and marca is None:
                    color = COLOR_AGUA_HOVER
                else:
                    color = self.color_agua(f, c)
                if flash and (f, c) in p.ultimo_hundido:  # destello del barco hundido
                    k = abs(math.sin(t_flash * 10)) * (1 - t_flash / 1.2)
                    color = mezclar(color, (255, 255, 255), 0.7 * k)
                pygame.draw.rect(self.pantalla, color, r)
                pygame.draw.rect(self.pantalla, COLOR_LINEA, r, 1)

                escala = self.escala_marca((f, c))
                if marca == "X":
                    self.dibujar_marca_tocado(r, COLOR_TEXTO, escala)
                elif marca == "A":
                    self.dibujar_marca_agua(r, escala)

        if hover is not None and vis.get(hover) is None:  # retícula pulsante
            cx, cy = self.centro_celda(x0, *hover)
            pygame.draw.circle(self.pantalla, COLOR_ACENTO, (cx, cy),
                               9 + int(2 * math.sin(self.ahora * 8)), 2)

        if self.invalida and self.ahora - self.invalida[1] < 0.5:  # parpadeo de aviso
            if int((self.ahora - self.invalida[1]) * 12) % 2 == 0:
                pygame.draw.rect(self.pantalla, COLOR_TOCADO,
                                 self.rect_celda(x0, *self.invalida[0]), 3)

        if interactivo:
            marco = pygame.Rect(x0, Y_TABLERO, TAM * CELDA, TAM * CELDA)
            color = mezclar(COLOR_ACENTO, (255, 255, 255), 0.5 + 0.5 * math.sin(self.ahora * 4))
            pygame.draw.rect(self.pantalla, color, marco, 3)

    # ---- mar animado
    def y_ola(self, x, base, amp, frec, vel):
        return base + amp * math.sin(x * frec + self.ahora * vel)

    def poligono_ola(self, base, amp, frec, vel, color):
        pts = [(x, self.y_ola(x, base, amp, frec, vel)) for x in range(0, ANCHO + 11, 10)]
        pts += [(ANCHO, ALTO), (0, ALTO)]
        pygame.draw.polygon(self.pantalla, color, pts)

    def dibujar_mar(self):
        ola_fondo = (560, 8, 0.018, 1.6)
        self.poligono_ola(*ola_fondo, (30, 64, 140))

        # barco navegando
        x = (self.ahora * 55) % (ANCHO + 240) - 120
        y = self.y_ola(x, *ola_fondo)
        pygame.draw.polygon(self.pantalla, (71, 85, 105),
                            [(x - 50, y - 14), (x + 50, y - 14), (x + 36, y + 6), (x - 38, y + 6)])
        pygame.draw.rect(self.pantalla, COLOR_BARCO, (x - 18, y - 34, 36, 20))
        pygame.draw.rect(self.pantalla, COLOR_TOCADO, (x - 6, y - 48, 12, 14))
        for i in range(3):
            pygame.draw.circle(self.pantalla, (100, 116, 139),
                               (int(x - 20 - i * 14), int(y - 50 - i * 8 - 3 * math.sin(self.ahora * 3 + i))),
                               5 + i * 2, 2)

        self.poligono_ola(590, 10, 0.014, 2.2, COLOR_AGUA)
        self.poligono_ola(625, 9, 0.02, 2.8, (29, 78, 190))

    def dibujar_mira(self):
        fila, col = self.disparo_celda
        cx, cy = self.centro_celda(X_DER, fila, col)
        p = min(1.0, (self.ahora - self.t_disparo) / T_APUNTAR)
        e = 1 - (1 - p) ** 3
        r = int(80 - (80 - 16) * e)
        color = COLOR_TOCADO if p > 0.8 else COLOR_ACENTO
        self.pantalla.set_clip(self.zona_ataque)
        pygame.draw.circle(self.pantalla, color, (cx, cy), r, 2)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            pygame.draw.line(self.pantalla, color,
                             (cx + dx * (r - 10), cy + dy * (r - 10)),
                             (cx + dx * (r + 14), cy + dy * (r + 14)), 2)
        pygame.draw.circle(self.pantalla, color, (cx, cy), 3)
        self.pantalla.set_clip(None)

    def dibujar_efectos(self):
        if not (self.particulas or self.ondas):
            return
        self.capa.fill((0, 0, 0, 0))
        for o in self.ondas:
            o.dibujar(self.capa)
        for pa in self.particulas:
            pa.dibujar(self.capa)
        self.pantalla.blit(self.capa, self.zona_ataque.topleft, self.zona_ataque)

    # ---- pantallas
    def pantalla_titulo(self):
        bob = int(6 * math.sin(self.ahora * 2))
        self.texto("HUNDIR LA FLOTA", self.f_titulo, COLOR_TEXTO, centro=(ANCHO // 2, 200 + bob))
        self.texto("Edición para dos jugadores", self.f_grande, COLOR_ACENTO, centro=(ANCHO // 2, 280))
        self.texto("Haz clic o pulsa ESPACIO para empezar", self.f_normal, COLOR_TEXTO_SUAVE,
                   centro=(ANCHO // 2, 400), alpha=self.pulso(110, 255))
        self.dibujar_mar()

    def pantalla_pase(self):
        j = self.partida.turno + 1
        self.texto(f"Turno del Jugador {j}", self.f_titulo, COLOR_TEXTO, centro=(ANCHO // 2, 210),
                   ancho_max=ANCHO - 80)
        self.texto("Pasa el control y asegúrate de que el rival no mira la pantalla",
                   self.f_normal, COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, 300), ancho_max=ANCHO - 80)
        self.texto("Haz clic o pulsa ESPACIO para continuar", self.f_normal, COLOR_ACENTO,
                   centro=(ANCHO // 2, 400), alpha=self.pulso(110, 255))
        self.dibujar_mar()

    def pantalla_juego(self):
        p = self.partida
        j = p.turno
        self.texto(f"Jugador {j + 1}", self.f_grande, COLOR_ACENTO, izq=(X_IZQ, 20))
        info = (f"Tus barcos en pie: {p.barcos_restantes(j)}   |   "
                f"Barcos enemigos en pie: {p.barcos_restantes(1 - j)}")
        self.texto(info, self.f_pequena, COLOR_TEXTO_SUAVE, izq=(X_IZQ, 62), ancho_max=ANCHO - 2 * X_IZQ)

        self.dibujar_tablero_propio(X_IZQ, j, "Tus barcos")
        self.dibujar_tablero_ataque(X_DER, j, "Tus disparos", self.estado == "juego")

        # banner: un único hueco para todos los mensajes
        k = min(1.0, (self.ahora - self.t_mensaje) / 0.25)
        pos = (ANCHO // 2, Y_BANNER + int(12 * (1 - k)))
        if self.estado == "animando":
            self.texto("Apuntando...", self.f_grande, COLOR_TEXTO_SUAVE,
                       centro=(ANCHO // 2, Y_BANNER), alpha=self.pulso(100, 255, 10))
        elif self.estado == "resultado":
            color = COLOR_AGUA_HOVER if p.mensaje == "¡Agua!" else COLOR_TOCADO
            self.texto(p.mensaje, self.f_banner, color, centro=pos, alpha=int(255 * k), ancho_max=800)
        elif p.mensaje:
            self.texto(p.mensaje, self.f_grande, COLOR_ACENTO, centro=pos, alpha=int(255 * k), ancho_max=800)

        # pie
        if self.estado == "juego":
            self.texto("Elige una casilla del tablero derecho para disparar",
                       self.f_normal, COLOR_TEXTO, centro=(ANCHO // 2, Y_PIE))
        elif self.estado == "resultado" and self.ahora >= self.bloqueo_hasta:
            self.texto("Haz clic o pulsa ESPACIO para continuar", self.f_normal,
                       COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, Y_PIE), alpha=self.pulso(110, 255))

    def pantalla_fin(self):
        p = self.partida
        color = mezclar(COLOR_ACENTO, (255, 255, 255), 0.5 + 0.5 * math.sin(self.ahora * 4))
        self.texto(f"¡Gana el Jugador {p.ganador + 1}!", self.f_titulo, color, centro=(ANCHO // 2, 50))
        self.texto("Pulsa R para jugar de nuevo o ESC para salir", self.f_normal,
                   COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, 108))
        self.dibujar_tablero_propio(X_IZQ, 0, "Tablero del Jugador 1")
        self.dibujar_tablero_propio(X_DER, 1, "Tablero del Jugador 2")

    # ---- efectos: creación
    def temblor(self, amp, dur):
        self.shake_amp, self.shake_dur, self.shake_fin = amp, dur, self.ahora + dur

    def desplazamiento_temblor(self):
        if self.ahora >= self.shake_fin:
            return 0, 0
        a = int(self.shake_amp * (self.shake_fin - self.ahora) / self.shake_dur)
        return random.randint(-a, a), random.randint(-a, a)

    def efecto_agua(self, cx, cy):
        for i in range(3):
            self.ondas.append(Onda(cx, cy, 58, 0.9, (220, 235, 255), retraso=i * 0.15))
        for _ in range(16):
            ang = random.uniform(math.pi * 1.15, math.pi * 1.85)  # hacia arriba
            v = random.uniform(80, 220)
            self.particulas.append(Particula(
                cx, cy, math.cos(ang) * v, math.sin(ang) * v, random.uniform(0.5, 0.9),
                (190, 220, 255), random.randint(2, 4), gravedad=500))

    def explosion(self, cx, cy, n_fuego, n_humo, radio, vel_max):
        self.ondas.append(Onda(cx, cy, radio, 0.35, (255, 220, 120), relleno=True))
        self.ondas.append(Onda(cx, cy, radio * 1.6, 0.6, (255, 160, 60), grosor=4))
        for _ in range(n_fuego):
            ang, v = random.uniform(0, math.tau), random.uniform(40, vel_max)
            self.particulas.append(Particula(
                cx, cy, math.cos(ang) * v, math.sin(ang) * v, random.uniform(0.4, 0.9),
                random.choice(FUEGO), random.randint(3, 7), gravedad=150, arrastre=0.96))
        for _ in range(n_humo):
            ang, v = random.uniform(0, math.tau), random.uniform(10, 70)
            self.particulas.append(Particula(
                cx, cy, math.cos(ang) * v, math.sin(ang) * v - 30, random.uniform(1.0, 1.6),
                (90, 90, 100), random.randint(6, 11), gravedad=-40, arrastre=0.97))

    def efecto_tocado(self, cx, cy):
        self.explosion(cx, cy, 26, 10, 34, 240)
        self.temblor(4, 0.3)

    def efecto_hundido(self, cx, cy):
        self.explosion(cx, cy, 70, 26, 60, 380)
        self.temblor(11, 0.7)
        self.t_flash_blanco = self.ahora
        for k, (f, c) in enumerate(sorted(self.partida.ultimo_hundido)):
            x, y = self.centro_celda(X_DER, f, c)
            self.programados.append((self.ahora + 0.08 * (k + 1), x, y))

    def iniciar_confeti(self):
        self.confeti = [Confeti(random.uniform(0, ANCHO), random.uniform(-ALTO, 0)) for _ in range(90)]

    # ---- lógica de la interfaz
    def impacto(self):
        p = self.partida
        p.oculta = None
        p.mensaje = self.resultado_pend
        self.t_mensaje = self.t_impacto = self.ahora
        self.bloqueo_hasta = self.ahora + 0.8
        cx, cy = self.centro_celda(X_DER, *self.disparo_celda)
        if p.mensaje == "¡Agua!":
            self.efecto_agua(cx, cy)
        elif p.mensaje == "¡Tocado!":
            self.efecto_tocado(cx, cy)
        else:
            self.efecto_hundido(cx, cy)
        self.cambiar_estado("resultado", fundido=False)

    def actualizar(self, dt):
        if self.estado == "animando" and self.ahora - self.t_disparo >= T_APUNTAR:
            self.impacto()

        pendientes = []
        for t, x, y in self.programados:
            if self.ahora >= t:
                self.explosion(x, y, 14, 4, 20, 170)
            else:
                pendientes.append((t, x, y))
        self.programados = pendientes

        for o in self.ondas:
            o.actualizar(dt)
        for pa in self.particulas:
            pa.actualizar(dt)
        self.ondas = [o for o in self.ondas if o.viva]
        self.particulas = [pa for pa in self.particulas if pa.viva]

        if self.estado == "fin":
            for _ in range(2):
                self.confeti.append(Confeti(random.uniform(0, ANCHO), -10))
            for c in self.confeti:
                c.actualizar(dt, self.ahora)
            self.confeti = [c for c in self.confeti if c.y < ALTO + 20]

    def avanzar(self):
        """Clic / espacio / enter en las pantallas de transición."""
        p = self.partida
        if self.estado == "titulo":
            self.cambiar_estado("pase")
        elif self.estado == "pase":
            p.mensaje = ""
            self.cambiar_estado("juego")
        elif self.estado == "resultado":
            if self.ahora < self.bloqueo_hasta:  # deja ver la explosión
                return
            self.reiniciar_animaciones()
            if p.ganador is not None:
                self.iniciar_confeti()
                self.cambiar_estado("fin")
            else:
                p.siguiente_turno()
                p.mensaje = ""
                self.cambiar_estado("pase")

    def clic_juego(self):
        p = self.partida
        celda = self.celda_bajo_raton(X_DER)
        if celda is None:
            return
        resultado = p.disparar(celda)
        if resultado is None:
            p.mensaje = "Disparo anteriormente realizado"
            self.t_mensaje = self.ahora
            self.invalida = (celda, self.ahora)
            return
        p.oculta = celda            # el resultado se revela al terminar la mira
        p.mensaje = ""
        self.disparo_celda = celda
        self.resultado_pend = resultado
        self.t_disparo = self.ahora
        self.cambiar_estado("animando", fundido=False)

    def procesar_eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return False
                if e.key == pygame.K_r and self.estado == "fin":
                    self.partida = Partida()
                    self.reiniciar_animaciones()
                    self.cambiar_estado("pase")
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN) and self.estado in ("titulo", "pase", "resultado"):
                    self.avanzar()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.estado == "juego":
                    self.clic_juego()
                elif self.estado in ("titulo", "pase", "resultado"):
                    self.avanzar()
        return True

    # ---- dibujo general
    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        if self.estado == "fin":  # el confeti va detrás de todo, nunca tapa textos
            for c in self.confeti:
                c.dibujar(self.pantalla, self.ahora)

        if self.estado == "titulo":
            self.pantalla_titulo()
        elif self.estado == "pase":
            self.pantalla_pase()
        elif self.estado in ("juego", "animando", "resultado"):
            self.pantalla_juego()
        elif self.estado == "fin":
            self.pantalla_fin()

        if self.estado == "animando":
            self.dibujar_mira()
        self.dibujar_efectos()

        k = 1 - (self.ahora - self.t_flash_blanco) / 0.3
        if k > 0:
            self.velo_blanco.set_alpha(int(150 * k))
            self.pantalla.blit(self.velo_blanco, (0, 0))

        a = int(255 * (1 - (self.ahora - self.t_fade) / 0.35))
        if a > 0:
            self.velo.set_alpha(a)
            self.pantalla.blit(self.velo, (0, 0))

        ox, oy = self.desplazamiento_temblor()
        self.ventana.fill(COLOR_FONDO)
        self.ventana.blit(self.pantalla, (ox, oy))

    def ejecutar(self):
        corriendo = True
        while corriendo:
            dt = min(self.reloj.tick(FPS) / 1000.0, 0.05)
            self.ahora += dt
            corriendo = self.procesar_eventos()
            self.actualizar(dt)
            self.dibujar()
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Interfaz().ejecutar()
