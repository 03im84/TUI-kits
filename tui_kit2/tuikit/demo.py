"""Corredores: uno para mirar, otro para probar.

``storyboard()`` recorre la interfaz con un guion fijo y devuelve los marcos. Es
determinista: las mismas teclas dan los mismos textos, byte a byte. Sirve para
la vista previa de la documentación y para comparar dos versiones de la TUI sin
abrir un terminal.

``run()`` es el corredor de verdad: modo crudo, tamaño real, repintado con
estilos. La aplicación no sabe que existe: recibe ``bytes`` traducidos a teclas
y devuelve celdas.
"""

from __future__ import annotations

import sys
from typing import IO

from .app import App
from .backend import Backend, DemoBackend
from .keys import decode
from .screen import Canvas
from . import term, theme

# Un guion que pasa por **las siete pantallas** y por los dos modales.
GUION: tuple[tuple[str, str], ...] = (
    ("inicio", ""),
    ("inicio · bajar", "DOWN"), ("inicio · bajar", "DOWN"),
    ("diagnóstico", "ENTER"),
    ("opciones", "char:o"),
    ("opciones · bajar", "DOWN"), ("opciones · bajar", "DOWN"),
    ("opciones · encender EPUB", "ENTER"),
    ("opciones · bajar", "DOWN"),
    ("opciones · métricas", "char:m"),
    ("opciones · cerrar métricas", "ESC"),
    ("convertir", "char:c"),
    ("convertir · ¿conservar el HTML?", "char:s"),
    ("resultado", ""),
    ("configuración", "char:s"),
    ("fuentes", "char:f"),
    ("ayuda", "F1"),
    ("fuentes · cerrar la ayuda", "ESC"),
    ("inicio", "ESC"),
)


def storyboard(width: int = 92, height: int = 26, *, lang: str = "es",
               ascii_only: bool = False, backend: Backend | None = None,
               guion: tuple[tuple[str, str], ...] = GUION) -> list[tuple[str, list[str]]]:
    """Devuelve ``[(título, marco), …]`` recorriendo el guion dado."""
    app = App(backend or DemoBackend(), lang=lang, ascii_only=ascii_only)
    marcos: list[tuple[str, list[str]]] = []
    for titulo, tecla in guion:
        if tecla:
            app.handle(tecla)
        # se dibuja el estado ocupado **antes** de hacer el trabajo: así se ve
        marcos.append((titulo, app.render(width, height)))
        # cada paso de trabajo deja su marco: así se ve el progreso avanzar
        while app.pending:
            app.advance()
            marcos.append((f"{titulo} → paso", app.render(width, height)))
    return marcos


def volcar(marcos: list[tuple[str, list[str]]], salida: IO[str] | None = None) -> str:
    """Storyboard en texto: un rótulo por marco y el marco debajo."""
    salida = salida if salida is not None else sys.stdout
    trozos: list[str] = []
    for titulo, lineas in marcos:
        trozos.append(f"── {titulo} ".ljust(76, "─"))
        trozos.extend(lineas)
        trozos.append("")
    texto = "\n".join(trozos)
    salida.write(texto)
    return texto


def _pintar(app: App, ancho: int, alto: int, estilos: dict[str, str],
            salida: IO[str]) -> None:
    """Vuelca un marco agrupando celdas del mismo estilo: menos secuencias ANSI."""
    canvas = Canvas(ancho, alto, ascii_only=app.ascii_only)
    app.draw(canvas)
    piezas: list[str] = ["\x1b[H"]
    for fila in canvas.grid:
        actual = ""
        for celda in fila:
            if celda.style != actual:
                piezas.append(estilos.get(celda.style, ""))
                actual = celda.style
            piezas.append(celda.char)
        piezas.append("\x1b[0m\n")
    salida.write("".join(piezas))
    salida.flush()


def run(lang: str = "es", ascii_only: bool = False, backend: Backend | None = None,
        entrada: IO | None = None, salida: IO[str] | None = None) -> int:
    """Corredor interactivo. Devuelve el código de salida."""
    entrada = entrada if entrada is not None else sys.stdin
    salida = salida if salida is not None else sys.stdout
    if not term.es_terminal(salida):
        # sin terminal no hay tamaño que adivinar ni pantalla que limpiar
        volcar(storyboard(lang=lang, ascii_only=ascii_only, backend=backend), salida)
        return 0

    app = App(backend or DemoBackend(), lang=lang, ascii_only=ascii_only)
    term.habilitar_ansi(salida)
    ancho, alto = term.tamano()
    with term.Teclado(entrada) as teclado:
        term.pantalla_alternativa(salida, True)
        try:
            while True:
                ancho, alto = term.tamano((ancho, alto))
                _pintar(app, ancho, alto, theme.styles(app.state.tui_theme), salida)
                if app.pending:
                    app.run_pending()
                    continue
                for tecla in decode(teclado.leer(espera=0.05)):
                    if app.handle(tecla) == "quit":
                        return 0
        except KeyboardInterrupt:                 # pragma: no cover
            return 0
        finally:                                  # pragma: no cover
            term.pantalla_alternativa(salida, False)


if __name__ == "__main__":   # pragma: no cover
    raise SystemExit(run(sys.argv[1] if len(sys.argv) > 1 else "es"))
