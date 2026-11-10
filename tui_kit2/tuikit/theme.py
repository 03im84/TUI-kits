"""Temas de terminal: los siete colores que existen porque en una terminal se ven.

Cada tema es una tabla ``estilo → (color 256, negrita)``. El lienzo solo conoce
nombres de estilo (``title``, ``muted``, ``ok``, ``warn``, ``error``,
``selected``, ``bar``, ``overlay``); esto los convierte en códigos ANSI.

Con ``no_color`` los estilos valen cadena vacía: la interfaz sigue diciendo lo
mismo porque **el color nunca es lo único que informa** —para eso están las
marcas ``[OK]``, ``[!]``, ``[x]`` y el puntero ``>``—.
"""

from __future__ import annotations

PALETTES: dict[str, dict[str, tuple[int, bool]]] = {
    "high_contrast": {"tenue": (37, False), "titulo": (96, True), "exito": (92, True),
                      "aviso": (93, True), "error": (91, True), "resaltado": (30, True)},
    "amber": {"tenue": (90, False), "titulo": (93, True), "exito": (33, False),
              "aviso": (93, True), "error": (97, True), "resaltado": (97, True)},
    "phosphor": {"tenue": (90, False), "titulo": (92, True), "exito": (32, False),
                 "aviso": (92, True), "error": (97, True), "resaltado": (97, True)},
    "phosphor_color": {"tenue": (32, False), "titulo": (92, True), "exito": (92, False),
                       "aviso": (93, True), "error": (91, True), "resaltado": (97, True)},
    "warm_white": {"tenue": (90, False), "titulo": (97, True), "exito": (37, False),
                   "aviso": (97, True), "error": (97, True), "resaltado": (97, True)},
    "dim_green": {"tenue": (90, False), "titulo": (32, True), "exito": (32, False),
                  "aviso": (32, True), "error": (97, True), "resaltado": (97, True)},
    "colorblind": {"tenue": (90, False), "titulo": (96, True), "exito": (94, False),
                   "aviso": (93, False), "error": (91, True), "resaltado": (97, True)},
}

THEMES = tuple(PALETTES)

#: El único de los siete que se lee igual sobre fondo claro y sobre fondo oscuro.
DEFAULT = "high_contrast"

LABELS = {
    "es": {"high_contrast": "Alto contraste", "amber": "Ámbar", "phosphor": "Fósforo",
           "phosphor_color": "Fósforo color", "warm_white": "Blanco cálido",
           "dim_green": "Verde apagado", "colorblind": "Daltónico"},
    "en": {"high_contrast": "High contrast", "amber": "Amber", "phosphor": "Phosphor",
           "phosphor_color": "Phosphor colour", "warm_white": "Warm white",
           "dim_green": "Dim green", "colorblind": "Colour-blind safe"},
}

ESTILOS = ("bar", "title", "muted", "ok", "warn", "error", "selected", "overlay")


def canonical(value: str | None) -> str:
    return value if value in PALETTES else DEFAULT


def styles(value: str | None, no_color: bool = False) -> dict[str, str]:
    """Códigos ANSI por nombre de estilo, que es lo que entiende el lienzo."""
    if no_color:
        return {nombre: "" for nombre in ESTILOS}
    colores = PALETTES[canonical(value)]

    def code(token: str, extra: str = "") -> str:
        color, negrita = colores.get(token, (37, False))
        return f"\x1b[{extra}{'1;' if negrita else ''}38;5;{color}m"

    return {
        "title": code("titulo"),
        "muted": code("tenue"),
        "ok": code("exito"),
        "warn": code("aviso"),
        "error": code("error"),
        "selected": code("resaltado"),
        "bar": "\x1b[7m" + code("titulo"),
        "overlay": "\x1b[7m" + code("tenue"),
    }


def label(value: str | None, lang: str = "es") -> str:
    tabla = LABELS.get(lang, LABELS["es"])
    nombre = canonical(value)
    return tabla.get(nombre, nombre)


def cycle(value: str | None, delta: int, lang: str = "es") -> str:
    orden = list(THEMES)
    actual = canonical(value)
    return orden[(orden.index(actual) + delta) % len(orden)]
