"""
Hundir la flota - Interfaz visual con pygame-ce (2 jugadores en el mismo equipo).

Requisitos:  pip install pygame-ce numpy
Uso:         colocar este archivo junto a utils.py y ejecutar:  python hundir_flota_gui.py

Controles:
  - Clic en el tablero derecho ("Tus disparos") para disparar.
  - Clic / ESPACIO / ENTER para avanzar entre pantallas.
  - R para reiniciar al terminar la partida. ESC para salir.
"""
import sys
import pygame
from utils import Tablero

# ---------------------------------------------------------------- Constantes
TAM = 10
CELDA = 40
ANCHO, ALTO = 1020, 640
FPS = 60

X_IZQ, X_DER, Y_TABLERO = 60, 560, 160

COLOR_FONDO = (15, 23, 42)
COLOR_PANEL = (30, 41, 59)
COLOR_AGUA = (37, 99, 235)
COLOR_AGUA_HOVER = (96, 165, 250)
COLOR_BARCO = (148, 163, 184)
COLOR_TOCADO = (220, 38, 38)
COLOR_HUNDIDO = (127, 29, 29)
COLOR_LINEA = (15, 23, 42)
COLOR_TEXTO = (241, 245, 249)
COLOR_TEXTO_SUAVE = (148, 163, 184)
COLOR_ACENTO = (250, 204, 21)

LETRAS = "ABCDEFGHIJ"


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

    def barcos_hundidos_por(self, jugador):
        """Casillas de los barcos enemigos ya hundidos por `jugador`."""
        rival = 1 - jugador
        hundidas = set()
        for celdas in self.barcos[rival]:
            if all(self.disparos[jugador].get(c) == "X" for c in celdas):
                hundidas |= celdas
        return hundidas

    def disparar(self, celda):
        """Devuelve el mensaje del disparo, o None si la casilla ya se había disparado."""
        jugador, rival = self.turno, 1 - self.turno
        if celda in self.disparos[jugador]:
            return None

        fila, col = celda
        for celdas in self.barcos[rival]:
            if celda in celdas:
                self.disparos[jugador][celda] = "X"
                self.tableros[jugador].matriz_juego[fila, col] = "X"
                hundido = all(self.disparos[jugador].get(c) == "X" for c in celdas)
                if all(
                    all(self.disparos[jugador].get(c) == "X" for c in b)
                    for b in self.barcos[rival]
                ):
                    self.ganador = jugador
                return "¡Hundido!" if hundido else "¡Tocado!"

        self.disparos[jugador][celda] = "A"
        self.tableros[jugador].matriz_juego[fila, col] = "A"
        return "¡Agua!"

    def barcos_restantes(self, jugador):
        """Barcos de `jugador` que aún no han sido hundidos por el rival."""
        rival = 1 - jugador
        return sum(
            1
            for celdas in self.barcos[jugador]
            if not all(self.disparos[rival].get(c) == "X" for c in celdas)
        )

    def siguiente_turno(self):
        self.turno = 1 - self.turno


