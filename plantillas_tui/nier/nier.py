#!/usr/bin/env python3
"""Mockups de una TUI tipo NieR: Automata, todo en matriz de puntos (Braille).

Paleta **medida** sobre dos capturas reales: el menú ITEM y el minijuego de
hackeo de 9S.

    papel          #c7c2aa     tinta          #504d44
    tinta tenue    #a7a28d     linea          #d4ceb5
    barra de sel.  #49463e     naranja        #f1954c
    morado         #451f4e     blanco         #dfdcd3

Es la primera serie **clara**: papel beige con tinta oscura. No hay fósforo ni
cristal; hay impresión.

Todo se dibuja con puntos: una celda de terminal con un carácter Braille son
2 × 4 puntos, así que 100 × 30 celdas son 200 × 120 puntos. El texto usa una
fuente 5 × 7 sin tildes — es una fuente de panel, y los paneles de puntos no
tienen tildes.

    python3 nier/nier.py            # nier.html y nier.txt
    python3 nier/nier.py --ansi     # pinta las pantallas en tu terminal
    python3 nier/nier.py --png      # vistas previas en nier/vista/
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402
from nier.braille import Puntos, fondo_rejilla  # noqa: E402

ANCHO, ALTO = 200, 120          # en puntos
CELDAS_X, CELDAS_Y = ANCHO // 2, ALTO // 4

#: Medidos sobre las capturas (ver docstring). La retícula usa el tenue medido.
PAPEL = {
    "papel": "#c3bea6",      # medido, con el margen un punto más bajo
    "tinta": "#504d44",      # medido en la pestaña activa
    "tinta2": "#7e7b6b",     # medido en el título ITEM
    "linea": "#d4ceb5",      # medido en el borde de panel
    "sel": "#49463e",        # medido en la barra de selección
    "naranja": "#f1954c",    # medido en las balas del hackeo
    "morado": "#451f4e",     # medido en las balas lentas
    "blanco": "#dfdcd3",     # medido en los cubos enemigos
    "rejilla": "#b1ac96",    # derivado: retícula entre papel y tenue
}


# ---------------------------------------------------------------------------
# mobiliario en puntos
# ---------------------------------------------------------------------------
def marco(p: Puntos) -> None:
    fondo_rejilla(p, "rejilla", paso=6)
    p.caja(2, 2, ANCHO - 4, ALTO - 4, "linea")


def regla(p: Puntos, y: int, x0: int = 8, x1: int = ANCHO - 8) -> None:
    for x in range(x0, x1, 2):
        p.punto(x, y, "tinta2")


def rotulo(p: Puntos, x: int, y: int, texto: str, color: str = "tinta") -> int:
    return p.texto(x, y, texto, color)


def etiqueta(p: Puntos, x: int, y: int, texto: str) -> int:
    """Rótulo pequeño en tenue, el de los paneles del menú."""
    return p.texto(x, y, texto, "tinta2")


def barra_puntos(p: Puntos, x: int, y: int, largo: int, valor: float,
                 color: str = "tinta", paso: int = 3) -> None:
    for indice in range(largo):
        p.relleno(x + indice * paso, y, 3, 3, color if indice / largo < valor else "linea")


# ---------------------------------------------------------------------------
# 01 · MENÚ · ITEM
# ---------------------------------------------------------------------------
def pantalla_menu(p: Puntos) -> None:
    marco(p)
    for nombre, x in (("MAPA", 10), ("MISION", 40), ("OBJETO", 86),
                      ("ARMA", 134), ("DATOS", 164)):
        if nombre == "OBJETO":
            p.relleno(x - 4, 5, p.ancho_texto(nombre) + 8, 11, "sel")
            p.texto(x, 7, nombre, None)
        else:
            p.texto(x, 7, nombre, "tinta2")

    p.texto(10, 24, "ITEM", "tinta", escala=2)
    p.texto(10, 44, "OBJETO", "tinta2")
    p.texto(96, 24, "2B", "tinta")
    p.texto(120, 24, "N5", "tinta2")
    p.texto(140, 24, "HP 4062", "tinta2")

    p.caja(8, 54, 100, 50, "linea")
    for indice, (nombre, cantidad) in enumerate((("RECUPERAR", "05"), ("RECUPERAR", "12"),
                                                 ("CHIP ATAQ.", "1"), ("DATOS", "01"))):
        fila = 58 + indice * 10
        if indice == 1:
            p.relleno(9, fila - 2, 98, 10, "sel")
            p.texto(12, fila, nombre, None)
            p.texto(94, fila, cantidad, None)
        else:
            p.texto(12, fila, nombre, "tinta")
            p.texto(94, fila, cantidad, "tinta2")

    p.caja(112, 54, 80, 50, "linea")
    p.texto(116, 58, "RECUPERAR 12", "tinta")
    p.rombo(172, 76, 8, "tinta")
    p.texto(116, 82, "HP +50", "tinta")
    p.texto(116, 90, "POR USO", "tinta2")
    p.texto(116, 96, "T 5/99", "tinta2")

    regla(p, 108)
    p.texto(8, 110, "ELIGE UN OBJETO", "tinta2")
    p.circulo(104, 113, 3, "tinta")
    p.texto(110, 110, "ELEGIR", "tinta")
    p.linea(150, 110, 155, 115, "tinta")
    p.linea(155, 110, 150, 115, "tinta")
    p.texto(160, 110, "VOLVER", "tinta")


# ---------------------------------------------------------------------------
# 02 · HACKEO
# ---------------------------------------------------------------------------
def pantalla_hackeo(p: Puntos) -> None:
    marco(p)
    p.texto(10, 8, "HACKEO", "tinta")
    p.texto(168, 8, "9S", "tinta")
    p.texto(10, 18, "NIVEL 2", "tinta2")

    # anillo del objetivo y sus cuatro marcas
    p.circulo(58, 58, 30, "tinta2")
    for x, y, dx, dy in ((58, 22, 0, 3), (58, 94, 0, -3), (22, 58, 3, 0), (94, 58, -3, 0)):
        p.linea(x, y, x + dx, y + dy, "tinta")

    # enemigos: relleno claro y contorno tenue (el blanco no contrasta con papel)
    for x, y, lado in ((22, 34, 12), (76, 30, 12), (30, 70, 14), (76, 66, 12)):
        p.relleno(x, y, lado, lado, "blanco")
        p.caja(x, y, lado, lado, "tinta2")

    # la nave y su estela
    p.triangulo(50, 54, 9, "tinta")
    for indice, (x, y) in enumerate(((64, 54), (70, 51), (76, 47), (82, 42),
                                     (87, 36), (91, 29), (94, 22), (96, 15))):
        p.relleno(x, y, 3, 3, "naranja" if indice % 3 else "morado")
    for x, y in ((44, 70), (38, 76), (30, 80), (22, 82)):
        p.relleno(x, y, 3, 3, "morado")

    # el jefe, abajo a la derecha del recuadro de juego
    p.relleno(84, 72, 20, 20, "blanco")
    p.caja(84, 72, 20, 20, "tinta")
    p.caja(80, 68, 28, 28, "tinta2")

    # panel de lectura
    p.caja(126, 22, 66, 78, "linea")
    p.texto(130, 26, "OBJETIVO", "tinta2")
    p.texto(130, 34, "MAQUINA", "tinta")
    p.texto(130, 42, "GRANDE", "tinta")
    p.texto(130, 56, "ESCUDO", "tinta2")
    barra_puntos(p, 130, 64, 12, 0.62)
    p.texto(130, 74, "62%", "tinta")
    p.texto(130, 88, "TIEMPO", "tinta2")
    p.texto(130, 96, "00:14", "tinta")

    regla(p, 104)
    p.texto(10, 108, "REPETIR", "tinta2")
    p.texto(60, 108, "SALIR", "tinta2")
    p.circulo(104, 111, 3, "tinta")
    p.texto(110, 108, "DISPARAR", "tinta")


# ---------------------------------------------------------------------------
# 03 · CHIPS
# ---------------------------------------------------------------------------
def pantalla_chips(p: Puntos) -> None:
    marco(p)
    p.texto(10, 10, "CHIP", "tinta", escala=2)
    p.texto(74, 20, "INSTALAR", "tinta2")

    # tablero 5 × 3 de rombos
    for fila in range(3):
        for columna in range(5):
            cx, cy = 22 + columna * 21, 42 + fila * 20
            activo = (fila + columna) % 3 != 2
            p.rombo(cx, cy, 7, "tinta" if activo else "tinta2", relleno=activo)
            if (fila, columna) == (1, 2):
                p.rombo(cx, cy, 10, "naranja")

    # lista y costes
    for indice, (nombre, coste, activo) in enumerate(
            (("ATAQUE +6", "21", True), ("SALUD +4", "14", True), ("EVASION", "09", True),
             ("PUNTERIA", "07", True), ("RUIDO", "03", False))):
        fila = 30 + indice * 10
        p.texto(128, fila, nombre, "tinta2" if not activo else "tinta")
        p.texto(186, fila, coste, "tinta2" if not activo else "tinta")

    regla(p, 86)
    p.texto(10, 92, "CAPACIDAD", "tinta2")
    p.texto(70, 92, "62 / 84", "tinta")
    barra_puntos(p, 10, 102, 46, 0.74, paso=3)
    p.texto(10, 110, "NO CABEN TODOS JUNTOS", "tinta2")


# ---------------------------------------------------------------------------
# 04 · MAPA
# ---------------------------------------------------------------------------
def pantalla_mapa(p: Puntos) -> None:
    marco(p)
    p.texto(10, 8, "MAPA", "tinta")
    p.texto(10, 18, "CIUDAD EN RUINAS", "tinta2")

    zonas = [("RUINAS", 14, 30, 44, 26), ("LLANO", 66, 30, 44, 26),
             ("PARQUE", 14, 66, 44, 26), ("FABRICA", 66, 66, 44, 26)]
    for nombre, x, y, ancho, alto in zonas:
        p.caja(x, y, ancho, alto, "tinta2")
        p.texto(x + (ancho - p.ancho_texto(nombre)) // 2, y + 14, nombre, "tinta")

    # caminos punteados entre centros de zona
    for (xa, ya), (xb, yb) in (((58, 43), (66, 43)), ((36, 56), (36, 66)),
                               ((88, 56), (88, 66)), ((58, 79), (66, 79))):
        pasos = max(abs(xb - xa), abs(yb - ya))
        for paso in range(0, pasos, 4):
            p.punto(xa + (xb - xa) * paso // pasos, ya + (yb - ya) * paso // pasos, "tinta2")

    p.triangulo(30, 38, 9, "tinta")          # el jugador
    for x, y in ((92, 38), (92, 74), (40, 74)):
        p.caja(x, y, 5, 5, "tinta")          # máquinas
    p.circulo(100, 36, 4, "naranja")          # punto de acceso

    p.caja(126, 30, 66, 62, "linea")
    p.triangulo(132, 36, 7, "tinta")
    p.texto(142, 36, "TU", "tinta2")
    p.caja(132, 50, 5, 5, "tinta")
    p.texto(142, 50, "MAQUINA", "tinta2")
    p.circulo(135, 66, 3, "naranja")
    p.texto(142, 64, "ACCESO", "tinta2")
    p.texto(132, 78, "SECTOR", "tinta2")
    p.texto(132, 86, "F-3", "tinta")

    regla(p, 104)
    p.texto(10, 108, "MOVER", "tinta2")
    p.texto(70, 108, "VIAJAR", "tinta2")
    p.texto(130, 108, "LEYENDA", "tinta2")


# ---------------------------------------------------------------------------
# 05 · MÁQUINA
# ---------------------------------------------------------------------------
def pantalla_maquina(p: Puntos) -> None:
    marco(p)
    p.texto(10, 8, "MAQUINA", "tinta")
    p.texto(10, 16, "CLASE PEQUENA", "tinta2")

    # cuerpo: cabeza redonda, dos ojos huecos, tronco y extremidades
    p.circulo(56, 46, 22, "tinta", relleno=True)
    for x in (48, 66):
        p.circulo(x, 40, 7, None, relleno=True)
        p.circulo(x, 40, 7, "tinta2")
    p.relleno(34, 68, 44, 20, "tinta")
    p.circulo(44, 92, 10, "tinta", relleno=True)
    p.circulo(66, 92, 10, "tinta", relleno=True)
    p.circulo(22, 74, 7, "tinta", relleno=True)
    p.circulo(90, 74, 7, "tinta", relleno=True)

    for x in range(14, 104, 3):              # línea de escaneo
        p.punto(x, 46, "naranja")
    for x, y, sx, sy in ((10, 24, 1, 1), (102, 24, -1, 1), (10, 104, 1, -1), (102, 104, -1, -1)):
        p.linea(x, y, x + 9 * sx, y, "tinta2")   # corchetes de escaneo
        p.linea(x, y, x, y + 9 * sy, "tinta2")

    p.caja(122, 22, 70, 84, "linea")
    p.texto(126, 26, "MAQUINA", "tinta")
    p.texto(126, 34, "PEQUENA", "tinta2")
    p.texto(126, 50, "HP", "tinta2")
    barra_puntos(p, 126, 58, 14, 0.35, color="naranja")
    p.texto(126, 68, "35%", "tinta")
    p.texto(126, 78, "HOSTIL", "tinta")
    p.texto(126, 88, "SIN DATOS", "tinta2")

    regla(p, 104)
    p.texto(10, 108, "ESCANEAR", "tinta2")
    p.texto(64, 108, "ATACAR", "tinta2")
    p.texto(112, 108, "HUIR", "tinta2")


# ---------------------------------------------------------------------------
# 06 · TÍTULO
# ---------------------------------------------------------------------------
def pantalla_titulo(p: Puntos) -> None:
    import math

    fondo_rejilla(p, "rejilla", paso=6)
    p.circulo(100, 58, 52, "linea")
    p.circulo(100, 58, 53, "linea")
    p.texto(56, 18, "NIER", "tinta", escala=3)
    p.texto(112, 30, ":", "tinta", escala=3)
    p.texto(18, 46, "AUTOMATA", "tinta", escala=3)
    p.texto(18, 74, "VER 1.0", "tinta2")

    regla(p, 86, 20, 180)
    p.relleno(14, 91, 92, 12, "sel")
    p.texto(20, 94, "NUEVA PARTIDA", None)
    p.texto(20, 106, "CARGAR", "tinta2")
    p.texto(148, 106, "YORHA", "tinta2")

    for angulo in range(5):                  # flor de luna
        rad = math.radians(-90 + angulo * 72)
        p.circulo(int(168 + 9 * math.cos(rad)), int(92 + 9 * math.sin(rad)), 5, "tinta")
    p.circulo(168, 92, 3, "tinta", relleno=True)
    p.linea(168, 100, 168, 112, "tinta")
    p.linea(168, 108, 161, 103, "tinta")


PANTALLAS = [
    ("01", "Menú (ITEM)", "El menú de objetos. Todo está hecho de puntos: la retícula "
     "de fondo que NieR ya dibuja de verdad, los rótulos con la fuente 5 × 7 y la fila "
     "elegida en vídeo inverso, que en Braille son puntos apagados dentro de una barra "
     "encendida.", pantalla_menu),
    ("02", "Hackeo", "El minijuego de 9S. La nave es un triángulo de puntos, las balas "
     "son puntos naranjas y morados, y los enemigos se ven por el contorno porque el "
     "blanco medido sobre papel beige no tiene contraste: eso es una limitación real del "
     "medio, no un descuido.", pantalla_hackeo),
    ("03", "Chips", "El tablero de chips en rombos, con el seleccionado marcado en "
     "naranja, la lista de costes y la barra de capacidad. Los rombos son la prueba de "
     "que el medio sirve para formas, no solo para letras.", pantalla_chips),
    ("04", "Mapa", "Las zonas de la ciudad en cajas de un punto, los caminos punteados "
     "y la leyenda. Un mapa es lo que peor lleva el Braille: las etiquetas tienen que ir "
     "en la fuente de puntos y caben pocas letras, así que las zonas se llaman con una "
     "palabra.", pantalla_mapa),
    ("05", "Máquina", "Una máquina pequeña dibujada con círculos rellenos y dos ojos "
     "huecos, atravesada por la línea de escaneo. Es la pantalla que demuestra que el "
     "dot matrix puede ser orgánico y no solo técnico.", pantalla_maquina),
    ("06", "Título", "La portada: el título a escala 3, el círculo de la luna y una flor "
     "de luna dibujada con puntos. Escala 3 son 15 × 21 puntos por letra; más grande no "
     "cabe, y eso también es información sobre el medio.", pantalla_titulo),
]


# ---------------------------------------------------------------------------
# salida
# ---------------------------------------------------------------------------
def construir() -> list[tuple[str, str, str, Lienzo, Puntos]]:
    salida, fallos, choques = [], [], {}
    for numero, nombre, nota, funcion in PANTALLAS:
        puntos = Puntos(ANCHO, ALTO)
        funcion(puntos)
        lienzo = puntos.a_lienzo()
        fallos.extend(f"[{numero}] {fallo}" for fallo in puntos.fallos)
        if puntos.avisos:
            choques[numero] = puntos.avisos
        salida.append((numero, nombre, nota, lienzo, puntos))
    if fallos:
        raise SystemExit("\n".join(fallos[:20]))
    for numero, avisos in choques.items():
        print(f"[{numero}] {len(avisos)} celdas con dos colores → "
              f"{'; '.join(avisos[:3])}", file=sys.stderr)
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
    salida = []
    for indice, trozo in enumerate(trozos):
        salida.append(f"<code>{html.escape(trozo)}</code>" if indice % 2 else html.escape(trozo))
    return "".join(salida)


def preview(puntos: Puntos, destino: Path, escala: int = 5) -> None:
    """Vuelca la matriz de puntos a PNG: la única forma honesta de revisarla a ojo."""
    from PIL import Image, ImageDraw

    imagen = Image.new("RGB", (ANCHO * escala, ALTO * escala), PAPEL["papel"])
    lapiz = ImageDraw.Draw(imagen)
    for y in range(ALTO):
        for x in range(ANCHO):
            color = puntos.rejilla[y][x]
            if color is None:
                continue
            if color == "rejilla":
                color = "tinta2"
            fila = PAPEL[color]
            rgb = (int(fila[1:3], 16), int(fila[3:5], 16), int(fila[5:7], 16))
            lapiz.rectangle((x * escala, y * escala,
                             x * escala + escala - 2, y * escala + escala - 2), fill=rgb)
    destino.parent.mkdir(parents=True, exist_ok=True)
    imagen.save(destino)


CSS = """
:root{--papel:#c7c2aa;--tinta:#504d44;--tinta2:#a7a28d;--linea:#d4ceb5;--sel:#49463e;
 --naranja:#f1954c;--morado:#451f4e;--blanco:#dfdcd3;--rejilla:#a7a28d;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
/* la misma paleta invertida: no está medida, son los dos LED de siempre */
html[data-pal="ambar"]{--papel:#140f08;--tinta:#f1954c;--tinta2:#8a5a2a;--linea:#3a2716;
 --sel:#f1954c;--naranja:#ffd08a;--morado:#7a3f80;--blanco:#3a2716;--rejilla:#3a2716}
html[data-pal="verde"]{--papel:#08130c;--tinta:#5fd78a;--tinta2:#2c6b43;--linea:#16331f;
 --sel:#5fd78a;--naranja:#a8ffc4;--morado:#3f7a80;--blanco:#16331f;--rejilla:#16331f}
*{box-sizing:border-box}
body{margin:0;background:#111110;color:#c9c6bb;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:36px 0 24px;border-bottom:1px solid #2a2a26;margin-bottom:28px}
h1{margin:0 0 8px;font-size:27px;letter-spacing:-.02em}
h1 span{color:var(--naranja);font-family:var(--mono)}
.sub{color:#8f8d83;font-size:15px;line-height:1.68;margin:0;max-width:82ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#8f8d83;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#1b1b18;color:#c9c6bb;border:1px solid #33332d;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 46px}
.head{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:var(--naranja);border:1px solid #33332d;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#8f8d83;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:92ch}
.nota code{font-family:var(--mono);background:#1b1b18;border:1px solid #2c2c27;border-radius:4px;padding:0 4px;color:#e0b98f}
.term{background:var(--papel);border-radius:6px;padding:14px 16px;overflow-x:auto;
 box-shadow:0 0 0 1px #00000030, 0 22px 50px -30px #000;position:relative}
.term pre{margin:0;font-family:var(--mono);white-space:pre;color:var(--tinta);
 line-height:1.0;letter-spacing:0;font-size:var(--zoom,13px)}
.c-papel{color:var(--papel)}
.c-tinta{color:var(--tinta)}
.c-tinta2{color:var(--tinta2)}
.c-linea{color:var(--linea)}
.c-sel{color:var(--sel)}
.c-naranja{color:var(--naranja)}
.c-morado{color:var(--morado)}
.c-blanco{color:var(--blanco)}
.c-rejilla{color:var(--rejilla)}
.vista{border:1px solid #2a2a26;border-radius:6px;max-width:100%;height:auto;display:block}
footer{color:#8f8d83;font-size:13.5px;line-height:1.75;border-top:1px solid #2a2a26;padding-top:20px}
footer code{font-family:var(--mono);background:#1b1b18;border:1px solid #2c2c27;border-radius:4px;padding:1px 5px;color:#b8b4a4}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #2a2a26;vertical-align:top}
th{color:#8f8d83;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:#d8d4c4;font-size:12.5px}
.swatch{display:inline-block;width:13px;height:13px;border-radius:2px;vertical-align:-2px;margin-right:7px;box-shadow:0 0 0 1px #00000040}
.aviso{background:#1a1a16;border-left:3px solid var(--naranja);padding:13px 16px;border-radius:0 7px 7px 0;
 color:#a9a69b;font-size:13.5px;line-height:1.68;margin-top:16px}
"""

JS = """
const pal=document.getElementById('pal'),zoom=document.getElementById('zoom');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
zoom.addEventListener('input',e=>document.documentElement.style.setProperty('--zoom',e.target.value+'px'));
"""


def construir_html(pantallas) -> str:
    secciones = []
    for numero, nombre, nota, lienzo, _puntos in pantallas:
        filas = "\n".join(spans(fila) for fila in lienzo.rejilla)
        secciones.append(f"""
<section>
  <div class="head"><span class="num">{numero}</span><h2>{html.escape(nombre)}</h2></div>
  <p class="nota">{marcas(nota)}</p>
  <div class="term"><pre>{filas}</pre></div>
</section>""")

    filas_color = ""
    for clave, nombre, uso in (
            ("papel", "papel", "fondo del menú"), ("tinta", "tinta", "texto y formas"),
            ("tinta2", "tinta tenue", "rótulos y retícula"),
            ("linea", "línea", "bordes de panel"),
            ("sel", "selección", "barra del objeto elegido"),
            ("naranja", "naranja", "balas y resalte"),
            ("morado", "morado", "balas lentas"),
            ("blanco", "blanco", "enemigos del hackeo"),
            ("rejilla", "retícula (derivada)", "fondo de puntos")):
        hexa = PAPEL[clave]
        filas_color += (f'<tr><td><span class="swatch" style="background:{hexa}"></span>'
                        f'<code>{hexa}</code></td><td>{nombre}</td><td>{uso}</td></tr>')

    return f"""<!DOCTYPE html>
<html lang="es" data-pal="papel">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NIER:AUTOMATA · TUI en matriz de puntos</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>NIER:AUTOMATA <span>· TUI en matriz de puntos</span></h1>
  <p class="sub">Seis pantallas de <strong>100 × 30 celdas</strong>, que en Braille son
  <strong>200 × 120 puntos</strong>. No hay un solo carácter de texto: cada celda es un
  carácter Braille y cada letra está dibujada con una fuente 5 × 7 hecha a mano. Es la
  primera serie <strong>clara</strong> — papel beige y tinta oscura, sin fósforo ni
  cristal. Y es la primera en la que el contenido no se puede copiar: esto es imagen,
  no texto.</p>
  <div class="controls">
    <label>Paleta <select id="pal">
      <option value="papel">Papel (medido)</option>
      <option value="ambar">LED ámbar (invertida)</option>
      <option value="verde">LED verde (invertida)</option>
    </select></label>
    <label>Zoom <input type="range" id="zoom" min="9" max="22" value="13" step="1"
      style="width:120px"></label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>El color, medido · y lo que el medio no da</h2></div>
  <p class="nota">Los ocho primeros valores salen de dos capturas reales: el menú ITEM y
  el minijuego de hackeo de 9S. El noveno, la retícula de fondo, es <em>derivado</em> —
  un tono entre el papel y el tenue para que la retícula no compita con las letras — y va
  marcado como tal.</p>
  <table>
    <tr><th>Color</th><th>Nombre</th><th>Uso</th></tr>
    {filas_color}
  </table>
  <div class="aviso"><strong>Un color por celda, no por punto.</strong> Los ocho puntos
  de una celda Braille comparten el color de la celda, porque en una terminal el color es
  de la celda. Un panel RGB punto a punto no se puede. Donde dos colores caen en la misma
  celda, uno gana: el generador lo cuenta y falla si ocurre.</div>
  <div class="aviso"><strong>Sin fondo encendido.</strong> Braille enciende puntos sobre
  vacío; no apaga puntos sobre una superficie luminosa. Por eso el vídeo inverso se hace
  apagando puntos dentro de una barra encendida, y por eso los LED ámbar y verde del
  selector son una <em>inversión de la paleta medida</em>, no una medida aparte.</div>
  <div class="aviso"><strong>Sin multiplexado.</strong> El parpadeo de filas del display
  real, el sangrado del LED saturado y el halo no existen aquí. Los puntos son tan
  nítidos como la fuente del terminal.</div>
  <div class="aviso"><strong>El texto deja de ser texto.</strong> En Braille no se
  selecciona ni se copia, y la fuente no lleva tildes: es una fuente de panel. Esto es
  un salto de categoría respecto a las cinco series anteriores, que eran texto con
  adornos.</div>
</section>
<footer>
  Generado por <code>nier/nier.py</code> · lienzo de puntos en
  <code>nier/braille.py</code> · motor de celdas en <code>mockups/celdas.py</code> ·
  solo biblioteca estándar.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


def _rgb(hexa: str) -> str:
    return f"{int(hexa[1:3], 16)};{int(hexa[3:5], 16)};{int(hexa[5:7], 16)}"


ANSI = {
    clave: f"\x1b[38;2;{_rgb(PAPEL[clave])};48;2;{_rgb(PAPEL['papel'])}m"
    for clave in PAPEL
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
    problemas = [(num, p) for num, _, _, lienzo, _ in pantallas for p in lienzo.comprobar()]
    if problemas:
        for numero, problema in problemas[:25]:
            print(f"[{numero}] {problema}", file=sys.stderr)
        return 1

    if "--ansi" in argv:
        for _, nombre, _, lienzo, _ in pantallas:
            print(f"\n── {nombre} " + "─" * (CELDAS_X - len(nombre) - 4))
            sys.stdout.write(pintar(lienzo))
        return 0

    destino = Path(__file__).resolve().parent
    if "--png" in argv:
        for numero, nombre, _, _, puntos in pantallas:
            ruta = destino / "vista" / f"{numero}.png"
            preview(puntos, ruta)
            print(f"{ruta}")
        return 0

    (destino / "nier.html").write_text(construir_html(pantallas), encoding="utf-8")
    with open(destino / "nier.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo, _ in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (CELDAS_X - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    anchos = {len(linea) for _, _, _, lienzo, _ in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {CELDAS_X}×{CELDAS_Y} celdas · {ANCHO}×{ALTO} puntos · "
          f"máx. {max(anchos)} columnas → nier.html y nier.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
