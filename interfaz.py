import pygame
import sys
import numpy as np
from utils import Tablero, crear_tablero

# Inicializar Pygame-CE
pygame.init()
pygame.font.init()

# Configuración de la ventana y colores
ANCHO, ALTO = 900, 650
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Hundir la Flota - Edición Gráfica")

# Paleta de colores (Diseño limpio y claro)
COLOR_FONDO = (245, 247, 250)
COLOR_TEXTO = (33, 37, 41)
COLOR_PANEL = (255, 255, 255)
COLOR_BORDE = (206, 212, 218)
COLOR_AGUA = (222, 226, 230)      # Casilla vacía / agua no descubierta
COLOR_TOCADO = (230, 57, 70)     # Rojo impacto
COLOR_HUNDIDO = (15, 76, 129)    # Azul oscuro barco destruido
COLOR_FALLO = (108, 117, 125)    # Gris agua disparada
COLOR_BARCO = (40, 116, 166)     # Azul visible en el tablero propio

TAM_CELDA = 35
MARGEN = 10

FUENTE = pygame.font.SysFont("Arial", 18)
FUENTE_TITULO = pygame.font.SysFont("Arial", 24, bold=True)
FUENTE_GRANDE = pygame.font.SysFont("Arial", 32, bold=True)

def dibujar_tablero_grafico(superficie, matriz, x_inicio, y_inicio, es_propio=False):
    """Dibuja una matriz de 10x10 en la pantalla con su cuadrícula y letras/números."""
    letras = "ABCDEFGHIJ"
    
    # Dibujar cabeceras de columnas (0-9)
    for col in range(10):
        texto = FUENTE.render(str(col), True, COLOR_TEXTO)
        superficie.blit(texto, (x_inicio + col * TAM_CELDA + TAM_CELDA // 3, y_inicio - 25))
        
    # Dibujar cabeceras de filas (A-J) y celdas
    for fila in range(10):
        # Letra de fila
        texto_letra = FUENTE.render(letras[fila], True, COLOR_TEXTO)
        superficie.blit(texto_letra, (x_inicio - 25, y_inicio + fila * TAM_CELDA + TAM_CELDA // 4))
        
        for col in range(10):
            val = matriz[fila, col]
            rect = pygame.Rect(x_inicio + col * TAM_CELDA, y_inicio + fila * TAM_CELDA, TAM_CELDA - 2, TAM_CELDA - 2)
            
            # Determinar color según el estado de la celda
            color = COLOR_AGUA
            if val == "X":
                color = COLOR_TOCADO
            elif val == "A":
                color = COLOR_FALLO
            elif es_propio and val == "O":
                color = COLOR_BARCO
            elif es_propio and val != "-":
                # Si en tu lógica interna usas otra marca para barcos tocados en el propio
                color = COLOR_BARCO

            pygame.draw.rect(superficie, color, rect, border_radius=4)
            pygame.draw.rect(superficie, COLOR_BORDE, rect, 1, border_radius=4)

def obtener_casilla_clic(pos_mouse, x_inicio, y_inicio):
    """Traduce las coordenadas de píxeles del ratón a índices de matriz (fila, col)."""
    x, y = pos_mouse
    if x_inicio <= x < x_inicio + 10 * TAM_CELDA and y_inicio <= y < y_inicio + 10 * TAM_CELDA:
        col = (x - x_inicio) // TAM_CELDA
        fila = (y - y_inicio) // TAM_CELDA
        return int(fila), int(col)
    return None

def main():
    reloj = pygame.time.Clock()
    
    # Inicializar jugadores usando tu función existente
    jugadores = crear_tablero()
    turno = 0  # 0 para Jugador 1, 1 para Jugador 2
    
    mensaje_estado = "¡Comienza la partida! Turno del Jugador 1 (Dispara al tablero derecho)"
    juego_terminado = False
    ganador = ""

    ejecutando = True
    while ejecutando:
        VENTANA.fill(COLOR_FONDO)
        
        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif evento.type == pygame.MOUSEBUTTONDOWN and not juego_terminado:
                if evento.button == 1: # Click izquierdo
                    pos = pygame.mouse.get_pos()
                    # El tablero derecho es donde dispares al enemigo
                    # Coordenada X de inicio del tablero enemigo: 480
                    casilla = obtener_casilla_clic(pos, 480, 120)
                    
                    if casilla:
                        fila, col = casilla
                        jugador_actual = jugadores[turno]
                        oponente = jugadores[1 - turno]
                        
                        # Comprobamos que no se haya disparado ya ahí en la matriz de juego
                        if jugador_actual.matriz_juego[fila, col] in ["X", "A"]:
                            mensaje_estado = "¡Ya has disparado en esa casilla! Elige otra."
                        else:
                            # Ejecutamos el disparo usando tu método integrado
                            # Nota: pasamos la celda en formato [fila, col] y el oponente
                            resultado_disparo = jugador_actual.disparar([fila, col], oponente)
                            mensaje_estado = f"Jugador {turno + 1}: {resultado_disparo}"
                            
                            # Verificar si se han acabado los barcos del oponente (comprobando vidas totales)
                            total_vidas_oponente = sum([b[2] for b in oponente.posiciones_barcos])
                            if total_vidas_oponente <= 0:
                                juego_terminado = True
                                ganador = f"¡Jugador {turno + 1} ha ganado la partida!"
                            else:
                                # Cambiar de turno
                                turno = 1 - turno

        # --- Dibujado de la interfaz ---
        # Título principal
        titulo = FUENTE_TITULO.render("HUNDIR LA FLOTA", True, COLOR_TEXTO)
        VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 20))
        
        # Indicador de Turno
        sub_titulo = FUENTE_GRANDE.render(f"Turno: Jugador {turno + 1}", True, COLOR_HUNDIDO if not juego_terminado else (40, 167, 69))
        VENTANA.blit(sub_titulo, (ANCHO // 2 - sub_titulo.get_width() // 2, 60))

        # Etiquetas de los tableros
        lbl_propios = FUENTE.render("Tus Barcos", True, COLOR_TEXTO)
        VENTANA.blit(lbl_propios, (80, 95))
        
        lbl_disparos = FUENTE.render("Tus Disparos al Enemigo", True, COLOR_TEXTO)
        VENTANA.blit(lbl_disparos, (480, 95))

        # Dibujar Tablero Propio (Izquierda: x=80, y=120)
        dibujar_tablero_grafico(VENTANA, jugadores[turno].matriz, 80, 120, es_propio=True)
        
        # Dibujar Tablero de Disparos / Radar (Derecha: x=480, y=120)
        dibujar_tablero_grafico(VENTANA, jugadores[turno].matriz_juego, 480, 120, es_propio=False)

        # Barra inferior de mensajes / estado
        pygame.draw.rect(VENTANA, COLOR_PANEL, (50, 500, ANCHO - 100, 50), border_radius=6)
        pygame.draw.rect(VENTANA, COLOR_BORDE, (50, 500, ANCHO - 100, 50), 1, border_radius=6)
        
        texto_msg = FUENTE.render(ganador if juego_terminado else mensaje_estado, True, COLOR_TEXTO if not juego_terminado else (40, 167, 69))
        VENTANA.blit(texto_msg, (70, 515))

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()