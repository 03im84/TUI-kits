#!/usr/bin/env python3
"""Mockups de una TUI tipo Pip-Boy: un solo fósforo, jerarquía por brillo.

Paleta **medida** sobre una captura real del Pip-Boy 3000 (Fallout 3, pantalla
STATS): los verdes salen de contar píxeles verdes de la propia imagen.

    fondo apagado  #102e16     fósforo medio   #1c5626
    fósforo claro  #64b887     pico de brillo  #63e59f

De ahí salen cinco niveles, que son **todo** el sistema de color: no hay un solo
acento. La jerarquía se hace subiendo o bajando el brillo, como en un tubo de
rayos catódicos de verdad.

Lenguaje visual traducido a celdas:

* **esquinas de corchete** `┌` … `┘` solo en los extremos: los lados sin dibujar;
* **títulos con filetes** `━━━ STATS ━━━`;
* **pestañas** arriba, con la activa en vídeo inverso;
* **reglas de escala** `└──┴──┘` con su marca de porcentaje, como la barra PWR;
* caracteres de tubo: `▓` como texto «encendido», `▒` como atenuado.

    python3 pipboy/pipboy.py            # pipboy.html y pipboy.txt
    python3 pipboy/pipboy.py --ansi     # pinta las pantallas en tu terminal
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo, pseudo  # noqa: E402

ANCHO, ALTO = 100, 30

#: Medidos sobre la captura del Pip-Boy 3000 (ver docstring).
FOSFORO = {
    "fondo": "#102e16",
    "tenue": "#1c5626",
    "medio": "#3d8a55",
    "claro": "#64b887",
    "pico": "#63e59f",
}


# ---------------------------------------------------------------------------
# mobiliario
# ---------------------------------------------------------------------------
def marco(c: Lienzo) -> None:
    """Marco de pantalla: filete arriba y abajo y esquinas de corchete."""
    c.texto(0, 0, "┌" + "─" * (ANCHO - 2) + "┐", "tenue")
    c.texto(0, ALTO - 1, "└" + "─" * (ANCHO - 2) + "┘", "tenue")


def cabecera(c: Lienzo, izquierda: str, derecha: str) -> None:
    c.texto(2, 1, izquierda, "claro")
    c.texto(ANCHO - len(derecha) - 2, 1, derecha, "tenue")
    c.texto(1, 2, "─" * (ANCHO - 2), "tenue")


def pestanas(c: Lienzo, nombres: list[str], activa: int, y: int = 3) -> None:
    x = 3
    for indice, nombre in enumerate(nombres):
        rotulo = f" {nombre} "
        if indice == activa:
            c.relleno(x - 1, y, len(rotulo) + 2, 1, "inverso")
            c.texto(x, y, rotulo, "inverso")
        else:
            c.texto(x, y, rotulo, "tenue")
        x += len(rotulo) + 3


def titulo(c: Lienzo, x: int, y: int, ancho: int, texto: str) -> None:
    """`━━━ TEXTO ━━━`: el encabezado de sección del Pip-Boy."""
    c.texto(x, y, texto.upper(), "pico")
    resto = ancho - len(texto) - 1
    if resto > 0:
        c.texto(x + len(texto) + 1, y, "━" * resto, "tenue")


def regla(c: Lienzo, x: int, y: int, ancho: int, marcas: int = 5) -> None:
    """Regla de escala con sus divisiones: `└──┴──┘`."""
    c.texto(x, y, "└" + "─" * (ancho - 2) + "┘", "tenue")
    for indice in range(1, marcas):
        columna = x + round(ancho * indice / marcas)
        c.texto(columna, y, "┴", "tenue")


def barra_fosforo(c: Lienzo, x: int, y: int, etiqueta: str, valor: float,
                  celdas: int) -> None:
    """Barra del Pip-Boy: llena `█`, vacía `·`, con la cifra siempre escrita."""
    c.texto(x, y, etiqueta, "claro")
    dentro = round(max(0.0, min(1.0, valor)) * celdas)
    c.texto(x + len(etiqueta) + 1, y, "█" * dentro + "·" * (celdas - dentro), "pico")
    c.texto(x + len(etiqueta) + celdas + 2, y, f"{int(valor * 100):3d} %", "claro")


def linea(c: Lienzo, x: int, y: int, etiqueta: str, valor: str, ancho: int = 20) -> None:
    c.texto(x, y, etiqueta, "tenue")
    c.texto(x + ancho, y, valor, "claro")


def pie(c: Lienzo, teclas: list[tuple[str, str]]) -> None:
    x = 3
    for tecla, accion in teclas:
        c.texto(x, ALTO - 2, f"[{tecla}]", "pico")
        x += len(tecla) + 2
        c.texto(x, ALTO - 2, accion + "   ", "tenue")
        x += len(accion) + 3


# ---------------------------------------------------------------------------
# 01 · STATS — el muñeco, tal cual
# ---------------------------------------------------------------------------
def pantalla_stats(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "STATS", "RAM 58.30 % · SWP 26.60 % · CPU 4.08 %")
    pestanas(c, ["STATS", "ITEMS", "DATA"], 0)

    # --- columna izquierda: radiación y salud -------------------------------
    c.texto(3, 5, "RAD", "tenue")
    c.texto(7, 5, "█" * 4 + "·" * 6, "pico")
    c.texto(3, 7, "HP", "tenue")
    c.texto(7, 7, "█" * 9 + "·", "pico")
    c.texto(18, 7, "94/100", "claro")
    c.texto(3, 9, "AP", "tenue")
    c.texto(7, 9, "█" * 7 + "·" * 3, "pico")
    c.texto(18, 9, "72/100", "claro")

    # --- el muñeco, centrado y con sitio propio ----------------------------
    muñeco = [
        "     ▄▄▄▄▄     ",
        "    █▀▀▀▀▀█    ",
        "    █ ◉ ◉ █    ",
        "    █  ▿  █    ",
        "     ▀▀▀▀▀     ",
        "   ▄▄█▀▀▀█▄▄   ",
        "  ███████████  ",
        "  █ ███████ █  ",
        "  █ ███████ █  ",
        "    ███████    ",
        "    ███████    ",
        "     ██ ██     ",
        "     ██ ██     ",
        "    ▄██ ██▄    ",
    ]
    for indice, fila in enumerate(muñeco):
        c.texto(40, 5 + indice, fila, "pico")

    # --- etiquetas a los dos lados del muñeco ------------------------------
    izquierda = [("SHUT DOWN", "Today", 0.18, "3"), ("RESTART", "", 0.10, "1"),
                 ("SLEEP", "", 0.26, "5")]
    for indice, (nombre, sub, valor, cifra) in enumerate(izquierda):
        fila = 6 + indice * 4
        c.texto(26, fila, nombre, "claro")
        if sub:
            c.texto(26, fila + 1, sub, "tenue")
            fila += 1
        c.texto(26, fila + 1, "█" * round(valor * 12) + "·" * (12 - round(valor * 12)), "pico")
        c.texto(39, fila + 1, cifra, "tenue")

    derecha = [("Sunday", 0.62, "9"), ("Saturday", 0.44, "7"), ("Friday", 0.72, "2")]
    for indice, (nombre, valor, cifra) in enumerate(derecha):
        fila = 6 + indice * 4
        c.texto(58, fila, nombre, "claro")
        c.texto(58, fila + 1, "█" * round(valor * 12) + "·" * (12 - round(valor * 12)), "pico")
        c.texto(71, fila + 1, cifra, "tenue")

    c.texto(76, 7, "█ GMAIL", "claro")
    c.texto(76, 8, "█" * 12 + "·" * 6, "pico")
    c.texto(76, 10, "█ DIARIO", "claro")
    c.texto(76, 11, "█" * 7 + "·" * 11, "pico")

    # --- barra PWR con su escala, como en la captura -----------------------
    c.texto(57, 19, "50 %", "tenue")
    c.texto(80, 19, "100 %", "tenue")
    regla(c, 36, 21, 52, 4)
    c.texto(84, 21, "▲", "pico")
    c.texto(36, 22, "PWR", "claro")
    c.texto(41, 22, "184/200", "pico")
    c.texto(52, 22, "consumo 0.6 kW", "tenue")

    # --- estado, abajo a la izquierda --------------------------------------
    titulo(c, 3, 18, 30, "estado")
    linea(c, 3, 19, "salud", "ESTABLE", 12)
    linea(c, 3, 20, "radiación", "12 RAD", 12)
    linea(c, 3, 21, "hambre", "—", 12)
    linea(c, 3, 22, "sueño", "—", 12)
    linea(c, 3, 23, "efectos", "2 activos", 12)
    pie(c, [("A/D", "pestaña"), ("↑↓", "selección"), ("TAB", "subpestaña"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 02 · ITEMS · inventario
# ---------------------------------------------------------------------------
def pantalla_items(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "ITEMS", "PESO 84.5 / 150 · CAPS 1 284")
    pestanas(c, ["STATS", "ITEMS", "DATA"], 1)

    # tabla: nombre 3-32, PESO 38-43, VALOR 45-50, CANT 52-55
    titulo(c, 3, 5, 33, "armas")
    c.texto(38, 5, "PESO", "tenue")
    c.texto(45, 5, "VALOR", "tenue")
    c.texto(52, 5, "CANT", "tenue")
    armas = [("RIFLE DE CAZA", 4.0, 32, 1), ("PISTOLA 10MM", 3.0, 95, 1),
             ("CUCHILLO DE COMBATE", 1.0, 25, 2), ("GRANADA DE FRAG.", 0.5, 40, 3)]
    for indice, (nombre, peso, valor, cant) in enumerate(armas):
        fila = 6 + indice
        c.texto(3, fila, nombre, "claro")
        c.texto(38, fila, f"{peso:4.1f}".rjust(6), "tenue")
        c.texto(45, fila, str(valor).rjust(6), "pico")
        c.texto(52, fila, str(cant).rjust(4), "claro")

    titulo(c, 3, 11, 33, "munición")
    c.texto(38, 11, "PESO", "tenue")
    c.texto(52, 11, "CANT", "tenue")
    for indice, (nombre, cant, peso) in enumerate(((".308", 24, 0.1), ("10mm", 68, 0.1),
                                                   ("célula", 12, 0.4))):
        fila = 12 + indice
        c.texto(3, fila, nombre, "claro")
        c.texto(38, fila, f"{peso:4.1f}".rjust(6), "tenue")
        c.texto(52, fila, str(cant).rjust(4), "pico")

    titulo(c, 3, 16, 33, "auxilio")
    c.texto(38, 16, "PESO", "tenue")
    c.texto(52, 16, "CANT", "tenue")
    for indice, (nombre, cant) in enumerate((("STIMPAK", 6), ("RAD-AWAY", 3), ("NUKA-COLA", 8))):
        fila = 17 + indice
        c.texto(3, fila, nombre, "claro")
        c.texto(38, fila, "   0.5".rjust(6), "tenue")
        c.texto(52, fila, str(cant).rjust(4), "pico")

    barra_fosforo(c, 3, 22, "PESO", 0.56, 30)

    # panel derecho: objeto seleccionado (59-96, interior 60-95)
    c.texto(59, 5, "┌" + "─" * 36 + "┐", "tenue")
    for fila in range(6, 25):
        c.texto(59, fila, "│", "tenue")
        c.texto(96, fila, "│", "tenue")
    c.texto(59, 25, "└" + "─" * 36 + "┘", "tenue")
    c.texto(61, 6, "RIFLE DE CAZA", "pico")
    c.texto(61, 7, "arma · dos manos", "tenue")
    c.texto(61, 9, "DAÑO      24", "tenue")
    c.texto(61, 10, "██████████····", "pico")
    c.texto(61, 12, "ALCANCE   68", "tenue")
    c.texto(61, 13, "███████·······", "pico")
    c.texto(61, 15, "CADENCIA   6", "tenue")
    c.texto(61, 16, "███···········", "pico")
    c.texto(61, 18, "Una carabina vieja,", "claro")
    c.texto(61, 19, "pero nunca falla.", "claro")
    c.texto(61, 21, "cargada: 5 / 5", "tenue")
    c.texto(61, 23, "valor venta 32 caps", "tenue")

    pie(c, [("↑↓", "objeto"), ("⏎", "usar/equipar"), ("X", "soltar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 03 · DATA · misiones
# ---------------------------------------------------------------------------
def pantalla_data(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "DATA", "MISIONES 3 / 12 · DÍA 2041")
    pestanas(c, ["STATS", "ITEMS", "DATA"], 2)

    titulo(c, 3, 5, 94, "misiones activas")
    misiones = [
        ("[ ]", "LA FUENTE DE LA VIDA", "refugio 101", "60 %", "habla con el alcalde"),
        ("[>]", "SANGRE LLAMANDO", "torres de megatón", "25 %", "sube a la antena"),
        ("[ ]", "EL ÁRBOL DE LA CIUDAD", "harold", "10 %", "riega el árbol"),
    ]
    for indice, (marca, nombre, donde, avance, nota) in enumerate(misiones):
        fila = 6 + indice * 4
        c.texto(3, fila, marca, "pico")
        c.texto(7, fila, nombre, "claro")
        c.texto(7, fila + 1, donde, "tenue")
        c.texto(30, fila + 1, "█" * round(int(avance[:-2]) / 10) + "·" * (10 - round(int(avance[:-2]) / 10)), "pico")
        c.texto(42, fila + 1, avance, "claro")
        c.texto(7, fila + 2, nota, "tenue")

    titulo(c, 3, 18, 94, "registro")
    registro = [
        ("2041.05.12", "saliste del refugio 101", "claro"),
        ("2041.05.13", "llegaste a megatón", "claro"),
        ("2041.05.14", "mataste un saqueador", "pico"),
        ("2041.05.14", "Buen Karma +2", "claro"),
        ("2041.05.15", "encontraste a tres perros", "tenue"),
    ]
    for indice, (fecha, texto, estilo) in enumerate(registro):
        c.texto(3, 19 + indice, fecha, "tenue")
        c.texto(15, 19 + indice, texto, estilo)

    c.texto(62, 19, "KARMA", "tenue")
    c.texto(62, 20, "███" + "·" * 17, "pico")
    c.texto(62, 21, "BUENO", "claro")
    c.texto(62, 23, "NIVEL 4", "pico")
    c.texto(62, 24, "xp 1 240 / 2 500", "tenue")
    pie(c, [("↑↓", "misión"), ("⏎", "marcar"), ("D", "diario"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 04 · RADIO
# ---------------------------------------------------------------------------
def pantalla_radio(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "RADIO", "SEÑAL 62 % · BANDA FM")
    pestanas(c, ["STATS", "ITEMS", "DATA", "RADIO"], 3)

    titulo(c, 3, 5, 94, "emisoras")
    emisoras = [("GALAXY NEWS", "noticias", True, 0.62),
                ("DIAMOND CITY RADIO", "música", False, 0.45),
                ("ENCLAVE RADIO", "propaganda", False, 0.30),
                ("— estática —", "", False, 0.18)]
    for indice, (nombre, tipo, activa, senal) in enumerate(emisoras):
        fila = 6 + indice * 3
        if activa:
            c.relleno(2, fila, 96, 1, "inverso")
            c.texto(3, fila, "> " + nombre, "inverso")
            c.texto(30, fila, tipo, "inverso")
            c.texto(52, fila, "SONANDO", "inverso")
        else:
            c.texto(3, fila, "  " + nombre, "claro" if "—" not in nombre else "tenue")
            c.texto(30, fila, tipo, "tenue")
        llenos = round(senal * 20)
        c.texto(3, fila + 1, "█" * llenos + "·" * (20 - llenos), "pico" if activa else "tenue")
        c.texto(26, fila + 1, f"{int(senal * 100)} %".rjust(4), "tenue")

    titulo(c, 3, 19, 94, "ahora suena")
    c.texto(3, 20, "«I DON'T WANT TO SET THE WORLD ON FIRE»", "pico")
    c.texto(3, 21, "The Ink Spots · 1941 · 78 rpm", "tenue")
    regla(c, 3, 23, 56, 6)
    c.texto(3, 24, "01:12", "claro")
    c.texto(54, 24, "04:38", "claro")
    avance = round(56 * 72 / 278)
    c.texto(3, 25, "─" * avance + "█" + "─" * (55 - avance), "pico")
    pie(c, [("↑↓", "emisora"), ("⏎", "sintonizar"), ("M", "silenciar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 05 · STATUS · el muñeco con daño por zonas
# ---------------------------------------------------------------------------
def pantalla_status(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "STATUS", "CONDICIÓN 78 % · EFECTOS 2")
    pestanas(c, ["STATS", "ITEMS", "DATA", "STATUS"], 4)

    # muñeco a la izquierda, con las zonas marcadas
    cuerpo = [
        "     ▄▄▄▄▄     ",
        "    █▀▀▀▀▀█    ",
        "    █ ◉ ◉ █    ",
        "    █  ▿  █    ",
        "     ▀▀▀▀▀     ",
        "  ▄▄██▀▀▀██▄▄   ",
        " █████████████  ",
        " ██ ███████ ██  ",
        " ██ ███████ ██  ",
        "    ███████     ",
        "    ███████     ",
        "     ██ ██      ",
        "     ██ ██      ",
        "    ▄██ ██▄     ",
    ]
    for indice, fila in enumerate(cuerpo):
        c.texto(6, 5 + indice, fila, "pico")

    zonas = [("CABEZA", 0.92, "ok"), ("TORSO", 0.64, "mal"), ("BRAZO IZQ.", 0.88, "ok"),
             ("BRAZO DER.", 0.41, "mal"), ("PIERNA IZQ.", 0.79, "ok"),
             ("PIERNA DER.", 0.95, "ok")]
    for indice, (zona, valor, estado) in enumerate(zonas):
        fila = 5 + indice * 2
        c.texto(28, fila, zona.ljust(14), "tenue")
        lleno = round(valor * 12)
        c.texto(43, fila, "█" * lleno + "·" * (12 - lleno), "pico" if estado == "ok" else "alerta")
        c.texto(57, fila, f"{int(valor * 100):3d} %", "claro")
        if estado == "mal":
            c.texto(64, fila, "◄ herido", "alerta")

    titulo(c, 28, 18, 68, "efectos activos")
    efectos = [("RADIACIÓN", "12 RAD · -1 RESISTENCIA", "alerta"),
               ("HAMBRE", "leve · -1 CARISMA", "tenue")]
    for indice, (nombre, detalle, estilo) in enumerate(efectos):
        c.texto(28, 19 + indice * 2, nombre.ljust(14), "claro")
        c.texto(43, 19 + indice * 2, detalle, estilo)

    titulo(c, 28, 23, 68, "resistencia")
    resistencias = [("DAÑO", 12), ("RAD", 8), ("VENENO", 5)]
    for indice, (nombre, valor) in enumerate(resistencias):
        c.texto(28 + indice * 22, 24, nombre, "tenue")
        c.texto(28 + indice * 22, 25, "█" * valor + "·" * (12 - valor), "pico")
    pie(c, [("TAB", "zona"), ("⏎", "curar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 06 · ARRANQUE — el tubo encendiéndose
# ---------------------------------------------------------------------------
def pantalla_arranque(c: Lienzo) -> None:
    marco(c)
    cabecera(c, "ROBCO INDUSTRIES (TM) TERMLINK", "PIP-OS v7.1.0")

    # barra de degradado con bloques: lo más parecido a un fundido de fósforo
    c.texto(4, 4, "▒▒▓▓███" + "█" * 78 + "███▓▓▒▒", "pico")
    c.texto(4, 5, "·" * 26 + "▒▒▓▓███▓▓▒▒" + "·" * 26, "tenue")

    c.texto(30, 8, "R O B C O", "pico")
    c.texto(26, 9, "I N D U S T R I E S  (TM)", "claro")
    c.texto(24, 11, "TERMLINK PROTOCOL · v7.1.0", "tenue")

    titulo(c, 12, 14, 76, "inicializando")
    pasos = [("[OK]", "memoria base  640 K", "pico"),
             ("[OK]", "tubo de fósforo  verde", "pico"),
             ("[OK]", "enlace con el refugio 101", "pico"),
             ("[..]", "calibrando la aguja", "tenue")]
    for indice, (marca, texto, estilo) in enumerate(pasos):
        c.texto(16, 15 + indice, marca, estilo)
        c.texto(22, 15 + indice, texto, "claro" if estilo == "pico" else "tenue")

    c.texto(12, 21, "ULTIMA CONEXION: 23.10.2077", "tenue")
    c.texto(12, 22, "INTRODUCE LA CONTRASEÑA PARA CONTINUAR", "claro")
    c.texto(12, 24, "> ", "pico")
    pista = "".join("█" if pseudo(k * 7) > 0.55 else " " for k in range(1, 40))
    c.texto(14, 24, pista, "tenue")
    c.texto(12, 26, "el cursor parpadea 2 veces por segundo", "tenue")
    pie(c, [("⏎", "entrar"), ("ESC", "apagar"), ("F1", "ayuda")])


PANTALLAS = [
    ("01", "STATS", "El muñeco de los puntos de habilidad, dibujado con bloques, con "
     "sus etiquetas y su barra PWR con escala `└──┴──┘`, como la captura original.",
     pantalla_stats),
    ("02", "ITEMS", "Inventario con columnas de peso, valor y cantidad, y panel de "
     "detalle con barras de daño/alcance. La cifra siempre al lado de la barra.",
     pantalla_items),
    ("03", "DATA", "Misiones con casillas `[ ] [>]`, barra de avance y diario. "
     "El karma es la única línea que se permite un tono distinto: el pico.",
     pantalla_data),
    ("04", "RADIO", "Emisoras, señal medida y la canción sonando con su escala. "
     "La estática también es un estado de la interfaz, no un error.", pantalla_radio),
    ("05", "STATUS", "Daño por zonas: las heridas se marcan con `◄ herido` además de "
     "bajar el brillo. Sin color, la señal sigue estando.", pantalla_status),
    ("06", "Arranque", "El tubo calentando: degradado `▒▒▓▓███` y pasos de "
     "inicialización de una máquina que ya no existe.", pantalla_arranque),
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
:root{--fondo:#102e16;--tenue:#1c5626;--medio:#3d8a55;--claro:#64b887;--pico:#63e59f;
 --inverso-fg:#0b2010;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
html[data-pal="ambar"]{--fondo:#2a1c08;--tenue:#5a3d10;--medio:#9a6a20;--claro:#e0a648;--pico:#ffcf6a;--inverso-fg:#1a1004}
html[data-pal="azul"]{--fondo:#0a1a2e;--tenue:#123a5c;--medio:#2f6f9e;--claro:#7fc0e8;--pico:#a8e6ff;--inverso-fg:#06101c}
html[data-pal="mono"]{--fondo:#0d0f13;--tenue:#3a3f46;--medio:#7a828c;--claro:#c8ced6;--pico:#ffffff;--inverso-fg:#0d0f13}
*{box-sizing:border-box}
body{margin:0;background:#070c08;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:36px 0 24px;border-bottom:1px solid #15241a;margin-bottom:28px}
h1{margin:0 0 8px;font-size:27px;letter-spacing:-.02em}
h1 span{color:var(--pico);font-family:var(--mono)}
.sub{color:#7d8590;font-size:15px;line-height:1.68;margin:0;max-width:80ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#7d8590;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#101a13;color:#c9d1d9;border:1px solid #25382a;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 46px}
.head{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:var(--pico);border:1px solid #24402d;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#7d8590;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:90ch}
.nota code{font-family:var(--mono);background:#101a13;border:1px solid #1e2f24;border-radius:4px;padding:0 4px;color:#9fd8b0}
.term{background:var(--fondo);border-radius:10px;padding:12px 14px;overflow-x:auto;
 box-shadow:0 0 0 1px #21382a, inset 0 0 60px #050b07, 0 26px 60px -34px #000;position:relative}
.term pre{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.32;white-space:pre;color:var(--claro)}
.c-tenue{color:var(--tenue)}
.c-medio{color:var(--medio)}
.c-claro{color:var(--claro)}
.c-pico{color:var(--pico);text-shadow:0 0 6px currentColor}
.c-alerta{color:var(--pico);text-decoration:underline dotted}
.c-inverso{background:var(--pico);color:var(--inverso-fg)}
html[data-crt="1"] .term::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:10px;
 background:repeating-linear-gradient(to bottom,rgba(0,0,0,.22) 0 1px,transparent 1px 3px)}
html[data-crt="1"] .term::before{content:"";position:absolute;inset:0;pointer-events:none;border-radius:10px;
 background:radial-gradient(ellipse at center,transparent 52%,rgba(0,0,0,.55) 100%)}
footer{color:#7d8590;font-size:13.5px;line-height:1.75;border-top:1px solid #15241a;padding-top:20px}
footer code{font-family:var(--mono);background:#101a13;border:1px solid #1e2f24;border-radius:4px;padding:1px 5px;color:#a9b6c9}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #15241a;vertical-align:top}
th{color:#7d8590;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:var(--claro);font-size:12.5px}
.swatch{display:inline-block;width:13px;height:13px;border-radius:3px;vertical-align:-2px;margin-right:7px;box-shadow:0 0 0 1px #ffffff18}
.aviso{background:#0b1410;border-left:3px solid var(--pico);padding:13px 16px;border-radius:0 7px 7px 0;
 color:#96a4b2;font-size:13.5px;line-height:1.68;margin-top:16px}
"""

