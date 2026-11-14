#!/usr/bin/env python3
"""Mockups de una TUI cyberpunk — y el generador que los dibuja.

Fuera del proyecto de FFmpeg: esto es diversión. Pero la diversión es honesta:
todo lo que se ve aquí es **texto y color**, dibujado sobre una rejilla de
celdas de 100×30 igual que la de cualquier terminal. No hay imágenes, ni fuentes
especiales, ni cursores gráficos, ni transparencias. Si está aquí, se puede
escribir con `sys.stdout.write`.

    python3 cyberpunk.py            # escribe cyberpunk.html y cyberpunk.txt
    python3 cyberpunk.py --ansi     # y lo pinta en tu terminal, con color de verdad

Solo biblioteca estándar.
"""

from __future__ import annotations

import html
import math
import sys
import unicodedata
from dataclasses import dataclass

ANCHO, ALTO = 100, 30

# ---------------------------------------------------------------------------
# Un lienzo mínimo: celdas y estilos. Es el mismo contrato que usa la TUI real.
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Celda:
    char: str = " "
    estilo: str = ""


class Lienzo:
    def __init__(self, ancho: int = ANCHO, alto: int = ALTO) -> None:
        self.ancho, self.alto = ancho, alto
        self.rejilla = [[Celda() for _ in range(ancho)] for _ in range(alto)]
        self._cajas: list[tuple[int, int, int, int, int]] = []

    def texto(self, x: int, y: int, valor: str, estilo: str = "") -> None:
        if not 0 <= y < self.alto:
            return
        fila = self.rejilla[y]
        for desplazamiento, ch in enumerate(valor):
            columna = x + desplazamiento
            if 0 <= columna < self.ancho:
                fila[columna] = Celda(ch, estilo)

    def relleno(self, x: int, y: int, ancho: int, alto: int, estilo: str) -> None:
        for f in range(y, y + alto):
            if 0 <= f < self.alto:
                self.texto(x, f, " " * ancho, estilo)

    def caja(self, x: int, y: int, ancho: int, alto: int, titulo: str = "",
            estilo: str = "grid", titulo_estilo: str = "title") -> None:
        self._cajas.append((x, y, ancho, alto, len(f" {titulo} ") if titulo else 0))
        self.texto(x, y, "┌" + "─" * (ancho - 2) + "┐", estilo)
        for f in range(y + 1, y + alto - 1):
            self.texto(x, f, "│", estilo)
            self.texto(x + ancho - 1, f, "│", estilo)
        self.texto(x, y + alto - 1, "└" + "─" * (ancho - 2) + "┘", estilo)
        if titulo:
            self.texto(x + 2, y, f" {titulo} ", titulo_estilo)

    # --- lectura -----------------------------------------------------------
    def lineas(self) -> list[str]:
        return ["".join(c.char for c in fila) for fila in self.rejilla]

    def comprobar(self) -> list[str]:
        """Nada que no se pueda pintar en una terminal de verdad."""
        problemas = []
        # Un borde pisado por texto es el fallo más fácil de cometer dibujando a
        # mano y el más difícil de ver. Se comprueba cada caja, celda a celda.
        for x, y, ancho, alto, largo_titulo in self._cajas:
            esperado = {
                (x, y): "┌", (x + ancho - 1, y): "┐",
                (x, y + alto - 1): "└", (x + ancho - 1, y + alto - 1): "┘",
            }
            for columna in range(x + 1, x + ancho - 1):
                if largo_titulo and x + 2 <= columna < x + 2 + largo_titulo:
                    continue            # el título va escrito sobre el borde
                esperado[(columna, y)] = "─"
                esperado[(columna, y + alto - 1)] = "─"
            for fila in range(y + 1, y + alto - 1):
                esperado[(x, fila)] = "│"
                esperado[(x + ancho - 1, fila)] = "│"
            for (columna, fila), glifo in esperado.items():
                real = self.rejilla[fila][columna].char
                if real != glifo and not (glifo == "─" and real not in " ─"):
                    problemas.append(
                        f"caja en ({x},{y}) {ancho}x{alto}: en ({columna},{fila}) "
                        f"se esperaba {glifo!r} y hay {real!r}")
        for indice, fila in enumerate(self.rejilla):
            if len(fila) != self.ancho:
                problemas.append(f"fila {indice}: {len(fila)} celdas")
            for celda in fila:
                if unicodedata.east_asian_width(celda.char) in ("W", "F"):
                    problemas.append(f"fila {indice}: carácter de doble ancho {celda.char!r}")
                if celda.char < " " or celda.char == "\x7f":
                    problemas.append(f"fila {indice}: carácter de control {celda.char!r}")
        return problemas


# ---------------------------------------------------------------------------
# Piezas de dibujo
# ---------------------------------------------------------------------------
BLOQUES = "▁▂▃▄▅▆▇█"


def recorta(texto: str, ancho: int) -> str:
    """Corta a ``ancho`` con puntos suspensivos: nunca parte una palabra a la mitad."""
    if len(texto) <= ancho:
        return texto
    corte = texto[: ancho - 1]
    if " " in corte:
        corte = corte[: corte.rfind(" ")]
    return corte.rstrip(" ,;:") + "…"


def barra(valor: float, celdas: int, lleno: str = "▓", vacio: str = "░") -> str:
    """Barra de progreso de ``celdas`` posiciones. ``valor`` va de 0 a 1."""
    dentro = round(max(0.0, min(1.0, valor)) * celdas)
    return lleno * dentro + vacio * (celdas - dentro)


