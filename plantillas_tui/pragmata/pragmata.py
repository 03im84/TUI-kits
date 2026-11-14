#!/usr/bin/env python3
"""Mockups de una TUI tipo Pragmata (Capcom): HUD de cristal y color funcional.

Paleta **medida** sobre dos capturas reales del juego (HUD de combate con la
rejilla de Diana y menu Unit Printer). Los valores son picos de brillo de pixeles
filtrados por tono: al ser JPEG con cristal translucido, el relleno plano real es
algo mas apagado que el numero.

    fondo        #0b151d     linea        #2e596b
    cian         #4d9ec4     pico cian    #94defb
    blanco       #d9efff     gris         #7a8ea1
    verde EXE    #69b66e     amarillo     #e2d922
    ambar        #f3b248     naranja      #e9983f
    rojo dano    #d54d59     morado       #856ad1

A diferencia de las series de fosforo (cyberpunk, Minority, juego, Pip-Boy), aqui
el color **hace un trabajo**: verde es el nodo meta, amarillo la habilidad elegida,
rojo el dano, morado lo raro. Por eso el HTML trae una paleta para deuteranopia
que cambia el par verde/rojo por cian/ambar.

Lenguaje visual traducido a celdas:

* **esquinas achaflanadas** `╱ ╲`: el cristal del HUD no tiene angulos rectos;
* **títulos espaciados** `T I T U L O` en blanco, sin caja;
* **rejilla de nodos**: retícula de puntos con el camino trazado encima;
* **llaves de mando** `[L1]` `[R1]`, numeros de dano flotando, contador `794 / 1000`.

    python3 pragmata/pragmata.py            # pragmata.html y pragmata.txt
    python3 pragmata/pragmata.py --ansi     # pinta las pantallas en tu terminal
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402

ANCHO, ALTO = 100, 30

#: Medidos sobre las capturas (ver docstring). ``velo`` es derivado, no medido.
PRAG = {
    "fondo": "#0b151d",
    "linea": "#2e596b",
    "cian": "#4d9ec4",
    "pico": "#94defb",
    "blanco": "#d9efff",
    "gris": "#7a8ea1",
    "verde": "#69b66e",
    "amarillo": "#e2d922",
    "ambar": "#f3b248",
    "naranja": "#e9983f",
    "rojo": "#d54d59",
    "morado": "#856ad1",
}


# ---------------------------------------------------------------------------
# mobiliario
# ---------------------------------------------------------------------------
def marco(c: Lienzo) -> None:
    """Filete de pantalla con las esquinas achaflanadas del HUD."""
    c.texto(0, 0, "╱" + "─" * (ANCHO - 2) + "╲", "linea")
    c.texto(0, ALTO - 1, "╲" + "─" * (ANCHO - 2) + "╱", "linea")


def cabecera(c: Lienzo, izquierda: str, derecha: str) -> None:
    c.texto(3, 1, izquierda, "blanco")
    c.texto(ANCHO - len(derecha) - 4, 1, derecha, "gris")
    c.texto(3, 2, "─" * (ANCHO - 6), "linea")


def panel(c: Lienzo, x: int, y: int, ancho: int, alto: int, titulo: str = "") -> None:
    """Panel de cristal: esquinas achaflanadas y lados de un solo trazo."""
    espaciado = " ".join(titulo.upper()) if titulo else ""
    c._paneles.append(c._registro(x, y, ancho, alto, espaciado,
                                  "╱", "╲", "╲", "╱", "─", "│"))
    c.texto(x, y, "╱" + "─" * (ancho - 2) + "╲", "linea")
    for fila in range(y + 1, y + alto - 1):
        c.texto(x, fila, "│", "linea")
        c.texto(x + ancho - 1, fila, "│", "linea")
    c.texto(x, y + alto - 1, "╲" + "─" * (ancho - 2) + "╱", "linea")
    if espaciado:
        c.texto(x + 2, y, f" {espaciado} ", "blanco")


def titulo(c: Lienzo, x: int, y: int, texto: str) -> None:
    c.texto(x, y, " ".join(texto.upper()), "blanco")


def barra(c: Lienzo, x: int, y: int, valor: float, ancho: int, estilo: str = "cian",
          vacio: str = "gris") -> None:
    llenos = round(max(0.0, min(1.0, valor)) * ancho)
    c.texto(x, y, "█" * llenos, estilo)
    c.texto(x + llenos, y, "·" * (ancho - llenos), vacio)


def llave(c: Lienzo, x: int, y: int, texto: str, estilo: str = "cian") -> int:
    """`[L1]` de mando. Devuelve la columna donde termina."""
    c.texto(x, y, texto, estilo)
    return x + len(texto)


def pie(c: Lienzo, teclas: list[tuple[str, str]]) -> None:
    x = 3
    for tecla, accion in teclas:
        x = llave(c, x, 28, f"[{tecla}]", "pico")
        c.texto(x, 28, accion + "   ", "gris")
        x += len(accion) + 3


def rejilla(c: Lienzo, x: int, y: int, cols: int, filas: int, paso_x: int = 5,
            paso_y: int = 2) -> list[tuple[int, int]]:
    """Retícula de puntos con sus aristas. Devuelve la posición de cada vértice.

    Es el dibujo nativo de Pragmata: el jugador traza un camino de nodo en nodo,
    así que la rejilla de caracteres no es una imitación, es el mismo objeto.
    """
    posiciones = []
    for j in range(filas):
        fila = y + j * paso_y
        for i in range(cols):
            columna = x + i * paso_x
            posiciones.append((columna, fila))
            if i < cols - 1:
                c.texto(columna + 1, fila, "─" * (paso_x - 1), "linea")
            c.texto(columna, fila, "·", "linea")
        if j < filas - 1:
            for i in range(cols):
                c.texto(x + i * paso_x, fila + 1, "│", "linea")
    return posiciones


def traza(c: Lienzo, vertices: list[tuple[int, int]], ruta: list[tuple[int, int]],
          estilo: str = "pico") -> None:
    """Dibuja el camino sobre la retícula, con esquinas donde dobla."""
    for (x0, y0), (x1, y1) in zip(ruta, ruta[1:]):
        if y0 == y1:
            for columna in range(min(x0, x1) + 1, max(x0, x1)):
                c.texto(columna, y0, "━", estilo)
        else:
            c.texto(x0, min(y0, y1) + 1, "┃", estilo)


# ---------------------------------------------------------------------------
# 01 · COMBATE
# ---------------------------------------------------------------------------
def pantalla_combate(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "COMBATE", "SECTOR 03 · LABORATORIO · 20.11.29")
    c.texto(3, 3, "[ DIANA ]  enlace 98 %", "blanco")
    c.texto(3, 4, "enlace estable · sin interferencia", "gris")
    c.texto(57, 3, "[ HUGH ]  traje 78 %", "blanco")
    c.texto(57, 4, "cargador 794 / 1000", "gris")

    panel(c, 3, 6, 48, 17, "enemigo")
    c.texto(6, 7, "SECTORGUARD · clase 4.2", "blanco")
    c.texto(6, 9, "ESCUDO", "gris")
    barra(c, 17, 9, 0.62, 22, "rojo", "linea")
    c.texto(41, 9, "62 %", "rojo")
    c.texto(6, 10, "INTEGRIDAD", "gris")
    barra(c, 17, 10, 1.00, 22, "verde", "linea")
    c.texto(41, 10, "100 %", "verde")
    c.texto(6, 12, "PUNTOS DÉBILES", "gris")
    c.texto(6, 13, "[ rodilla izq. ]  [ cuello ]", "cian")
    c.texto(6, 15, "el escudo anula el daño", "rojo")
    c.texto(6, 16, "rompe los emisores", "gris")
    c.texto(6, 18, "o hackea la rejilla", "gris")
    c.texto(40, 7, "114", "rojo")
    c.texto(42, 12, "87", "rojo")
    c.texto(40, 15, "114", "rojo")
    c.texto(38, 18, "152", "rojo")

    panel(c, 55, 6, 42, 17, "rejilla")
    vertices = rejilla(c, 58, 8, 6, 5, 6, 2)
    c.texto(vertices[1][0], vertices[1][1], "+", "cian")
    c.texto(vertices[2][0], vertices[2][1], "*", "amarillo")
    c.texto(vertices[3][0], vertices[3][1], "#", "rojo")
    c.texto(vertices[4][0], vertices[4][1], "%", "morado")
    meta = vertices[4 * 6 + 5]
    c.texto(meta[0], meta[1], "◉", "verde")
    c.texto(58, 19, "EXE · 6 nodos a la derecha", "gris")
    c.texto(58, 20, "escudo en la columna 4", "rojo")
    c.texto(58, 21, "hackeo", "gris")
    barra(c, 66, 21, 0.35, 24, "cian", "linea")

    c.texto(3, 24, "MUNICIÓN", "gris")
    c.texto(12, 24, "794 / 1000", "blanco")
    barra(c, 25, 24, 0.794, 24, "ambar", "linea")
    c.texto(53, 24, "GADGETS  3 / 6", "gris")
    c.texto(69, 24, "◉◉◉○○○", "ambar")
    pie(c, [("LT", "apuntar"), ("ABXY", "trazar"), ("B", "curar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 02 · HACKEO · la rejilla en grande
# ---------------------------------------------------------------------------
def pantalla_hackeo(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "HACKEO", "DIANA · REJILLA DE COMBATE")
    c.texto(3, 3, "nodo meta verde · bonificadores azules · escudo rojo", "gris")

    vertices = rejilla(c, 6, 6, 9, 8, 5, 2)
    cols = 9

    def v(i: int, j: int) -> tuple[int, int]:
        return vertices[j * cols + i]

    especiales = {
        (2, 1): ("+", "cian"), (4, 2): ("+", "cian"), (3, 4): ("+", "cian"),
        (6, 2): ("%", "morado"), (7, 5): ("*", "amarillo"),
        (5, 5): ("#", "rojo"), (4, 6): ("#", "rojo"), (7, 3): ("*", "amarillo"),
    }
    for (i, j), (glifo, estilo) in especiales.items():
        x, y = v(i, j)
        c.texto(x, y, glifo, estilo)

    ruta = [v(0, 0), v(1, 0), v(2, 0), v(2, 1), v(2, 2), v(2, 3), v(3, 3),
            v(4, 3), v(4, 4), v(4, 5), v(5, 5), v(6, 5), v(7, 5), v(8, 5),
            v(8, 6), v(8, 7)]
    traza(c, vertices, ruta)

    # el camino pasa por los nodos, no los borra: se vuelven a pintar encima
    por_posicion = {vertices[j * cols + i]: valor for (i, j), valor in especiales.items()}
    for x, y in ruta[1:-1]:
        glifo, estilo = por_posicion.get((x, y), ("·", "pico"))
        c.texto(x, y, glifo, estilo)
    c.texto(ruta[0][0], ruta[0][1], "◉", "pico")
    c.texto(ruta[-1][0], ruta[-1][1], "◉", "verde")

    panel(c, 55, 6, 42, 20, "lectura")
    c.texto(58, 8, "OBJETIVO", "gris")
    c.texto(58, 9, "SECTORGUARD 4.2", "blanco")
    c.texto(58, 11, "CAMINO", "gris")
    c.texto(58, 12, "16 nodos · 4 giros", "cian")
    c.texto(58, 14, "BONIFICADORES", "gris")
    c.texto(58, 15, "+ daño      × 2 alcanzado", "cian")
    c.texto(58, 16, "* habilidad  arco eléctrico", "amarillo")
    c.texto(58, 17, "% raro       no alcanzado", "morado")
    c.texto(58, 19, "OBSTÁCULO", "gris")
    c.texto(58, 20, "# escudo     2 celdas", "rojo")
    c.texto(58, 21, "una en el camino, una fuera", "gris")
    c.texto(58, 23, "MEDIDOR", "gris")
    barra(c, 67, 23, 0.68, 22, "cian", "linea")
    c.texto(90, 23, "68 %", "pico")

    c.texto(6, 22, "·", "linea")
    c.texto(8, 22, "nodo libre", "gris")
    c.texto(26, 22, "+", "cian")
    c.texto(28, 22, "daño × 2", "gris")
    c.texto(42, 22, "*", "amarillo")
    c.texto(44, 22, "habilidad", "gris")
    c.texto(6, 23, "#", "rojo")
    c.texto(8, 23, "escudo", "gris")
    c.texto(26, 23, "◉", "verde")
    c.texto(28, 23, "nodo EXE", "gris")
    pie(c, [("ABXY", "trazar"), ("LB", "auto-hackeo"), ("RT", "disparar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 03 · UNIT PRINTER
# ---------------------------------------------------------------------------
def pantalla_impresora(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "UNIT PRINTER", "LUNUM 5058 · LUNAFILAMENTO")
    c.texto(3, 3, "[L1]", "gris")
    c.texto(8, 3, "ARMAS", "gris")
    c.texto(15, 3, "HACKEO", "gris")
    c.texto(23, 3, "HABILIDADES", "inverso")
    c.texto(37, 3, "ACCESORIOS", "gris")
    c.texto(68, 3, "[R1]", "gris")

    tarjetas = [
        ("AUTO-HACKEO", "traza sola", "150", False),
        ("BOT SCAN", "marca débiles", "150", False),
        ("OBJECT SCAN", "resalta saqueo", "150", False),
        ("CRITICAL SHOT", "disparo × 3", "800", True),
        ("FAST MOVES", "esquiva barata", "COMPLETO", True),
        ("EC THRUSTERS", "planeo largo", "1", False),
    ]
    for indice, (nombre, descripcion, coste, hecha) in enumerate(tarjetas):
        columna = 3 + (indice % 2) * 30
        fila = 6 + (indice // 2) * 6
        panel(c, columna, fila, 28, 4, "")
        c.texto(columna + 2, fila + 1, nombre, "ambar" if indice == 3 else "blanco")
        c.texto(columna + 2, fila + 2, descripcion, "gris")
        c.texto(columna + 18, fila + 2, coste.rjust(8), "verde" if hecha else "ambar")

    panel(c, 65, 6, 32, 20, "detalle")
    c.texto(67, 8, "CRITICAL SHOT", "blanco")
    c.texto(67, 9, "nivel 1 · desbloqueada", "verde")
    c.texto(67, 11, "El primer disparo tras", "gris")
    c.texto(67, 12, "cada hackeo hace × 3", "gris")
    c.texto(67, 13, "de daño en el punto", "gris")
    c.texto(67, 14, "débil.", "gris")
    c.texto(67, 16, "Lv.1  desbloquea la", "cian")
    c.texto(67, 17, "      habilidad", "cian")
    c.texto(67, 18, "Lv.2  × 3 → × 3,5", "naranja")
    c.texto(67, 19, "Lv.3  × 3 → × 4", "naranja")
    c.texto(67, 21, "coste", "naranja")
    c.texto(75, 21, "800 lunum", "ambar")
    c.texto(67, 22, "tienes", "naranja")
    c.texto(75, 22, "5 058", "blanco")
    c.texto(67, 24, "[ A ] imprimir", "inverso")
    pie(c, [("←→", "pestaña"), ("↑↓", "objeto"), ("A", "imprimir"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 04 · DIANA
# ---------------------------------------------------------------------------
def busto() -> list[str]:
    """Silueta simétrica: cada fila es una anchura centrada en la columna 13, así
    que el dibujo no puede quedar torcido. La cara se pinta después, en
    coordenadas fijas, para que los ojos y la boca no se dupliquen con el espejo."""
    anchos = [7, 11, 15, 19, 21, 21, 19, 17, 11, 13, 17, 21, 25, 27, 27]
    filas = []
    for indice, ancho in enumerate(anchos):
        if indice == 0:
            relleno = "▄" * ancho
        elif indice >= 13:
            relleno = "▒" + "▓" * (ancho - 2) + "▒"
        else:
            relleno = "▓" * ancho
        filas.append(relleno.center(27))
    return filas


def pantalla_diana(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "DIANA", "ANDROIDE · LUNAFILAMENTO")
    c.texto(3, 3, "unidad tipo Pragmata · enlace con Hugh activo", "gris")

    for indice, fila in enumerate(busto()):
        for desplazamiento, ch in enumerate(fila):
            if ch != " ":
                c.texto(6 + desplazamiento, 6 + indice, ch, "cian")
    for x, y, ch in ((15, 9, "◉"), (23, 9, "◉"), (19, 10, "▿"), (19, 16, "◇")):
        c.texto(x, y, ch, "pico")
    c.texto(6, 22, "núcleo ◇ · se lee sin color", "gris")

    panel(c, 36, 5, 61, 21, "estado")
    c.texto(39, 7, "INTEGRIDAD DE LUNAFILAMENTO", "gris")
    barra(c, 39, 8, 0.91, 34, "verde", "linea")
    c.texto(75, 8, "91 %", "verde")
    c.texto(39, 10, "ENLACE CON HUGH", "gris")
    barra(c, 39, 11, 0.98, 34, "cian", "linea")
    c.texto(75, 11, "98 %", "pico")
    c.texto(39, 13, "BLOQUEO ENEMIGO", "gris")
    c.texto(39, 14, "ninguno", "gris")
    c.texto(39, 16, "MÓDULOS", "gris")
    c.texto(39, 17, "voz        ◉ activo", "blanco")
    c.texto(39, 18, "análisis   ◉ activo", "blanco")
    c.texto(39, 19, "proyección ○ en espera", "gris")
    c.texto(39, 21, "VOZ", "gris")
    c.texto(39, 22, "▁▂▅▇▅▂▁▃▆▇▆▃▁▂▄▆▄▂▁▃▅▇▅▃▁", "pico")
    c.texto(39, 23, "«ya casi llegamos, Hugh»", "blanco")
    pie(c, [("TAB", "módulo"), ("⏎", "activar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 05 · ESTACIÓN
# ---------------------------------------------------------------------------
def pantalla_estacion(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "ESTACIÓN", "BASE LUNAR · 20.11.29 · 04:12")
    c.texto(3, 3, "plano de módulos · el apagón viene del núcleo", "gris")

    panel(c, 3, 5, 62, 21, "plano")
    modulos = [(6, 7, 20, "[ S01 · LAB ]"), (32, 7, 27, "[ S02 · MANTENIMIENTO ]"),
               (6, 13, 20, "[ S03 · CELDAS ]"), (32, 13, 20, "[ S04 · NÚCLEO ]"),
               (6, 19, 20, "[ S05 · MUELLE ]"), (32, 19, 24, "[ S06 · EXTERIOR ]")]
    for x, y, ancho, texto in modulos:
        c.caja(x, y, ancho, 3, "", "linea")
        c.texto(x + 2, y + 1, texto, "cian")
    # conductos: un solo trazo por tramo, y siempre en la canaleta
    c.texto(28, 8, "──▶", "gris")
    c.texto(28, 14, "───", "linea")
    for x, filas in ((15, (10, 11, 12)), (42, (10, 11, 12)),
                     (15, (16, 17, 18)), (42, (16, 17, 18))):
        for fila in filas[:-1]:
            c.texto(x, fila, "│", "linea")
        c.texto(x, filas[-1], "▼", "gris")
    c.texto(6, 22, "◉ S04 sin tensión        ◄ S06 sin presión", "rojo")
    c.texto(6, 23, "04:10  caída de tensión en S04", "gris")
    c.texto(6, 24, "04:11  Diana detecta la firma de la IA", "blanco")

    panel(c, 68, 5, 29, 21, "lecturas")
    c.texto(71, 7, "OXÍGENO", "gris")
    barra(c, 71, 8, 0.72, 19, "cian", "linea")
    c.texto(71, 9, "72 % · 6 h 40 min", "blanco")
    c.texto(71, 11, "ENERGÍA", "gris")
    barra(c, 71, 12, 0.18, 19, "rojo", "linea")
    c.texto(71, 13, "18 % · reserva", "rojo")
    c.texto(71, 15, "GRAVEDAD", "gris")
    c.texto(71, 16, "0,16 g", "blanco")
    c.texto(71, 17, "exterior 0,16 g", "gris")
    c.texto(71, 19, "TEMPERATURA", "gris")
    c.texto(71, 20, "−18 °C  fuera", "blanco")
    c.texto(71, 22, "SECTOR", "gris")
    c.texto(71, 23, "S05 · sin presión", "rojo")
    pie(c, [("↑↓", "módulo"), ("M", "mapa"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 06 · TRAJE
# ---------------------------------------------------------------------------
def pantalla_traje(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "TRAJE", "HUGH WILLIAMS · INTEGRIDAD 78 %")
    c.texto(3, 3, "cuatro zonas · la energía se comparte entre esquivar y planear", "gris")

    panel(c, 3, 5, 52, 21, "zonas")
    zonas = [("CASCO", 0.96, "verde"), ("PECHO", 0.71, "ambar"), ("BRAZO DER.", 0.44, "rojo"),
             ("BRAZO IZQ.", 0.88, "verde"), ("PIERNA DER.", 0.66, "ambar"),
             ("PIERNA IZQ.", 0.83, "verde")]
    for indice, (nombre, valor, color) in enumerate(zonas):
        fila = 7 + indice * 3
        c.texto(6, fila, nombre, "gris")
        barra(c, 22, fila, valor, 22, color, "linea")
        c.texto(46, fila, f"{int(valor * 100)} %".rjust(3), "blanco")
        if valor < 0.5:
            c.texto(32, fila + 1, "◄ sangra", "rojo")
    c.texto(6, 24, "reparar con B · material 3 / 5", "gris")

    panel(c, 57, 5, 40, 6, "energía")
    c.texto(60, 6, "ESQUIVA · PLANEO", "gris")
    barra(c, 60, 7, 0.55, 32, "pico", "linea")
    c.texto(60, 8, "55 % · se recupera al estar quieto", "blanco")

    panel(c, 57, 12, 40, 14, "armas")
    armas = [("PISTOLA", "∞ recarga", True), ("ESCOPETA", "6 / 12", False),
             ("CAÑÓN DE RED", "2 / 4", False), ("BLASTER", "1 / 2", False)]
    for indice, (nombre, municion, activa) in enumerate(armas):
        fila = 14 + indice * 2
        if activa:
            c.texto(60, fila, "▸", "ambar")
        c.texto(62, fila, nombre, "ambar" if activa else "gris")
        c.texto(80, fila, municion.rjust(8), "blanco" if activa else "gris")
    c.texto(60, 23, "LB/RB cambia · 1 de 4", "gris")
    pie(c, [("LB/RB", "arma"), ("B", "reparar"), ("X", "recargar"), ("ESC", "salir")])


PANTALLAS = [
    ("01", "Combate", "El HUD de combate: el enemigo con su escudo, la rejilla de Diana "
     "en pequeño a la derecha y los números de daño flotando. El escudo explica por qué "
     "hay que hackear antes de disparar.", pantalla_combate),
    ("02", "Hackeo", "La rejilla en grande. Se traza el camino de nodo en nodo hasta el "
     "`◉` verde; los `+` azules suman daño, el `*` amarillo activa la habilidad y el `#` "
     "rojo es un escudo que hay que romper a tiros. Esta pantalla es el motivo por el que "
     "Pragmata cabe en una terminal: el juego ya es una cuadrícula.", pantalla_hackeo),
    ("03", "Unit Printer", "El menú de impresión de habilidades, con sus tarjetas, el "
     "coste en lunum y el panel de detalle con los niveles. Aquí el ámbar marca la "
     "selección y el verde lo ya desbloqueado.", pantalla_impresora),
    ("04", "Diana", "El androide de Lunafilamento en wireframe, con su integridad y el "
     "enlace con Hugh. El retrato está dibujado con `╱ ╲ │ ·` y nada más: sin colores "
     "añadidos, porque la silueta tiene que leerse en una terminal de un solo tono.",
     pantalla_diana),
    ("05", "Estación", "El plano de los seis módulos de la base lunar, con el apagón "
     "marcado en rojo sobre el núcleo y las lecturas de oxígeno, energía y gravedad.",
     pantalla_estacion),
    ("06", "Traje", "La integridad del traje de Hugh por zonas y el selector de las "
     "cuatro armas. La barra de energía es compartida entre esquivar y planear, que es "
     "la decisión de diseño del juego: moverse cuesta lo mismo que salvarse.",
     pantalla_traje),
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


CSS = """
:root{--fondo:#0b151d;--linea:#2e596b;--cian:#4d9ec4;--pico:#94defb;
 --blanco:#d9efff;--gris:#7a8ea1;--verde:#69b66e;--amarillo:#e2d922;--ambar:#f3b248;
 --naranja:#e9983f;--rojo:#d54d59;--morado:#856ad1;--inverso-fg:#0b151d;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
/* solo cian: demuestra que sin color funcional el HUD pierde información */
html[data-pal="cian"]{--verde:#94defb;--amarillo:#94defb;--ambar:#94defb;--rojo:#94defb;
 --morado:#94defb;--naranja:#94defb;--pico:#ffffff;--blanco:#d9efff}
/* deuteranopia: el par verde/rojo pasa a cian/ambar, que sí se distingue */
html[data-pal="deuteranopia"]{--verde:#5fd7e8;--rojo:#f3b248;--amarillo:#e2d922;
 --ambar:#e8ee8a}
*{box-sizing:border-box}
body{margin:0;background:#070d12;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:36px 0 24px;border-bottom:1px solid #14232e;margin-bottom:28px}
h1{margin:0 0 8px;font-size:27px;letter-spacing:-.02em}
h1 span{color:var(--pico);font-family:var(--mono)}
.sub{color:#7d8590;font-size:15px;line-height:1.68;margin:0;max-width:82ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#7d8590;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#0f1b24;color:#c9d1d9;border:1px solid #22333f;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 46px}
.head{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:var(--pico);border:1px solid #22333f;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#7d8590;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:92ch}
.nota code{font-family:var(--mono);background:#0f1b24;border:1px solid #1d2e39;border-radius:4px;padding:0 4px;color:#9fd0e0}
.term{background:var(--fondo);border-radius:10px;padding:12px 14px;overflow-x:auto;
 box-shadow:0 0 0 1px #1e3341, inset 0 0 60px #050a0e, 0 26px 60px -34px #000;position:relative}
.term pre{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.32;white-space:pre;color:var(--blanco)}
.c-linea{color:var(--linea)}
.c-gris{color:var(--gris)}
.c-cian{color:var(--cian)}
.c-pico{color:var(--pico);text-shadow:0 0 7px currentColor}
.c-blanco{color:var(--blanco)}
.c-verde{color:var(--verde)}
.c-amarillo{color:var(--amarillo)}
.c-ambar{color:var(--ambar)}
.c-naranja{color:var(--naranja)}
.c-rojo{color:var(--rojo)}
.c-morado{color:var(--morado)}
.c-inverso{background:var(--ambar);color:var(--inverso-fg)}
html[data-glass="1"] .term::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:10px;
 background:linear-gradient(160deg,rgba(148,222,251,.07),transparent 42%,rgba(148,222,251,.045))}
footer{color:#7d8590;font-size:13.5px;line-height:1.75;border-top:1px solid #14232e;padding-top:20px}
footer code{font-family:var(--mono);background:#0f1b24;border:1px solid #1d2e39;border-radius:4px;padding:1px 5px;color:#a9b6c9}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #14232e;vertical-align:top}
th{color:#7d8590;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:var(--blanco);font-size:12.5px}
.swatch{display:inline-block;width:13px;height:13px;border-radius:3px;vertical-align:-2px;margin-right:7px;box-shadow:0 0 0 1px #ffffff18}
.aviso{background:#0b1720;border-left:3px solid var(--pico);padding:13px 16px;border-radius:0 7px 7px 0;
 color:#96a4b2;font-size:13.5px;line-height:1.68;margin-top:16px}
"""

JS = """
const pal=document.getElementById('pal'),glass=document.getElementById('glass');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
glass.addEventListener('change',e=>document.documentElement.dataset.glass=e.target.checked?'1':'0');
"""


def marcas(texto: str) -> str:
    """Convierte `x` en <code>x</code> emparejando las comillas graves de dos en dos."""
    trozos = texto.split("`")
    salida = []
    for indice, trozo in enumerate(trozos):
        if indice % 2:
            salida.append(f"<code>{html.escape(trozo)}</code>")
        else:
            salida.append(html.escape(trozo))
    return "".join(salida)


def construir_html(pantallas) -> str:
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
    for clave, nombre, medido in (
            ("fondo", "fondo del HUD", "medido"),
            ("linea", "filete y retícula", "medido"), ("cian", "estructura", "medido"),
            ("pico", "brillo del texto clave", "medido"), ("blanco", "títulos", "medido"),
            ("gris", "texto de apoyo", "medido"), ("verde", "nodo EXE / desbloqueado", "medido"),
            ("amarillo", "barra de vida del enemigo", "medido"), ("ambar", "selección", "medido"),
            ("naranja", "palabras clave", "medido"), ("rojo", "daño y escudo", "medido"),
            ("morado", "nodo raro", "medido")):
        hexa = PRAG[clave]
        filas_color += (f'<tr><td><span class="swatch" style="background:{hexa}"></span>'
                        f'<code>{hexa}</code></td><td>{nombre}</td><td>{medido}</td></tr>')

    paletas = [("pragmata", "Pragmata (medido)"), ("cian", "Solo cian, sin color funcional"),
               ("deuteranopia", "Deuteranopía")]
    opciones = "".join(f'<option value="{v}">{n}</option>' for v, n in paletas)
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="pragmata" data-glass="0">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PRAGMATA · TUI de HUD de cristal</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>PRAGMATA <span>· TUI de HUD de cristal</span></h1>
  <p class="sub">Seis pantallas en <strong>100 × 30 celdas</strong>. A diferencia de las
  series de fósforo, aquí el <strong>color hace un trabajo</strong>: verde es el nodo
  meta, amarillo la habilidad, rojo el daño, morado lo raro. Y el juego ya es una
  cuadrícula — el hackeo de Diana se juega trazando un camino de nodo en nodo — así que
  la terminal no disfraza la interfaz, <em>es</em> la interfaz. Los colores están
  <strong>medidos</strong> sobre dos capturas reales del juego.</p>
  <div class="controls">
    <label>Paleta <select id="pal">{opciones}</select></label>
    <label><input type="checkbox" id="glass"> reflejo de cristal (solo aquí, no es del TUI)</label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>El color, medido</h2></div>
  <p class="nota">Se filtraron los píxeles por tono en el HUD de combate y en el menú
  Unit Printer, y se tomó el percentil alto de brillo de cada grupo. Son <em>picos</em>,
  no rellenos: las capturas son JPEG sobre cristal translúcido y el color plano real es
  algo más apagado. Los doce están medidos; ninguno está inventado.</p>
  <table>
    <tr><th>Color</th><th>Uso</th><th>Origen</th></tr>
    {filas_color}
  </table>
  <div class="aviso"><strong>El par verde / rojo no es accesible.</strong> El nodo meta
  y el escudo enemigo se distinguen solo por tono, que es exactamente lo que falla con
  deuteranopía. El selector de paleta trae una variante que los pasa a cian y ámbar.
  Y la opción «solo cian» existe para ver lo contrario: sin color funcional el HUD
  pierde información, no solo gracia.</div>
  <div class="aviso"><strong>Lo que no se puede copiar del HUD:</strong> el cristal es
  translúcido y desenfoca lo que hay detrás, el anillo de hackeo es un círculo perfecto
  y las líneas tienen grosor real. En celdas: la transparencia se sustituye por relleno
  plano, el círculo por un octógono y el grosor por doble trazo. El reflejo de esta
  página es decoración de la galería y viene apagado.</div>
</section>
<footer>
  Generado por <code>pragmata/pragmata.py</code> · motor de celdas en
  <code>mockups/celdas.py</code> · solo biblioteca estándar.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


def _rgb(hexa: str) -> str:
    return f"{int(hexa[1:3], 16)};{int(hexa[3:5], 16)};{int(hexa[5:7], 16)}"


def _ansi(nombre: str, negrita: bool = False) -> str:
    fg, bg = PRAG[nombre], PRAG["fondo"]
    return f"\x1b[{'1;' if negrita else ''}38;2;{_rgb(fg)};48;2;{_rgb(bg)}m"


ANSI = {
    "": _ansi("blanco"),
    "linea": _ansi("linea"),
    "gris": _ansi("gris"),
    "cian": _ansi("cian"),
    "pico": _ansi("pico", True),
    "blanco": _ansi("blanco"),
    "verde": _ansi("verde"),
    "amarillo": _ansi("amarillo"),
    "ambar": _ansi("ambar"),
    "naranja": _ansi("naranja"),
    "rojo": _ansi("rojo"),
    "morado": _ansi("morado"),
    "inverso": f"\x1b[1;38;2;{_rgb(PRAG['fondo'])};48;2;{_rgb(PRAG['ambar'])}m",
}
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
    (destino / "pragmata.html").write_text(construir_html(pantallas), encoding="utf-8")
    with open(destino / "pragmata.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    anchos = {len(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · máx. {max(anchos)} columnas · "
          f"0 de doble ancho → pragmata.html y pragmata.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
