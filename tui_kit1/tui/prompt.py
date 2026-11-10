"""Entrada segura de teclado para terminal.

Funciones para pedir datos al usuario sin romperse ante Ctrl+C o fin de entrada.
"""

from __future__ import annotations

from .lienzo import Lienzo


def preguntar_texto(
    lienzo: Lienzo,
    mensaje: str,
    defecto: str | None = None,
) -> str | None:
    """Pide una línea de texto al usuario.

    Devuelve None si el usuario cancela con Ctrl+C o Ctrl+D.
    """
    try:
        if defecto is not None:
            completo = f"{mensaje} [{defecto}]: "
        else:
            completo = f"{mensaje}: "
        valor = input(completo)
        if not valor and defecto is not None:
            return defecto
        return valor
    except (EOFError, KeyboardInterrupt):
        lienzo.escribir("")
        return None


def preguntar_clave(
    lienzo: Lienzo,
    mensaje: str,
    propuesta: str | None = None,
) -> str | None:
    """Pide una contraseña sin mostrarla en pantalla.

    Si se da `propuesta`, se sugiere y el usuario puede aceptarla con Enter.
    Devuelve None si se cancela.
    """
    import getpass

    try:
        if propuesta:
            completo = f"{mensaje} [{propuesta}]: "
        else:
            completo = f"{mensaje}: "
        valor = getpass.getpass(completo)
        if not valor and propuesta:
            return propuesta
        return valor
    except (EOFError, KeyboardInterrupt):
        lienzo.escribir("")
        return None


def preguntar_si_no(
    lienzo: Lienzo,
    mensaje: str,
    defecto_si: bool = False,
) -> bool | None:
    """Pide confirmación sí/no.

    Devuelve True/False o None si se cancela.
    """
    sufijo = " (S/n)" if defecto_si else " (s/N)"
    try:
        valor = input(f"{mensaje}{sufijo}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        lienzo.escribir("")
        return None

    if not valor:
        return defecto_si
    return valor in ("s", "si", "sí", "y", "yes", "1")