def chispa(valores: list[float]) -> str:
    """Serie de 0..1 → línea de bloques de un solo renglón."""
    return "".join(BLOQUES[min(len(BLOQUES) - 1, int(v * (len(BLOQUES) - 1) + 0.5))] for v in valores)


def pseudo(semilla: int) -> float:
    """Ruido determinista: el mismo mockup, siempre igual, sin `random`."""
    x = (semilla * 1103515245 + 12345) & 0x7FFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0x7FFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFF) / 0xFFFF


def barra_superior(c: Lienzo, izquierda: str, derecha: str) -> None:
    c.relleno(0, 0, ANCHO, 1, "bar")
    c.texto(1, 0, izquierda, "bar")
    c.texto(ANCHO - len(derecha) - 1, 0, derecha, "bar")


def barra_inferior(c: Lienzo, teclas: list[tuple[str, str]]) -> None:
    c.relleno(0, ALTO - 1, ANCHO, 1, "bar")
    x = 1
    for tecla, accion in teclas:
        c.texto(x, ALTO - 1, f"[{tecla}]", "bar_tecla")
        x += len(tecla) + 3          # "[", "]" y un hueco
        c.texto(x, ALTO - 1, accion + "   ", "bar")
        x += len(accion) + 3


def tira_estado(c: Lienzo, partes: list[tuple[str, str]]) -> None:
    """Fila de datos separados por · , cada uno con su estilo."""
    x = 2
    for indice, (texto, estilo) in enumerate(partes):
        if indice:
            c.texto(x, 1, " · ", "dim")
            x += 3
        c.texto(x, 1, texto, estilo)
        x += len(texto)


# ---------------------------------------------------------------------------
# 01 · Arranque
# ---------------------------------------------------------------------------
FUENTE = {
    "N": ["█  █", "██ █", "█ ██", "█  █", "█  █"],
    "E": ["████", "█   ", "███ ", "█   ", "████"],
    "U": ["█  █", "█  █", "█  █", "█  █", "████"],
    "R": ["████", "█  █", "███ ", "█ █ ", "█  █"],
    "O": ["████", "█  █", "█  █", "█  █", "████"],
    "L": ["█   ", "█   ", "█   ", "█   ", "████"],
    "I": ["████", "  █ ", "  █ ", "  █ ", "████"],
    "K": ["█  █", "█ █ ", "██  ", "█ █ ", "█  █"],
}


def letrero(c: Lienzo, x: int, y: int, palabra: str, estilo: str = "title") -> int:
    for posicion, letra in enumerate(palabra):
        for fila, tira in enumerate(FUENTE[letra]):
            c.texto(x + posicion * 5, y + fila, tira, estilo)
    return x + len(palabra) * 5


def pantalla_arranque(c: Lienzo) -> None:
    barra_superior(c, "▓▓ NEUROLINK", "SECTOR 7 · TERMINAL 04 · 04:12:07 ▓▓")
    tira_estado(c, [("▸ enlace NEURAL-3", "ok"), ("cifrado AES-512", "dim"),
                    ("latencia 12 ms", "dim"), ("proxy ON", "ok"), ("combustible 71 %", "warn")])

    letrero(c, 32, 3, "NEUROLINK", "title")
    c.texto(26, 9, "i m p l a n t e   d e   a c c e s o   c o r t i c a l", "dim")
    c.texto(33, 10, "v4.2.1 · núcleo 0x7F3A · parche 21 · build 2087-11", "ghost")

    c.caja(4, 12, 56, 11, "AUTODIAGNÓSTICO")
    pruebas = [
        ("núcleo motor", 0.98, "ok", "[OK]"),
        ("bus neuronal", 0.92, "ok", "[OK]"),
        ("hielo defensivo", 0.71, "warn", "[OK]"),
        ("handshake ICE", 0.00, "dim", "[..]"),
    ]
    for indice, (nombre, valor, estilo, marca) in enumerate(pruebas):
        fila = 13 + indice * 2
        c.texto(6, fila, marca, estilo)
        c.texto(11, fila, nombre.ljust(20), "dim" if not valor else "")
        c.texto(32, fila, barra(valor, 10), "title" if valor else "ghost")
        c.texto(44, fila, f"{int(valor * 100):3d} %" if valor else "  -- %",
                estilo if valor else "ghost")
        if valor:
            c.texto(50, fila, chispa([0.2 + 0.8 * pseudo(fila * 9 + k) for k in range(6)]),
                    "ghost")
    c.texto(6, 21, "▸ el hielo defensivo caduca en 3 días hábiles.", "warn")

    c.caja(62, 12, 34, 11, "BIOMÉTRICA")
    c.texto(64, 13, "PULSO", "dim")
    c.texto(78, 13, "64 lpm", "ok")
    c.texto(64, 14, chispa([0.4 + 0.5 * pseudo(k * 7 + 3) for k in range(22)]), "title")
    c.texto(64, 15, "SUDOR", "dim")
    c.texto(78, 15, "12 %", "")
    c.texto(64, 16, "CORTISOL", "dim")
    c.texto(74, 16, barra(0.48, 8), "warn")
    c.texto(84, 16, "48 %", "warn")
    c.texto(64, 17, "ADN", "dim")
    c.texto(78, 17, "✓ verificado", "ok")
    c.texto(64, 18, "SUEÑO", "dim")
    c.texto(78, 18, "3 h 12 m", "error")
    c.texto(64, 19, "IMPLANTES", "dim")
    c.texto(78, 19, "5 / 7", "")
    c.texto(64, 20, "TOLERANCIA", "dim")
    c.texto(76, 20, barra(0.63, 6), "warn")
    c.texto(84, 20, "63 %", "warn")
    c.texto(64, 21, recorta("▸ neurobloqueante: 18 % en sangre", 30), "ghost")

    c.texto(4, 24, "CONECTANDO AL NODO 0x7F3A · capa 3 de 5", "title")
    c.texto(93, 24, "67 %", "ok")
    c.texto(4, 25, "█" * 64 + "░" * 32, "title")
    c.texto(4, 26, "tiempo estimado 00:07 · no cierres la sesión · ▮", "dim")
    barra_inferior(c, [("F1", "ayuda"), ("⏎", "conectar"), ("ESC", "abortar"), ("?", "manifiesto")])


