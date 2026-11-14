#!/usr/bin/env python3
"""Mockups de una TUI con la paleta de la referencia sci-fi tipo consola de juego.

La paleta **no está inventada**: sale de muestrear una imagen real de Alamy de la
serie «vector cartoon set de UI sci-fi» (autora Yuliya Pauliukevich). El enlace
que pasó el usuario devuelve 404, así que se muestreó la pieza hermana de la misma
serie y se midieron las regiones (fondo, botón azul, botón amarillo, panel, barra
rosa, barra verde, barra amarilla, botón rojo, botón verde). Los hexadecimales de
:data:`MUESTRAS` son los medidos.

Traducción del lenguaje visual a celdas de terminal:

* paneles con **contorno de doble línea** (`╔═╗║╚╝`), como el trazo luminoso;
* **relleno azul profundo** dentro del panel, no transparencia;
* **botones gruesos de tres filas** (`▛▀▜ / ▌ ▐ / ▙▄▟`), que es lo más parecido
  a los botones biselados de la referencia;
* **barras segmentadas** (`▮▯`) para vida, créditos y energía, con sus colores
  medidos: rosa, verde y amarillo.

    python3 juego/juego.py            # juego.html y juego.txt
    python3 juego/juego.py --ansi     # pinta las pantallas en tu terminal
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo, barra, pseudo, recorta  # noqa: E402

ANCHO, ALTO = 100, 30

#: Colores medidos sobre la imagen de referencia (mediana por región).
MUESTRAS = {
    "fondo": "#131f2d",
    "panel": "#082873",
    "borde": "#1f6fac",
    "azul": "#0d90fa",
    "cian": "#44c8f9",
    "amarillo": "#e5d818",
    "rosa": "#da1e7d",
    "verde": "#05b769",
    "rojo": "#fd4299",
}


# ---------------------------------------------------------------------------
# mobiliario
# ---------------------------------------------------------------------------
def barra_superior(c: Lienzo, izquierda: str, derecha: str) -> None:
    c.texto(0, 0, " " * ANCHO, "top")
    c.texto(1, 0, izquierda, "top_marca")
    c.texto(ANCHO - len(derecha) - 2, 0, derecha, "top_dim")


def rail(c: Lienzo, y: int) -> None:
    """Fila decorativa de bloques: el adorno de esquina de la referencia."""
    piezas = [(2, 10, "cyan"), (13, 6, "blue"), (20, 3, "gold")]
    for x, ancho, estilo in piezas:
        c.texto(x, y, "▄" * ancho, estilo)


def barra_inferior(c: Lienzo, teclas: list[tuple[str, str]]) -> None:
    c.texto(0, ALTO - 1, " " * ANCHO, "top")
    x = 2
    for tecla, accion in teclas:
        c.texto(x, ALTO - 1, f"▛ {tecla} ▜", "key")
        x += len(tecla) + 5
        c.texto(x, ALTO - 1, accion + "   ", "top_dim")
        x += len(accion) + 3


def boton(c: Lienzo, x: int, y: int, ancho: int, texto: str,
          seleccionado: bool = False, acento: str = "blue") -> None:
    """Botón biselado de tres filas, como los de la referencia."""
    borde = "btn_sel" if seleccionado else f"btn_{acento}"
    relleno = "fill_sel" if seleccionado else "fill"
    rotulo = "btn_sel_texto" if seleccionado else "btn_texto"
    c.texto(x, y, "▛" + "▀" * (ancho - 2) + "▜", borde)
    c.texto(x, y + 1, "▌", borde)
    c.texto(x + 1, y + 1, " " * (ancho - 2), relleno)
    c.texto(x + 1, y + 1, texto.center(ancho - 2), rotulo)
    c.texto(x + ancho - 1, y + 1, "▐", borde)
    c.texto(x, y + 2, "▙" + "▄" * (ancho - 2) + "▟", borde)


def pips(valor: float, celdas: int, estilo: str) -> None:
    dentro = round(max(0.0, min(1.0, valor)) * celdas)
    return None


def medidor(c: Lienzo, x: int, y: int, etiqueta: str, valor: float, celdas: int,
            estilo: str, cifra: str) -> None:
    """Barra segmentada: `▮` lleno, `▯` vacío, con su etiqueta y su cifra."""
    c.texto(x, y, etiqueta, "dim")
    dentro = round(max(0.0, min(1.0, valor)) * celdas)
    c.texto(x + len(etiqueta) + 1, y, "▮" * dentro + "▯" * (celdas - dentro), estilo)
    c.texto(x + len(etiqueta) + celdas + 2, y, cifra, "text")


def campo(c: Lienzo, x: int, y: int, ancho: int, etiqueta: str, valor: str,
          activo: bool = False) -> None:
    """Campo de formulario: etiqueta encima y caja con el valor dentro."""
    c.texto(x, y, etiqueta, "dim")
    c.texto(x, y + 1, "┌" + "─" * (ancho - 2) + "┐", "field_sel" if activo else "field")
    c.texto(x, y + 2, "│" + " " * (ancho - 2) + "│", "field")
    c.texto(x + 2, y + 2, valor, "text")
    c.texto(x, y + 3, "└" + "─" * (ancho - 2) + "┘", "field_sel" if activo else "field")
    if activo:
        c.texto(x + 2 + len(valor), y + 2, "█", "cyan")


# ---------------------------------------------------------------------------
# 01 · Acceso
# ---------------------------------------------------------------------------
def pantalla_acceso(c: Lienzo) -> None:
    barra_superior(c, "◤ NEXUS-9", "TERMINAL 04 · SESIÓN 118 · 20:41:07")
    rail(c, 1)

    c.texto(2, 3, "N E X U S - 9", "brand")
    c.texto(2, 4, "consola de mando · versión 4.2.1", "dim")

    c.texto(2, 6, "MENÚ", "dim")
    menu = [("PLAY", True), ("RESUME", False), ("OPTIONS", False), ("EXIT", False)]
    for indice, (texto, sel) in enumerate(menu):
        boton(c, 2, 7 + indice * 4, 26, texto, seleccionado=sel,
              acento="gold" if sel else "blue")

    c.relleno(32, 6, 34, 17, "panel")
    c.marco(32, 6, 34, 17, "ACCESO", "stroke")
    campo(c, 34, 8, 30, "NOMBRE", "kestrel.04", activo=False)
    campo(c, 34, 13, 30, "CLAVE", "••••••••••", activo=True)
    boton(c, 44, 18, 10, "OK", seleccionado=True, acento="cyan")

    c.texto(70, 6, "SISTEMA", "dim")
    boton(c, 70, 7, 8, ">", acento="cyan")
    boton(c, 79, 7, 8, "II", acento="blue")
    boton(c, 88, 7, 8, "=", acento="blue")
    boton(c, 70, 11, 8, "A", acento="blue")
    boton(c, 79, 11, 8, "x", acento="red")
    boton(c, 88, 11, 8, "v", acento="green")

    c.texto(70, 16, "ESTADO", "dim")
    medidor(c, 70, 17, "VIDA", 0.72, 12, "pink", "72 %")
    medidor(c, 70, 19, "CRÉD", 0.48, 12, "green", "4 210")
    medidor(c, 70, 21, "ENER", 0.86, 12, "gold", "86 %")

    c.texto(70, 24, "canal", "dim")
    c.texto(78, 24, "▬" * 18, "track")
    c.texto(78 + 11, 24, "▮", "cyan")

    c.texto(2, 26, "▸ el sistema pide credenciales antes de cargar el sector.", "ghost")
    barra_inferior(c, [("⏎", "entrar"), ("↑↓", "menú"), ("ESC", "salir"), ("F1", "ayuda")])


# ---------------------------------------------------------------------------
# 02 · Perfil
# ---------------------------------------------------------------------------
def pantalla_perfil(c: Lienzo) -> None:
    barra_superior(c, "◤ PERFIL", "OPERADOR kestrel.04 · NIVEL 27")
    rail(c, 1)

    c.relleno(2, 3, 44, 17, "panel")
    c.marco(2, 3, 44, 17, "OPERADOR", "stroke")
    c.texto(4, 5, "K E S T R E L", "brand")
    c.texto(4, 6, "especialista en intrusión · sombra", "dim")
    c.texto(4, 8, "NIVEL", "dim")
    c.texto(12, 8, "27", "gold")
    c.texto(16, 8, "XP", "dim")
    c.texto(4, 9, barra(0.64, 38, "█", "░"), "cyan")
    c.texto(4, 10, "8 240 / 12 800 XP", "ghost")

    c.texto(4, 12, "ATRIBUTOS", "dim")
    atributos = [("cuerpo", 0.78, "pink"), ("reflejos", 0.92, "cyan"),
                 ("tecnología", 0.85, "blue"), ("voluntad", 0.61, "gold")]
    for indice, (nombre, valor, estilo) in enumerate(atributos):
        fila = 13 + indice
        c.texto(4, fila, nombre.ljust(12), "")
        c.texto(17, fila, "▮" * round(valor * 16) + "▯" * (16 - round(valor * 16)), estilo)
        c.texto(35, fila, f"{int(valor * 100):3d}", "text")

    c.relleno(48, 3, 50, 10, "panel")
    c.marco(48, 3, 50, 10, "RECURSOS", "stroke")
    medidor(c, 50, 5, "VIDA", 0.72, 24, "pink", "720 / 1 000")
    medidor(c, 50, 7, "CRÉDITOS", 0.48, 24, "green", "4 210 ₡")
    medidor(c, 50, 9, "ENERGÍA", 0.86, 24, "gold", "860 / 1 000")
    c.texto(50, 11, "▸ la energía se recupera en los nodos.", "ghost")

    c.relleno(48, 14, 50, 14, "panel")
    c.marco(48, 14, 50, 14, "HISTORIAL", "stroke")
    eventos = [
        ("20:38", "sector 09 despejado", "green"),
        ("20:31", "compra: filo de plasma", "gold"),
        ("20:12", "alerta: rastreador activo", "red"),
        ("19:58", "nodo de descanso usado", "cyan"),
        ("19:40", "misión secundaria aceptada", "blue"),
    ]
    for indice, (hora, texto, estilo) in enumerate(eventos):
        c.texto(50, 16 + indice * 2, hora, "ghost")
        c.texto(57, 16 + indice * 2, texto, estilo)
    c.texto(50, 26, "▸ 5 de 128 · el resto, en el registro", "ghost")

    c.texto(2, 21, "INSIGNIAS", "dim")
    insignias = [("◆", "cyan"), ("◆", "gold"), ("◆", "pink"), ("◇", "dim"), ("◇", "dim")]
    for indice, (glifo, estilo) in enumerate(insignias):
        c.texto(2 + indice * 3, 22, glifo, estilo)
    c.texto(2, 24, "3 de 5", "dim")
    barra_inferior(c, [("TAB", "inventario"), ("E", "equipar"), ("ESC", "volver")])


# ---------------------------------------------------------------------------
# 03 · Tienda
# ---------------------------------------------------------------------------
def pantalla_tienda(c: Lienzo) -> None:
    barra_superior(c, "◤ MERCADO", "PUESTO 7 · CRÉDITOS 4 210 ₡")
    rail(c, 1)

    c.relleno(2, 3, 64, 15, "panel")
    c.marco(2, 3, 64, 15, "CATÁLOGO", "stroke")
    c.texto(4, 5, "ARTÍCULO".ljust(26) + "CLASE".ljust(12) + "PRECIO".rjust(10), "ghost")
    c.texto(4, 6, "═" * 60, "stroke")

    articulos = [
        ("FILO DE PLASMA", "cuerpo", "1 200", False),
        ("IMPULSO NEURAL", "reflejos", "2 400", True),
        ("DECK MK-IV", "tecnología", "3 800", False),
        ("FILTRO ÓPTICO", "voluntad", "900", False),
        ("BLINDAJE LIGERO", "cuerpo", "1 650", False),
        ("PARCHE DE HIELO", "tecnología", "600", False),
        ("SANGRE SINT. 2 L", "cuerpo", "310", False),
    ]
    for indice, (nombre, clase, precio, seleccionado) in enumerate(articulos):
        fila = 7 + indice
        if seleccionado:
            c.relleno(3, fila, 62, 1, "sel")
            c.texto(4, fila, "> " + nombre.ljust(24), "sel")
            c.texto(30, fila, clase.ljust(12), "sel")
            c.texto(52, fila, f"{precio} ₡".rjust(10), "sel")
        else:
            c.texto(4, fila, "  " + nombre.ljust(24), "text")
            c.texto(30, fila, clase.ljust(12), "dim")
            c.texto(52, fila, f"{precio} ₡".rjust(10), "gold")
    c.texto(4, 15, "▸ 7 de 42 artículos · el precio cambia con la reputación.", "ghost")

    c.relleno(68, 3, 30, 13, "panel")
    c.marco(68, 3, 30, 13, "DETALLE", "stroke")
    c.texto(70, 5, "IMPULSO NEURAL", "brand")
    c.texto(70, 6, "clase: reflejos", "dim")
    c.texto(70, 8, "+12 % velocidad", "green")
    c.texto(70, 9, "-4 % voluntad", "red")
    c.texto(70, 11, "PRECIO", "dim")
    c.texto(78, 11, "2 400 ₡", "gold")
    c.texto(70, 12, "SALDO", "dim")
    c.texto(78, 12, "4 210 ₡", "green")
    c.texto(70, 14, "▸ quedan 1 en el puesto.", "ghost")

    c.relleno(68, 17, 30, 7, "panel")
    c.marco(68, 17, 30, 7, "ACCIONES", "stroke")
    boton(c, 69, 18, 28, "COMPRAR", seleccionado=True, acento="gold")
    c.texto(70, 22, "NEGOCIAR", "dim")
    c.texto(82, 22, "SALIR", "dim")
    barra_inferior(c, [("↑↓", "artículo"), ("⏎", "comprar"), ("N", "negociar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 04 · Mapa
# ---------------------------------------------------------------------------
def pantalla_mapa(c: Lienzo) -> None:
    barra_superior(c, "◤ SECTOR 09", "POSICIÓN 41.2 / 08.7 · OXÍGENO 94 %")
    rail(c, 1)

    c.relleno(2, 3, 66, 21, "panel")
    c.marco(2, 3, 66, 21, "MAPA", "stroke")
    rutas = [(7, 8), (23, 8), (39, 8), (55, 8), (7, 15), (23, 15), (39, 15), (55, 15)]
    for indice, (x, y) in enumerate(rutas):
        c.texto(x, y, "┼", "track")
        if indice % 4 != 3:
            c.texto(x + 1, y, "─" * 15, "track")
        if indice < 4:
            for paso in range(1, 7):
                c.texto(x, y + paso, "│", "track")
    nodos = [(10, 10, "▣", "cyan", "nodo 3"), (26, 10, "▣", "green", "nodo 7"),
             (48, 17, "▣", "gold", "nodo 9"), (14, 18, "▣", "cyan", "nodo 1")]
    for x, y, glifo, estilo, nombre in nodos:
        c.texto(x, y, glifo, estilo)
        c.texto(x + 2, y, nombre, "dim")
    c.texto(41, 12, "►", "red")
    c.texto(43, 12, "tú", "red")
    c.texto(26, 19, "◆", "pink")
    c.texto(28, 19, "rastreador", "pink")
    c.texto(4, 21, "▸ el rastreador se mueve: hace 2 ciclos estaba en el nodo 3.", "ghost")

    c.relleno(70, 3, 28, 11, "panel")
    c.marco(70, 3, 28, 11, "LEYENDA", "stroke")
    leyenda = [("▣", "cyan", "nodo de descanso"), ("▣", "green", "nodo seguro"),
               ("▣", "gold", "puesto"), ("►", "red", "tú"), ("◆", "pink", "rastreador")]
    for indice, (glifo, estilo, texto) in enumerate(leyenda):
        c.texto(72, 5 + indice, glifo, estilo)
        c.texto(75, 5 + indice, texto, "dim")

    c.relleno(70, 15, 28, 9, "panel")
    c.marco(70, 15, 28, 9, "DISTANCIA", "stroke")
    c.texto(72, 17, "al nodo 9", "dim")
    c.texto(88, 17, "1.4 km", "text")
    c.texto(72, 18, "al nodo 7", "dim")
    c.texto(88, 18, "2.9 km", "text")
    c.texto(72, 20, "OXÍGENO", "dim")
    c.texto(72, 21, "▮" * 18 + "▯" * 6, "cyan")
    c.texto(72, 22, "▸ a este ritmo: 9 min.", "ghost")
    barra_inferior(c, [("←→", "mover"), ("⏎", "viajar"), ("M", "marcar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 05 · HUD en juego
# ---------------------------------------------------------------------------
def pantalla_hud(c: Lienzo) -> None:
    barra_superior(c, "◤ SECTOR 09 · COMBATE", "OLAS 3/5 · 20:44:12")
    c.texto(2, 2, "VIDA", "dim")
    c.texto(7, 2, "▮" * 16 + "▯" * 6, "pink")
    c.texto(31, 2, "720", "text")
    c.texto(36, 2, "ENERGÍA", "dim")
    c.texto(44, 2, "▮" * 18 + "▯" * 4, "gold")
    c.texto(67, 2, "860", "text")
    c.texto(72, 2, "OLAS", "dim")
    c.texto(78, 2, "▮▮▮▯▯", "cyan")

    c.relleno(2, 4, 62, 18, "hud")
    c.marco(2, 4, 62, 18, "ESCENA", "stroke")
    # skyline: torres de distinta altura y anchura, sin solaparse
    torres = [(4, 9, 8), (15, 7, 5), (24, 10, 7), (36, 6, 4), (44, 12, 8), (58, 3, 6)]
    for x, ancho, alto in torres:
        for fila in range(alto):
            c.texto(x, 15 - fila, "█" * ancho, "silueta")
        c.texto(x, 15 - alto, "▀" * ancho, "silueta")
    c.texto(3, 16, "▄" * 58, "suelo")
    # marcadores en la calle, y sus etiquetas en el renglón de abajo
    c.texto(6, 17, "◆", "cyan")
    c.texto(20, 17, "◇", "red")
    c.texto(41, 17, "►", "gold")
    c.texto(54, 17, "◇", "red")
    c.texto(5, 18, "◆ aliado", "cyan")
    c.texto(19, 18, "◇ hostil", "red")
    c.texto(40, 18, "► tú", "gold")
    c.texto(53, 18, "◇ hostil", "red")
    c.texto(4, 19, "▸ el hostil de la derecha está fuera de cobertura.", "ghost")

    c.relleno(66, 4, 32, 9, "hud")
    c.marco(66, 4, 32, 9, "RADAR", "stroke")
    for fila in range(5, 12):
        for columna in range(68, 96):
            if (columna + fila) % 7 == 0:
                c.texto(columna, fila, "·", "ghost")
    c.texto(81, 8, "●", "cyan")
    c.texto(74, 6, "◇", "red")
    c.texto(88, 10, "◇", "red")
    c.texto(80, 11, "►", "gold")

    c.relleno(66, 14, 32, 10, "hud")
    c.marco(66, 14, 32, 10, "OBJETIVOS", "stroke")
    objetivos = [("[x]", "despejar el nodo 3", "green"),
                 ("[x]", "recoger el paquete", "green"),
                 ("[>]", "llegar al nodo 9", "gold"),
                 ("[ ]", "sobrevivir a la ola 5", "dim")]
    for indice, (marca, texto, estilo) in enumerate(objetivos):
        c.texto(68, 16 + indice * 2, marca, estilo)
        c.texto(72, 16 + indice * 2, texto, "text" if estilo != "dim" else "dim")

    boton(c, 2, 22, 20, "DISPARAR", seleccionado=True, acento="red")
    boton(c, 24, 22, 20, "CUBRIRSE", acento="blue")
    boton(c, 46, 22, 20, "RECARGAR", acento="gold")
    c.texto(68, 25, "munición", "dim")
    c.texto(78, 25, "▮▮▮▮▮▮▮▯▯▯", "cyan")
    c.texto(90, 25, "28", "text")
    barra_inferior(c, [("ESP", "disparar"), ("E", "cubrirse"), ("R", "recargar"), ("ESC", "pausa")])


# ---------------------------------------------------------------------------
# 06 · Pausa (modal)
# ---------------------------------------------------------------------------
def pantalla_pausa(c: Lienzo) -> None:
    barra_superior(c, "◤ NEXUS-9", "SESIÓN EN PAUSA · 20:45:03")
    rail(c, 1)
    # el fondo sigue visible pero apagado: un modal no necesita trama que lo tape
    for fila in range(3, 27):
        c.texto(2, fila, "· " * 24, "fondo_puntos")

    c.relleno(26, 5, 48, 22, "modal")
    c.marco(26, 5, 48, 22, "PAUSA", "modal_borde")
    c.texto(42, 7, "S E S I Ó N   E N   P A U S A", "brand")
    c.texto(32, 9, "el sector sigue ahí fuera; aquí no corre", "dim")
    c.texto(32, 10, "el tiempo.", "dim")
    boton(c, 30, 12, 40, "CONTINUE", seleccionado=True, acento="cyan")
    boton(c, 30, 16, 40, "OPTIONS", acento="blue")
    boton(c, 30, 20, 40, "EXIT", acento="red")
    c.texto(30, 24, "▸ salir pierde el progreso de esta oleada.", "ghost")
    barra_inferior(c, [("⏎", "continuar"), ("↑↓", "elegir"), ("ESC", "seguir jugando")])


PANTALLAS = [
    ("01", "Acceso", "Los tres recursos de la referencia —vida rosa, créditos verdes, "
     "energía amarilla— en barras segmentadas `▮▯`, y el botón biselado de tres filas "
     "`▛▀▜ / ▌ ▐ / ▙▄▟`.", pantalla_acceso),
    ("02", "Perfil", "Atributos con la misma barra segmentada y el panel de recursos "
     "con sus cifras a la derecha, siempre escritas: el color no informa solo.", pantalla_perfil),
    ("03", "Tienda", "Tabla con precios en `═` de separación, fila elegida en invertido "
     "y panel de detalle a la derecha. El saldo se compara con el precio a la vista.",
     pantalla_tienda),
    ("04", "Mapa", "Rejilla de rutas con `┼─│`, nodos `▣`, el jugador `►` y el rastreador "
     "`◆` en rosa. Leyenda explícita: ninguna forma se explica sola.", pantalla_mapa),
    ("05", "HUD de combate", "La pantalla más densa: vida y energía arriba, radar a la "
     "derecha, objetivos con casillas `[x] [>] [ ]` y tres botones de acción abajo.",
     pantalla_hud),
    ("06", "Pausa", "Un modal opaco sobre el fondo apagado con puntos `·`. Sin trama "
     "dentro del panel: lo que se lee no lleva adornos encima.", pantalla_pausa),
]


# ---------------------------------------------------------------------------
# serialización y salida
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
:root{--bg:#131f2d;--panel:#082873;--fill:#0a2050;--fill-sel:#0d90fa;
 --stroke:#2f8fe0;--cyan:#44c8f9;--blue:#0d90fa;--gold:#e5d818;--pink:#da1e7d;
 --green:#05b769;--red:#fd4299;--text:#eaf4ff;--dim:#8fb2d4;--ghost:#4d6b8a;
 --sel-bg:#44c8f9;--sel-fg:#08132b;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
html[data-pal="consola"]{--bg:#0d1622;--panel:#062046;--fill:#081a3a;--stroke:#1f6fac}
html[data-pal="ambar"]{--bg:#1a1408;--panel:#3a2a06;--fill:#2a1e05;--stroke:#a86f10;
 --cyan:#ffcf5f;--blue:#e5a318;--gold:#ffe45f;--text:#fff6de;--dim:#c0a070;--ghost:#6b5730}
html[data-pal="mono"]{--bg:#0d0f13;--panel:#15181d;--fill:#1a1e24;--stroke:#9aa4b0;
 --cyan:#ffffff;--blue:#c8d0d8;--gold:#e8e8e8;--pink:#d8d8d8;--green:#e8e8e8;
 --red:#ffffff;--text:#f0f0f0;--dim:#9aa0a8;--ghost:#5a6068;--sel-bg:#e8e8e8;--sel-fg:#0d0f13}
*{box-sizing:border-box}
body{margin:0;background:#080c12;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:36px 0 24px;border-bottom:1px solid #17202b;margin-bottom:28px}
h1{margin:0 0 8px;font-size:27px;letter-spacing:-.02em}
h1 span{color:var(--cyan);font-family:var(--mono)}
.sub{color:#7d8590;font-size:15px;line-height:1.68;margin:0;max-width:80ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#7d8590;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#101822;color:#c9d1d9;border:1px solid #22303f;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 46px}
.head{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:var(--cyan);border:1px solid #1d3346;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#7d8590;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:90ch}
.nota code{font-family:var(--mono);background:#101822;border:1px solid #1b2836;border-radius:4px;padding:0 4px;color:#9fd8ff}
.term{background:var(--bg);border-radius:8px;padding:12px 14px;overflow-x:auto;
 box-shadow:0 0 0 1px #1b2b3c, 0 26px 60px -34px #000}
.term pre{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.32;white-space:pre;color:var(--text)}
.c-top{background:#0b1622}
.c-top_marca{color:var(--cyan);font-weight:700}
.c-top_dim{color:var(--dim)}
.c-brand{color:var(--text);font-weight:700;letter-spacing:.06em}
.c-dim{color:var(--dim)}
.c-ghost{color:var(--ghost)}
.c-text{color:var(--text)}
.c-cyan{color:var(--cyan)}
.c-blue{color:var(--blue)}
.c-gold{color:var(--gold)}
.c-pink{color:var(--pink)}
.c-green{color:var(--green)}
.c-red{color:var(--red)}
.c-stroke{color:var(--stroke)}
.c-panel{background:var(--panel)}
.c-fill{background:var(--fill)}
.c-fill_sel{background:var(--fill-sel)}
.c-hud{background:#0a1a30}
.c-modal{background:#0b1c33}
.c-modal_borde{color:var(--cyan)}
.c-field{color:#17456e}
.c-field_sel{color:var(--cyan)}
.c-track{color:#2a4a6b}
.c-silueta{color:#16324f}
.c-suelo{color:#1b3b5c}
.c-fondo_puntos{color:#1a2634}
.c-btn_blue{color:var(--stroke)}
.c-btn_cyan{color:var(--cyan)}
.c-btn_gold{color:var(--gold)}
.c-btn_red{color:var(--red)}
.c-btn_green{color:var(--green)}
.c-btn_sel{color:var(--cyan)}
.c-btn_texto{color:var(--text);background:var(--fill)}
.c-btn_sel_texto{color:var(--sel-fg);background:var(--fill-sel);font-weight:700}
.c-sel{background:var(--sel-bg);color:var(--sel-fg);font-weight:700}
.c-key{background:var(--sel-bg);color:var(--sel-fg);font-weight:700}
footer{color:#7d8590;font-size:13.5px;line-height:1.75;border-top:1px solid #17202b;padding-top:20px}
footer code{font-family:var(--mono);background:#101822;border:1px solid #1b2836;border-radius:4px;padding:1px 5px;color:#a9b6c9}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #17202b;vertical-align:top}
th{color:#7d8590;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:#9fd8ff;font-size:12.5px}
.swatch{display:inline-block;width:13px;height:13px;border-radius:3px;vertical-align:-2px;margin-right:7px;box-shadow:0 0 0 1px #ffffff22}
.aviso{background:#0b1420;border-left:3px solid var(--gold);padding:13px 16px;border-radius:0 7px 7px 0;
 color:#96a4b2;font-size:13.5px;line-height:1.68;margin-top:16px}
"""

