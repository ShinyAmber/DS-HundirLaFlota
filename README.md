<div align="center">

#  :smirk: :computer:Hundir :passenger_ship: la :boom: flota :computer: :scream: 

<img src="./img/WhatsApp Image 2026-09-19 at 01.26.38.jpeg" width="125" align="center" alt="Yixuan Interknot Network Profile Picture Zenless Zone Zero" style="display:block; margin: 0;"> 
<div style="margin: 0; line-height: 50%; width:80%;">
    (Holy random)
</div>


### Proyecto del Bootcamp <br> de Data Science 2026

</div>

## 🚢 Contenido
En este repositorio está el proyecto de Hundir la Flota, realizado con Python, Numpy y pygame (opcional)

Dos modos de juego:
- Jugador contra jugador (mísma maquina)
- Jugador contra la máquina

## ✨ Características

- Tablero de `10 × 10` casillas.
- Colocación aleatoria de los barcos.
- Cada jugador tiene dos vistas:
  - Su tablero de barcos.
  - Su tablero de disparos.
- Disparos por coordenadas, por ejemplo: `A3`, `C7`, `J9`.
- Resultados del disparo:
  - `¡Tocado!`
  - `¡Hundido!`
  - `¡Agua!`
- Interfaz sencilla para consola.

## 📦 Requisitos

- Python 3.x
- [NumPy](https://www.np.org/) ```pip install numpy```

## 🛠️ Instalación

Abre una terminal en la carpeta del proyecto e instala la dependencia:

```bash
pip install numpy
```

## ▶️ Cómo ejecutar el juego

```bash
python main.py
```

Después de abrir el programa:

1. Se muestra el título del juego.
2. Se pide elegir el modo de juego:
   - `0` para **Jugador contra Jugador**
   - `1` para **Jugador contra IA**
3. Se generan los tableros y comienza la partida.
4. Cada jugador dispara escribiendo una casilla, por ejemplo:
   - `A3`
   - `C7`
   - `J9`

## 📂 Estructura del proyecto

```text
.
├── main.py
└── utils.py
```

### `main.py`

Punto de entrada del programa.

Llama a las funciones necesarias para comenzar el juego.

### `utils.py`

Contiene las funciones y la clase principal del juego.

Funciones principales:

- `limpiar_pantalla()`: limpia la pantalla de la consola.
- `esperar_y_limpiar(segundos)`: espera unos segundos y limpia la pantalla.
- `pantalla_titulo()`: muestra el título y el menú de selección de modo.
- `crear_tablero(numero=10)`: crea los tableros para los jugadores.
- `crear_coordenadas(tamano)`: genera coordenadas aleatorias válidas.

Clase principal:

- `Tablero`: representa un tablero de juego.

Métodos de la clase:

- `colocar_barco(contador)`: coloca los barcos aleatoriamente en el tablero.
- `recibe_disparo(casilla)`: registra un disparo recibido.
- `comprobar_disparo(casilla, tablero_enemigo)`: comprueba el resultado del disparo.
- `disparar_ia(jugador)`: permite que la IA elija un disparo.
- `disparar_humano(casilla, jugador)`: procesa la entrada del jugador.

## 🧩 Lógica básica del juego

Cada tablero está representado con una matriz de `10 × 10`.

Los barcos se colocan de forma aleatoria dentro del tablero.

Cuando se dispara:

- Si acierta en un barco, se marca la casilla y se indica `¡Tocado!`.
- Si el barco queda hundido, se indica `¡Hundido!`.
- Si el disparo no toca ningún barco, se indica `¡Agua!`.

Los turnos se alternan entre los jugadores hasta que se cumple la condición de victoria.

## 🎮 Cómo jugar

Las coordenadas usan letras de `A` a `J` y números de `0` a `9`.

Ejemplos válidos:

```text
A0
A9
J0
J9
C5
F3
```

## 🏆 Victoria

La partida finaliza cuando se detecta la victoria del jugador que hundió la flota del rival.

---

<div align="center">
¡Gracias por leer este README!
</div>