# ---------------------------------------------------------------------------
# 02 · Intrusión (ICE)
# ---------------------------------------------------------------------------
HEX = "0123456789ABCDEF"


def pantalla_intrusion(c: Lienzo) -> None:
    barra_superior(c, "▓▓ NEUROLINK // INTRUSIÓN", "ICE NEGRO · CAPA 2/5 · 04:12:31 ▓▓")
    tira_estado(c, [("▸ objetivo 0x7F3A", "mag"), ("rastreo 34 %", "warn"),
                    ("ram 6/12", "ok"), ("tiempo 00:24", "error")])

    c.caja(2, 3, 44, 21, "MATRIZ DE ACCESO")
    camino = {(1, 2), (2, 2), (2, 3), (3, 3), (3, 4), (4, 4), (4, 5)}
    actual = (2, 3)
    for fila in range(8):
        for columna in range(6):
            par = HEX[(fila * 7 + columna * 3) % 16] + HEX[(columna * 5 + fila) % 16]
            x, y = 6 + columna * 6, 5 + fila * 2
            if (columna, fila) == actual:
                c.texto(x - 2, y, "▸", "mag")
                c.relleno(x - 1, y, 3, 1, "sel")
                c.texto(x, y, par, "sel")
            elif (columna, fila) in camino:
                c.texto(x - 2, y, "·", "ok")
                c.texto(x, y, par, "ok")
            else:
                c.texto(x - 2, y, " ", "")
                c.texto(x, y, par, "dim" if pseudo(fila * 31 + columna) > 0.35 else "")
    # marcador de la ruta aceptada: el inverso del color no es la única señal
    c.texto(4, 21, "▸ ruta: 7F A3 91 C4 (marcada con ·)", "ok")
    c.texto(4, 22, "▸ siguiente: busca FF en la columna 4", "mag")

    c.caja(48, 3, 50, 9, "DAEMONS")
    daemons = [
        ("ICEPICK.EXE", 3, 4, "ok", "listo"),
        ("DATAMINE", 2, 3, "ok", "listo"),
        ("TURRET_SHUT", 4, 4, "warn", "en cola"),
        ("MASK_IDENTITY", 1, 2, "dim", "bloqueado"),
    ]
    for indice, (nombre, ram, total, estilo, estado) in enumerate(daemons):
        fila = 4 + indice * 2
        c.texto(50, fila, nombre.ljust(15), estilo)
        c.texto(66, fila, "▓" * ram + "░" * (total - ram), estilo)
        c.texto(74, fila, f"{ram}/{total} ram", "dim")
        c.texto(88, fila, estado, estilo)

    c.caja(48, 13, 50, 12, "TRAZA")
    c.texto(50, 14, "rastreo del anfitrión", "dim")
    c.texto(88, 14, "34 %", "warn")
    c.texto(50, 15, barra(0.34, 46), "warn")
    eventos = [
        ("04:12:29", "ping recibido desde 10.0.7.4", "dim"),
        ("04:12:30", "barrido de puertos :8080", "dim"),
        ("04:12:31", "firma desconocida en RAM", "error"),
        ("04:12:31", "contramedida: ruido blanco", "ok"),
        ("04:12:32", "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", "ghost"),
        ("04:12:32", "paquete perdido · reintento 1/3", "warn"),
        ("04:12:33", "ICE negro olfatea la sesión", "error"),
    ]
    for indice, (hora, texto, estilo) in enumerate(eventos):
        c.texto(50, 17 + indice, hora, "ghost")
        c.texto(60, 17 + indice, texto, estilo)

    c.texto(2, 25, "TIEMPO 00:24", "error")
    c.texto(16, 25, barra(0.62, 40), "error")
    c.texto(58, 25, "▸ quedan 2 capas · ICE negro", "mag")
    c.texto(2, 27, "▸ cada segundo aquí dentro sube el rastreo un 2 %", "dim")
    barra_inferior(c, [("↑↓", "matriz"), ("⏎", "inyectar"), ("TAB", "daemons"),
                       ("ESC", "desconectar")])


