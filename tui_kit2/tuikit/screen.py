"""Lienzo de caracteres para la TUI.

Un framebuffer de celdas: la aplicación escribe en una rejilla y el corredor la
vuelca al terminal. Así la interfaz se puede **probar sin terminal**: las
pruebas y el arnés de evidencia piden ``lines()`` y comparan texto.

Reglas de accesibilidad que se aplican aquí, no en cada pantalla:

* El color nunca es el único portador de significado: el estado se marca además
  con ``[OK]``, ``[!]``, ``[x]`` o con el símbolo de selección ``>``.
* Con ``ascii_only=True`` se usan ``+ - |`` en lugar de dibujo de caja.
"""

from __future__ import annotations

from dataclasses import dataclass

UNICODE_SET = {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│",
               "tee_l": "├", "tee_r": "┤"}
ASCII_SET = {"tl": "+", "tr": "+", "bl": "+", "br": "+", "h": "-", "v": "|",
             "tee_l": "+", "tee_r": "+"}

MARKS = {"ok": "[OK]", "warn": "[!]", "error": "[x]", "pending": "[ ]"}


@dataclass
class Cell:
    char: str = " "
    style: str = ""


class Canvas:
    """Rejilla de celdas con utilidades de composición."""

    def __init__(self, width: int, height: int, *, ascii_only: bool = False) -> None:
        self.width = max(20, width)
        self.height = max(6, height)
        self.ascii_only = ascii_only
        self.chars = ascii_only
        self.grid = [[Cell() for _ in range(self.width)] for _ in range(self.height)]

    # --- primitivas ---------------------------------------------------------
    def clear(self) -> None:
        self.grid = [[Cell() for _ in range(self.width)] for _ in range(self.height)]

    def text(self, x: int, y: int, value: str, style: str = "") -> None:
        if y < 0 or y >= self.height:
            return
        for offset, char in enumerate(value):
            column = x + offset
            if 0 <= column < self.width:
                self.grid[y][column] = Cell(char, style)

    def fill(self, x: int, y: int, width: int, height: int, style: str = "") -> None:
        for row in range(y, y + height):
            for column in range(x, x + width):
                if 0 <= row < self.height and 0 <= column < self.width:
                    self.grid[row][column] = Cell(" ", style)

    def box(self, x: int, y: int, width: int, height: int, title: str = "",
            style: str = "") -> None:
        glyphs = ASCII_SET if self.ascii_only else UNICODE_SET
        if width < 2 or height < 2:
            return
        self.text(x, y, glyphs["tl"] + glyphs["h"] * (width - 2) + glyphs["tr"], style)
        for row in range(y + 1, y + height - 1):
            self.text(x, row, glyphs["v"], style)
            self.text(x + width - 1, row, glyphs["v"], style)
        self.text(x, y + height - 1, glyphs["bl"] + glyphs["h"] * (width - 2) + glyphs["br"], style)
        if title:
            label = f" {title} "
            self.text(x + 2, y, label[: max(0, width - 4)], style)

    def rule(self, x: int, y: int, width: int, style: str = "") -> None:
        glyph = "-" if self.ascii_only else "─"
        self.text(x, y, glyph * width, style)

    # --- composición --------------------------------------------------------
    def wrap(self, width: int, value: str) -> list[str]:
        """Ajuste de línea por palabras, respetando palabras larguísimas."""
        words = value.split(" ")
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip() if current else word
            if len(candidate) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
            while len(word) > width:
                lines.append(word[:width])
                word = word[width:]
            current = word
        if current:
            lines.append(current)
        return lines or [""]

    def paragraph(self, x: int, y: int, width: int, value: str, style: str = "",
                  max_lines: int | None = None) -> int:
        """Escribe un párrafo ajustado. Devuelve la altura consumida."""
        lines = self.wrap(width, value)
        if max_lines is not None:
            lines = lines[:max_lines]
        for offset, line in enumerate(lines):
            self.text(x, y + offset, line, style)
        return len(lines)

    def lines(self) -> list[str]:
        """Texto plano del lienzo (sin estilos): lo que ven las pruebas."""
        return ["".join(cell.char for cell in row).rstrip() for row in self.grid]

    def size(self) -> tuple[int, int]:
        return self.width, self.height
