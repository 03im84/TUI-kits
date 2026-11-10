"""Capa de terminal: lo único del producto que sabe en qué sistema corre.

Todo lo demás (lienzo, pantallas, teclas, corredor) es igual en cualquier
sistema. Aquí se encierra la diferencia, que es corta pero real:

* **POSIX** — ``termios``/``tty`` para el modo crudo y ``select`` para esperar.
* **Windows** — ``msvcrt`` para las teclas y ``ctypes`` para pedirle a la consola
  que entienda secuencias ANSI (``ENABLE_VIRTUAL_TERMINAL_PROCESSING``).

La capa devuelve **bytes** en los dos casos, así que ``keys.decode`` sigue siendo
el único decodificador del producto y las pantallas no se enteran de nada.

Adaptado de la capa de plataforma de Muelle (obra del mismo autor), recortado a
lo que Incunable usa: la versión original traía además ayudas de sockets y de
procesos que aquí no tienen sitio — esta herramienta no abre un solo puerto.
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from typing import IO

IS_WINDOWS = os.name == "nt"

#: Chrome del terminal: lienzo aparte y cursor oculto.
ENTRAR_PANTALLA = "\x1b[?1049h\x1b[?25l"
SALIR_PANTALLA = "\x1b[?25h\x1b[?1049l"


def habilitar_ansi(salida: IO | None = None) -> bool:
    """Permite secuencias ANSI en la consola de Windows 10+. En POSIX, nada.

    Windows nace sin interpretar los códigos de color; la consola moderna los
    entiende si se le pide por la API. Si la llamada falla (consola antigua,
    redirección a un archivo), se devuelve ``False`` y el corredor sigue
    adelante: los marcos ``[OK]``/``[x]`` se leen igual sin color.
    """
    if not IS_WINDOWS:
        return True
    try:  # pragma: no cover - solo se ejecuta en Windows
        import ctypes

        kernel32 = ctypes.windll.kernel32
        habilitado = True
        for identificador in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            manejador = kernel32.GetStdHandle(identificador)
            modo = ctypes.c_uint32()
            if not kernel32.GetConsoleMode(manejador, ctypes.byref(modo)):
                habilitado = False
                continue
            if not kernel32.SetConsoleMode(manejador, modo.value | 0x0004):
                habilitado = False
        return habilitado
    except Exception:
        return False


#: Teclas extendidas de ``msvcrt``: llegan en dos tiempos (``\x00`` o ``\xe0`` y
#: luego la letra) y se traducen a la misma secuencia que manda un terminal POSIX.
_EXTENDIDAS = {
    "H": b"\x1b[A",  # arriba
    "P": b"\x1b[B",  # abajo
    "M": b"\x1b[C",  # derecha
    "K": b"\x1b[D",  # izquierda
    "G": b"\x1b[H",  # inicio
    "O": b"\x1b[F",  # fin
    "S": b"\x1b[3~",  # suprimir
    "R": b"\x1b[2~",  # insertar (sin uso, pero no se pierde)
    ";": b"\x1bOP",  # F1
    "<": b"\x1bOQ",  # F2
    "=": b"\x1bOR",  # F3
    ">": b"\x1bOS",  # F4
}


def traducir_windows(tecla: str, siguiente: str | None = None) -> bytes:
    """Traduce lo que devuelve ``msvcrt.getwch`` a bytes de terminal POSIX.

    Es una función pura a propósito: así se prueba la rama de Windows sin tener
    Windows, que es justo lo que no se puede hacer en este entorno.
    """
    if tecla in ("\x00", "\xe0"):
        if siguiente is None:
            return b""
        return _EXTENDIDAS.get(siguiente, b"")
    return tecla.encode("utf-8", "replace")


class Teclado:
    """Lee teclas sueltas sin esperar al Enter, aquí y en Windows.

    Se usa como gestor de contexto porque en Unix hay que dejar la terminal como
    estaba: si el programa se va sin restaurarla, la consola de quien lo lanzó
    se queda sin eco y sin saltos de línea.
    """

    def __init__(self, entrada: IO | None = None) -> None:
        self.entrada = entrada if entrada is not None else sys.stdin
        self._guardado = None
        self._modo = ""

    @property
    def modo(self) -> str:
        """``"posix"``, ``"windows"`` o ``""`` si no hay terminal."""
        return self._modo

    def __enter__(self) -> "Teclado":
        if not es_terminal(self.entrada):
            self._modo = ""
            return self
        if IS_WINDOWS:  # pragma: no cover - solo Windows
            self._modo = "windows"
            return self
        try:  # pragma: no cover - necesita una terminal de verdad
            import termios
            import tty

            self._guardado = termios.tcgetattr(self.entrada)
            tty.setcbreak(self.entrada.fileno())
            self._modo = "posix"
        except Exception:
            self._modo = ""
        return self

    def __exit__(self, *_: object) -> None:
        if self._modo == "posix" and self._guardado is not None:  # pragma: no cover
            import termios

            termios.tcsetattr(self.entrada, termios.TCSADRAIN, self._guardado)
        self._modo = ""

    def leer(self, espera: float = 0.0) -> bytes:
        """Devuelve las teclas pulsadas, o ``b""`` si no hubo ninguna."""
        if self._modo == "windows":  # pragma: no cover - solo Windows
            import msvcrt

            limite = time.monotonic() + espera
            while True:
                if msvcrt.kbhit():
                    tecla = msvcrt.getwch()
                    if tecla in ("\x00", "\xe0"):
                        return traducir_windows(tecla, msvcrt.getwch())
                    return traducir_windows(tecla)
                if time.monotonic() >= limite:
                    return b""
                time.sleep(0.02)
        if self._modo != "posix":
            return b""
        import select  # pragma: no cover - ruta POSIX

        descriptor = self.entrada.fileno()
        if not select.select([descriptor], [], [], espera)[0]:
            return b""
        # os.read y no self.entrada.read: el lector con búfer esperaría a llenar
        # el bloque y la interfaz no respondería a una sola tecla (F-27).
        return os.read(descriptor, 64)


def es_terminal(flujo: IO | None = None) -> bool:
    """¿Hay una terminal de verdad al otro lado del flujo?"""
    flujo = flujo if flujo is not None else sys.stdout
    try:
        return bool(flujo.isatty())
    except (AttributeError, ValueError):
        return False


def pantalla_alternativa(salida: IO | None = None, entrar: bool = True) -> None:
    """Entra o sale del lienzo aparte, sin pisar lo que había en la consola."""
    salida = salida if salida is not None else sys.stdout
    if not es_terminal(salida):
        return
    try:
        salida.write(ENTRAR_PANTALLA if entrar else SALIR_PANTALLA)
        salida.flush()
    except (BrokenPipeError, ValueError):  # pragma: no cover
        pass


def tamano(defecto: tuple[int, int] = (80, 24)) -> tuple[int, int]:
    """Ancho y alto del terminal, con un tamaño razonable si no lo dice."""
    medida = shutil.get_terminal_size(defecto)
    return max(20, medida.columns), max(8, medida.lines)
