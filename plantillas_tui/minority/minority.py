#!/usr/bin/env python3
"""Mockups de una TUI «Minority Report» — precrime, cristal y sala de mando.

Segundo estilo, mismo motor: :mod:`mockups.celdas`. Aquí no hay neón sobre negro
sino **paneles de cristal pálido flotando en una sala a oscuras**: marcos
discontinuos `╌`, esquinas sueltas, tramas `░` que insinúan translucidez y mucho
hueco. Todo sigue siendo texto y color sobre una rejilla de 100 × 30.

    python3 minority/minority.py            # minority.html y minority.txt
    python3 minority/minority.py --ansi     # pinta las pantallas en tu terminal

Solo biblioteca estándar.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import (  # noqa: E402
    Lienzo, barra, chispa, espaciado, pseudo, recorta,
)


def barra_hielo(valor: float, celdas: int) -> str:
    """Barra de este estilo: llena `▓`, vacía `·`. El `░` ya es la textura del panel."""
    return barra(valor, celdas, "▓", "·")

ANCHO, ALTO = 100, 30


# ---------------------------------------------------------------------------
# mobiliario común
# ---------------------------------------------------------------------------
def cabecera(c: Lienzo, izquierda: str, derecha: str) -> None:
    c.texto(2, 0, izquierda, "dim")
    c.texto(ANCHO - len(derecha) - 2, 0, derecha, "dim")
    c.texto(0, 1, "╌" * ANCHO, "rule")


def pie(c: Lienzo, teclas: list[tuple[str, str]], nota: str = "") -> None:
    if nota:
        c.texto(2, ALTO - 2, nota, "ghost")
    x = 2
    for tecla, accion in teclas:
        c.texto(x, ALTO - 1, tecla, "key")
        x += len(tecla) + 1
        c.texto(x, ALTO - 1, accion + "    ", "dim")
        x += len(accion) + 4


def etiqueta(c: Lienzo, x: int, y: int, nombre: str, valor: str, ancho_valor: int = 12,
             estilo_valor: str = "") -> None:
    c.texto(x, y, recorta(nombre, ancho_valor - 2), "dim")
    c.texto(x + ancho_valor, y, valor, estilo_valor)


# ---------------------------------------------------------------------------
# 01 · Sala de mando
# ---------------------------------------------------------------------------
def pantalla_mando(c: Lienzo) -> None:
    cabecera(c, "DEPT. DE PRECRIME · DIVISIÓN WASHINGTON D.C.", "24 MAY 2054 · 06:12:44")

    c.texto(2, 3, espaciado("PRECRIME", 2), "brand")
    c.texto(3, 4, "sistema de anticipación de homicidios · v9.4 · acreditación federal 2054/07", "dim")

    c.panel(2, 6, 46, 14, "PREDICCIONES DE HOY")
    casos = [
        ("06:12", "HOMICIDIO", "mujer, 34 años · cuchillo", "SEVERO", 0.91),
        ("14:38", "HOMICIDIO", "hombre, 51 años · vehículo", "SEVERO", 0.72),
        ("21:05", "HOMICIDIO", "mujer, 27 años · arma de fuego", "SEVERO", 0.44),
    ]
    for indice, (hora, tipo, quien, gravedad, confianza) in enumerate(casos):
        fila = 7 + indice * 4
        c.texto(4, fila, hora, "ice")
        c.texto(11, fila, tipo, "alert" if confianza > 0.8 else "")
        c.texto(21, fila, f"{int(confianza * 100)} %", "dim")
        c.texto(27, fila, barra_hielo(confianza, 18), "ice" if confianza > 0.8 else "cool")
        c.texto(4, fila + 1, recorta(quien, 42), "dim")
        c.texto(4, fila + 2, f"precog: AGATHA · registro 24-0512-0{indice + 1}", "ghost")

    c.panel(50, 6, 48, 14, "PRECOG · AGATHA")
    c.texto(52, 7, "enlace neuronal", "dim")
    c.texto(76, 7, "ESTABLE", "ok")
    c.texto(52, 8, "ritmo", "dim")
    c.texto(76, 8, "92 lpm", "warn")
    c.texto(52, 9, "carga", "dim")
    c.texto(76, 9, "71 %", "warn")
    c.texto(52, 10, "deriva", "dim")
    c.texto(76, 10, "3 %", "ok")
    c.texto(52, 11, "sueño inducido", "dim")
    c.texto(76, 11, "4 h 12 m", "")
    c.texto(52, 13, "actividad cortical · últimos 40 ciclos", "ghost")
    c.texto(52, 14, chispa([0.25 + 0.6 * pseudo(k * 11 + 7) for k in range(42)]), "ice")
    c.texto(52, 16, recorta("▸ dos predicciones comparten el mismo autor.", 44), "warn")
    c.texto(52, 17, recorta("▸ el tercer caso llegó con la visión gastada.", 44), "dim")
    c.texto(52, 18, "▸ no se puede rebobinar: solo avanzar.", "ghost")

    c.panel(2, 21, 96, 6, "SCRUB · CASO 24-0512-01")
    c.texto(4, 22, "06:12:44", "ice")
    c.texto(14, 22, "▸", "alert")
    c.texto(16, 22, "█" * 8 + "▓" * 6 + "▒" * 14 + "·" * 22, "cool")
    c.texto(68, 22, "cuchillo · callejón", "dim")
    c.texto(4, 23, "frame 1 214 / 3 400 · confianza 91 % · dos precogs de acuerdo", "ghost")
    c.texto(4, 25, "▸ si los informes discrepan, el caso se detiene y se archiva.", "ghost")
    pie(c, [("⏎", "abrir scrub"), ("TAB", "cambiar precog"), ("F", "filtrar"), ("ESC", "salir")],
        "sala en espera · sin unidades despachadas")


# ---------------------------------------------------------------------------
# 02 · Scrub (la pantalla insignia)
# ---------------------------------------------------------------------------
def marco_escena(c: Lienzo, x: int, y: int, ancho: int, alto: int, semilla: int,
                 seleccionado: bool = False) -> None:
    """Miniatura abstracta de una escena: horizonte, suelo, dos figuras y lluvia."""
    estilo_borde = "frame_sel" if seleccionado else "frame"
    c.texto(x, y, "┌" + "─" * (ancho - 2) + "┐", estilo_borde)
    for fila in range(y + 1, y + alto - 1):
        c.texto(x, fila, "│", estilo_borde)
        c.texto(x + ancho - 1, fila, "│", estilo_borde)
    c.texto(x, y + alto - 1, "└" + "─" * (ancho - 2) + "┘", estilo_borde)

    interior = ancho - 2
    suelo = y + alto - 2
    # siluetas de edificios en el horizonte: cada fotograma tiene su skyline
    cielo = ""
    for columna in range(interior):
        alto_edificio = int(pseudo(semilla * 53 + columna // 3) * 2.2)
        cielo += "▄" if alto_edificio and columna % 2 == 0 else " "
    c.texto(x + 1, y + 2, cielo, "cool")
    c.texto(x + 1, suelo, "▄" * interior, "cool")
    lluvia = ""
    for columna in range(interior):
        lluvia += "┊" if pseudo(semilla * 31 + columna) > 0.72 else " "
    c.texto(x + 1, y + 1, lluvia, "rain")
    # siluetas: dos figuras de distinta altura, con un hueco entre ellas
    f1 = x + 3 + int(pseudo(semilla * 7) * 4)
    f2 = f1 + 6 + int(pseudo(semilla * 13) * 3)
    for figura, altura in ((f1, 3), (f2, 2)):
        for paso in range(altura):
            c.texto(figura, suelo - 1 - paso, "█", "figure")
        c.texto(figura, suelo, "▀", "figure")
    if semilla % 4 == 1:                    # el paraguas rojo, solo en un fotograma
        c.texto(f2 + 1, suelo - 2, "▒", "alert")
        c.texto(f2 + 2, suelo - 2, "▒", "alert")
    if semilla % 3 == 0:
        c.texto(x + interior - 5, suelo - 1, "▬▬▬", "cool")


def pantalla_scrub(c: Lienzo) -> None:
    cabecera(c, "CASO 24-0512-01 · HOMICIDIO ANTICIPADO", "FRAME 1 214 / 3 400 · 06:12:44")

    c.texto(2, 3, espaciado("SCRUB", 2), "brand")
    c.texto(22, 3, "AGATHA · visión primaria · 24 MAY 2054", "dim")

    for indice in range(5):
        marco_escena(c, 2 + indice * 19, 5, 17, 8, semilla=indice + 1213, seleccionado=indice == 1)
    c.texto(2, 13, "1 212", "ghost")
    c.texto(21, 13, "1 213", "ghost")
    c.texto(40, 13, "▲ 1 214", "ice")
    c.texto(59, 13, "1 215", "ghost")
    c.texto(78, 13, "1 216", "ghost")

    # pista de arrastre: 96 columnas, una por cada dos fotogramas, cabeza en 40
    c.texto(2, 15, "├", "rule")
    c.texto(3, 15, "".join("┼" if paso % 10 == 0 else "─" for paso in range(1, 95)), "rule")
    c.texto(97, 15, "┤", "rule")
    c.texto(40, 14, "▲", "ice")
    c.texto(2, 16, "▸ arrastra con ←→ · 10 fotogramas por pulsación · SHIFT acelera", "ghost")
    c.texto(84, 16, "1 214 / 3 400", "dim")

    c.panel(2, 18, 46, 9, "EN ESTA ESCENA")
    detalles = [("paraguas rojo", 0.94), ("callejón de servicio", 0.88),
                ("coche blanco", 0.61), ("rostro del autor", 0.41)]
    for indice, (nombre, valor) in enumerate(detalles):
        fila = 19 + indice * 2
        c.texto(4, fila, nombre.ljust(20), "" if valor > 0.6 else "dim")
        c.texto(26, fila, barra_hielo(valor, 14), "ice" if valor > 0.6 else "warn")
        c.texto(42, fila, f"{int(valor * 100):3d} %", "dim")

    c.panel(50, 18, 48, 9, "LECTURA")
    c.texto(52, 19, "ángulo", "dim")
    c.texto(64, 19, "45° · picado", "cool")
    c.texto(52, 20, "estabilidad", "dim")
    c.texto(64, 20, "0.82 · tiembla", "warn")
    c.texto(52, 21, "deriva", "dim")
    c.texto(64, 21, "3 % por ciclo", "dim")
    c.texto(52, 23, "▸ esto es la precog, no una cámara.", "ghost")
    c.texto(52, 24, "▸ lo que falta se marca, no se rellena.", "ghost")
    c.texto(52, 25, "▸ detener aquí exige dos firmas.", "warn")
    pie(c, [("←→", "arrastrar"), ("⏎", "detener aquí"), ("Z", "zoom"), ("TAB", "tilt")],
        "caso detenido · ni despachado ni archivado")


# ---------------------------------------------------------------------------
# 03 · Dosier
# ---------------------------------------------------------------------------
def pantalla_dosier(c: Lienzo) -> None:
    cabecera(c, "DOSIER · CASO 24-0512-01", "CONFIDENCIAL · NIVEL 3 · 06:14:02")

    c.texto(2, 3, espaciado("DOSIER CRUZADO", 1), "brand")
    c.texto(3, 4, "las dos personas que la visión pone en el mismo callejón", "dim")

    c.panel(2, 6, 46, 16, "VÍCTIMA · PRESUNTA")
    victimas = [("nombre", "ELENA VOSS"), ("edad", "34"), ("domicilio", "sector 4, bloque 7"),
                ("profesión", "técnica de mantenimiento"), ("antecedentes", "ninguno"),
                ("vínculo con el autor", "compañera de trabajo")]
    for indice, (campo, valor) in enumerate(victimas):
        etiqueta(c, 4, 7 + indice * 2, campo, recorta(valor, 18), 22, "ice" if indice == 0 else "")

    c.panel(52, 6, 46, 16, "AUTOR · PRESUNTO")
    autores = [("nombre", "MARCUS ORR"), ("edad", "37"), ("domicilio", "sector 4, bloque 7"),
               ("profesión", "técnico de mantenimiento"), ("antecedentes", "una agresión, 2051"),
               ("vínculo con la víctima", "compañero de trabajo")]
    for indice, (campo, valor) in enumerate(autores):
        etiqueta(c, 54, 7 + indice * 2, campo, recorta(valor, 18), 22, "alert" if indice == 0 else "")

    c.panel(2, 23, 96, 4, "CRUCE")
    c.texto(4, 24, "3 coincidencias · 0 testigos · 0 denuncias previas entre ellos", "warn")
    c.texto(4, 25, "▸ el sistema no sabe por qué: solo anticipa cuándo y dónde.", "ghost")
    pie(c, [("⏎", "abrir ficha"), ("C", "cruzar con archivo"), ("ESC", "volver")])


# ---------------------------------------------------------------------------
# 04 · La visión
# ---------------------------------------------------------------------------
def pantalla_vision(c: Lienzo) -> None:
    cabecera(c, "VISIÓN RECONSTRUIDA · AGATHA", "CONFIANZA GLOBAL 87 % · 06:14:40")

    c.texto(2, 3, espaciado("VISIÓN", 1), "brand")
    c.texto(3, 4, "lo que la precog vio · reconstruido fotograma a fotograma", "dim")

    c.caja(2, 6, 62, 17, "", "frame")
    # la leyenda va sobre fondo limpio: el ruido es la imagen, no el texto
    c.limpiar(3, 20, 60, 2)
    for fila in range(7, 20):
        for columna in range(3, 63):
            valor = pseudo(fila * 71 + columna * 13)
            glifo = "▒" if valor > 0.70 else ("░" if valor > 0.34 else " ")
            c.texto(columna, fila, glifo, "rain" if valor > 0.55 else "ghost")

    # Formas reconocidas, numeradas. La leyenda va aparte: así ninguna etiqueta
    # pisa a otra ni tapa la propia imagen, que es lo que pasaba antes.
    formas = [
        (1, 8, 9, 7, "paraguas", 0.94),
        (2, 24, 12, 4, "figura A", 0.81),
        (3, 37, 12, 4, "figura B", 0.77),
        (4, 47, 15, 8, "coche", 0.61),
    ]
    for numero, x, y, ancho, nombre, confianza in formas:
        c.texto(x, y, "█" * ancho, "figure")
        c.texto(x, y + 1, "▀" * ancho, "figure")
        c.limpiar(x - 3, y, 4, 1)          # hueco: el número no pelea con el ruido
        c.texto(x - 2, y, str(numero), "ice")
    c.texto(3, 20, "1 paraguas 94%  2 fig. A 81%  3 fig. B 77%  4 coche 61%", "label")
    c.texto(3, 21, "sin resolver: el rostro del autor · 41 % · no se rellena", "alert")

    c.panel(66, 6, 32, 12, "DESGLOSE")
    partes = [("escena", 0.92), ("hora", 0.88), ("lugar", 0.74), ("arma", 0.69),
              ("rostro", 0.41)]
    for indice, (nombre, valor) in enumerate(partes):
        fila = 7 + indice * 2
        c.texto(68, fila, nombre.ljust(9), "dim")
        c.texto(78, fila, barra_hielo(valor, 12), "ice" if valor > 0.6 else "warn")
        c.texto(92, fila, f"{int(valor * 100):2d}", "dim")

    c.panel(66, 19, 32, 8, "CONCORDANCIA")
    c.texto(68, 20, "AGATHA", "dim")
    c.texto(78, 20, "de acuerdo", "ok")
    c.texto(68, 21, "DASHIELL", "dim")
    c.texto(78, 21, "de acuerdo", "ok")
    c.texto(68, 22, "ARTHUR", "dim")
    c.texto(78, 22, "sin visión", "warn")
    c.texto(68, 23, "▸ 2 de 3 coinciden.", "warn")
    c.texto(68, 24, "▸ el desacuerdo se guarda", "ghost")
    c.texto(68, 25, "  como informe minoritario.", "warn")

    c.panel(2, 23, 62, 4, "")
    c.texto(4, 24, "▸ reconstruir es recordar, no ver: lo que falta, faltó.", "ghost")
    c.texto(4, 25, "▸ lo que no se resolvió no se rellena a mano.", "ghost")
    pie(c, [("⏎", "ver informe minoritario"), ("P", "comparar precogs"), ("ESC", "volver")])


# ---------------------------------------------------------------------------
# 05 · Despacho
# ---------------------------------------------------------------------------
def pantalla_despacho(c: Lienzo) -> None:
    cabecera(c, "DESPACHO · UNIDAD 12 Y 07", "TIEMPO HASTA EL HECHO 00:41:12 · 06:15:20")

    c.texto(2, 3, espaciado("DESPACHO", 1), "brand")
    c.texto(3, 4, "sector 4 · el callejón está a dos manzanas de la comisaría", "dim")

    c.caja(2, 6, 60, 15, "", "frame")
    # Solo cuatro calles verticales y tres horizontales: una ciudad, no una hoja
    # cuadriculada. Las manzanas son bloques de ▒ entre ellas.
    verticales = (10, 24, 38, 52)
    horizontales = (9, 13, 17)
    for columna in verticales:
        for fila in range(7, 20):
            if fila not in horizontales:
                c.texto(columna, fila, "│", "map")
    for fila in horizontales:
        c.texto(3, fila, "─" * 58, "map")
        for columna in verticales:
            c.texto(columna, fila, "┼", "map")
    for (x, y, ancho, alto) in ((11, 14, 12, 2), (25, 7, 12, 1), (39, 18, 12, 1),
                                (11, 7, 12, 1), (39, 10, 12, 2)):
        for fila in range(y, y + alto):
            c.texto(x, fila, "▒" * ancho, "block")
    c.texto(16, 18, "▲", "unit")
    c.texto(18, 18, "U-12", "unit")
    c.texto(45, 15, "▲", "unit")
    c.texto(47, 15, "U-07", "unit")
    c.texto(33, 13, "◆", "alert")
    c.texto(35, 13, "objetivo", "alert")
    c.texto(3, 19, "  callejón de servicio · sin salida por el norte", "ghost")

    c.panel(66, 6, 32, 15, "UNIDADES")
    unidades = [("U-12", "a 0.8 km", "00:02:10", "ok"), ("U-07", "a 1.4 km", "00:03:40", "ok"),
                ("U-03", "a 4.0 km", "00:11:05", "warn"), ("médica", "en base", "—", "dim")]
    for indice, (nombre, donde, eta, estilo) in enumerate(unidades):
        fila = 7 + indice * 2
        c.texto(68, fila, nombre.ljust(8), "ice")
        c.texto(77, fila, donde.ljust(10), "dim")
        c.texto(88, fila, eta, estilo)
    c.texto(68, 16, "▸ sin orden de detención", "warn")
    c.texto(68, 17, "  no hay delito todavía.", "ghost")
    c.texto(68, 18, "▸ interceptar exige", "ghost")
    c.texto(68, 19, "  mandato de precrime.", "ghost")

    c.panel(2, 22, 96, 5, "COMUNICACIONES")
    c.texto(4, 23, "06:15:02  U-12  «llegamos al callejón, no hay nadie»", "dim")
    c.texto(4, 24, "06:15:14  mando «esperad, faltan 41 minutos»", "")
    c.texto(4, 25, "06:15:20  U-07  «el sujeto está aquí, solo. Sin arma.»", "alert")
    pie(c, [("⏎", "autorizar interceptación"), ("M", "mandato"), ("ESC", "volver")])


# ---------------------------------------------------------------------------
# 06 · Archivo
# ---------------------------------------------------------------------------
def pantalla_archivo(c: Lienzo) -> None:
    cabecera(c, "ARCHIVO · INFORMES MINORITARIOS", "6 AÑOS DE PRECRIME · 06:16:00")

    c.texto(2, 3, espaciado("ARCHIVO", 1), "brand")
    c.texto(3, 4, "lo que el sistema predijo y no ocurrió · lo que sí ocurrió y no predijo", "dim")

    c.panel(2, 6, 30, 12, "HOMICIDIOS")
    c.texto(4, 7, "0", "ok")
    c.texto(7, 7, "en seis años", "ghost")
    c.texto(4, 9, "predicciones", "dim")
    c.texto(24, 9, "128", "ice")
    c.texto(4, 10, "despachos", "dim")
    c.texto(24, 10, "96", "")
    c.texto(4, 11, "informes minoritarios", "dim")
    c.texto(26, 11, "4", "warn")
    c.texto(4, 13, "▸ sin homicidios desde 2050.", "ghost")
    c.texto(4, 15, "▸ nadie verificó el sin:", "warn")
    c.texto(4, 16, "  no hay con qué comparar.", "ghost")

    c.panel(34, 6, 30, 12, "PRECOGS")
    c.texto(36, 7, "AGATHA", "dim")
    c.texto(50, 7, "4 h 12 m", "")
    c.texto(36, 8, "DASHIELL", "dim")
    c.texto(50, 8, "4 h 03 m", "")
    c.texto(36, 9, "ARTHUR", "dim")
    c.texto(50, 9, "3 h 40 m", "warn")
    c.texto(36, 11, "descanso oblig.", "dim")
    c.texto(56, 11, "6 h", "")
    c.texto(36, 13, "casos por año", "ghost")
    c.texto(36, 14, chispa([0.2, 0.35, 0.28, 0.5, 0.42, 0.61, 0.55, 0.7, 0.66]), "ice")
    c.texto(36, 15, "2050" + " " * 14 + "2054", "ghost")
    c.texto(36, 16, "▸ sube y nadie la lee.", "warn")

    c.panel(66, 6, 32, 12, "CADENA DE CUSTODIA")
    c.texto(68, 7, "soporte", "dim")
    c.texto(80, 7, "cristal óptico", "")
    c.texto(68, 8, "copias", "dim")
    c.texto(80, 8, "2 · sala y juzgado", "")
    c.texto(68, 9, "revisión", "dim")
    c.texto(80, 9, "semanal", "")
    c.texto(68, 10, "borrado", "dim")
    c.texto(80, 10, "nunca", "ok")
    c.texto(68, 12, "▸ el informe minoritario", "ghost")
    c.texto(68, 13, "  se guarda, se consulta", "ghost")
    c.texto(68, 14, "  y no se corrige.", "ghost")
    c.texto(68, 16, "▸ archivar no es juzgar.", "dim")

    c.panel(2, 19, 96, 8, "LA PREGUNTA")
    c.texto(4, 20, "Esto es ficción. En la película, el sistema detiene a personas por algo que", "dim")
    c.texto(4, 21, "todavía no han hecho, y el «informe minoritario» es la prueba de que el", "dim")
    c.texto(4, 22, "futuro no siempre es único. La interfaz no opina: muestra la predicción, la", "dim")
    c.texto(4, 23, "confianza y el desacuerdo en la misma pantalla, sin esconder ninguno.", "dim")
    c.texto(4, 25, "▸ un mockup también puede negarse a celebrar lo que dibuja.", "ghost")
    pie(c, [("⏎", "abrir informe"), ("I", "ver precog"), ("ESC", "salir")])


PANTALLAS = [
    ("01", "Sala de mando", "Lo primero es la ausencia: mucho negro, paneles con esquinas "
     "sueltas y tramas `░` en vez de marcos. La autoridad se sugiere con huecos y "
     "espaciado, no con barras llenas.", pantalla_mando),
    ("02", "Scrub", "Cinco miniaturas de 17×8: cada una es horizonte, lluvia y dos siluetas "
     "de `█` colocadas con la misma función de ruido, en posiciones distintas. La de "
     "en medio lleva el paraguas rojo y el marco encendido.", pantalla_scrub),
    ("03", "Dosier cruzado", "Dos fichas simétricas y una franja de cruce: el estilo "
     "pide columnas limpias, etiqueta a la izquierda y valor a la derecha, con aire "
     "en medio.", pantalla_dosier),
    ("04", "Visión", "Un campo de `▒▒░` con ruido determinista, sobre el que se dibujan "
     "las formas reconocidas. Lo que no se resolvió se queda como hueco y se dice: "
     "41 % no es 100 %.", pantalla_vision),
    ("05", "Despacho", "Mapa de calles con `─│┼`, manzanas `▓`, y unidades `▲`. El reloj "
     "de arriba es el recurso dramático: todo está a punto de pasar.", pantalla_despacho),
    ("06", "Archivo", "La pantalla que se permite dudar. Cifras, una serie temporal y la "
     "pregunta ética escrita sin adorno.", pantalla_archivo),
]


# ---------------------------------------------------------------------------
# serialización y salida
# ---------------------------------------------------------------------------
def construir() -> list[tuple[str, str, str, Lienzo]]:
    salida = []
    for numero, nombre, nota, funcion in PANTALLAS:
        lienzo = Lienzo(ANCHO, ALTO)
        funcion(lienzo)
        lienzo.revestir_paneles()          # tinte de cristal, sin reflejo
        salida.append((numero, nombre, nota, lienzo))
    return salida


def comparativa() -> tuple[Lienzo, Lienzo]:
    """La misma pantalla con el reflejo antiguo y sin él, para comparar."""
    antes, despues = Lienzo(ANCHO, ALTO), Lienzo(ANCHO, ALTO)
    pantalla_mando(antes)
    pantalla_mando(despues)
    antes.revestir_paneles(reflejo=True)
    despues.revestir_paneles()
    return antes, despues


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
:root{--bg:#02060d;--fg:#dceaf7;--dim:#7e9aae;--ghost:#41586a;--rule:#1d3346;
 --glass-fill:#0a161f;--title:#bfe6ff;--ice:#e8f6ff;--cool:#8fc8e8;--alert:#ff5d6c;
 --ok:#7ef0c0;--warn:#ffc163;--sel-fg:#02060d;--sel-bg:#bfe6ff;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
html[data-pal="crepusculo"]{--bg:#070512;--fg:#e6dcf5;--dim:#9a86b8;--ghost:#4f3f6b;
 --rule:#2a1f45;--glass-fill:#130d24;--title:#d9c6ff;--ice:#f2e9ff;--cool:#b39ff0;
 --alert:#ff6b8a;--ok:#8ef0d0;--warn:#ffcf7a;--sel-bg:#d9c6ff;--sel-fg:#070512}
html[data-pal="oxido"]{--bg:#0b0703;--fg:#f3e4cd;--dim:#a08a68;--ghost:#5a4830;
 --rule:#3a2a16;--glass-fill:#171006;--title:#ffd9a3;--ice:#fff2dc;--cool:#e0b070;
 --alert:#ff6f4a;--ok:#c8e08a;--warn:#ffc163;--sel-bg:#ffd9a3;--sel-fg:#0b0703}
html[data-pal="mono"]{--bg:#0d0f13;--fg:#e8e8e8;--dim:#909090;--ghost:#555;--rule:#3a3a3a;
 --glass-fill:#16181c;--title:#fff;--ice:#fff;--cool:#c8c8c8;--alert:#fff;--ok:#fff;
 --warn:#c8c8c8;--sel-bg:#e8e8e8;--sel-fg:#0d0f13}
*{box-sizing:border-box}
body{margin:0;background:#04070b;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:38px 0 26px;border-bottom:1px solid #121821;margin-bottom:30px}
h1{margin:0 0 8px;font-size:27px;letter-spacing:-.02em;font-weight:600}
h1 span{color:#bfe6ff;font-family:var(--mono);font-weight:500}
.sub{color:#7d8590;font-size:15px;line-height:1.68;margin:0;max-width:80ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#7d8590;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#0f131a;color:#c9d1d9;border:1px solid #222a35;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 48px}
.head{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:#bfe6ff;border:1px solid #1d3346;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#7d8590;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:90ch}
.nota code{font-family:var(--mono);background:#0f131a;border:1px solid #1a2029;border-radius:4px;padding:0 4px;color:#9fd8ff}
.term{background:var(--bg);border-radius:8px;padding:14px 16px;overflow-x:auto;
 box-shadow:0 0 0 1px #16202b, 0 30px 70px -40px #000;position:relative}
.term pre{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.34;white-space:pre;color:var(--fg)}
.c-dim{color:var(--dim)}
.c-ghost{color:var(--ghost)}
.c-rule{color:var(--rule)}
.c-brand{color:var(--title);letter-spacing:.14em;font-weight:600}
.c-title{color:var(--title)}
.c-ice{color:var(--ice);font-weight:600}
.c-cool{color:var(--cool)}
.c-alert{color:var(--alert);font-weight:600}
.c-ok{color:var(--ok)}
.c-warn{color:var(--warn)}
.c-glass_fill{background:var(--glass-fill)}
.c-glare{color:#1b2f3d;background:var(--glass-fill)}
.c-glass{color:#2b4a61}
.c-frame{color:#33566e}
.c-frame_sel{color:var(--title)}
.c-figure{color:#cfe6f5}
.c-rain{color:#2c4a5e}
.c-label{color:var(--cool)}
.c-map{color:#22405a}
.c-block{color:#16293c}
.c-unit{color:var(--ok)}
.c-key{background:var(--sel-bg);color:var(--sel-fg);font-weight:700}
html[data-tint="0"] .c-glass_fill{background:transparent}
html[data-glow="1"] .term pre{text-shadow:0 0 8px currentColor;filter:saturate(1.1)}
footer{color:#7d8590;font-size:13.5px;line-height:1.75;border-top:1px solid #121821;padding-top:20px}
footer code{font-family:var(--mono);background:#0f131a;border:1px solid #1a2029;border-radius:4px;padding:1px 5px;color:#a9b6c9}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #121821;vertical-align:top}
th{color:#7d8590;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:#9fd8ff;font-size:12.5px}
.aviso{background:#080d13;border-left:3px solid #bfe6ff;padding:13px 16px;border-radius:0 7px 7px 0;
 color:#96a4b2;font-size:13.5px;line-height:1.68;margin-top:16px}
"""