# ---------------------------------------------------------------------------
# 03 · Diagnóstico corporal
# ---------------------------------------------------------------------------
def pantalla_diagnostico(c: Lienzo) -> None:
    barra_superior(c, "▓▓ NEUROLINK // DIAGNÓSTICO", "CUERPO · 04:13:02 ▓▓")
    tira_estado(c, [("▸ sujeto K-117", "mag"), ("implantes 5/7", "ok"),
                    ("rechazo 4 %", "warn"), ("seguro médico: ninguno", "error")])

    c.caja(2, 3, 48, 12, "NEURAL")
    c.texto(4, 4, "latencia al Net", "dim")
    c.texto(34, 4, "12 ms", "ok")
    c.texto(4, 5, "ancho de banda", "dim")
    c.texto(34, 5, "940 Mb/s", "")
    c.texto(4, 6, "paquetes perdidos", "dim")
    c.texto(34, 6, "0.02 %", "ok")
    serie = [0.3 + 0.6 * pseudo(k * 13 + 1) for k in range(42)]
    c.texto(4, 8, chispa(serie), "title")
    c.texto(4, 9, "últimos 60 s · tráfico sináptico", "ghost")
    c.texto(4, 11, "sobrecarga cognitiva", "dim")
    c.texto(27, 11, barra(0.28, 10), "warn")
    c.texto(39, 11, "28 %", "warn")
    c.texto(4, 12, "firewall cortical", "dim")
    c.texto(34, 12, "activo", "ok")
    c.texto(4, 13, "sincronía hemisférica", "dim")
    c.texto(34, 13, "0.7 ms", "")

    c.caja(52, 3, 46, 12, "BIÓNICA")
    implantes = [("ojo izquierdo", 0.96), ("brazo derecho", 0.88), ("columna L4", 0.61),
                 ("filtro hepático", 0.74), ("cortex auxiliar", 0.99)]
    for indice, (nombre, valor) in enumerate(implantes):
        fila = 4 + indice
        estilo = "ok" if valor > 0.85 else ("warn" if valor > 0.65 else "error")
        c.texto(54, fila, nombre.ljust(18), "")
        c.texto(72, fila, barra(valor, 16), estilo)
        c.texto(90, fila, f"{int(valor * 100):3d} %", estilo)
    c.texto(54, 10, "▸ columna L4: microfisura detectada", "warn")
    c.texto(54, 11, "▸ garantía de los 5 implantes: caducada", "ghost")
    c.texto(54, 12, "▸ próxima revisión: hace 40 días", "warn")

    c.caja(2, 15, 48, 10, "ENTORNO")
    c.texto(4, 16, "temperatura", "dim")
    c.texto(28, 16, "31 °C", "warn")
    c.texto(4, 17, "radiación", "dim")
    c.texto(28, 17, "0.4 mSv", "ok")
    c.texto(4, 18, "calidad del aire", "dim")
    c.texto(24, 18, barra(0.18, 10), "error")
    c.texto(36, 18, "18 %", "error")
    c.texto(4, 19, "señal del sector", "dim")
    c.texto(24, 19, "▂▄▆█▆▄▂▁▃▅", "title")
    c.texto(4, 20, "vecinos hostiles", "dim")
    c.texto(28, 20, "2 · a 40 m", "error")
    c.texto(4, 21, "salida de emergencia", "dim")
    c.texto(28, 21, "bloqueada", "error")
    c.texto(4, 22, "▸ el aire empeora: 18 % (ayer 24 %)", "ghost")

    c.caja(52, 15, 46, 10, "REGISTRO")
    eventos = [
        ("04:09:12", "implante 3: microfisura sellada", "warn"),
        ("04:10:44", "neurobloqueante 20 ml", ""),
        ("04:11:58", "pico de cortisol normalizado", "ok"),
        ("04:12:50", "seguro caducado hace 214 días", "error"),
        ("04:13:01", "sincronía con NEURAL-3 completa", "ok"),
        ("04:13:02", "lectura de implantes: 5 de 7", "dim"),
    ]
    for indice, (hora, texto, estilo) in enumerate(eventos):
        c.texto(54, 16 + indice, hora, "ghost")
        c.texto(63, 16 + indice, recorta(texto, 33), estilo)
    c.texto(54, 23, "▸ 6 eventos · el resto va al registro", "ghost")

    c.texto(2, 26, "ESTADO GENERAL", "dim")
    c.texto(18, 26, barra(0.78, 34), "ok")
    c.texto(54, 26, "ESTABLE · revisión en 3 días", "ok")
    c.texto(2, 27, "⚠ dos implantes por debajo del 70 % · garantía nula", "warn")
    barra_inferior(c, [("↑↓", "sistema"), ("⏎", "detalle"), ("R", "recalibrar"),
                       ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 04 · Mercado negro
# ---------------------------------------------------------------------------
def pantalla_mercado(c: Lienzo) -> None:
    barra_superior(c, "▓▓ MERCADO NEGRO", "CANAL 7 · OFERTAS 41 · 04:13:40 ▓▓")
    tira_estado(c, [("▸ saldo 12 480 ₡", "ok"), ("reputación 7.2", "mag"),
                    ("deuda 3 000 ₡", "error"), ("rastreo 0 %", "ok")])

    c.caja(2, 3, 66, 23, "OFERTAS")
    c.texto(6, 4, "ARTÍCULO".ljust(22) + "RIESGO".ljust(10) + "STOCK".ljust(8) + "PRECIO".rjust(9), "ghost")
    c.texto(4, 5, "─" * 62, "grid")
    ofertas = [
        ("DECK MK-IV", 0.35, "3", "4 200"),
        ("CORTEX AUX 2.1", 0.72, "1", "3 100"),
        ("NEUROBLOQ x50", 0.12, "12", "640"),
        ("ICE NEGRO (copia)", 0.94, "1", "8 900"),
        ("MANUAL DE VUELO", 0.05, "5", "120"),
        ("SANGRE SINT. 2 L", 0.28, "8", "310"),
        ("PISTOLA TÁSER", 0.61, "2", "1 750"),
        ("ID FALSA (nivel 4)", 0.88, "1", "5 400"),
        ("ÓPTICA TÉRMICA", 0.44, "4", "2 250"),
        ("FILTRO RENAL", 0.19, "6", "980"),
        ("COPIA DE LLAVE", 0.79, "3", "3 600"),
        ("MUNICIÓN 9 mm", 0.52, "20", "480"),
        ("JAMMER PORTÁTIL", 0.83, "2", "6 700"),
        ("PARCHE DE HIELO", 0.31, "9", "1 100"),
    ]
    for indice, (nombre, riesgo, stock, precio) in enumerate(ofertas):
        fila = 6 + indice
        seleccionada = indice == 3
        estilo = "sel" if seleccionada else ""
        if seleccionada:
            c.relleno(3, fila, 64, 1, "sel")
        marca = ">" if seleccionada else " "
        c.texto(4, fila, f"{marca} {nombre:<20}", estilo)
        lleno = round(riesgo * 5)
        c.texto(28, fila, "▓" * lleno + "░" * (5 - lleno), estilo)
        c.texto(38, fila, stock.rjust(4), estilo)
        c.texto(56, fila, f"{precio} ₡".rjust(9), estilo)
    c.texto(4, 21, "─" * 62, "grid")
    c.texto(4, 22, "▸ los precios no incluyen el impuesto de tránsito (18 %)", "warn")
    c.texto(4, 23, "▸ stock orientativo: el vendedor miente una de cada tres veces", "ghost")
    c.texto(4, 24, "▸ ◆ = identidad verificada · sin marca = sin firma", "ghost")

    c.caja(70, 3, 28, 14, "DETALLE")
    c.texto(72, 4, "ICE NEGRO (copia)", "mag")
    c.texto(72, 5, "copia no verificada", "dim")
    c.texto(72, 7, "Origen", "dim")
    c.texto(72, 8, "búnker 12, sin", "")
    c.texto(72, 9, "procedencia", "")
    c.texto(72, 10, "Vendedor", "dim")
    c.texto(72, 11, "◆ «el de la capa 4»", "warn")
    c.texto(72, 13, "RIESGO DE RASTREO", "dim")
    c.texto(72, 14, barra(0.94, 24), "error")
    c.texto(72, 15, "94 % · puede delatarte", "error")

    c.caja(70, 17, 28, 9, "ACCIONES")
    acciones = [("COMPRAR      8 900 ₡", "ok"), ("NEGOCIAR", ""), ("VER VENDEDOR", ""),
                ("DENUNCIAR  [F]", "dim")]
    for indice, (texto, estilo) in enumerate(acciones):
        c.texto(72, 18 + indice * 2, texto, estilo)

    c.texto(2, 27, "⏎ comprar · N negociar · F denunciar · ESC salir", "ghost")
    barra_inferior(c, [("↑↓", "oferta"), ("⏎", "comprar"), ("N", "negociar"),
                       ("F", "denunciar")])


# ---------------------------------------------------------------------------
# 05 · Comms
# ---------------------------------------------------------------------------
def pantalla_comms(c: Lienzo) -> None:
    barra_superior(c, "▓▓ COMMS // INTERCEPTOR", "CANAL 7 · CIFRADO ROTO · 04:14:10 ▓▓")
    tira_estado(c, [("▸ 3 sin leer", "mag"), ("interceptados 128", "dim"),
                    ("confianza 61 %", "warn"), ("trampa: posible", "error")])

    c.caja(2, 3, 58, 23, "BANDEJA")
    mensajes = [
        ("04:14", "◆ V", "re: entrega del paquete", True),
        ("04:11", "anon", "el cargamento no llegó", True),
        ("04:03", "◆ K", "no confíes en el de la capa 4", True),
        ("03:58", "broker", "precio cerrado: 8 900 ₡", False),
        ("03:40", "◆ V", "quema el deck cuando termines", False),
        ("03:22", "sistema", "parche de hielo disponible", False),
        ("03:05", "◆ R", "el médico quiere su parte", False),
        ("02:59", "anon", "▒▒▒▒▒▒ ▒▒▒▒▒", False),
        ("02:47", "broker", "el trato sigue en pie", False),
        ("02:40", "◆ K", "nos vemos en el bar", False),
        ("02:31", "sistema", "reputación +0.1", False),
        ("02:18", "anon", "¿sigues ahí?", False),
    ]
    for indice, (hora, quien, asunto, nuevo) in enumerate(mensajes):
        fila = 4 + indice
        seleccionada = indice == 2
        estilo = "sel" if seleccionada else ""
        if seleccionada:
            c.relleno(3, fila, 56, 1, "sel")
        c.texto(4, fila, "●" if nuevo else " ", "sel" if seleccionada else "mag")
        c.texto(6, fila, ">" if seleccionada else " ", estilo)
        c.texto(8, fila, hora, "sel" if seleccionada else "ghost")
        c.texto(14, fila, quien.ljust(7), estilo if seleccionada else
                ("warn" if quien == "anon" else ""))
        c.texto(22, fila, recorta(asunto, 36), estilo)
    c.texto(4, 18, "─" * 54, "grid")
    c.texto(4, 19, "● sin leer · ◆ identidad verificada · anon = sin firma", "ghost")
    c.texto(4, 21, "▸ 12 de 128 · orden: más reciente primero", "dim")
    c.texto(4, 22, "▸ 3 mensajes llevan la misma firma quebrada", "warn")
    c.texto(4, 23, "▸ el adjunto de ◆ K no se ha abierto todavía", "ghost")

    c.caja(62, 3, 36, 12, "INTERCEPTO")
    c.texto(64, 4, "de: ◆ K  ·  para: V", "dim")
    c.texto(64, 5, "asunto: no confíes en el de", "title")
    c.texto(64, 6, "        la capa 4", "title")
    c.texto(64, 8, "el de la capa 4 vendió tu", "")
    c.texto(64, 9, "firma hace dos noches.", "")
    c.texto(64, 10, "si te pregunta por el", "")
    c.texto(64, 11, "deck, no contestes.", "")
    c.texto(64, 12, "y no vayas al bar solo.", "warn")
    c.texto(64, 13, "— K", "mag")

    c.caja(62, 16, 36, 10, "ANÁLISIS")
    c.texto(64, 17, "cifrado", "dim")
    c.texto(80, 17, "ROTO  ▒▒▒▒", "error")
    c.texto(64, 18, "firma", "dim")
    c.texto(80, 18, "dudosa", "warn")
    c.texto(64, 19, "retransmisión", "dim")
    c.texto(80, 19, "14 saltos", "")
    c.texto(64, 20, "origen", "dim")
    c.texto(80, 20, "desconocido", "error")
    c.texto(64, 21, "adjunto", "dim")
    c.texto(80, 21, "1 archivo", "warn")
    c.texto(64, 22, "trampa probable", "dim")
    c.texto(80, 22, barra(0.61, 12), "warn")
    c.texto(64, 23, "▸ el adjunto no se ha abierto", "ghost")
    barra_inferior(c, [("↑↓", "mensaje"), ("⏎", "abrir"), ("D", "descargar"),
                       ("X", "borrar"), ("ESC", "salir")])


# ---------------------------------------------------------------------------
# 06 · Reproductor / visualizador
# ---------------------------------------------------------------------------
def pantalla_audio(c: Lienzo) -> None:
    barra_superior(c, "▓▓ VHS DREAMS // REPRODUCTOR", "SALIDA: JACK CRANEAL · 04:15:02 ▓▓")
    tira_estado(c, [("▸ 118 BPM", "mag"), ("vol 72 %", "dim"), ("fuente: cinta", "warn"),
                    ("ruido -42 dB", "ok")])

    c.caja(2, 3, 96, 6, "SONANDO")
    c.texto(4, 4, "NIGHT_CITY.EXE", "title")
    c.texto(4, 5, "VHS DREAMS · lado A · 1986 (remaster 2087)", "dim")
    c.texto(4, 7, "01:12", "ghost")
    total, avance = 85 - 10, round(0.26 * 75)
    c.texto(10, 7, "▓" * avance + "░" * (total - avance), "title")
    c.texto(88, 7, "04:38", "ghost")

    c.caja(2, 10, 66, 16, "ESPECTRO")
    for columna in range(60):
        # Envolvente con forma (graves altos, caída hacia los agudos) más ruido
        # determinista. Sin la envolvente, el espectro es un muro y no dice nada.
        x = columna / 59
        envolvente = math.exp(-1.7 * x) + 0.42 * math.exp(-7 * (x - 0.26) ** 2)
        pulso = 0.82 + 0.18 * math.sin(columna / 3.1)
        altura = 1 + (envolvente * pulso * (0.30 + 1.05 * pseudo(columna * 17 + 5))) * 11
        if columna % 17 == 9:
            altura *= 0.25             # un hueco: la música respira
        altura = min(13.0, altura)
        entero = int(altura)
        resto = altura - entero
        base = 23                      # los bloques no tocan el borde inferior
        for fila in range(entero):
            c.texto(4 + columna, base - fila, "█", "title" if fila % 4 else "mag")
        if entero < 13 and resto > 0.2:
            c.texto(4 + columna, base - entero, BLOQUES[min(7, int(resto * 8))], "mag")
    c.texto(5, 24, "20 Hz" + " " * 47 + "20 kHz", "ghost")

    c.caja(70, 10, 28, 16, "MEDIDORES")
    medidores = [("GRAVES", 0.72), ("MEDIOS", 0.54), ("AGUDOS", 0.31),
                 ("REVERB", 0.40), ("SATURACIÓN", 0.86), ("WOBBLE", 0.22),
                 ("CINTA", 0.61), ("RUIDO", 0.34)]
    for indice, (nombre, valor) in enumerate(medidores):
        fila = 11 + indice
        estilo = "error" if valor > 0.8 else ("warn" if valor > 0.5 else "ok")
        c.texto(72, fila, nombre.ljust(12), "dim")
        c.texto(84, fila, "▓" * round(valor * 10) + "░" * (10 - round(valor * 10)), estilo)
    c.texto(72, 20, "─" * 24, "grid")
    c.texto(72, 21, "SALIDA ESTÉREO", "ghost")
    c.texto(72, 22, "▮▮▮▮▮▮▮▯▯▯  L", "title")
    c.texto(72, 23, "▮▮▮▮▮▯▯▯▯▯  R", "title")
    c.texto(72, 24, "compresor 4:1 · 8 ms", "dim")

    c.texto(2, 27, "▸ cinta rebobinada a mano · la velocidad puede bailar", "warn")
    barra_inferior(c, [("␣", "pausa"), ("←→", "pista"), ("S", "shuffle"),
                       ("V", "visual"), ("ESC", "salir")])


PANTALLAS = [
    ("01", "Arranque", "El logo son cinco filas de `█` sobre una fuente de 4×5 que "
     "cabe en el propio código. Debajo, barras `▓/░` y una línea de bloques `▁▂▃▄▅▆▇█`.",
     pantalla_arranque),
    ("02", "Intrusión", "Todo son pares hexadecimales en una rejilla de 6×8. El "
     "camino se marca invirtiendo el fondo de la celda: sin color, seguiría viéndose.",
     pantalla_intrusion),
    ("03", "Diagnóstico", "Barras horizontales y una serie temporal de un solo "
     "renglón. Cada estado lleva su porcentaje escrito al lado: el color nunca informa solo.",
     pantalla_diagnostico),
    ("04", "Mercado negro", "Tabla con columnas alineadas a la derecha, fila "
     "seleccionada por fondo invertido y panel de detalle a la derecha.",
     pantalla_mercado),
    ("05", "Comms", "Bandeja, lector y análisis en tres paneles. El texto corrompido "
     "son `▒` de verdad, no un efecto: lo que no se pudo descifrar no se inventa.",
     pantalla_comms),
    ("06", "Visualizador", "62 columnas de espectro con `█` y remates `▁▂▃▄▅▆▇`: "
     "cada columna es una altura entera más un bloque parcial.",
     pantalla_audio),
]


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------
def construir() -> list[tuple[str, str, str, Lienzo]]:
    salida = []
    for numero, nombre, nota, funcion in PANTALLAS:
        lienzo = Lienzo()
        funcion(lienzo)
        salida.append((numero, nombre, nota, lienzo))
    return salida


def spans(fila: list[Celda]) -> str:
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
:root{--bg:#04070c;--fg:#9fe8ff;--dim:#4a7f8f;--ghost:#26404a;--grid:#17414f;
 --title:#00f0ff;--mag:#ff2ec4;--ok:#39ff88;--warn:#ffd400;--error:#ff2e63;
 --sel-fg:#04070c;--sel-bg:#00f0ff;--bar-fg:#04070c;--bar-bg:#00f0ff;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
html[data-pal="magenta"]{--bg:#0b040d;--fg:#ffd9f6;--dim:#8a4374;--ghost:#3a1a30;
 --grid:#5a1b4a;--title:#ff2ec4;--mag:#00f0ff;--ok:#2effc8;--warn:#ffd400;
 --error:#ff3355;--sel-bg:#ff2ec4;--sel-fg:#0b040d;--bar-bg:#ff2ec4;--bar-fg:#0b040d}
html[data-pal="fosforo"]{--bg:#000;--fg:#7dff9d;--dim:#2f8f4c;--ghost:#123a20;
 --grid:#1c6b34;--title:#7dff9d;--mag:#b6ff7a;--ok:#7dff9d;--warn:#d7ff5f;
 --error:#ff5f5f;--sel-bg:#7dff9d;--sel-fg:#000;--bar-bg:#7dff9d;--bar-fg:#000}
html[data-pal="ambar"]{--bg:#0a0703;--fg:#ffcf7a;--dim:#8a5f22;--ghost:#3a2a10;
 --grid:#5c3d10;--title:#ffb000;--mag:#ff7043;--ok:#ffd75f;--warn:#ffb000;
 --error:#ff5f3f;--sel-bg:#ffb000;--sel-fg:#0a0703;--bar-bg:#ffb000;--bar-fg:#0a0703}
html[data-pal="mono"]{--bg:#0d0f13;--fg:#e6e6e6;--dim:#8a8a8a;--ghost:#4a4a4a;
 --grid:#5a5a5a;--title:#fff;--mag:#d0d0d0;--ok:#fff;--warn:#d0d0d0;--error:#fff;
 --sel-bg:#e6e6e6;--sel-fg:#0d0f13;--bar-bg:#e6e6e6;--bar-fg:#0d0f13}
*{box-sizing:border-box}
body{margin:0;background:#05070b;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:36px 0 24px;border-bottom:1px solid #14181f;margin-bottom:28px}
h1{margin:0 0 8px;font-size:28px;letter-spacing:-.02em}
h1 span{color:#00f0ff;font-family:var(--mono)}
.sub{color:#7d8590;font-size:15px;line-height:1.65;margin:0;max-width:78ch}
.controls{display:flex;gap:18px;align-items:center;margin-top:18px;font-size:13px;color:#7d8590;flex-wrap:wrap}
select{font-family:var(--mono);font-size:12.5px;background:#101319;color:#c9d1d9;border:1px solid #232a36;border-radius:7px;padding:6px 9px}
label{display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
section{margin:0 0 46px}
.head{display:flex;align-items:baseline;gap:11px;margin-bottom:5px}
.num{font-family:var(--mono);font-size:11px;color:#00f0ff;border:1px solid #12384a;border-radius:5px;padding:4px 7px}
h2{font-size:18px;margin:0;font-weight:600}
.nota{color:#7d8590;font-size:13.5px;line-height:1.6;margin:0 0 12px;max-width:88ch}
.nota code{font-family:var(--mono);background:#101319;border:1px solid #1b212b;border-radius:4px;padding:0 4px;color:#9fe8ff}
.term{background:var(--bg);border-radius:10px;padding:12px 14px;overflow-x:auto;
 box-shadow:0 0 0 1px #1d2530, 0 26px 60px -34px #000;position:relative}
.term pre{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.32;white-space:pre;color:var(--fg)}
.c-dim{color:var(--dim)}
.c-ghost{color:var(--ghost)}
.c-grid{color:var(--grid)}
.c-title{color:var(--title);font-weight:700}
.c-mag{color:var(--mag)}
.c-ok{color:var(--ok)}
.c-warn{color:var(--warn)}
.c-error{color:var(--error)}
.c-sel{background:var(--sel-bg);color:var(--sel-fg);font-weight:700}
.c-bar{background:var(--bar-bg);color:var(--bar-fg);font-weight:700}
.c-bar_tecla{background:var(--sel-fg);color:var(--bar-bg);font-weight:700}
html[data-crt="1"] .term::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:10px;
 background:repeating-linear-gradient(to bottom,rgba(0,0,0,.28) 0 1px,transparent 1px 3px)}
html[data-crt="1"] .term{text-shadow:0 0 7px currentColor}
html[data-crt="1"] .term::before{content:"";position:absolute;inset:0;pointer-events:none;border-radius:10px;
 background:radial-gradient(ellipse at center,transparent 55%,rgba(0,0,0,.45) 100%)}
footer{color:#7d8590;font-size:13.5px;line-height:1.75;border-top:1px solid #14181f;padding-top:20px}
footer code{font-family:var(--mono);background:#101319;border:1px solid #1b212b;border-radius:4px;padding:1px 5px;color:#a9b6c9}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0 0}
th,td{text-align:left;padding:8px 12px 8px 0;border-bottom:1px solid #14181f;vertical-align:top}
th{color:#7d8590;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:#9fe8ff;font-size:12.5px}
.aviso{background:#0b1016;border-left:3px solid #ff2ec4;padding:12px 15px;border-radius:0 7px 7px 0;
 color:#9aa7b4;font-size:13.5px;line-height:1.65;margin-top:16px}
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

    paletas = [("cian", "Cian neón"), ("magenta", "Magenta Miami"), ("fosforo", "Fósforo verde"),
               ("ambar", "Ámbar tóxico"), ("mono", "Sin color")]
    opciones = "".join(f'<option value="{v}">{n}</option>' for v, n in paletas)
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="cian" data-crt="0">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEUROLINK · mockups de una TUI cyberpunk</title>
<style>{CSS}</style></head>
<body>
<div class="wrap">
<header>
  <h1>NEUROLINK <span>· mockups de una TUI cyberpunk</span></h1>
  <p class="sub">Seis pantallas de una terminal que no existe, dibujadas sobre una rejilla
  de <strong>100 × 30 celdas</strong>. Todo lo que ves son caracteres y colores: ningún
  elemento de esta página es una imagen. El conmutador de paleta cambia el tema real; el
  interruptor CRT es <em>decoración de la galería</em> y está desactivado por defecto,
  porque una terminal de verdad no tiene curvatura ni líneas de barrido.</p>
  <div class="controls">
    <label>Paleta <select id="pal">{opciones}</select></label>
    <label><input type="checkbox" id="crt"> efecto CRT (solo aquí, no es del TUI)</label>
  </div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">07</span><h2>Por qué esto se puede construir de verdad</h2></div>
  <p class="nota">El compromiso de estos mockups es que ninguno promete algo que una
  terminal no pueda hacer. Cada pantalla se valida al generarse: si una línea se pasa de
  100 columnas o aparece un carácter de doble ancho, el script falla.</p>
  <table>
    <tr><th>Lo que se ve</th><th>Cómo se consigue</th></tr>
    <tr><td>Foto fija de 100×30</td><td><code>sys.stdout.write</code> de 30 líneas de 100 caracteres. Nada más</td></tr>
    <tr><td>Colores neón</td><td>SGR <code>38;2;r;g;b</code> (color verdadero) con caída a <code>38;5;n</code> (256) y a los 16 clásicos</td></tr>
    <tr><td>Bloques <code>█▓▒░</code></td><td>Caracteres de dibujo de bloques. Ancho uno en terminales occidentales</td></tr>
    <tr><td>Serie <code>▁▂▃▄▅▆▇█</code></td><td>Ocho niveles de altura reales: se elige el nivel por valor, sin trucos</td></tr>
    <tr><td>Filas resaltadas</td><td>Fondo invertido (<code>7m</code>) o color de fondo explícito. Nunca solo negrita</td></tr>
    <tr><td>Marcos y paneles</td><td>Dibujo de caja <code>┌─┐│└┘</code>, o <code>+-|</code> en modo ASCII</td></tr>
    <tr><td>Espectro "animado"</td><td>Repintado de celdas a 4–8 fotogramas por segundo; aquí va congelado</td></tr>
  </table>
  <div class="aviso"><strong>Lo que no hay, a propósito:</strong> ni imágenes, ni fuentes
  incrustadas, ni transparencias, ni degradados suaves, ni texto de tamaño variable, ni
  emoji a color. Un degradado real en terminal se hace con dithering de bloques o con
  pasos de 256 colores — y se nota. Elegir el palo corto es lo que hace que el mockup
  sea creíble.</div>
</section>
<footer>
  Generado por <code>cyberpunk.py</code> · solo biblioteca estándar ·
  misma rejilla de celdas que usa cualquier TUI: si cabe aquí, cabe en tu terminal.
</footer>
</div>
<script>{JS}</script>
</body></html>"""


# ---------------------------------------------------------------------------
# Salida por terminal, con color de verdad
# ---------------------------------------------------------------------------
ANSI = {
    "": "\x1b[38;2;159;232;255m", "dim": "\x1b[38;2;74;127;143m",
    "ghost": "\x1b[38;2;38;64;74m", "grid": "\x1b[38;2;23;65;79m",
    "title": "\x1b[1;38;2;0;240;255m", "mag": "\x1b[1;38;2;255;46;196m",
    "ok": "\x1b[38;2;57;255;136m", "warn": "\x1b[38;2;255;212;0m",
    "error": "\x1b[1;38;2;255;46;99m", "sel": "\x1b[1;38;2;4;7;12;48;2;0;240;255m",
    "bar": "\x1b[1;38;2;4;7;12;48;2;0;240;255m",
    "bar_tecla": "\x1b[1;38;2;0;240;255;48;2;4;7;12m",
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
        for numero, problema in problemas[:20]:
            print(f"[{numero}] {problema}", file=sys.stderr)
        return 1

    if "--ansi" in argv:
        for _, nombre, _, lienzo in pantallas:
            print(f"\n── {nombre} " + "─" * (ANCHO - len(nombre) - 4))
            sys.stdout.write(pintar(lienzo))
        return 0

    destino_html = "cyberpunk.html"
    with open(destino_html, "w", encoding="utf-8") as fh:
        fh.write(construir_html(pantallas))
    with open("cyberpunk.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")

    anchos = {len(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · máx. {max(anchos)} columnas "
          f"· 0 caracteres de doble ancho → {destino_html} y cyberpunk.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
