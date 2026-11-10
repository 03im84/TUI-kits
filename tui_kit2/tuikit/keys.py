"""Decodificación de teclas del terminal.

Sin dependencias: las secuencias de escape se leen como bytes y se convierten en
nombres estables. Todo el producto se maneja sin ratón, así que esta tabla es el
contrato de entrada completo:

``UP DOWN LEFT RIGHT HOME END ENTER ESC TAB BACKSPACE DELETE F1 CTRL_C`` y
cualquier carácter imprimible como ``char:<c>``.
"""

from __future__ import annotations

UP = "UP"
DOWN = "DOWN"
LEFT = "LEFT"
RIGHT = "RIGHT"
HOME = "HOME"
END = "END"
PAGEUP = "PAGEUP"
PAGEDOWN = "PAGEDOWN"
ENTER = "ENTER"
ESC = "ESC"
TAB = "TAB"
BACKSPACE = "BACKSPACE"
DELETE = "DELETE"
F1 = "F1"
CTRL_C = "CTRL_C"

_SEQUENCES = {
    b"\x1b[A": UP, b"\x1b[B": DOWN, b"\x1b[C": RIGHT, b"\x1b[D": LEFT,
    b"\x1bOA": UP, b"\x1bOB": DOWN, b"\x1bOC": RIGHT, b"\x1bOD": LEFT,
    b"\x1b[H": HOME, b"\x1b[F": END, b"\x1b[1~": HOME, b"\x1b[4~": END,
    b"\x1b[3~": DELETE, b"\x1bOP": F1, b"\x1b[11~": F1,
    # Estas dos existían en la aplicación (el modal de métricas las maneja desde
    # la 1.5.0) pero el decodificador no las producía: no funcionaban.
    b"\x1b[5~": PAGEUP, b"\x1b[6~": PAGEDOWN,
    b"\r": ENTER, b"\n": ENTER, b"\t": TAB, b"\x7f": BACKSPACE, b"\x08": BACKSPACE,
    b"\x03": CTRL_C, b"\x1b": ESC,
}


def decode(data: bytes) -> list[str]:
    """Convierte bytes leídos del terminal en una lista de teclas lógicas."""
    keys: list[str] = []
    index = 0
    while index < len(data):
        matched = False
        for length in (4, 3):
            chunk = data[index:index + length]
            if chunk in _SEQUENCES:
                keys.append(_SEQUENCES[chunk])
                index += length
                matched = True
                break
        if matched:
            continue
        chunk = data[index:index + 1]
        if chunk in _SEQUENCES:
            keys.append(_SEQUENCES[chunk])
        else:
            try:
                keys.append("char:" + chunk.decode("utf-8"))
            except UnicodeDecodeError:
                keys.append("char:?")
        index += 1
    return keys