JS = """
const pal=document.getElementById('pal'),crt=document.getElementById('crt');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
crt.addEventListener('change',e=>document.documentElement.dataset.crt=e.target.checked?'1':'0');
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
    for nombre, clave in (("fondo del tubo", "fondo"), ("fósforo tenue", "tenue"),
                          ("fósforo medio", "medio"), ("fósforo claro", "claro"),
                          ("pico de brillo", "pico")):
        hexa = FOSFORO[clave]
        filas_color += (f'<tr><td><span class="swatch" style="background:{hexa}"></span>'
                        f'<code>{hexa}</code></td><td>{nombre}</td></tr>')

    paletas = [("fosforo", "Fósforo verde"), ("ambar", "Ámbar"), ("azul", "Azul"),
               ("mono", "Sin color")]
    opciones = "".join(f'<option value="{v}">{n}</option>' for v, n in paletas)
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="fosforo" data-crt="0">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ROBCO TERMLINK · TUI tipo Pip-Boy</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>ROBCO TERMLINK <span>· TUI tipo Pip-Boy</span></h1>
  <p class="sub">Seis pantallas en <strong>100 × 30 celdas</strong> con un solo fósforo y
  cinco niveles de brillo. Aquí no hay acentos de color: la jerarquía se hace
  <em>subiendo o bajando el brillo</em>, como en un tubo de rayos catódicos de verdad.
  Los verdes están <strong>medidos</strong> sobre una captura real del Pip-Boy 3000.</p>
  <div class="controls">
    <label>Paleta <select id="pal">{opciones}</select></label>
    <label><input type="checkbox" id="crt"> efecto CRT (solo aquí, no es del TUI)</label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>El fósforo, medido</h2></div>
  <p class="nota">Se contaron los píxeles verdes de la captura y se ordenaron por
  brillo. Los cinco niveles del sistema salen de esos percentiles: no se eligió ningún
  color a ojo.</p>
  <table>
    <tr><th>Medido</th><th>Uso</th></tr>
    {filas_color}
  </table>
  <div class="aviso"><strong>Lo que no se puede copiar de un tubo:</strong> el
  <em>bloom</em> (el halo que sangra alrededor de las letras), la curvatura del cristal,
  las líneas de barrido y el parpadeo. Un terminal puede simular el color, no la
  óptica. El brillo de fósforo y el CRT de esta página son decoración de la galería y
  vienen apagados por eso. Lo que sí es del diseño: un solo tono, cinco niveles, y
  todo el texto legible sin depender del color.</div>
</section>
<footer>
  Generado por <code>pipboy/pipboy.py</code> · motor de celdas en
  <code>mockups/celdas.py</code> · solo biblioteca estándar.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


def _rgb(hexa: str) -> str:
    return f"{int(hexa[1:3], 16)};{int(hexa[3:5], 16)};{int(hexa[5:7], 16)}"


ANSI = {
    "": f"\x1b[38;2;{_rgb(FOSFORO['claro'])};48;2;{_rgb(FOSFORO['fondo'])}m",
    "tenue": f"\x1b[38;2;{_rgb(FOSFORO['tenue'])};48;2;{_rgb(FOSFORO['fondo'])}m",
    "medio": f"\x1b[38;2;{_rgb(FOSFORO['medio'])};48;2;{_rgb(FOSFORO['fondo'])}m",
    "claro": f"\x1b[38;2;{_rgb(FOSFORO['claro'])};48;2;{_rgb(FOSFORO['fondo'])}m",
    "pico": f"\x1b[1;38;2;{_rgb(FOSFORO['pico'])};48;2;{_rgb(FOSFORO['fondo'])}m",
    "alerta": f"\x1b[4;38;2;{_rgb(FOSFORO['pico'])};48;2;{_rgb(FOSFORO['fondo'])}m",
    "inverso": f"\x1b[1;38;2;11;32;16;48;2;{_rgb(FOSFORO['pico'])}m",
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
    (destino / "pipboy.html").write_text(construir_html(pantallas), encoding="utf-8")
    with open(destino / "pipboy.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    anchos = {len(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · máx. {max(anchos)} columnas · "
          f"0 de doble ancho → pipboy.html y pipboy.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