JS = """
const pal=document.getElementById('pal'),glow=document.getElementById('glow'),
      tint=document.getElementById('tint');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
glow.addEventListener('change',e=>document.documentElement.dataset.glow=e.target.checked?'1':'0');
tint.addEventListener('change',e=>document.documentElement.dataset.tint=e.target.checked?'1':'0');
"""


def construir_html(pantallas) -> str:
    antes, despues = comparativa()
    secciones = []
    for numero, nombre, nota, lienzo in pantallas:
        filas = "\n".join(spans(fila) for fila in lienzo.rejilla)
        secciones.append(f"""
<section>
  <div class="head"><span class="num">{numero}</span><h2>{html.escape(nombre)}</h2></div>
  <p class="nota">{html.escape(nota).replace("`", "")}</p>
  <div class="term"><pre>{filas}</pre></div>
</section>""")

    paletas = [("hielo", "Hielo"), ("crepusculo", "Crepúsculo"), ("oxido", "Óxido"),
               ("mono", "Sin color")]
    opciones = "".join(f'<option value="{v}">{n}</option>' for v, n in paletas)
    antes_filas = "\n".join(spans(fila) for fila in antes.rejilla)
    despues_filas = "\n".join(spans(fila) for fila in despues.rejilla)
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="hielo" data-glow="0" data-glare="si">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PRECRIME · mockups de una TUI Minority Report</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>PRECRIME <span>· mockups de una TUI «Minority Report»</span></h1>
  <p class="sub">Seis pantallas de la sala de mando del Departamento de Precrime, en
  <strong>100 × 30 celdas</strong>. El lenguaje es el contrario al cyberpunk: allí la caja
  encierra y el neón grita; aquí el panel <em>flota</em> —esquinas sueltas y bordes
  discontinuos <code>╌</code>— y el silencio hace el resto. Todo es texto y color.</p>
  <p class="sub" style="margin-top:10px;color:#96a4b2"><strong>Corregido tras tu
  crítica:</strong> la primera versión tramaba todo el interior de los paneles con
  <code>░</code> y competía con el texto. Ahora hay <strong>tinte plano</strong> en el
  interior y la trama queda de <strong>reflejo</strong> solo en las dos filas del borde
  superior y solo donde hay siete columnas libres seguidas. Además viene
  <strong>apagado por defecto</strong>: al final de la página tienes las dos versiones de
  la misma pantalla, una encima de otra, para comparar.</p>
  <div class="controls">
    <label>Paleta <select id="pal">{opciones}</select></label>
    <label><input type="checkbox" id="tint" checked> tinte de cristal</label>
    <label><input type="checkbox" id="glow"> brillo de fósforo (solo aquí)</label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>Antes y después · la misma pantalla</h2></div>
  <p class="nota">Arriba, la versión que criticaste: trama <code>░</code> por todo el interior,
  compitiendo con las cifras. Abajo, la actual: tinte plano y ni un carácter de adorno
  detrás del texto. El cristal se sigue leyendo —esquinas, borde discontinuo y fondo
  propio— pero la información ya no pelea con la textura.</p>
  <div class="term"><pre><span class="c-dim">ANTES · trama en todo el interior</span>
{antes_filas}</pre></div>
  <div class="term" style="margin-top:14px"><pre><span class="c-dim">AHORA · tinte plano, sin reflejo</span>
{despues_filas}</pre></div>
</section>
<section>
  <div class="head"><span class="num">08</span><h2>Qué es realizable y qué es puesta en escena</h2></div>
  <p class="nota">La regla de esta serie: nada que una terminal no pueda pintar. El
  verificador del generador comprueba cada esquina de cada panel, rechaza caracteres de
  doble ancho y falla si una línea pasa de 100 columnas.</p>
  <table>
    <tr><th>Lo que se ve</th><th>Cómo se consigue</th></tr>
    <tr><td>Paneles de cristal</td><td>Cuatro esquinas, bordes <code>╌</code>, tinte de fondo por celda y un reflejo <code>░</code> solo en el borde alto</td></tr>
    <tr><td>Sensación de flotar</td><td>Huecos: los paneles no se tocan y el fondo oscuro ocupa la mayor parte de la pantalla</td></tr>
    <tr><td>Miniaturas del scrub</td><td>Formas de 17×8 dibujadas con <code>█ ▀ ▄ ┊ ─</code> y posiciones derivadas de una función de ruido determinista</td></tr>
    <tr><td>Visión «reconstruida»</td><td>Campo de <code>▒ ░</code> con umbral; las formas reconocidas son bloques encima, cada una con su etiqueta</td></tr>
    <tr><td>Paleta pálida</td><td>Color verdadero <code>38;2;r;g;b</code> con caída a 256 y a 16 colores. Cuatro paletas conmutables, incluida «sin color»</td></tr>
    <tr><td>Transparencia real</td><td><strong>No.</strong> No existe en una terminal. Se insinúa con trama y con contraste, y aquí se dice abiertamente</td></tr>
  </table>
  <div class="aviso"><strong>Nota que no es de diseño:</strong> en la película el sistema
  detiene a gente por algo que aún no ha hecho, y el «informe minoritario» demuestra que
  el futuro no es único. La pantalla 06 pone eso en primer plano en vez de esconderlo. Un
  mockup puede ser bonito y no estar de acuerdo con lo que dibuja.</div>