JS = """
const pal=document.getElementById('pal');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
"""


def construir_html(pantallas) -> str:
    secciones = []
    for numero, nombre, nota, lienzo in pantallas:
        filas = "\n".join(spans(fila) for fila in lienzo.rejilla)
        secciones.append(f"""
<section>
  <div class="head"><span class="num">{numero}</span><h2>{html.escape(nombre)}</h2></div>
  <p class="nota">{html.escape(nota).replace("`", "")}</p>
  <div class="term"><pre>{filas}</pre></div>
</section>""")

    filas_color = ""
    for nombre, clave in (("fondo", "fondo"), ("panel", "panel"), ("borde", "borde"),
                          ("azul", "azul"), ("cian", "cian"), ("amarillo", "amarillo"),
                          ("rosa", "rosa"), ("verde", "verde"), ("rojo", "rojo")):
        hexa = MUESTRAS[clave]
        filas_color += (f'<tr><td><span class="swatch" style="background:{hexa}"></span>'
                        f'<code>{hexa}</code></td><td>{nombre}</td></tr>')

    paletas = [("arcade", "Arcade"), ("consola", "Consola oscura"),
               ("ambar", "Ámbar"), ("mono", "Sin color")]
    opciones = "".join(f'<option value="{v}">{n}</option>' for v, n in paletas)
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="arcade">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEXUS-9 · TUI con la paleta de la referencia sci-fi</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>NEXUS-9 <span>· TUI con la paleta de tu referencia</span></h1>
  <p class="sub">Seis pantallas de consola de juego, en <strong>100 × 30 celdas</strong>, con
  los colores <strong>medidos</strong> sobre la imagen de Alamy que enviaste: azul profundo
  de fondo, contornos luminosos, y los tres acentos de sus barras —rosa, verde y amarillo—.
  El lenguaje visual se traduce a lo que una terminal permite: contorno de doble línea
  <code>╔═╗</code>, relleno azul sólido y botones biselados de tres filas.</p>
  <div class="controls">
    <label>Paleta <select id="pal">{opciones}</select></label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>De dónde salen estos colores</h2></div>
  <p class="nota">No están elegidos a ojo. Se descargó la imagen de referencia y se midió
  la mediana de color en nueve regiones (fondo, cuerpo y borde del panel, botón azul,
  botón amarillo, las tres barras y los botones de validar y cancelar). Estos son los
  valores medidos, tal cual:</p>
  <table>
    <tr><th>Color medido</th><th>De dónde se sacó</th></tr>
    {filas_color}
  </table>
  <div class="aviso"><strong>Aviso importante sobre el enlace:</strong> la página exacta
  que enviaste (<code>…game-image539565602.html</code>) devuelve <em>404 · Page not found</em>
  en Alamy, y su CDN ya no sirve ese identificador. Lo que se midió es la pieza hermana de
  la misma serie y la misma autora (Yuliya Pauliukevich, «Game buttons and frames in sci fi
  style… vector cartoon set», ID 2H0HNK8), que es de la misma familia visual: botones
  biselados, barras de vida/dinero/energía y marcos con contorno luminoso. Si me pasas la
  imagen exacta —basta con arrastrarla aquí— vuelvo a medir y ajusto la paleta al píxel.</div>
