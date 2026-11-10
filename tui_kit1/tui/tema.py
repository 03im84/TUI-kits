"""Temas para terminal (emulaciones de monitores antiguos).

Solo los 7 temas que tienen sentido en una TUI (terminal de texto),
no los 3 de interfaz gráfica/web (oscuro, claro, sepia) que aquí no aplican:

* `alto_contraste` — blanco puro sobre negro, máximo contraste.
* `ambar` — texto ámbar sobre negro, como monitores IBM antiguos.
* `blanco_calido` — blanco con tono amarillento sobre negro.
* `daltonico` — colores seguros para daltónicos (evita confusión rojo/verde).
* `fosforo` — texto verde fosforescente sobre negro, monitores antiguos.
* `fosforo_color` — verde fosforescente con acento de color.
* `verde_apagado` — texto verde oscuro sobre negro, monitores de oficina.

Incluye `mono` para tuberías o sesiones remotas sin color.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Colores:
    """Paleta mínima para terminal."""

    texto: str
    tenue: str
    resaltado: str
    exito: str
    aviso: str
    error: str
    borde: str
    etiqueta: str
    valor: str


#: Paletas por defecto. Códigos ANSI estándar y de 256 colores.
_PALETAS = {
    "alto_contraste": Colores(
        texto="\033[38;5;231m",   # blanco puro
        tenue="\033[38;5;252m",   # blanco tenue
        resaltado="\033[1;38;5;231m",
        exito="\033[38;5;46m",    # verde brillante
        aviso="\033[38;5;214m",   # naranja brillante
        error="\033[38;5;196m",   # rojo brillante
        borde="\033[38;5;252m",
        etiqueta="\033[38;5;15m", # blanco brillante
        valor="\033[38;5;231m",
    ),
    "ambar": Colores(
        texto="\033[38;5;214m",   # ámbar clásico
        tenue="\033[38;5;209m",
        resaltado="\033[1;38;5;214m",
        exito="\033[38;5;214m",
        aviso="\033[38;5;214m",
        error="\033[38;5;196m",
        borde="\033[38;5;209m",
        etiqueta="\033[38;5;214m",
        valor="\033[38;5;214m",
    ),
    "blanco_calido": Colores(
        texto="\033[38;5;223m",   # blanco cálido / crema
        tenue="\033[38;5;230m",
        resaltado="\033[1;38;5;223m",
        exito="\033[38;5;154m",   # verde claro
        aviso="\033[38;5;222m",   # amarillo suave
        error="\033[38;5;210m",   # rojo suave
        borde="\033[38;5;230m",
        etiqueta="\033[38;5;223m",
        valor="\033[38;5;223m",
    ),
    "daltonico": Colores(
        texto="\033[38;5;33m",    # azul seguro para daltónicos
        tenue="\033[38;5;69m",
        resaltado="\033[1;38;5;33m",
        exito="\033[38;5;214m",   # naranja (seguro para daltónicos)
        aviso="\033[38;5;202m",   # rojo-naranja
        error="\033[38;5;196m",
        borde="\033[38;5;69m",
        etiqueta="\033[38;5;33m",
        valor="\033[38;5;33m",
    ),
    "fosforo": Colores(
        texto="\033[38;5;46m",    # verde fosforescente clásico
        tenue="\033[38;5;82m",
        resaltado="\033[1;38;5;46m",
        exito="\033[38;5;46m",
        aviso="\033[38;5;214m",
        error="\033[38;5;196m",
        borde="\033[38;5;82m",
        etiqueta="\033[38;5;46m",
        valor="\033[38;5;46m",
    ),
    "fosforo_color": Colores(
        texto="\033[38;5;46m",    # verde fosforescente
        tenue="\033[38;5;82m",
        resaltado="\033[1;38;5;46m",
        exito="\033[38;5;46m",
        aviso="\033[38;5;226m",   # amarillo brillante
        error="\033[38;5;196m",
        borde="\033[38;5;82m",
        etiqueta="\033[38;5;226m",
        valor="\033[38;5;46m",
    ),
    "verde_apagado": Colores(
        texto="\033[38;5;28m",    # verde oscuro de oficina
        tenue="\033[38;5;58m",
        resaltado="\033[1;38;5;28m",
        exito="\033[38;5;28m",
        aviso="\033[38;5;184m",   # amarillo pálido
        error="\033[38;5;124m",   # rojo oscuro
        borde="\033[38;5;58m",
        etiqueta="\033[38;5;28m",
        valor="\033[38;5;28m",
    ),
    "mono": Colores(
        texto="",
        tenue="",
        resaltado="",
        exito="",
        aviso="",
        error="",
        borde="",
        etiqueta="",
        valor="",
    ),
}

RESET = "\033[0m"
NEGRITA = "\033[1m"


def soporta_colores() -> bool:
    """Devuelve True si la terminal parece soportar colores ANSI."""
    import os

    return os.name != "nt" or "WT_SESSION" in os.environ or "TERM" in os.environ


class Tema:
    """Tema de colores para la interfaz de terminal.

    No sabe de aplicaciones específicas. Solo traduce semántica
    (éxito, aviso, error, borde…) a códigos ANSI.
    """

    def __init__(self, nombre: str = "alto_contraste", forzar_mono: bool = False) -> None:
        if forzar_mono or nombre not in _PALETAS:
            nombre = "mono"
        self._colores = _PALETAS[nombre]
        self._activo = soporta_colores() and nombre != "mono"

    def pinta(self, texto: str, clave: str) -> str:
        """Envuelve `texto` con el código ANSI de `clave` si hay colores activos."""
        if not self._activo:
            return texto
        codigo = getattr(self._colores, clave, self._colores.texto)
        return f"{codigo}{texto}{RESET}"

    @property
    def nombre(self) -> str:
        return next(
            (k for k, v in _PALETAS.items() if v == self._colores), "mono"
        )

    @staticmethod
    def disponibles() -> tuple[str, ...]:
        return (
            "alto_contraste",
            "ambar",
            "blanco_calido",
            "daltonico",
            "fosforo",
            "fosforo_color",
            "verde_apagado",
            "mono",
        )
