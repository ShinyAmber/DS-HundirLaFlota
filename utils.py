import subprocess
import os
import time
import numpy as np

def limpiar_pantalla():
    if (os.name == "nt"):
        subprocess.run('cls')
    else:
        subprocess.run('clear')

def esperar_y_limpiar(segundos):
    time.sleep(segundos)
    limpiar_pantalla()

def pantalla_titulo():
    limpiar_pantalla()
    print("HUNDIR LA FLOTA - PYTHON")
    print("Elige modo de juego")
    modo = (int(input("0 - Jugador contra Jugador / 1 - Jugador contra IA \n")))
    if (modo == 0):
        iniciar_juego_consola()
    else:
        iniciar_juego_ia_consola()

# pantalla_titulo()

def crear_tablero(numero = 10):
    tablero_jugador1 = Tablero()
    tablero_jugador2 = Tablero()

    tablero_jugador1.colocar_barco(0)
    tablero_jugador2.colocar_barco(0)

    return [tablero_jugador1, tablero_jugador2]

def crear_coordenadas(tamano):
    numeroX = np.random.randint(0,10)
    numeroY = np.random.randint(0,10)

    checking = True
    while checking == True:
        # print(numeroX,numeroY)
        if (numeroX > 8 or numeroY > 8):
            numeroX = np.random.randint(0,10)
            numeroY = np.random.randint(0,10)
        else:
            checking = False
            break

    return [numeroX, numeroY]


class Tablero(object):

    vidas_barcos = [4,3,3,2,2,2]

    barcos = np.full((6,2), "*")
    posiciones_barcos = []
    

    def __init__(self,tamano = 10):
        self.tamano = tamano
        self.matriz = np.full((tamano, tamano), "-")
        self.matriz_juego = self.matriz.copy()
        self.posiciones_barcos = []
        self.puntuacion_actual = 0


    def colocar_barco(self, contador):

        tablero = self.matriz.copy() # Aqui hacemos la copia del tablero para intentar colocar las casillas

        if (contador >= len(self.vidas_barcos)):
            return
        
        sentido = np.random.randint(0,4)
        
        numeros = crear_coordenadas(self.tamano)
        # 0 = izquierda
        # 1 = derecha
        # 2 = arriba
        # 3 = abajo
        generating = True
        while generating == True:
            # print("Sentido:", sentido)
            longitud = self.vidas_barcos[contador]
            if (sentido < 2): # Horizontal
                fil_inicial = max(0, numeros[0] - 1)
                fil_final = min(self.tamano, numeros[0] + 2)

                if(sentido == 0): # Izquierda -- ABSOLUTE VICOTORY: 14-10-26 12:41 
                    if((numeros[1] < longitud)):
                        numeros = crear_coordenadas(self.tamano)
                        continue
            
                    rango_barco = tablero[fil_inicial:fil_final,max(0, (numeros[1] - (longitud) -1)):min(self.tamano,numeros[1] + 2)]
            
                else: # Derecha
                    if ((numeros[1] + longitud > self.tamano)):
                        numeros = crear_coordenadas(self.tamano)
                        continue
            
                    rango_barco = tablero[fil_inicial:fil_final, max(0, numeros[1] - 1):min(self.tamano, (numeros[1] +longitud) + 1)]
            
            else:
                col_inicial = max(0, numeros[1] - 1)
                col_final = min(self.tamano, numeros[1] + 2)
            
                if(sentido == 2): # Arriba
                    if (numeros[0] < longitud):
                        numeros = crear_coordenadas(self.tamano)
                        continue
            
                    rango_barco = tablero[max(0, (numeros[0] - longitud)):min(self.tamano, numeros[0] + 2), col_inicial:col_final] 

                else:
                    if (numeros[0] + longitud > self.tamano):
                        numeros = crear_coordenadas(self.tamano)
                        continue
            
                    rango_barco = tablero[max(0, numeros[0] - 1):min(self.tamano, numeros[0] + longitud +2), col_inicial:col_final]
            
            
            if (np.any(rango_barco != "-")):
                numeros = crear_coordenadas(self.tamano)
                continue
            else:
                if (sentido < 2):
                    if (sentido == 0):
                        tablero[numeros[0], numeros[1] - longitud + 1:(numeros[1])+ 1] = "O"
                        # (fila:ini;fila_fin;columna:ini;columna:fin;eslora,sentido)
                        self.posiciones_barcos.append([[numeros[0],numeros[0]],[numeros[1],numeros[1] - longitud + 1],longitud, sentido]) 
                    else:
                        tablero[numeros[0], numeros[1]: (numeros[1] + longitud)] = "O"
                        self.posiciones_barcos.append([[numeros[0],numeros[0]],[numeros[1],numeros[1] + longitud], longitud, sentido])
                else:
                    if(sentido == 2):
                        tablero[(numeros[0] - longitud + 1):(numeros[0] + 1), numeros[1]] = "O"
                        self.posiciones_barcos.append([[numeros[0],numeros[0] - longitud + 1], [numeros[1], numeros[1]],longitud, sentido])
                    else:
                        tablero[numeros[0]:(numeros[0] + longitud), numeros[1]] = "O"
                        self.posiciones_barcos.append([[numeros[0], numeros[0] + longitud - 1], [numeros[1], numeros[1]], longitud, sentido])

            generating = False
            

        contador += 1
        self.matriz = tablero
        self.colocar_barco(contador)

    def recibe_disparo(self, casilla):
        self.matriz[casilla[0], casilla[1]] = "X"
        resultado = 0
        for i in self.posiciones_barcos:
            filas = i[0]
            columnas = i[1]

            fila_min = min (filas[0], filas[1])
            fila_max = max (filas[0], filas[1])
            columna_min = min(columnas[0], columnas[1])
            columna_max = max(columnas[0], columnas[1])

            if (fila_min <= casilla[0] <= fila_max and columna_min <= casilla[1] <= columna_max):
                i[2] -= 1

                if (i[2] == 0):
                    resultado = 1
                else:
                    resultado = 0

                break
                
        return resultado


    def comprobar_disparo(self, casilla, tablero_enemigo):
        if (tablero_enemigo.recibe_disparo(casilla) == 0):
            self.puntuacion_actual += 1
            return "¡Tocado!"
        else:
            return "¡Hundido!"

    
    def disparar_ia(self, jugador):
        disparando = True
        while disparando == True:
            indice_0 = np.random.randint(0,self.tamano)
            indice_1 = np.random.randint(0,self.tamano)

            if (self.matriz_juego[indice_0,indice_1] == "A" or self.matriz_juego[indice_0, indice_1] == "X"):
                continue
            elif (jugador.matriz[indice_0, indice_1] == "O"):
                self.matriz_juego[indice_0,indice_1] = "X"
                return self.comprobar_disparo([indice_0,indice_1], jugador)
            else:
                self.matriz_juego[indice_0, indice_1] == "A"
                disparando = False
                return "¡Agua!"
           
    def disparar_humano(self,casilla, jugador):
        disparando = True
        while disparando:
            if (len(casilla) < 2 or len(casilla) > 2):
                print("Disparo no valido!")
                casilla = input("")
                continue
            
            letras = "ABCDEFGHIJ"
        
            try:
                letra = str(casilla[0]).upper()
                indice_0 = int(letras.index(letra))
                indice_1 = int(casilla[1])
        
                if(jugador.matriz[indice_0, indice_1] == "O"):
                    self.matriz_juego[indice_0, indice_1] = "X"
                    disparando = False
                    return self.comprobar_disparo([indice_0, indice_1], jugador)
                elif (self.matriz_juego[indice_0,indice_1] == "A"):
                    print("Disparo anteriormente realizado!")
                    casilla = (input(""))
                    continue
                else:
                    self.matriz_juego[indice_0, indice_1] = "A"
                    disparando = False
                    return "¡Agua!"
            except:
                    print("Disparo no valido!")
                    casilla = (input(""))
                    continue



