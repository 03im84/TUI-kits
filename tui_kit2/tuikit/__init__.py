"""Réplica desacoplada de la TUI de Incunable.

Siete pantallas, teclas de verdad y un marco de texto por fotograma. El mundo
exterior está detrás de :class:`tuikit.backend.Backend`; por defecto se usa el
mundo de mentira (:class:`DemoBackend`).

    from tuikit import App, DemoBackend
    app = App(DemoBackend())
    app.handle("ENTER"); app.run_pending()
    print("\\n".join(app.render(90, 26)))

Módulos:

* ``keys``   · de pulsaciones a nombres de tecla.
* ``screen`` · lienzo de celdas, marcas y dibujo de caja.
* ``term``   · el aparato: modo crudo, tamaño, pintado con estilos.
* ``theme``  · siete temas de terminal y estilos con nombre.
* ``i18n``   · textos en español e inglés, fuera de las pantallas.
* ``app``    · las siete pantallas y el teclado.
* ``demo``   · corredor de marcos para vista previa y pruebas.
"""

from __future__ import annotations

from .app import SCREENS, App
from .backend import Analisis, Backend, DemoBackend, Libro
from .i18n import Translator
from .screen import Canvas
from . import theme

__all__ = ["App", "SCREENS", "Canvas", "Translator", "Backend", "DemoBackend",
           "Libro", "Analisis", "theme"]
__version__ = "0.1.0"
