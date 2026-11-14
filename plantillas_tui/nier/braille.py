#!/usr/bin/env python3
"""Lienzo de puntos Braille y fuente 5 × 7 para las pantallas dot matrix.

Una celda de terminal con un carácter Braille (U+2800–U+28FF) contiene una
matriz de 2 × 4 puntos, así que un lienzo de 100 × 30 celdas son **200 × 120
puntos**. Ese es el orden de magnitud de un cartel de puntos real, no una
imitación a ojo.

Este módulo trabaja en coordenadas de punto y luego funde el resultado en un
`Lienzo` de celdas: cada celda recibe el carácter Braille correcto y el color
de sus puntos.

Límites que el medio impone, dichos aquí y no descubiertos después:

* **un color por celda**: los ocho puntos de una celda comparten color de
  primer plano, porque en una terminal el color es de la celda, no del punto;
* **sin fondo encendido**: Braille enciende puntos sobre vacío, no apaga puntos
  sobre una superficie luminosa;
* **no es texto**: cada celda es un trozo de imagen; no se selecciona ni se
  copia. El texto se dibuja con una fuente 5 × 7 propia, sin tildes.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402

# ---------------------------------------------------------------------------
# fuente 5 × 7
# ---------------------------------------------------------------------------
#: Cada glifo son 7 filas de 5 puntos. Se dibujan con un punto de separación,
#: así que un carácter ocupa 6 × 8 puntos. Sin minúsculas ni tildes: es una
#: fuente de panel, y los paneles de puntos no tienen tildes.
_GLIFOS = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01110/10001/10000/10000/10000/10001/01110",
    "D": "11100/10010/10001/10001/10001/10010/11100",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01110/10001/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "01110/00100/00100/00100/00100/00100/01110",
    "J": "00111/00010/00010/00010/00010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/11001/10101/10011/10011/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/11011/10001",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00110/01000/10000/11111",
    "3": "11111/00010/00100/00010/00001/10001/01110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/11110/00001/00001/10001/01110",
    "6": "00110/01000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00010/01100",
    " ": "00000/00000/00000/00000/00000/00000/00000",
    ".": "00000/00000/00000/00000/00000/01100/01100",
    ",": "00000/00000/00000/00000/01100/01100/11000",
    ":": "00000/01100/01100/00000/01100/01100/00000",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    "+": "00000/00100/00100/11111/00100/00100/00000",
    "/": "00001/00010/00010/00100/01000/01000/10000",
    "%": "11001/11010/00010/00100/01000/01011/10011",
    "(": "00010/00100/01000/01000/01000/00100/00010",
    ")": "01000/00100/00010/00010/00010/00100/01000",
    "?": "01110/10001/00001/00110/00100/00000/00100",
    "!": "00100/00100/00100/00100/00100/00000/00100",
    "<": "00001/00010/00100/01000/00100/00010/00001",
    ">": "10000/01000/00100/00010/00100/01000/10000",
    "=": "00000/11111/00000/11111/00000/00000/00000",
    "#": "01010/01010/11111/01010/11111/01010/01010",
    "*": "00000/10101/01110/11111/01110/10101/00000",
    "'": "00100/00100/00000/00000/00000/00000/00000",
    "·": "00000/00000/00000/01100/01100/00000/00000",
}

FUENTE = {clave: [fila for fila in valor.split("/")] for clave, valor in _GLIFOS.items()}

ANCHO_GLIFO, ALTO_GLIFO, PASO_GLIFO = 5, 7, 6
ALTO_LINEA = 8


# ---------------------------------------------------------------------------
# lienzo de puntos
# ---------------------------------------------------------------------------
class Puntos:
    """Matriz de 200 × 120 puntos; cada punto guarda un color o nada."""

    def __init__(self, ancho: int = 200, alto: int = 120) -> None:
        self.ancho, self.alto = ancho, alto
        self.rejilla = [[None] * ancho for _ in range(alto)]
        self.fallos: list[str] = []
        self.avisos: list[str] = []

    # --- primitivas --------------------------------------------------------
    def punto(self, x: int, y: int, color: str | None) -> None:
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            self.rejilla[y][x] = color

    def relleno(self, x: int, y: int, ancho: int, alto: int, color: str | None) -> None:
        for fila in range(y, y + alto):
            for columna in range(x, x + ancho):
                self.punto(columna, fila, color)

    def caja(self, x: int, y: int, ancho: int, alto: int, color: str) -> None:
        for columna in range(x, x + ancho):
            self.punto(columna, y, color)
            self.punto(columna, y + alto - 1, color)
        for fila in range(y, y + alto):
            self.punto(x, fila, color)
            self.punto(x + ancho - 1, fila, color)

    def linea(self, x0: int, y0: int, x1: int, y1: int, color: str) -> None:
        """Bresenham: una recta de puntos entre dos extremos."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx + dy
        while True:
            self.punto(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            doble = 2 * error
            if doble >= dy:
                error += dy
                x0 += sx
            if doble <= dx:
                error += dx
                y0 += sy

    def circulo(self, cx: int, cy: int, radio: float, color: str,
                relleno: bool = False) -> None:
        for y in range(int(cy - radio) - 1, int(cy + radio) + 2):
            for x in range(int(cx - radio) - 1, int(cx + radio) + 2):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if (d <= radio if relleno else abs(d - radio) < 0.55):
                    self.punto(x, y, color)

    def rombo(self, cx: int, cy: int, radio: int, color: str, relleno: bool = False) -> None:
        for y in range(cy - radio, cy + radio + 1):
            for x in range(cx - radio, cx + radio + 1):
                d = abs(x - cx) + abs(y - cy)
                if (d <= radio if relleno else d == radio):
                    self.punto(x, y, color)

    def triangulo(self, x: int, y: int, alto: int, color: str, relleno: bool = True) -> None:
        """Triángulo apuntando a la derecha: la nave del hackeo."""
        for fila in range(alto):
            mitad = abs(fila - alto // 2)
            largo = max(1, alto // 2 + 1 - mitad)
            for columna in range(largo):
                self.punto(x + columna, y + fila, color)

    # --- texto -------------------------------------------------------------
    def texto(self, x: int, y: int, texto: str, color: str | None = None,
              escala: int = 1, limpia: bool = True) -> int:
        """Dibuja con la fuente 5 × 7. ``color=None`` apaga puntos (inverso).

        ``limpia`` borra la retícula de fondo bajo el texto. Sin eso, los puntos
        del fondo asoman por los huecos entre trazos y una letra parece tener una
        línea de puntos cruzándola. La regla de la casa: nunca se dibuja nada
        decorativo detrás de una letra.
        """
        if limpia:
            # Solo se borra la retícula del fondo, nunca un relleno sólido: si no,
            # el texto inverso abriría un agujero claro dentro de su propia barra.
            for fila in range(max(0, y - 1), min(self.alto, y + ALTO_GLIFO * escala + 1)):
                for columna in range(max(0, x - 1),
                                     min(self.ancho, x + self.ancho_texto(texto, escala) + 1)):
                    if self.rejilla[fila][columna] == "rejilla":
                        self.rejilla[fila][columna] = None
        cursor = x
        for ch in texto.upper():
            glifo = FUENTE.get(ch)
            if glifo is None:
                self.fallos.append(f"glifo ausente: {ch!r}")
                glifo = FUENTE["?"]
            for fila, linea in enumerate(glifo):
                for columna, encendido in enumerate(linea):
                    if encendido == "1":
                        self.relleno(cursor + columna * escala, y + fila * escala,
                                     escala, escala, color)
            cursor += PASO_GLIFO * escala
        return cursor

    def ancho_texto(self, texto: str, escala: int = 1) -> int:
        return len(texto) * PASO_GLIFO * escala

    # --- conversión --------------------------------------------------------
    def a_lienzo(self) -> Lienzo:
        """Funde la matriz de puntos en un lienzo de celdas con caracteres Braille.

        El bit de cada punto sigue el orden Braille: (0,0)=1, (0,1)=2, (0,2)=3,
        (1,0)=4, (1,1)=5, (1,2)=6, (0,3)=7, (1,3)=8.

        Una celda tiene un solo color de primer plano, así que si dos colores caen
        en la misma celda gana el que tenga más puntos (y en empate, el primero en
        orden Braille). Esos choques se cuentan en ``avisos``: son la señal de que
        dos elementos se están tocando, no un fallo del medio.
        """
        assert self.ancho % 2 == 0 and self.alto % 4 == 0
        lienzo = Lienzo(self.ancho // 2, self.alto // 4)
        bits = ((0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (1, 0, 0x08),
                (1, 1, 0x10), (1, 2, 0x20), (0, 3, 0x40), (1, 3, 0x80))
        for celda_y in range(lienzo.alto):
            for celda_x in range(lienzo.ancho):
                valor, conteo, rejilla = 0, {}, False
                for dx, dy, bit in bits:
                    color = self.rejilla[celda_y * 4 + dy][celda_x * 2 + dx]
                    if color is None:
                        continue
                    valor |= bit
                    if color == "rejilla":
                        rejilla = True
                    else:
                        conteo[color] = conteo.get(color, 0) + 1
                if conteo:
                    # mayoría de puntos; en empate gana el primero en orden Braille
                    estilo = max(conteo, key=conteo.get)
                    if len(conteo) > 1:
                        self.avisos.append(
                            f"celda ({celda_x},{celda_y}): "
                            + " y ".join(f"{c}×{n}" for c, n in conteo.items())
                            + f" → {estilo}")
                else:
                    estilo = "rejilla" if rejilla else "papel"
                lienzo.rejilla[celda_y][celda_x].char = chr(0x2800 + valor)
                lienzo.rejilla[celda_y][celda_x].estilo = estilo
        return lienzo

    # --- diagnóstico -------------------------------------------------------
    def mapa(self) -> str:
        """Vista en ASCII del lienzo de puntos, para depurar a ojo."""
        salida = []
        for fila in self.rejilla:
            salida.append("".join("." if c is None else ("+" if c == "rejilla" else "#")
                                  for c in fila))
        return "\n".join(salida)


def fondo_rejilla(p: Puntos, color: str = "rejilla", paso: int = 6) -> None:
    """La retícula de puntos que el menú de NieR ya dibuja de verdad."""
    for y in range(paso // 2, p.alto, paso):
        for x in range(paso // 2, p.ancho, paso):
            p.punto(x, y, color)
