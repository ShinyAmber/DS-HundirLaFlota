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
    matriz_titulo = np.full((20,20)," ")
    matriz_titulo[0:1,0:] = "*"
    matriz_titulo[:,:1] = "*"
    matriz_titulo[-1] = "*"
    matriz_titulo[:,-1] = "*"
    print(matriz_titulo)

    for i in range(matriz_titulo.shape[0]):
        for j in range(matriz_titulo.shape[1]):
            print(matriz_titulo[i,j],end=" ")
        print("")

# pantalla_titulo()

def crear_tablero(numero = 10):
    tablero_jugador1 = Tablero(10)
    tablero_jugador2 = Tablero(10)

    tablero_jugador1.colocar_barco(0)
    tablero_jugador2.colocar_barco(0)

def colocar_barco(barco, tablero):
    pass

def disparar(casilla,tablero):
    letras = "ABCDEFGHIJ"
    indice_0 = letras.index(casilla[0])
    if (tablero[indice_0, casilla[1]] == "O"):
        tablero[indice_0, casilla[1]] = "X"
    else:
        tablero[indice_0, casilla[1]] = "A"

def crear_coordenadas(tamano):
    numeroX = np.random.randint(0,10)
    numeroY = np.random.randint(0,10)

    checking = True
    while checking == True:
        if (numeroX == 9 or numeroY == 9):
            numeroX = np.random.randint(0,10)
            numeroY = np.random.randint(0,10)
        else:
            checking = False
            return [numeroX, numeroY]


class Tablero():

    puntuacion_actual = 0
    casilla_inicial = "0"

    vidas_barcos = [4,3,3,2,2,2]
    
    
    barcos = np.full((6,2), "*")
    posiciones_barcos = []
    

    def __init__(self,tamano = 10):
        self.tamano = tamano
        self.matriz = np.full((tamano, tamano), "-")

    def colocar_barco(self, contador):
        print("Contador =", contador)
        tablero = self.matriz.copy() # Aqui hacemos la copia del tablero para intentar colocar las casillas

        if (contador > len(self.vidas_barcos) -1):
            return
        
        sentido = np.random.randint(0,2)
        # 0 = horizontal
        # 1 = vertical
        numeros = crear_coordenadas(self.tamano)

        if (sentido == 1): # Vertical
            bucle_creacion = True
            while bucle_creacion == True:
                if (tablero[numeros[0], numeros[1]] == "O" or (numeros[0] + self.vidas_barcos[contador]) > 9):
                    crear_coordenadas(self.tamano)
                    continue
                else:
                    for i in range(0, self.vidas_barcos[contador]):
                        if (tablero[numeros[0] + i, numeros[1]] == "O" or (numeros[0] + i) > 9):
                            crear_coordenadas(self.tamano)
                            continue
                        else:
                            tablero[numeros[0] + i, numeros[1]] = "O"
                            bucle_creacion = False
                            break

            print("Representacion: ")
            print(tablero)
            contador += 1
            self.colocar_barco(contador)

        else:
            bucle_creacion = True
            while bucle_creacion == True:
                if (tablero[numeros[0], numeros[1]] == "O" or (numeros[1] + self.vidas_barcos[contador]) > 9):
                    crear_coordenadas(self.tamano)
                    continue
                else:
                    for i in range(0, self.vidas_barcos[contador]):
                        if (tablero[numeros[0], numeros[1] + i] == "O" or (numeros[1] + i) > 9):
                            crear_coordenadas(self.tamano)
                            continue
                        else:
                            tablero[numeros[0], numeros[1] + i] = "O"
                            bucle_creacion = False
                            break
            

            print("Representacion: ")
            print(tablero)
            contador += 1
            self.colocar_barco(contador)

    def comprobar_puntuacion(self):
        if self.puntuacion_actual < 15:
            return 1
        else:
            return 0
        
            

    def disparar(self,casilla):
        letras = "ABCDEFGHIJ"
        indice_0 = letras.index(casilla[0])
        if(self.matriz[indice_0, casilla[1]] == "O"):
            self.matriz[indice_0, casilla[1]] = "X"
        else:
            self.matriz[indice_0, casilla[1]] = "A"

        self.comprobar_puntuacion([indice_0, casilla[1]], 0)