def iniciar_juego_consola():
    esperar_y_limpiar(1)
    time.sleep(1)
    print("Bienvenid@ a")
    time.sleep(1)
    print("Hundir la flota. Edición para dos jugadores.")
    print("Generando tableros...")
    jugadores = crear_tablero()
    esperar_y_limpiar(1)
    game = True
    turno = 0
    while game == True:
            print("Tus barcos:")
            print(jugadores[turno].matriz)
            print()
            print("Tus disparos:")
            print(jugadores[turno].matriz_juego)
            print(jugadores[turno].disparar_humano(input("¿Donde quieres disparar? Escribe una casilla A-J y 0-9, ejemplo: A3 \n"),jugadores[turno - 1]))
            if (jugadores[turno].puntuacion_actual > 15):
                break
            esperar_y_limpiar(1)
            if (turno == 0):
                turno = 1
            else:
                turno = 0

    esperar_y_limpiar(1)
    print("El jugador",turno,"ha ganado!")


def iniciar_juego_ia_consola():
    esperar_y_limpiar(1)
    time.sleep(1)
    print("Bienvenid@ a")
    time.sleep(1)
    print("Hundir la flota. Edición para un jugador.")
    print("Generando tableros...")
    jugadores = crear_tablero()
    esperar_y_limpiar(1)
    game = True
    turno = 0
    while game == True:
            if turno == 0:
                print("Tus barcos:")
                print(jugadores[turno].matriz)
                print()
                print("Tus disparos:")
                print(jugadores[turno].matriz_juego)
                print(jugadores[turno].disparar_humano(input("¿Donde quieres disparar? Escribe una casilla A-J y 0-9, ejemplo: A3 \n"),jugadores[turno - 1]))
            else:
                print("Turno de la ia:")
                time.sleep(0.5)
                print(jugadores[turno].disparar_ia(jugadores[turno -1]))
            if (jugadores[turno].puntuacion_actual > 15):
                break

            if (turno == 0):
                turno += 1
            else:
                turno -= 1

            esperar_y_limpiar(1)

    esperar_y_limpiar(1)
    if (turno == 0):
        print("¡Has ganado a la IA! ¡Enhorabuena!")
    else:
        print("¡Ha ganado la IA! Si que es inteligente, si.")