# ------------------------------------------------------------------- Dibujo
class Interfaz:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hundir la flota")
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.f_titulo = pygame.font.SysFont("arial", 56, bold=True)
        self.f_grande = pygame.font.SysFont("arial", 32, bold=True)
        self.f_normal = pygame.font.SysFont("arial", 22)
        self.f_pequena = pygame.font.SysFont("arial", 18)
        self.estado = "titulo"  # titulo | pase | juego | resultado | fin
        self.partida = Partida()

    # ---- utilidades de texto
    def texto(self, txt, fuente, color, centro=None, izq=None):
        img = fuente.render(txt, True, color)
        rect = img.get_rect()
        if centro:
            rect.center = centro
        elif izq:
            rect.topleft = izq
        self.pantalla.blit(img, rect)

    # ---- tableros
    def rect_celda(self, x0, fila, col):
        return pygame.Rect(x0 + col * CELDA, Y_TABLERO + fila * CELDA, CELDA, CELDA)

    def dibujar_etiquetas(self, x0):
        for i in range(TAM):
            self.texto(str(i), self.f_pequena, COLOR_TEXTO_SUAVE,
                       centro=(x0 + i * CELDA + CELDA // 2, Y_TABLERO - 16))
            self.texto(LETRAS[i], self.f_pequena, COLOR_TEXTO_SUAVE,
                       centro=(x0 - 16, Y_TABLERO + i * CELDA + CELDA // 2))

    def dibujar_marca_tocado(self, rect, color=COLOR_TEXTO):
        p = 10
        pygame.draw.line(self.pantalla, color, (rect.left + p, rect.top + p),
                         (rect.right - p, rect.bottom - p), 4)
        pygame.draw.line(self.pantalla, color, (rect.right - p, rect.top + p),
                         (rect.left + p, rect.bottom - p), 4)

    def dibujar_marca_agua(self, rect):
        pygame.draw.circle(self.pantalla, COLOR_TEXTO, rect.center, 6)

    def dibujar_tablero_propio(self, x0, jugador, titulo):
        """Tablero con los barcos de `jugador` y los disparos recibidos."""
        p = self.partida
        self.texto(titulo, self.f_normal, COLOR_TEXTO, izq=(x0, Y_TABLERO - 62))
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
                    color = COLOR_AGUA
                pygame.draw.rect(self.pantalla, color, r)
                pygame.draw.rect(self.pantalla, COLOR_LINEA, r, 1)
                marca = recibidos.get((f, c))
                if marca == "X":
                    self.dibujar_marca_tocado(r, COLOR_TOCADO if (f, c) not in hundidos else COLOR_TEXTO)
                elif marca == "A":
                    self.dibujar_marca_agua(r)

    def dibujar_tablero_ataque(self, x0, jugador, titulo, interactivo):
        """Tablero enemigo oculto: sólo se ven los disparos de `jugador`."""
        p = self.partida
        self.texto(titulo, self.f_normal, COLOR_TEXTO, izq=(x0, Y_TABLERO - 62))
        self.dibujar_etiquetas(x0)
        mis_disparos = p.disparos[jugador]
        hundidos = p.barcos_hundidos_por(jugador)
        celda_hover = self.celda_bajo_raton(x0) if interactivo else None

        for f in range(TAM):
            for c in range(TAM):
                r = self.rect_celda(x0, f, c)
                marca = mis_disparos.get((f, c))
                if (f, c) in hundidos:
                    color = COLOR_HUNDIDO
                elif marca == "X":
                    color = COLOR_TOCADO
                elif (f, c) == celda_hover and marca is None:
                    color = COLOR_AGUA_HOVER
                else:
                    color = COLOR_AGUA
                pygame.draw.rect(self.pantalla, color, r)
                pygame.draw.rect(self.pantalla, COLOR_LINEA, r, 1)
                if marca == "X":
                    self.dibujar_marca_tocado(r)
                elif marca == "A":
                    self.dibujar_marca_agua(r)

        if interactivo:
            marco = pygame.Rect(x0, Y_TABLERO, TAM * CELDA, TAM * CELDA)
            pygame.draw.rect(self.pantalla, COLOR_ACENTO, marco, 3)

    def celda_bajo_raton(self, x0):
        mx, my = pygame.mouse.get_pos()
        col, fila = (mx - x0) // CELDA, (my - Y_TABLERO) // CELDA
        if 0 <= fila < TAM and 0 <= col < TAM:
            return (fila, col)
        return None

    # ---- pantallas
    def pantalla_titulo(self):
        self.texto("HUNDIR LA FLOTA", self.f_titulo, COLOR_TEXTO, centro=(ANCHO // 2, 220))
        self.texto("Edición para dos jugadores", self.f_grande, COLOR_ACENTO, centro=(ANCHO // 2, 290))
        self.texto("Haz clic o pulsa ESPACIO para empezar", self.f_normal,
                   COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, 420))

    def pantalla_pase(self):
        j = self.partida.turno + 1
        self.texto(f"Turno del Jugador {j}", self.f_titulo, COLOR_TEXTO, centro=(ANCHO // 2, 240))
        self.texto("Pasa el control y asegúrate de que el rival no mira la pantalla",
                   self.f_normal, COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, 320))
        self.texto("Haz clic o pulsa ESPACIO para continuar", self.f_normal,
                   COLOR_ACENTO, centro=(ANCHO // 2, 420))

    def pantalla_juego(self):
        p = self.partida
        j = p.turno
        self.texto(f"Jugador {j + 1}", self.f_grande, COLOR_ACENTO, izq=(X_IZQ, 24))
        info = (f"Tus barcos en pie: {p.barcos_restantes(j)}   |   "
                f"Barcos enemigos en pie: {p.barcos_restantes(1 - j)}")
        self.texto(info, self.f_pequena, COLOR_TEXTO_SUAVE, izq=(X_IZQ, 70))

        interactivo = self.estado == "juego"
        self.dibujar_tablero_propio(X_IZQ, j, "Tus barcos")
        self.dibujar_tablero_ataque(X_DER, j, "Tus disparos", interactivo)

        if self.estado == "juego":
            self.texto("Elige una casilla del tablero derecho para disparar",
                       self.f_normal, COLOR_TEXTO, centro=(ANCHO // 2, 600))
            if p.mensaje:  # avisos como "casilla ya disparada"
                self.texto(p.mensaje, self.f_normal, COLOR_ACENTO, centro=(ANCHO // 2, 112))
        else:  # resultado
            color = COLOR_TOCADO if p.mensaje != "¡Agua!" else COLOR_AGUA_HOVER
            self.texto(p.mensaje, self.f_titulo, color, centro=(ANCHO // 2, 112))
            self.texto("Haz clic o pulsa ESPACIO para continuar", self.f_normal,
                       COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, 600))

    def pantalla_fin(self):
        p = self.partida
        self.texto(f"¡Gana el Jugador {p.ganador + 1}!", self.f_titulo, COLOR_ACENTO,
                   centro=(ANCHO // 2, 60))
        self.texto("Pulsa R para jugar de nuevo o ESC para salir", self.f_normal,
                   COLOR_TEXTO_SUAVE, centro=(ANCHO // 2, 110))
        self.dibujar_tablero_propio(X_IZQ, 0, "Tablero del Jugador 1")
        self.dibujar_tablero_propio(X_DER, 1, "Tablero del Jugador 2")

    # ---- eventos
    def avanzar(self):
        """Gestiona clic / espacio / enter para las pantallas de transición."""
        p = self.partida
        if self.estado == "titulo":
            self.estado = "pase"
        elif self.estado == "pase":
            p.mensaje = ""
            self.estado = "juego"
        elif self.estado == "resultado":
            if p.ganador is not None:
                self.estado = "fin"
            else:
                p.siguiente_turno()
                self.estado = "pase"

    def clic_juego(self):
        p = self.partida
        celda = self.celda_bajo_raton(X_DER)
        if celda is None:
            return
        resultado = p.disparar(celda)
        if resultado is None:
            p.mensaje = "Disparo anteriormente realizado"
            return
        p.mensaje = resultado
        self.estado = "resultado"

    def procesar_eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return False
                if e.key == pygame.K_r and self.estado == "fin":
                    self.partida = Partida()
                    self.estado = "pase"
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN) and self.estado != "juego":
                    self.avanzar()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.estado == "juego":
                    self.clic_juego()
                elif self.estado != "fin":
                    self.avanzar()
        return True

    # ---- bucle principal
    def ejecutar(self):
        corriendo = True
        while corriendo:
            corriendo = self.procesar_eventos()
            self.pantalla.fill(COLOR_FONDO)
            if self.estado == "titulo":
                self.pantalla_titulo()
            elif self.estado == "pase":
                self.pantalla_pase()
            elif self.estado in ("juego", "resultado"):
                self.pantalla_juego()
            elif self.estado == "fin":
                self.pantalla_fin()
            pygame.display.flip()
            self.reloj.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Interfaz().ejecutar()