</section>
<footer>
  Generado por <code>minority/minority.py</code> · motor de celdas compartido en
  <code>mockups/celdas.py</code> · solo biblioteca estándar.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


ANSI = {
    "": "\x1b[38;2;220;234;247m", "dim": "\x1b[38;2;126;154;174m",
    "ghost": "\x1b[38;2;65;88;106m", "rule": "\x1b[38;2;29;51;70m",
    "glass_fill": "\x1b[48;2;10;22;31m", "glare": "\x1b[38;2;27;47;61;48;2;10;22;31m", "brand": "\x1b[1;38;2;191;230;255m",
    "title": "\x1b[38;2;191;230;255m", "ice": "\x1b[1;38;2;232;246;255m",
    "cool": "\x1b[38;2;143;200;232m", "alert": "\x1b[1;38;2;255;93;108m",
    "ok": "\x1b[38;2;126;240;192m", "warn": "\x1b[38;2;255;193;99m",
    "frame": "\x1b[38;2;51;86;110m", "frame_sel": "\x1b[38;2;191;230;255m",
    "figure": "\x1b[38;2;207;230;245m", "rain": "\x1b[38;2;44;74;94m",
    "label": "\x1b[38;2;143;200;232m", "map": "\x1b[38;2;34;64;90m",
    "block": "\x1b[38;2;22;41;60m", "unit": "\x1b[38;2;126;240;192m",
    "key": "\x1b[1;38;2;2;6;13;48;2;191;230;255m",
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
    (destino / "minority.html").write_text(construir_html(pantallas), encoding="utf-8")
    with open(destino / "minority.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    anchos = {len(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · máx. {max(anchos)} columnas · "
          f"0 de doble ancho → minority.html y minority.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
