#!/usr/bin/env python3
"""Motor de celdas compartido por los mockups.

Sale del generador cyberpunk, que ya funcionaba: misma rejilla, mismo verificador
de bordes, mismas utilidades de barra y serie. Se separa aquí para que un segundo
estilo (Minority Report) no tenga que copiarlo ni tocarlo.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

BLOQUES = "▁▂▃▄▅▆▇█"


@dataclass(slots=True)
class Celda:
    char: str = " "
    estilo: str = ""


class Lienzo:
    def __init__(self, ancho: int, alto: int) -> None:
        self.ancho, self.alto = ancho, alto
        self.rejilla = [[Celda() for _ in range(ancho)] for _ in range(alto)]
        self._paneles: list[dict] = []

    # --- primitivas --------------------------------------------------------
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

    def revestir_paneles(self, reflejo: bool = False) -> None:
        """Da cuerpo de cristal a los paneles **sin ensuciar la lectura**.

        Antes esto era una trama `░` por todo el interior y competía con el texto:
        un panel lleno de puntos es bonito de lejos y agotador de cerca. Ahora hay
        dos capas distintas:

        1. **Tinte plano** en todas las celdas vacías del interior: da volumen al
           panel sin dibujar un solo carácter.
        2. **Reflejo** `░` opcional, solo en las dos primeras filas del borde
           superior y solo donde hay siete columnas libres seguidas. Viene apagado:
           el cristal se lee igual sin él y el texto no paga el adorno.

        El resultado se lee igual de bien en una terminal de 16 colores que en una
        con color verdadero, porque la legibilidad ya no depende del contraste de un
        glifo de fondo.
        """
        for panel in self._paneles:
            x, y, ancho, alto = panel["x"], panel["y"], panel["ancho"], panel["alto"]
            for fila in range(y + 1, y + alto - 1):
                if not 0 <= fila < self.alto:
                    continue
                for columna in range(x + 1, x + ancho - 1):
                    celda = self.rejilla[fila][columna]
                    if celda.char == " " and celda.estilo == "":
                        celda.estilo = "glass_fill"
            # El reflejo solo se posa donde hay aire: una celda cuenta como libre
            # si lo están también sus tres vecinas de cada lado. Siete columnas
            # seguidas de blanco son una zona vacía de verdad, no un hueco entre
            # dos palabras.
            if not reflejo:
                continue
            for paso, fila_reflejo in ((3, y + 1), (7, y + 2)):
                if fila_reflejo >= y + alto - 1 or not 0 <= fila_reflejo < self.alto:
                    continue
                fila_ref = self.rejilla[fila_reflejo]
                for columna in range(x + 4, x + ancho - 5):
                    if (columna + fila_reflejo) % paso:
                        continue
                    vecinas = fila_ref[columna - 3:columna + 4]
                    if any(v.char != " " for v in vecinas):
                        continue
                    fila_ref[columna] = Celda("░", "glare")

    def _registro(self, x, y, ancho, alto, titulo, tl, tr, bl, br, h, v) -> dict:
        return {"x": x, "y": y, "ancho": ancho, "alto": alto,
                "titulo": len(f" {titulo} ") if titulo else 0,
                "tl": tl, "tr": tr, "bl": bl, "br": br, "h": h, "v": v}

    def marco(self, x: int, y: int, ancho: int, alto: int, titulo: str = "",
              estilo: str = "stroke", titulo_estilo: str | None = None) -> None:
        """Marco de doble línea: el contorno grueso y luminoso del estilo consola."""
        self._paneles.append(self._registro(x, y, ancho, alto, titulo,
                                            "╔", "╗", "╚", "╝", "═", "║"))
        self.texto(x, y, "╔" + "═" * (ancho - 2) + "╗", estilo)
        for f in range(y + 1, y + alto - 1):
            self.texto(x, f, "║", estilo)
            self.texto(x + ancho - 1, f, "║", estilo)
        self.texto(x, y + alto - 1, "╚" + "═" * (ancho - 2) + "╝", estilo)
        if titulo:
            self.texto(x + 2, y, f" {titulo} ", titulo_estilo or estilo)

    def caja(self, x: int, y: int, ancho: int, alto: int, titulo: str = "",
             estilo: str = "grid", titulo_estilo: str = "title") -> None:
        """Caja cerrada de toda la vida: borde continuo. Para lo que no es cristal."""
        self._paneles.append(self._registro(x, y, ancho, alto, titulo,
                                            "┌", "┐", "└", "┘", "─", "│"))
        self.texto(x, y, "┌" + "─" * (ancho - 2) + "┐", estilo)
        for f in range(y + 1, y + alto - 1):
            self.texto(x, f, "│", estilo)
            self.texto(x + ancho - 1, f, "│", estilo)
        self.texto(x, y + alto - 1, "└" + "─" * (ancho - 2) + "┘", estilo)
        if titulo:
            self.texto(x + 2, y, f" {titulo} ", titulo_estilo)

    def panel(self, x: int, y: int, ancho: int, alto: int, titulo: str = "",
              estilo: str = "glass", titulo_estilo: str = "title") -> None:
        """Panel flotante: esquinas sueltas y bordes discontinuos ``╌``."""
        self._paneles.append(self._registro(x, y, ancho, alto, titulo,
                                            "┌", "┐", "└", "┘", "╌", ""))
        self.texto(x, y, "┌", estilo)
        self.texto(x + ancho - 1, y, "┐", estilo)
        self.texto(x, y + alto - 1, "└", estilo)
        self.texto(x + ancho - 1, y + alto - 1, "┘", estilo)
        for columna in range(x + 1, x + ancho - 1):
            self.texto(columna, y, "╌", estilo)
            self.texto(columna, y + alto - 1, "╌", estilo)
        if titulo:
            self.texto(x + 2, y, f" {titulo} ", titulo_estilo)

    def limpiar(self, x: int, y: int, ancho: int, alto: int, estilo: str = "glass_fill") -> None:
        """Deja una zona limpia: fondo plano y ni un carácter. Para leyendas."""
        for fila in range(y, y + alto):
            if 0 <= fila < self.alto:
                for columna in range(x, x + ancho):
                    if 0 <= columna < self.ancho:
                        self.rejilla[fila][columna] = Celda(" ", estilo)

    # --- lectura -----------------------------------------------------------
    def lineas(self) -> list[str]:
        return ["".join(c.char for c in fila) for fila in self.rejilla]

    def comprobar(self) -> list[str]:
        problemas = []
        for indice, fila in enumerate(self.rejilla):
            if len(fila) != self.ancho:
                problemas.append(f"fila {indice}: {len(fila)} celdas")
            for celda in fila:
                if unicodedata.east_asian_width(celda.char) in ("W", "F"):
                    problemas.append(f"fila {indice}: doble ancho {celda.char!r}")
                if celda.char < " " or celda.char == "\x7f":
                    problemas.append(f"fila {indice}: control {celda.char!r}")
        for panel in self._paneles:
            x, y, ancho, alto = panel["x"], panel["y"], panel["ancho"], panel["alto"]
            tl, tr = panel["tl"], panel["tr"]
            bl, br = panel["bl"], panel["br"]
            h, v = panel["h"], panel["v"]
            largo_titulo = panel["titulo"]
            esperado = {
                (x, y): tl, (x + ancho - 1, y): tr,
                (x, y + alto - 1): bl, (x + ancho - 1, y + alto - 1): br,
            }
            for columna in range(x + 1, x + ancho - 1):
                if largo_titulo and x + 2 <= columna < x + 2 + largo_titulo:
                    continue
                esperado[(columna, y)] = h
                esperado[(columna, y + alto - 1)] = h
            if v:
                for fila in range(y + 1, y + alto - 1):
                    esperado[(x, fila)] = v
                    esperado[(x + ancho - 1, fila)] = v
            for fila in range(y, y + alto):
                for columna in (x + ancho, x + ancho + 1):
                    if columna < self.ancho and self.rejilla[fila][columna].char not in " ":
                        problemas.append(
                            f"panel ({x},{y}) {ancho}x{alto}: el contenido se sale por la "
                            f"derecha, en ({columna},{fila}) hay "
                            f"{self.rejilla[fila][columna].char!r}")
            for (columna, fila), glifo in esperado.items():
                real = self.rejilla[fila][columna].char
                if real != glifo and not (glifo in ("╌", "═") and real == glifo):
                    problemas.append(
                        f"panel ({x},{y}) {ancho}x{alto}: en ({columna},{fila}) "
                        f"se esperaba {glifo!r} y hay {real!r}")
        return problemas


# ---------------------------------------------------------------------------
# utilidades de composición
# ---------------------------------------------------------------------------
def recorta(texto: str, ancho: int) -> str:
    if len(texto) <= ancho:
        return texto
    corte = texto[: max(1, ancho - 1)]
    if " " in corte:
        corte = corte[: corte.rfind(" ")]
    return corte.rstrip(" ,;:") + "…"


def barra(valor: float, celdas: int, lleno: str = "▓", vacio: str = "░") -> str:
    dentro = round(max(0.0, min(1.0, valor)) * celdas)
    return lleno * dentro + vacio * (celdas - dentro)


def chispa(valores: list[float]) -> str:
    return "".join(BLOQUES[min(7, int(v * 7 + 0.5))] for v in valores)


def pseudo(semilla: int) -> float:
    x = (semilla * 1103515245 + 12345) & 0x7FFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0x7FFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFF) / 0xFFFF


def espaciado(texto: str, huecos: int = 1) -> str:
    """'PRECRIME' → 'P R E C R I M E': versalitas espaciadas, tan de este estilo."""
    return (" " * huecos).join(texto)
