#!/usr/bin/env python3
"""Mockups de una TUI a partir de una pieza de interfaz sci-fi de ArtStation.

Referencia: la imagen que dio el usuario (1800 × 1201), un kit de paneles con
ENERGY REACTOR, MEMORY CLASTERS, ENGINE LIST, ES.CS.2S1 y 6215.0.50FUDG.

Paleta **medida** sobre esa imagen. Lo importante del resultado: la pieza **no
tiene blanco**. Son tres canales y un gris.

    fondo     #090d18     cian      #1ad3d6     naranja  #f76c0a
    malla     #0d2a33*    cian pál. #90f4ec     rojo     #f00001
    trazo     #11565e*    teal      #25a39f     gris     #424345
    borde     #14898b     (*) derivados: filetes finos y retícula de fondo

Lenguaje visual, todo sacado de la pieza:

* **cabecera achaflanada**: el borde superior sobresale una columna y acaba en
  `╲`; el inferior hace lo mismo con `╱`. Es la forma que más la identifica;
* **placa de número** `[00]` al principio de cada cabecera;
* **cuñas de esquina** `◤` y `◢`, en diagonal opuesta;
* **franjas de peligro** a 45° hechas con `╱` desplazadas una columna por fila;
* **números gigantes** con una fuente de bloques de 4 × 5;
* **cita en naranja** y cuerpo en teal: el color no adorna, clasifica (cian =
  correcto, naranja = atención, rojo = error, gris = en espera).

    python3 reactor/reactor.py            # reactor.html y reactor.txt
    python3 reactor/reactor.py --ansi     # pinta las pantallas en tu terminal
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402

ANCHO, ALTO = 100, 30

REACTOR = {
    "fondo": "#090d18",
    "malla": "#0d2a33",
    "trazo": "#11565e",
    "borde": "#14898b",
    "cian": "#1ad3d6",
    "pico": "#90f4ec",
    "teal": "#25a39f",
    "naranja": "#f76c0a",
    "rojo": "#f00001",
    "gris": "#424345",
    "gris2": "#3d4547",
}

#: fuente de bloques 4 × 5 para los números gigantes
GRANDES = {
    "0": ["████", "█  █", "█  █", "█  █", "████"],
    "1": ["  █ ", " ██ ", "  █ ", "  █ ", "████"],
    "2": ["████", "   █", "████", "█   ", "████"],
    "3": ["████", "   █", "████", "   █", "████"],
    "4": ["█  █", "█  █", "████", "   █", "   █"],
    "5": ["████", "█   ", "████", "   █", "████"],
    "6": ["████", "█   ", "████", "█  █", "████"],
    "7": ["████", "   █", "   █", "   █", "   █"],
    "8": ["████", "█  █", "████", "█  █", "████"],
    "9": ["████", "█  █", "████", "   █", "████"],
    "%": ["█  █", "   █", "  █ ", " █  ", "█  █"],
}


# ---------------------------------------------------------------------------
# mobiliario
# ---------------------------------------------------------------------------
def _titulo_que_cabe(titulo: str, hueco: int) -> str:
    """Título espaciado si cabe; si no, apretado; si tampoco, recortado."""
    espaciado = " ".join(titulo)
    if len(espaciado) <= hueco:
        return espaciado
    return titulo[:hueco]


def cabecera(c: Lienzo, x: int, y: int, ancho: int, placa: str, titulo: str) -> None:
    """Tira de cabecera de la pieza: dos filetes y el título entre ellos.

    El filete superior sobresale una columna y acaba en `╲`; el inferior en `╱`.
    Es la forma que más identifica la referencia, así que se copia tal cual.
    """
    c.texto(x, y, "┌" + "─" * (ancho - 1) + "╲", "borde")
    c.texto(x, y + 1, "│", "borde")
    c.texto(x + ancho - 2, y + 1, "│", "borde")
    c.texto(x, y + 2, "└" + "─" * (ancho - 1) + "╱", "borde")
    c.texto(x + 2, y + 1, f"[{placa}]", "cian")
    titulo = _titulo_que_cabe(titulo, ancho - 12)
    c.texto(x + 8, y + 1, titulo, "cian")


def cuerpo(c: Lienzo, x: int, y: int, ancho: int, alto: int) -> None:
    """Cuerpo del panel, también con las esquinas achaflanadas y sus cuñas."""
    c.texto(x, y, "┌" + "─" * (ancho - 1) + "╲", "borde")
    for fila in range(y + 1, y + alto - 1):
        c.texto(x, fila, "│", "borde")
        c.texto(x + ancho - 2, fila, "│", "borde")
    c.texto(x, y + alto - 1, "└" + "─" * (ancho - 1) + "╱", "borde")
    c.texto(x + 1, y + 1, "◤", "cian")
    c.texto(x + ancho - 3, y + alto - 2, "◢", "cian")


def franjas(c: Lienzo, x: int, y: int, ancho: int, alto: int, estilo: str = "naranja") -> None:
    """Franjas de peligro a 45°: cada fila va desplazada una columna.

    Se llaman **antes** que el texto de su zona: el texto siempre gana, y la
    franja no se dibuja nunca detrás de una letra.
    """
    for fila in range(alto):
        for columna in range(fila % 3, ancho, 3):
            c.texto(x + columna, y + fila, "╱", estilo)


def hueco(c: Lienzo, x: int, y: int, ancho: int) -> None:
    """Abre un hueco limpio en una banda de franjas antes de escribir encima."""
    c.texto(x, y, " " * ancho, "")


def numero_grande(c: Lienzo, x: int, y: int, texto: str, estilo: str = "cian") -> None:
    for indice, ch in enumerate(texto):
        glifo = GRANDES.get(ch)
        if glifo is None:
            continue
        for fila, linea in enumerate(glifo):
            c.texto(x + indice * 5, y + fila, linea, estilo)


def deslizador(c: Lienzo, x: int, y: int, ancho: int, valor: float) -> None:
    """Raíl fino con topes y mango cuadrado, como los de la pieza."""
    posicion = min(ancho - 1, max(0, round(valor * (ancho - 1))))
    c.texto(x, y, "╞" + "╌" * ancho + "╡", "trazo")
    c.texto(x + 1 + posicion, y, "◆", "cian")


def barra_superior(c: Lienzo, izquierda: str, derecha: str) -> None:
    """Fila 0: la tira de contexto que la pieza lleva sobre los paneles."""
    c.texto(2, 0, izquierda, "teal")
    c.texto(ANCHO - len(derecha) - 2, 0, derecha, "gris")


def pie(c: Lienzo, teclas: list[tuple[str, str]]) -> None:
    x = 2
    for tecla, accion in teclas:
        c.texto(x, 28, f"[{tecla}]", "cian")
        c.texto(x + len(tecla) + 2, 28, accion + "  ", "gris")
        x += len(tecla) + len(accion) + 5


# ---------------------------------------------------------------------------
# 01 · ENERGÍA
# ---------------------------------------------------------------------------
def pantalla_energia(c: Lienzo) -> None:
    barra_superior(c, "22:31:04", "SCAN 03 · CANAL RED 18 %")
    cabecera(c, 0, 1, 54, "00", "ENERGY REACTOR")
    cuerpo(c, 0, 4, 54, 16)

    c.texto(3, 6, "LAST SCAN RESULTS:", "naranja")
    for indice, (codigo, texto, color) in enumerate((
            ("000.002.235", "NO ERRORS FOUND", "teal"),
            ("000.002.552", "NO ERRORS FOUND", "teal"),
            ("000.005.156", "NO CRITICAL", "teal"),
            ("", "ERRORS WERE FOUND", "naranja"))):
        c.texto(3, 7 + indice, codigo, "teal")
        c.texto(16, 7 + indice, texto, color)
    c.texto(3, 11, "REPORTING BUG FIXED", "gris")

    franjas(c, 32, 15, 14, 3, "trazo")
    numero_grande(c, 3, 13, "95", "cian")
    c.texto(13, 17, "%", "cian")
    c.texto(18, 14, "REACTOR", "gris")
    c.texto(18, 15, "NOMINAL", "teal")

    cabecera(c, 58, 1, 42, "01", "REACTOR CORE")
    cuerpo(c, 58, 4, 42, 16)
    for indice, (etiqueta, valor, color) in enumerate((
            ("TEMPERATURE", "1 842 K", "pico"),
            ("PRESSURE", "22.4 BAR", "pico"),
            ("COOLANT", "38 %", "teal"),
            ("STATE", "CRITICAL", "rojo"))):
        c.texto(61, 6 + indice * 3, etiqueta, "gris")
        c.texto(61, 7 + indice * 3, valor, color)
    c.texto(61, 16, "███·············", "cian")

    # banda inferior de error, con franjas solo en los extremos
    franjas(c, 0, 21, 12, 4, "naranja")
    franjas(c, 88, 21, 12, 4, "naranja")
    c.texto(14, 22, "ERROR", "rojo")
    c.texto(20, 22, "000.005.156 · CRITICAL", "naranja")
    c.texto(14, 23, "REPORTING BUG FIXED", "teal")
    c.texto(14, 24, "CHANNEL RED EN 18 % · PURGA EN CURSO", "gris")

    c.texto(2, 26, "REACTOR", "gris")
    deslizador(c, 11, 26, 26, 0.95)
    c.texto(40, 26, "95 %", "cian")
    c.texto(51, 26, "FLUX", "gris")
    deslizador(c, 57, 26, 26, 0.62)
    c.texto(86, 26, "62 %", "cian")
    pie(c, [("TAB", "panel"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 02 · MEMORIA
# ---------------------------------------------------------------------------
def pantalla_memoria(c: Lienzo) -> None:
    barra_superior(c, "ES.CS.251", "MEMORIA 62 % · LEYENDO")
    cabecera(c, 0, 1, 64, "00", "MEMORY CLASTERS")
    cuerpo(c, 0, 4, 64, 21)

    # lo que se está escribiendo, en naranja
    for fila, bloques in enumerate((
            ((4, 12), (18, 8), (28, 16)),
            ((4, 8), (14, 14), (30, 12)),
            ((4, 16), (22, 8), (32, 10)))):
        for x, ancho in bloques:
            c.texto(x, 6 + fila, "▓" * ancho, "naranja")

    # el volcado gris
    for fila, ancho in enumerate((42, 38, 40, 36, 42, 39, 41)):
        c.texto(4, 10 + fila, "▒" * ancho, "gris2")

    # lo que sí se lee
    for fila, ancho in enumerate((30, 34, 22)):
        c.texto(4, 18 + fila, "█" * ancho, "pico")
    c.texto(4, 22, "MEMORIA LIBRE · 4 512 B", "teal")

    # regla de marcas: en la pieza va girada 90°; aquí no se puede girar texto
    for indice, marca in enumerate(("22", "65", "45")):
        fila = 5 + indice * 6
        c.texto(68, fila, marca, "gris")
        for paso in range(1, 6):
            c.texto(71, fila + paso, "┊", "trazo")
        c.texto(71, fila, "╵", "trazo")

    cabecera(c, 74, 1, 26, "03", "SCAN")
    cuerpo(c, 74, 4, 26, 21)
    for indice, (etiqueta, valor, color) in enumerate((("SF0", "5469.5489", "teal"),
                                                       ("S0B", "9875.2635", "teal"),
                                                       ("S0D", "0000.0000", "rojo"),
                                                       ("S0D", "9056.6321", "teal"),
                                                       ("SC0", "6523.2365", "teal"))):
        fila = 6 + indice * 3
        c.texto(77, fila, etiqueta, "cian")
        c.texto(81, fila, valor, color)
        c.texto(95, fila, "■", "trazo")
    pie(c, [("TAB", "panel"), ("R", "releer"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 03 · UNIDADES
# ---------------------------------------------------------------------------
def pantalla_unidades(c: Lienzo) -> None:
    cabecera(c, 0, 1, 100, "00", "ES.CS.251")
    barra_superior(c, "22:31:04", "ES.CS.251 · 3 DE 4")
    c.texto(2, 5, "UNIDADES CONECTADAS · 3 DE 4", "gris")
    c.texto(2, 6, "LA CUARTA NO RESPONDE DESDE 22:31:04", "naranja")

    tarjetas = [("SF0", "5469.5489.1234", 4, "cian"), ("S0B", "9875.2635.2663", 33, "pico"),
                ("S0D", "0000.0000.0002", 62, "rojo")]
    for nombre, serie, x, color in tarjetas:
        c.texto(x, 7, "┌──────────────┐", "borde")
        for fila in range(1, 5):
            c.texto(x, 7 + fila, "│              │", "borde")
        c.texto(x, 12, "└──────────────┘", "borde")
        c.texto(x + 3, 9, nombre, color)
        c.texto(x + 3, 10, "◤" * 10, "trazo")
        c.texto(x, 13, serie, "teal")

    for indice in range(5):
        fila = 6 + indice * 2
        c.texto(88, fila, "━", "trazo")
        c.texto(90, fila, "■", "cian" if indice % 3 else "rojo")
        c.texto(92, fila, "5469.54", "teal")

    cabecera(c, 0, 16, 100, "01", "REGISTRO DE UNIDADES")
    cuerpo(c, 0, 19, 100, 9)
    for indice, (nombre, serie, estado, color) in enumerate((
            ("SF0", "5469.5489.1234", "LINK", "cian"),
            ("S0B", "9875.2635.2663", "LINK", "pico"),
            ("S0D", "0000.0000.0002", "NO LINK", "rojo"))):
        fila = 21 + indice * 2
        c.texto(3, fila, nombre, color)
        c.texto(8, fila, serie, "teal")
        c.texto(30, fila, estado, color)
        c.texto(40, fila, "◤" * 14, "trazo")
        c.texto(58, fila, ("100 %" if estado == "LINK" else "00 %").rjust(6), "teal")
        c.texto(68, fila, "22:31:04" if estado == "LINK" else "—", "gris")
    pie(c, [("↑↓", "unidad"), ("⏎", "reconectar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 04 · MOTORES
# ---------------------------------------------------------------------------
def triangulo(c: Lienzo, x: int, y: int, color: str) -> None:
    """Triángulo de aviso con las mismas diagonales que las esquinas del panel."""
    c.texto(x + 4, y, "╱╲", color)
    c.texto(x + 3, y + 1, "╱  ╲", color)
    c.texto(x + 2, y + 2, "╱    ╲", color)
    c.texto(x + 1, y + 3, "╱      ╲", color)
    c.texto(x, y + 4, "╱────────╲", color)


def pantalla_motores(c: Lienzo) -> None:
    barra_superior(c, "22:31:04", "ENGINE LIST · 4 UNIDADES")
    cabecera(c, 0, 1, 100, "00", "ENGINE LIST")
    c.texto(2, 5, "CUATRO MOTORES · DOS EN MARCHA", "gris")

    motores = [(14, "22", "ENGINE 1", "LOADING", "cian"),
               (38, "93", "ENGINE 2", "WORKING", "pico"),
               (62, "00", "ENGINE 3", "ERROR", "naranja"),
               (86, "100", "ENGINE 4", "WAITING", "gris")]
    for x, numero, nombre, estado, color in motores:
        triangulo(c, x, 7, color)
        c.texto(x + 5 - len(numero) // 2, 10, numero, color)
        c.texto(x + 5 - len(nombre) // 2, 13, nombre, color)
        c.texto(x + 5 - len(estado) // 2, 14, estado, color)

    cabecera(c, 0, 16, 100, "01", "LÍNEAS DE CARGA")
    cuerpo(c, 0, 19, 100, 8)
    c.texto(3, 20, "ENGINE 3 SIN TENSIÓN · L3 A CERO", "naranja")
    for indice, (etiqueta, valor) in enumerate((("L1", 0.90), ("L2", 0.55), ("L3", 0.00))):
        fila = 22 + indice
        c.texto(3, fila, etiqueta, "gris")
        deslizador(c, 7, fila, 74, valor)
        c.texto(84, fila, f"{int(valor * 100):3d} %", "cian" if valor else "gris")
    pie(c, [("↑↓", "motor"), ("⏎", "reiniciar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 05 · CÓDIGO
# ---------------------------------------------------------------------------
def pantalla_codigo(c: Lienzo) -> None:
    barra_superior(c, "22:31:05", "VOLCADO · CANAL 0")
    cabecera(c, 0, 1, 62, "00", "6215.0.50FUDG")
    cuerpo(c, 0, 4, 62, 21)

    lineas = [("656923///", "cian"), ("//26541.6542DF5.64425", "teal"),
              ("265.//50DFCU255.269.2", "teal"), ("26H.C//F50.2364.50F.3.3", "teal"),
              ("45652.2326//5.36H.564", "teal"), ("23.266542.52352.265", "teal"),
              ("654///", "teal"), ("646542.2236", "teal"), ("26.///", "teal"),
              ("5694///", "teal")]
    for indice, (texto, color) in enumerate(lineas):
        c.texto(3, 6 + indice, texto, color)
    c.texto(3, 17, "◤◤◤◤◤◤◤◤◤◤◤◤◤◤", "trazo")
    c.texto(3, 18, "FIN DEL VOLCADO · 6 542 BYTES", "gris")
    for indice, (x, valor) in enumerate(((3, 0.35), (33, 0.70))):
        deslizador(c, x, 21, 26, valor)
    c.texto(3, 23, "SECTOR 6215 · CANAL 0 · FASE 50", "teal")

    cabecera(c, 66, 1, 34, "01", "265.//S0FF")
    cuerpo(c, 66, 4, 34, 21)
    for indice, texto in enumerate(("CU255.269.2", "656923///", "//26541.654",
                                    "20F5.64425", "45652.2326", "//5.36H.564",
                                    "23.266542.2", "65662.265", "546///", "26H.C//F50")):
        c.texto(69, 6 + indice, texto, "teal")
    c.texto(69, 18, "◤◤◤◤◤◤◤◤◤◤", "trazo")
    deslizador(c, 69, 21, 24, 0.55)
    c.texto(69, 23, "ESPEJO DEL CANAL", "gris")
    pie(c, [("↑↓", "línea"), ("C", "copiar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 06 · ERROR
# ---------------------------------------------------------------------------
def pantalla_error(c: Lienzo) -> None:
    franjas(c, 0, 0, 100, 3, "naranja")
    franjas(c, 0, 27, 100, 3, "naranja")
    hueco(c, 1, 1, 22)
    hueco(c, 76, 1, 22)
    c.texto(2, 1, "ERROR DE REACTOR", "rojo")
    c.texto(77, 1, "CHANNEL RED", "rojo")

    numero_grande(c, 5, 5, "156", "rojo")
    c.texto(22, 6, "CODIGO", "gris")
    c.texto(22, 7, "CRITICO", "naranja")
    c.texto(5, 12, "000.005.156", "rojo")
    c.texto(5, 13, "NO CRITICAL ERRORS WERE FOUND", "teal")
    c.texto(5, 14, "REPORTING BUG FIXED", "teal")

    for fila in range(3):
        for columna in range(6):
            x, y = 54 + columna * 7, 5 + fila * 4
            caido = (fila, columna) == (1, 4)
            color = "rojo" if caido else "trazo"
            c.texto(x, y, "┌────┐", color)
            c.texto(x, y + 1, "│    │", color)
            c.texto(x, y + 2, "└────┘", color)
            c.texto(x + 2, y + 1, "XX" if caido else "00", color)
    c.texto(54, 18, "18 NODOS · 1 CAIDO", "gris")

    c.texto(5, 20, "ACCIONES", "gris")
    c.texto(5, 21, "[R] REINICIAR REACTOR", "cian")
    c.texto(5, 22, "[P] PURGAR CANAL ROJO", "cian")
    c.texto(5, 23, "[S] APAGAR SISTEMA", "naranja")
    deslizador(c, 34, 21, 46, 0.18)
    c.texto(34, 22, "PURGA 18 %", "rojo")
    deslizador(c, 34, 24, 46, 0.95)
    c.texto(34, 25, "ENERGIA 95 %", "cian")



# ---------------------------------------------------------------------------
# versión ASCII de 7 bits
# ---------------------------------------------------------------------------
#: El set usa 29 caracteres que no son ASCII. Esta es la traducción, con el
#: criterio de conservar la silueta: las esquinas pasan a `.` y `'` para que se
#: distingan arriba y abajo, el chaflán se queda en `/` y `\`, y los rellenos se
#: escalonan en `#` `%` `:` para no perder los tres niveles de gris.
TABLA_ASCII = {
    "─": "-", "━": "=", "│": "|", "┊": ":", "╌": "-",
    "┌": ".", "┐": ".", "└": "'", "┘": "'",
    "╱": "/", "╲": "\\", "╵": "|", "╞": "|", "╡": "|",
    "█": "#", "▓": "%", "▒": ":", "░": ".", "■": "#",
    "◆": "o", "◤": "/", "◢": "\\",
    "Í": "I", "Ó": "O", "í": "i", "ó": "o", "á": "a", "é": "e", "ú": "u",
    "Á": "A", "É": "E", "Ú": "U", "Ñ": "N", "ñ": "n", "º": "o", "ª": "a",
    "—": "-", "·": "-", "¿": "?", "¡": "!",
    "↑": "^", "↓": "v", "⏎": ">",
}


def a_ascii(lienzo: Lienzo) -> Lienzo:
    """Copia el lienzo cambiando cada glifo por su equivalente de 7 bits."""
    salida = Lienzo(lienzo.ancho, lienzo.alto)
    for fila in range(lienzo.alto):
        for columna in range(lienzo.ancho):
            origen = lienzo.rejilla[fila][columna]
            destino = salida.rejilla[fila][columna]
            destino.char = TABLA_ASCII.get(origen.char, origen.char)
            destino.estilo = origen.estilo
    return salida


def faltantes_ascii(pantallas) -> list[str]:
    """Glifos que se quedarían fuera de 7 bits: tiene que estar vacío."""
    fuera = set()
    for _, _, _, lienzo in pantallas:
        for fila in lienzo.rejilla:
            for celda in fila:
                if ord(celda.char) > 127:
                    fuera.add(celda.char)
    return sorted(fuera)


PANTALLAS = [
    ("01", "Energía", "El panel principal de la pieza: la cabecera achaflanada con su "
     "placa `[00]`, el registro del escaneo en teal con la cita en naranja, el `95%` "
     "gigante de la fuente de bloques y el error en rojo con sus franjas de peligro.",
     pantalla_energia),
    ("02", "Memoria", "El volcado de memoria: el bloque naranja arriba, las barras grises "
     "del volcado y el bloque pálido de lo que sí se lee. A la derecha, la regla de "
     "marcas; en la pieza va girada 90° y aquí no se puede girar el texto.", pantalla_memoria),
    ("03", "Unidades", "Las tarjetas de unidades con su número de serie y, debajo, la "
     "tabla de enlaces. Una unidad caída en rojo: el color clasifica, no decora.",
     pantalla_unidades),
    ("04", "Motores", "Los cuatro triángulos de aviso, uno por estado —cargando, en "
     "marcha, error y en espera— y las tres líneas de carga con sus raíles.",
     pantalla_motores),
    ("05", "Código", "El volcado de código en dos paneles, teal sobre fondo, con los "
     "raíles y el identificador del sector. Es la pantalla más callada del set y sirve "
     "para ver cuánto aguanta el ojo sin color.", pantalla_codigo),
    ("06", "Error", "Pantalla completa de fallo, construida solo con el vocabulario de "
     "la pieza: franjas de peligro, número gigante, rejilla de nodos con el caído en "
     "rojo y los raíles de purga.", pantalla_error),
]


# ---------------------------------------------------------------------------
# salida
# ---------------------------------------------------------------------------
def construir() -> list[tuple[str, str, str, Lienzo]]:
    salida = []
    for numero, nombre, nota, funcion in PANTALLAS:
        lienzo = Lienzo(ANCHO, ALTO)
        funcion(lienzo)
        salida.append((numero, nombre, nota, lienzo))
    return salida


def spans(fila) -> str:
    trozos, actual, buffer = [], None, ""
    for celda in fila:
        if celda.estilo != actual:
            if buffer:
                texto = html.escape(buffer)
                trozos.append(f'<span class="c-{actual}">{texto}</span>' if actual else texto)
            actual, buffer = celda.estilo, celda.char
        else:
            buffer += celda.char
    if buffer:
        texto = html.escape(buffer)
        trozos.append(f'<span class="c-{actual}">{texto}</span>' if actual else texto)
    return "".join(trozos)


def marcas(texto: str) -> str:
    trozos = texto.split("`")
    return "".join(f"<code>{html.escape(t)}</code>" if i % 2 else html.escape(t)
                   for i, t in enumerate(trozos))


CSS = """
:root{--fondo:#090d18;--malla:#0d2a33;--trazo:#11565e;--borde:#14898b;--cian:#1ad3d6;
 --pico:#90f4ec;--teal:#25a39f;--naranja:#f76c0a;--rojo:#f00001;--gris:#424345;
 --gris2:#3d4547;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
/* un solo canal: se ve cuánto del diseño era información y cuánto color */
html[data-pal="cian"]{--naranja:#1ad3d6;--rojo:#1ad3d6;--gris:#11565e;--gris2:#11565e;
 --pico:#90f4ec;--teal:#25a39f}
*{box-sizing:border-box}
body{margin:0;background:#060810;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:36px 0 24px;border-bottom:1px solid #13202c;margin-bottom:28px}
h1{margin:0 0 8px;font-size:27px;letter-spacing:-.02em}
h1 span{color:var(--cian);font-family:var(--mono)}
.sub{color:#7d8996;font-size:15px;line-height:1.68;margin:0;max-width:82ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#7d8996;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#0c141d;color:#c9d1d9;border:1px solid #1e303d;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 46px}
.head{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:var(--cian);border:1px solid #1e303d;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#7d8996;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:92ch}
.nota code{font-family:var(--mono);background:#0c141d;border:1px solid #1a2833;border-radius:4px;padding:0 4px;color:#7fd8da}
.term{background:var(--fondo);border-radius:8px;padding:12px 14px;overflow-x:auto;
 box-shadow:0 0 0 1px #12222c, 0 26px 60px -34px #000;position:relative}
.term pre{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.28;white-space:pre;
 color:var(--teal);position:relative;z-index:1}
.c-malla{color:var(--malla)}
.c-trazo{color:var(--trazo)}
.c-borde{color:var(--borde)}
.c-cian{color:var(--cian)}
.c-pico{color:var(--pico)}
.c-teal{color:var(--teal)}
.c-naranja{color:var(--naranja)}
.c-rojo{color:var(--rojo)}
.c-gris{color:var(--gris)}
.c-gris2{color:var(--gris2)}
/* la rejilla de fondo: solo en los huecos, nunca detrás de una letra */
html[data-malla="1"] .term::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:0;
 background-image:linear-gradient(to right,rgba(26,211,214,.10) 1px,transparent 1px),
 linear-gradient(to bottom,rgba(26,211,214,.07) 1px,transparent 1px);
 background-size:calc(100%/50) 100%, 100% 38px}
footer{color:#7d8996;font-size:13.5px;line-height:1.75;border-top:1px solid #13202c;padding-top:20px}
footer code{font-family:var(--mono);background:#0c141d;border:1px solid #1a2833;border-radius:4px;padding:1px 5px;color:#a9b6c9}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #13202c;vertical-align:top}
th{color:#7d8996;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:#d8e2e6;font-size:12.5px}
.swatch{display:inline-block;width:13px;height:13px;border-radius:3px;vertical-align:-2px;margin-right:7px;box-shadow:0 0 0 1px #ffffff18}
.aviso{background:#0b1420;border-left:3px solid var(--cian);padding:13px 16px;border-radius:0 7px 7px 0;
 color:#96a4b2;font-size:13.5px;line-height:1.68;margin-top:16px}
"""

JS = """
const pal=document.getElementById('pal'),malla=document.getElementById('malla');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
malla.addEventListener('change',e=>document.documentElement.dataset.malla=e.target.checked?'1':'0');
"""


def construir_html(pantallas, ascii_: bool = False) -> str:
    secciones = []
    for numero, nombre, nota, lienzo in pantallas:
        filas = "\n".join(spans(fila) for fila in lienzo.rejilla)
        secciones.append(f"""
<section>
  <div class="head"><span class="num">{numero}</span><h2>{html.escape(nombre)}</h2></div>
  <p class="nota">{marcas(nota)}</p>
  <div class="term"><pre>{filas}</pre></div>
</section>""")

    filas_color = ""
    for clave, nombre, uso, origen in (
            ("fondo", "fondo", "vacío del panel", "medido"),
            ("malla", "malla", "retícula de fondo", "derivado"),
            ("trazo", "trazo", "filetes y franjas apagadas", "derivado"),
            ("borde", "borde", "contorno de panel", "medido"),
            ("cian", "cian", "títulos y elementos activos", "medido"),
            ("pico", "cian pálido", "bloques legibles", "medido"),
            ("teal", "teal", "cuerpo de texto y código", "medido"),
            ("naranja", "naranja", "atención y franjas", "medido"),
            ("rojo", "rojo", "error y canal rojo", "medido"),
            ("gris", "gris", "en espera", "medido"),
            ("gris2", "gris azulado", "barras del volcado", "medido")):
        filas_color += (f'<tr><td><span class="swatch" style="background:{REACTOR[clave]}"></span>'
                        f'<code>{REACTOR[clave]}</code></td><td>{nombre}</td><td>{uso}</td>'
                        f'<td>{origen}</td></tr>')

    if ascii_:
        titulo = "REACTOR · versión ASCII de 7 bits"
        entrada = """  <p class="sub">La misma serie, dibujada <strong>solo con caracteres ASCII de
  7 bits</strong>: sin un solo glifo de dibujo de cajas, sin bloques y sin acentos.
  Esto es lo que se ve en un terminal de hace treinta años, en una consola de serie, en
  un `less` o en una fuente que no tiene ni una línea Unicode. El .txt que acompaña a
  esta página no lleva <em>ningún</em> código de escape: se puede imprimir tal cual.</p>"""
        extra = """  <div class="aviso"><strong>Lo que se pierde al bajar a 7 bits.</strong> Las esquinas
  pasan a <code>.</code> y <code>'</code> para distinguir arriba de abajo; el chaflán se
  queda en <code>/</code> y <code>\\</code>, que es lo único que aún se parece al
  original. Los rellenos bajan de tres niveles a tres glifos: <code># % :</code>. Los
  acentos desaparecen —<code>ENERGÍA</code> pasa a <code>ENERGIA</code>— y las teclas
  <code>↑ ↓ ⏎</code> pasan a <code>^ v &gt;</code>.</div>
  <div class="aviso"><strong>El color sobrevive; el glifo no.</strong> En esta página los
  puntos siguen teniendo su color medido, porque el color va por celda y no depende del
  carácter. En el .txt, en cambio, no hay color en absoluto: ahí manda el texto. Es la
  prueba de fuego de cualquier interfaz de este estilo — si al quitarle el color y los
  glifos sigue diciendo lo mismo, el diseño estaba en la información y no en el adorno.</div>"""
    else:
        titulo = "REACTOR · TUI de interfaz sci-fi"
        entrada = """  <p class="sub">Seis pantallas en <strong>100 × 30 celdas</strong> construidas sobre una
  pieza de interfaz sci-fi que dio el usuario. La paleta está <strong>medida</strong> sobre
  esa imagen y lo primero que salió al medirla es que <em>no tiene blanco</em>: son tres
  canales —cian, naranja, rojo— y un gris neutro. El color no adorna, clasifica.</p>"""
        extra = ""
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="medido" data-malla="0">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>REACTOR <span>· {'versión ASCII de 7 bits' if ascii_ else 'TUI de interfaz sci-fi'}</span></h1>
{entrada}
  <div class="controls">
    <label>Paleta <select id="pal">
      <option value="medido">Medida</option>
      <option value="cian">Un solo canal</option>
    </select></label>
    <label><input type="checkbox" id="malla"> rejilla de fondo (no es del TUI)</label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>El color, medido · y lo que no se copia</h2></div>
  <p class="nota">Nueve de los once valores salen de filtrar píxeles por tono en la
  imagen de referencia. Los otros dos —la malla del fondo y el trazo de los filetes—
  son <em>derivados</em>: en la pieza son tan finos que la medición devuelve casi negro,
  así que se reconstruyen a partir de los bordes medidos. Van marcados.</p>
  <table>
    <tr><th>Color</th><th>Nombre</th><th>Uso</th><th>Origen</th></tr>
    {filas_color}
  </table>
  <div class="aviso"><strong>La separación de canales no se puede pintar.</strong> En la
  pieza cada letra lleva una copia roja desplazada un píxel y otra cian, el glitch de
  las tres capas. En una terminal el color es de la celda: no hay dos colores en el mismo
  carácter. Lo que sí se copia es el <em>efecto</em> a otra escala: el rojo aparece como
  acento suelto y las franjas de peligro hacen de textura.</div>
  <div class="aviso"><strong>El texto girado 90° tampoco.</strong> La regla de marcas
  (22 / 65 / 45) va vertical en la pieza; aquí no se puede rotar texto, así que los
  números van horizontales junto a la regla y se dice.</div>
  <div class="aviso"><strong>La tipografía de píxeles.</strong> La pieza usa una fuente
  de bloques real. Aquí los títulos van espaciados —que es lo que hace ella— y solo los
  números grandes usan una fuente de bloques de 4 × 5 dibujada a mano. El resto es texto
  de terminal.</div>
{extra}
</section>
<footer>
  Generado por <code>reactor/reactor.py</code> · motor de celdas en
  <code>mockups/celdas.py</code> · solo biblioteca estándar.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


def _rgb(hexa: str) -> str:
    return f"{int(hexa[1:3], 16)};{int(hexa[3:5], 16)};{int(hexa[5:7], 16)}"


ANSI = {clave: f"\x1b[38;2;{_rgb(valor)};48;2;{_rgb(REACTOR['fondo'])}m"
        for clave, valor in REACTOR.items()}
RESET = "\x1b[0m"


def pintar(lienzo: Lienzo) -> str:
    salida = []
    for fila in lienzo.rejilla:
        actual, buffer = None, ""
        for celda in fila:
            if celda.estilo != actual:
                if buffer:
                    salida.append(f"{ANSI.get(actual, '')}{buffer}{RESET}")
                actual, buffer = celda.estilo, celda.char
            else:
                buffer += celda.char
        if buffer:
            salida.append(f"{ANSI.get(actual, '')}{buffer}{RESET}")
        salida.append("\n")
    return "".join(salida)


def main(argv: list[str]) -> int:
    pantallas = construir()
    problemas = [(num, p) for num, _, _, lienzo in pantallas for p in lienzo.comprobar()]
    if problemas:
        for numero, problema in problemas[:25]:
            print(f"[{numero}] {problema}", file=sys.stderr)
        return 1

    if "--ansi" in argv:
        for _, nombre, _, lienzo in pantallas:
            print(f"\n── {nombre} " + "─" * (ANCHO - len(nombre) - 4))
            sys.stdout.write(pintar(lienzo))
        return 0

    destino = Path(__file__).resolve().parent

    if "--ascii" in argv:
        simples = [(n, nom, nota, a_ascii(lienzo)) for n, nom, nota, lienzo in pantallas]
        fuera = faltantes_ascii(simples)
        if fuera:
            print(f"quedan glifos fuera de 7 bits: {fuera}", file=sys.stderr)
            return 1
        (destino / "reactor-ascii.html").write_text(
            construir_html(simples, ascii_=True), encoding="utf-8")
        with open(destino / "reactor-ascii.txt", "w", encoding="utf-8") as fh:
            for numero, nombre, _, lienzo in simples:
                titulo = "".join(TABLA_ASCII.get(c, c) for c in nombre)
                fh.write(f"\n=== {numero} - {titulo} " + "=" * (ANCHO - len(titulo) - 10) + "\n")
                fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
        texto = (destino / "reactor-ascii.txt").read_text(encoding="utf-8")
        escapes = texto.count("\x1b")
        print(f"{len(simples)} pantallas · ASCII de 7 bits · "
              f"carácter más alto {max(ord(c) for c in texto)} · "
              f"{escapes} códigos de escape → reactor-ascii.html y reactor-ascii.txt")
        return 0

    with open(destino / "reactor.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 10) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    anchos = {len(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · máx. {max(anchos)} columnas · "
          f"0 de doble ancho → reactor.html y reactor.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