</section>
<footer>
  Generado por <code>juego/juego.py</code> · motor de celdas en <code>mockups/celdas.py</code>
  · solo biblioteca estándar · los colores de la imagen se usan como referencia de paleta,
  no se reproduce la ilustración.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


# ---------------------------------------------------------------------------
# ANSI (color verdadero con los valores medidos)
# ---------------------------------------------------------------------------
def _rgb(hexa: str) -> str:
    r, g, b = int(hexa[1:3], 16), int(hexa[3:5], 16), int(hexa[5:7], 16)
    return f"{r};{g};{b}"


F, P, B, AZ, CY = MUESTRAS["fondo"], MUESTRAS["panel"], MUESTRAS["borde"], MUESTRAS["azul"], MUESTRAS["cian"]
AM, RO, VE, RJ = MUESTRAS["amarillo"], MUESTRAS["rosa"], MUESTRAS["verde"], MUESTRAS["rojo"]
ANSI = {
    "": f"\x1b[38;2;234;244;255;48;2;{_rgb(F)}m",
    "text": f"\x1b[38;2;234;244;255;48;2;{_rgb(F)}m",
    "dim": f"\x1b[38;2;143;178;212;48;2;{_rgb(F)}m",
    "ghost": f"\x1b[38;2;77;107;138;48;2;{_rgb(F)}m",
    "cyan": f"\x1b[38;2;{_rgb(CY)};48;2;{_rgb(F)}m",
    "blue": f"\x1b[38;2;{_rgb(AZ)};48;2;{_rgb(F)}m",
    "gold": f"\x1b[38;2;{_rgb(AM)};48;2;{_rgb(F)}m",
    "pink": f"\x1b[38;2;{_rgb(RO)};48;2;{_rgb(F)}m",
    "green": f"\x1b[38;2;{_rgb(VE)};48;2;{_rgb(F)}m",
    "red": f"\x1b[38;2;{_rgb(RJ)};48;2;{_rgb(F)}m",
    "brand": f"\x1b[1;38;2;234;244;255;48;2;{_rgb(F)}m",
    "top": f"\x1b[38;2;234;244;255;48;2;11;22;34m",
    "top_marca": f"\x1b[1;38;2;{_rgb(CY)};48;2;11;22;34m",
    "top_dim": f"\x1b[38;2;143;178;212;48;2;11;22;34m",
    "key": f"\x1b[1;38;2;8;19;43;48;2;{_rgb(CY)}m",
    "sel": f"\x1b[1;38;2;8;19;43;48;2;{_rgb(CY)}m",
    "stroke": f"\x1b[38;2;{_rgb(B)};48;2;{_rgb(P)}m",
    "panel": f"\x1b[48;2;{_rgb(P)}m",
    "fill": f"\x1b[48;2;10;32;80m",
    "fill_sel": f"\x1b[48;2;{_rgb(AZ)}m",
    "hud": f"\x1b[48;2;10;26;48m",
    "modal": f"\x1b[48;2;11;28;51m",
    "modal_borde": f"\x1b[38;2;{_rgb(CY)};48;2;11;28;51m",
    "field": f"\x1b[38;2;23;69;110;48;2;{_rgb(F)}m",
    "field_sel": f"\x1b[38;2;{_rgb(CY)};48;2;{_rgb(F)}m",
    "track": f"\x1b[38;2;42;74;107;48;2;{_rgb(F)}m",
    "silueta": f"\x1b[38;2;22;50;79;48;2;10;26;48m",
    "suelo": f"\x1b[38;2;27;59;92;48;2;10;26;48m",
    "fondo_puntos": f"\x1b[38;2;26;38;52;48;2;{_rgb(F)}m",
    "btn_blue": f"\x1b[38;2;{_rgb(B)};48;2;{_rgb(F)}m",
    "btn_cyan": f"\x1b[38;2;{_rgb(CY)};48;2;{_rgb(F)}m",
    "btn_gold": f"\x1b[38;2;{_rgb(AM)};48;2;{_rgb(F)}m",
    "btn_red": f"\x1b[38;2;{_rgb(RJ)};48;2;{_rgb(F)}m",
    "btn_green": f"\x1b[38;2;{_rgb(VE)};48;2;{_rgb(F)}m",
    "btn_sel": f"\x1b[38;2;{_rgb(CY)};48;2;{_rgb(F)}m",
    "btn_sel_texto": f"\x1b[1;38;2;8;19;43;48;2;{_rgb(AZ)}m",
    "btn_texto": f"\x1b[38;2;234;244;255;48;2;10;32;80m",
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
    (destino / "juego.html").write_text(construir_html(pantallas), encoding="utf-8")
    with open(destino / "juego.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    anchos = {len(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · máx. {max(anchos)} columnas · "
          f"0 de doble ancho → juego.html y juego.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
