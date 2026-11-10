"""TUI Kit — Interfaz de terminal genérica.

Extraído de los patrones de Muelle pero desvinculado de cualquier producto
específico. Sirve como base para construir aplicaciones de línea de órdenes
con paneles, cajas, tablas y prompts seguros.

Solo biblioteca estándar de Python.
"""

from .lienzo import Lienzo
from .tema import Tema
from .prompt import preguntar_clave, preguntar_si_no, preguntar_texto

__all__ = [
    "Lienzo",
    "Tema",
    "preguntar_clave",
    "preguntar_si_no",
    "preguntar_texto",
]
