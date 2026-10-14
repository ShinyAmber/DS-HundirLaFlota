import pygame as pgame

pgame.init()
pgame.font.init() # Para las fuentes y textos
pgame.mixer.init() # Para los sonidos
pgame.mixer.pre_init() # Valores por dfecto

pgame.mixer.set_soundfont("soundfonts/Gameboy_GM_Soundfont_2_FixTest.SF2.sf2")
title = pgame.mixer.Sound("sounds/Sml2th.mid")
pgame.mixer.Sound.play(title)

# Ventana del juego
ANCHO, ALTO = 640, 480
pantalla = pgame.display.set_mode((ANCHO, ALTO))
pgame.display.set_caption("Hundir la flota")
reloj = pgame.time.Clock()

# Nuestro personaje: un cuadrado
x, y = 10, 10
tam = 20
velocidad = 3

sigue = True

fuente_texto = pgame.font.Font("fonts/Jersey10-Regular.ttf", 30)
fuente_titulo = pgame.font.Font("fonts/PressStart2P-Regular.ttf",42)

while sigue:
    # Eventos: cerrar ventana, teclas, etc.
    for evento in pgame.event.get():
        if evento.type == pgame.QUIT:
            sigue = False
        elif evento.type == pgame.KEYDOWN:
            if evento.key == pgame.K_ESCAPE:
                sigue = False

    # Movimiento continuo con flechas
    teclas = pgame.key.get_pressed()

    if teclas[pgame.K_UP]:
        y -= velocidad
    if teclas[pgame.K_DOWN]:
        y += velocidad
    if teclas[pgame.K_LEFT]:
        x -= velocidad
    if teclas[pgame.K_RIGHT]:
        x += velocidad

    # Para que no salga de la ventana
    x = max(0, min(ANCHO - tam, x))
    y = max(0, min(ALTO - tam, y))

    # Dibujar
    pantalla.fill((0, 0, 0))
    pgame.draw.rect(pantalla, (255, 255, 255), (x, y, tam, tam))

    # Prueba texto
    fuente_texto = pgame.font.Font("fonts/Jersey10-Regular.ttf", 30)
    fuente_titulo = pgame.font.Font("fonts/PressStart2P-Regular.ttf",42)
    texto = fuente_titulo.render("HUNDIR\nLA\nFLOTA", False, (255,255,255))
    pantalla.blit(texto,((ANCHO /2),( ALTO /2)))

    # Mostrar lo dibujado
    pgame.display.update()

    # Limitar a 60 frames por segundo
    reloj.tick(120)

pgame.quit()
