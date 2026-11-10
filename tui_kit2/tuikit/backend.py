"""El mundo exterior, detrás de una interfaz.

La réplica de la TUI **no sabe convertir**: pide. Todo lo que toca el sistema de
archivos, un PDF o un convertidor vive detrás de este protocolo, y la aplicación
—pantallas, teclas, estado— no importa nada de ahí. Esa es la adaptación que hace
la interfaz portable: cambiar de producto es escribir otro ``Backend``.

``DemoBackend`` es una implementación completa y **determinista** —sin relojes, sin
esperas, sin disco— que sirve para tres cosas: enseñar la interfaz sin instalar
nada, probarla sin terminal y grabar los marcos de la vista previa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol


@dataclass
class Libro:
    """Un libro a la vista: lo que la lista necesita para pintarse."""

    ruta: Path
    nombre: str
    lugar: str = ""
    #: ``pdf``, ``epub`` o ``html`` (intermedio). Se muestra como prefijo.
    formato: str = "pdf"
    #: Tamaño conocido de antemano. Si es ``None`` se pregunta al disco.
    peso: int | None = None

    @property
    def tamano(self) -> int:
        if self.peso is not None:
            return self.peso
        try:
            return self.ruta.stat().st_size
        except OSError:
            return 0


@dataclass
class Analisis:
    """Lo que el diagnóstico enseña del libro elegido."""

    formato: str = "pdf"
    paginas: int = 0
    tamano_hoja: str = ""
    cifrado: bool = False
    caracteres: int = 0
    fuentes: int = 0
    imagenes: int = 0
    convertibles: int = 0
    bloques: int = 0
    avisos: int = 0
    palabras: int = 0
    capitulos: int = 0
    paginas_lectura: int = 0
    perfil: str = "limpio"

    def filas(self) -> dict[str, Any]:
        return {
            "pages": self.paginas, "page_sizes": [self.tamano_hoja] if self.tamano_hoja else [],
            "encrypted": self.cifrado, "chars": self.caracteres, "fonts": self.fuentes,
            "images": self.imagenes, "convertible": self.convertibles,
            "blocks": self.bloques, "warnings": self.avisos, "format": self.formato,
        }


class Backend(Protocol):
    """Lo que la interfaz necesita del mundo. Cinco cosas y ninguna más."""

    nombre_app: str
    version: str

    def libros(self) -> list[Libro]:
        """Los libros a la vista, ya ordenados. La lista es del backend."""

    def analizar(self, libro: Libro) -> Analisis:
        """Diagnóstico del libro. Se llama al pulsar ``i`` o Enter."""

    def medir(self, libro: Libro) -> dict[str, Any]:
        """Cifras para «El libro»: palabras, páginas, capítulos."""

    def convertir(self, libro: Libro, opciones: dict[str, Any],
                  progreso: Callable[[str, int, int], None]) -> dict[str, Any]:
        """Convierte y devuelve ``{"outputs": [...], "fidelity": {...}, "warnings": [...]}``."""


@dataclass
class DemoBackend:
    """Un mundo de mentira, pero con las formas del de verdad."""

    nombre_app: str = "Incunable"
    version: str = "1.12.0"
    contrato: str = "1.17"
    base: Path = field(default_factory=lambda: Path("/libros"))
    pasos: tuple[str, ...] = ("extract", "html", "md", "epub", "ebook", "reports")

    _libros: list[Libro] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self._libros:
            self._libros = [
                Libro(self.base / "ensayo" / "el-principito.pdf", "el-principito.pdf",
                      "ensayo", "pdf", 1_048_576),
                Libro(self.base / "ensayo" / "viaje-al-centro.pdf", "viaje-al-centro.pdf",
                      "ensayo", "pdf", 3_355_443),
                Libro(self.base / "ensayo" / "rayuela.pdf", "rayuela.pdf", "ensayo", "pdf", 2_202_010),
                Libro(self.base / "novela" / "fahrenheit-451.epub", "fahrenheit-451.epub",
                      "novela", "epub", 512_000),
                Libro(self.base / "novela" / "1984.epub", "1984.epub", "novela", "epub", 470_016),
                Libro(self.base / "manuales" / "manual-de-tipografia.pdf",
                      "manual-de-tipografia.pdf", "manuales", "pdf", 8_388_608),
                Libro(self.base / "manuales" / "el-arte-del-libro.pdf",
                      "el-arte-del-libro.pdf", "manuales", "pdf", 5_452_595),
                Libro(self.base / "salida" / "el-principito.html", "el-principito.html",
                      "salida", "html", 219_004),
            ]

    # --- interfaz ----------------------------------------------------------
    def libros(self) -> list[Libro]:
        return list(self._libros)

    def analizar(self, libro: Libro) -> Analisis:
        es_epub = libro.formato == "epub"
        return Analisis(
            formato=libro.formato,
            paginas=53 if libro.formato == "pdf" else 12,
            tamano_hoja="" if es_epub else "595.28x841.89",
            caracteres=0 if es_epub else 74_312,
            fuentes=6 if libro.formato == "pdf" else 0,
            imagenes=9 if libro.formato == "pdf" else 3,
            convertibles=9 if libro.formato == "pdf" else 3,
            bloques=412 if libro.formato == "pdf" else 96,
            avisos=2,
        )

    def medir(self, libro: Libro) -> dict[str, Any]:
        return {"words": 13_586, "pages": 53, "reading": 45, "chapters": 27,
                "per_page": 302, "structural": 12, "profile": "limpio"}

    def convertir(self, libro: Libro, opciones: dict[str, Any],
                  progreso: Callable[[str, int, int], None]) -> dict[str, Any]:
        salidas = []
        pedidos = [nombre for nombre, activo in opciones.get("targets", {}).items() if activo]
        for indice, paso in enumerate(pedidos, start=1):
            progreso(paso, indice, len(pedidos))
            salidas.append({
                "format": paso,
                "path": f"{opciones.get('out', 'output')}/{libro.ruta.stem}/{libro.ruta.stem}"
                        + {"html": ".html", "md": ".md", "epub": ".epub",
                           "ebook": ".ebook.html", "print": ".print.html"}.get(paso, ""),
                "bytes": {"html": 219_004, "md": 214_345, "epub": 146_909,
                          "ebook": 227_186, "print": 221_540}.get(paso, 0),
                "fidelity": 1.0,
            })
        return {"outputs": salidas,
                "fidelity": {paso["format"]: 1.0 for paso in salidas},
                "warnings": [{"code": "W-META-DUMMY",
                              "message": "Metadatos de relleno en subtitle, publisher…"}],
                "words": 13_586, "pages": 53, "reading": 45}
