"""Máquina de estados de la interfaz: siete pantallas y una barra de teclas.

La aplicación es **pura**: recibe teclas y devuelve marcos de texto. No abre el
terminal, no lee de la entrada estándar, no imprime y no espera. Eso la hace
probable sin terminal (basta pedir ``render(80, 24)`` y comparar líneas) y deja
el manejo del aparato al corredor.

El mundo exterior está detrás de :class:`tuikit.backend.Backend`: aquí no se abre
un archivo ni se convierte nada. Cambiar de producto es escribir otro backend.

Reglas que se ven en el dibujo, no en los comentarios:

* El color nunca informa solo: hay marcas ``[OK]``/``[!]``/``[x]`` y puntero ``>``.
* El pie **dice qué hace cada tecla** en la pantalla donde estás.
* Una línea de estado dice qué va a pasar si pulsas Enter.
* Las cifras se agrupan por miles y se alinean a la derecha.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .backend import Analisis, Backend, Libro
from .i18n import Translator
from .screen import MARKS, Canvas
from . import theme as temas

SCREENS = ("inicio", "diagnostico", "opciones", "progreso", "resultado", "config", "fuentes")
SCREEN_KEYS = {nombre: f"tui.screen.{clave}" for nombre, clave in (
    ("inicio", "start"), ("diagnostico", "diagnosis"), ("opciones", "options"),
    ("progreso", "progress"), ("resultado", "result"), ("config", "config"),
    ("fuentes", "sources"),
)}
PAPERS = ("a4", "letter", "legal")
PAPER_LABELS = {
    "a4": {"es": "A4 · 210×297 mm", "en": "A4 · 210×297 mm"},
    "letter": {"es": "Carta · 215,9×279,4 mm", "en": "US Letter · 8.5×11 in"},
    "legal": {"es": "Oficio · 215,9×355,6 mm", "en": "US Legal · 8.5×14 in"},
    "auto": {"es": "sin papel", "en": "no paper"},
}
KEEPS = ("ask", "yes", "no")
KEEP_LABELS = {"ask": {"es": "preguntar", "en": "ask"},
               "yes": {"es": "conservar", "en": "keep"},
               "no": {"es": "descartar", "en": "discard"}}
SPREADS = ("vertical", "horizontal", "dos")
SPREAD_LABELS = {"vertical": {"es": "una hoja", "en": "one page"},
                 "horizontal": {"es": "de lado", "en": "sideways"},
                 "dos": {"es": "dos hojas", "en": "two pages"}}
THEMES_DOC = ("auto", "light", "dark", "sepia", "epaper")
FORMATS = (("html", "HTML"), ("md", "Markdown"), ("epub", "EPUB"), ("ebook", "Ebook"),
           ("print", "PDF/imprimir"))

CONFIG_ORDER = ("lang", "theme", "tui_theme", "paper", "out_dir", "keep_intermediate",
                "reader_panel", "reader_spread", "words_per_page", "log_level", "overwrite")

DEFAULTS: dict[str, Any] = {
    "lang": "es", "theme": "auto", "tui_theme": temas.DEFAULT, "paper": "letter",
    "out_dir": "output", "keep_intermediate": "ask", "reader_panel": False,
    "reader_spread": "vertical", "words_per_page": 300, "log_level": "info",
    "overwrite": False,
}


#: Lo que no es dibujo de caja pero tampoco es ASCII, con reemplazo de un carácter.
ASCII_MAP = str.maketrans({"↑": "^", "↓": "v", "←": "<", "→": ">", "·": "-",
                           "«": '"', "»": '"', "×": "x", "—": "-", "’": "'",
                           "▸": ">", "▾": "v", "│": "|", "─": "-", "▲": "^", "▼": "v"})


@dataclass
class Step:
    """Un paso del progreso, con su marca."""

    name: str
    status: str = "pending"      # pending | running | done | failed


@dataclass
class ConvertState:
    """Lo que se va a hacer: formatos, papel, temas y reparto."""

    targets: dict[str, bool] = field(default_factory=lambda: {
        "html": True, "md": True, "epub": False, "ebook": False, "print": False})
    paper: str = "letter"
    paper_ebook: str = "auto"
    theme: str = "auto"
    tui_theme: str = temas.DEFAULT
    keep: str = "ask"
    out: str = "output"
    reader: bool = False
    spread: str = "vertical"

    def pedidos(self) -> list[str]:
        return [nombre for nombre, activo in self.targets.items() if activo]


class App:
    """Estado y dibujo. Toda la interfaz está aquí y nada más está aquí."""

    def __init__(self, backend: Backend, *, lang: str = "es", ascii_only: bool = False,
                 config: dict[str, Any] | None = None,
                 on_save_config: Callable[[dict[str, Any]], None] | None = None) -> None:
        self.backend = backend
        self.lang = lang if lang in ("es", "en") else "es"
        self.tr = Translator(self.lang)
        self.ascii_only = ascii_only
        self.on_save_config = on_save_config

        self.screen = "inicio"
        self.return_screen = "inicio"
        self.quit_requested = False
        self.help_visible = False
        self.metrics_panel = False
        self.metrics_scroll = 0
        self.message = ""
        self.message_style = "muted"
        self.pending: str | None = None
        self.busy = ""
        self.confirming_keep = False
        self.answer = ""

        # --- lista de libros (Inicio) ---------------------------------------
        self.files: list[Libro] = list(backend.libros())
        self.cursor = 0
        self.plegados: set[str] = set()
        self.agrupar = True
        self.filtrando = False
        self.filtro = ""
        self.editing = False
        self.path_text = ""
        self.pagina = 10

        # --- documento elegido y su análisis --------------------------------
        self.source: Libro | None = None
        self.info: Analisis | None = None
        self.resultado: dict[str, Any] | None = None
        self.steps: list[Step] = []
        self._cola: list[str] = []
        self._salidas: list[dict[str, Any]] = []
        self._avisos: list[dict[str, Any]] = []

        # --- opciones --------------------------------------------------------
        self.state = ConvertState()
        self.option_index = 0
        self._medidas_cache: tuple[Any, dict[str, Any]] = (None, {})
        self.config = dict(DEFAULTS, **(config or {}))
        self.config_index = 0
        self._aplicar_config()

        # --- fuentes ---------------------------------------------------------
        self.fuentes: list[str] = sorted({libro.lugar for libro in self.files if libro.lugar})
        self.fuentes_editing = False
        self.fuentes_text = ""
        self.fuentes_cursor = 0
        self.fuentes_probando = ""

    # --- configuración -----------------------------------------------------
    def _aplicar_config(self) -> None:
        self.state.paper = str(self.config.get("paper", "letter"))
        self.state.theme = str(self.config.get("theme", "auto"))
        self.state.tui_theme = temas.canonical(self.config.get("tui_theme"))
        self.state.keep = str(self.config.get("keep_intermediate", "ask"))
        self.state.out = str(self.config.get("out_dir", "output"))
        self.state.reader = bool(self.config.get("reader_panel", False))
        self.state.spread = str(self.config.get("reader_spread", "vertical"))

    # --- la lista ----------------------------------------------------------
    def libros_visibles(self) -> list[Libro]:
        return [libro for libro in self.files if self._coincide(libro)]

    def _coincide(self, libro: Libro) -> bool:
        if not self.filtro:
            return True
        aguja = self._plano(self.filtro)
        return aguja in self._plano(libro.nombre) or aguja in self._plano(libro.lugar)

    @staticmethod
    def _plano(texto: str) -> str:
        """Minúsculas y sin acentos: buscar «saint» encuentra «Saint-Exupéry»."""
        reemplazos = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
        return str(texto).translate(reemplazos).casefold()

    def filas(self) -> list[tuple[str, Any, int]]:
        """Filas de la lista: ``("grupo", carpeta, n)`` o ``("libro", Libro, 1)``."""
        visibles = self.libros_visibles()
        if not self.agrupar:
            return [("libro", libro, 1) for libro in visibles]
        grupos: dict[str, list[Libro]] = {}
        for libro in visibles:
            grupos.setdefault(libro.lugar, []).append(libro)
        filas: list[tuple[str, Any, int]] = []
        for carpeta in sorted(grupos):
            filas.append(("grupo", carpeta, len(grupos[carpeta])))
            if carpeta in self.plegados:
                continue
            filas.extend(("libro", libro, 1) for libro in grupos[carpeta])
        return filas

    def fila_actual(self) -> tuple[str, Any, int] | None:
        filas = self.filas()
        return filas[self.cursor] if 0 <= self.cursor < len(filas) else None

    def libro_actual(self) -> Libro | None:
        fila = self.fila_actual()
        return fila[1] if fila and fila[0] == "libro" else None

    def _libro_elegido(self) -> Libro | None:
        """El libro sobre el que actuar. Con una carpeta elegida, el primero suyo.

        Es una concesión deliberada: pulsar «i» sobre un grupo hace lo obvio en
        lugar de regañar. La lista nunca deja de ser determinista.
        """
        if self.path_text:
            ruta = Path(self.path_text).expanduser()
            return Libro(ruta, ruta.name, str(ruta.parent), self._formato_de(ruta))
        fila = self.fila_actual()
        if fila is not None and fila[0] == "grupo":
            del_grupo = [libro for libro in self.files if libro.lugar == fila[1]]
            if del_grupo:
                return del_grupo[0]
        return self.libro_actual() or self.source

    @staticmethod
    def _formato_de(ruta: Path) -> str:
        return {"epub": "epub", "html": "html", "htm": "html"}.get(
            ruta.suffix.lstrip(".").lower(), "pdf")

    def _mover_cursor(self, delta: int) -> None:
        filas = self.filas()
        if not filas:
            self.cursor = 0
            return
        self.cursor = max(0, min(len(filas) - 1, self.cursor + delta))

    def _alternar_grupo(self, clave: str) -> None:
        self.plegados.symmetric_difference_update({clave})
        for indice, fila in enumerate(self.filas()):
            if fila[0] == "grupo" and fila[1] == clave:
                self.cursor = indice
                return
        self.cursor = min(self.cursor, max(0, len(self.filas()) - 1))

    def _plegar_grupo_actual(self) -> None:
        fila = self.fila_actual()
        if fila is None:
            return
        self._alternar_grupo(fila[1] if fila[0] == "grupo" else fila[1].lugar)

    def _fijar_filtro(self, texto: str) -> None:
        self.filtro = texto
        self.cursor = 0

    # --- teclado -----------------------------------------------------------
    def handle(self, key: str) -> str | None:
        """Procesa una tecla. Devuelve ``"quit"`` cuando hay que salir."""
        if key == "CTRL_C":
            return "quit"
        if self.metrics_panel:
            return self._key_metrics(key)
        if key in ("F1", "char:?"):
            self.help_visible = not self.help_visible
            return None
        if self.help_visible:
            self.help_visible = False
            return None
        if self.confirming_keep:
            self._answer_keep(key)
            return None
        if self.fuentes_editing:
            self._key_fuentes(key)
            return None
        if self.filtrando:
            self._key_inicio(key)
            return "quit" if self.quit_requested else None
        if self.editing and self._key_editing(key):
            return "quit" if self.quit_requested else None
        if key.startswith("char:") and not self.editing and self._shortcut(key[5:]):
            return "quit" if self.quit_requested else None
        handler = getattr(self, f"_key_{self.screen}", None)
        if handler is not None:
            handler(key)
        return "quit" if self.quit_requested else None

    def _key_editing(self, key: str) -> bool:
        if key == "BACKSPACE":
            self.path_text = self.path_text[:-1]
        elif key == "ESC":
            self.editing, self.path_text = False, ""
        elif key == "ENTER":
            self.editing = False
            self._abrir_ruta()
        elif key.startswith("char:"):
            char = key[5:]
            if char.isprintable():
                self.path_text += char
        else:
            return False
        return True

    def _abrir_ruta(self) -> None:
        """Enter sobre una ruta escrita: se analiza esa, no la fila de la lista."""
        libro = self._libro_elegido()
        if libro is None:
            self._error("ERR-INP-003", self.tr("tui.msg.no_document"))
            return
        self.source, self.info = libro, None
        self.pending = "analyze"

    def _shortcut(self, char: str) -> bool:
        """Atajos comunes: cada tecla hace lo que su nombre dice."""
        if char == "q":
            self.quit_requested = True
            return True
        if char == "r" and self.screen == "inicio":
            self.editing, self.path_text = True, ""
            return True
        if char == "b" and self.screen == "inicio":
            self.filtrando, self.message = True, ""
            return True
        if char == "f" and self.screen in ("inicio", "config"):
            self.return_screen = "inicio"
            self.screen = "fuentes"
            return True
        if char == "s" and self.screen != "config":
            self.return_screen = self.screen
            self.screen, self.config_index = "config", 0
            return True
        if char == "i":
            libro = self._libro_elegido()
            if libro is None:
                self._error("ERR-INP-003", self.tr("tui.msg.no_document"))
                return True
            self.source, self.info = libro, None
            self.pending = "analyze"
            return True
        if char == "o":
            if self.screen in ("inicio", "diagnostico", "resultado"):
                self.screen, self.option_index = "opciones", 0
                return True
            return False
        if char == "c":
            if self.screen in ("inicio", "diagnostico", "resultado"):
                libro = self._libro_elegido()
                if libro is None:
                    self._error("ERR-INP-003", self.tr("tui.msg.no_document"))
                    return True
                self.source, self.info = libro, None
                self.screen, self.option_index = "opciones", 0
                return True
            if self.screen == "opciones":
                self._convertir()
                return True
            return False
        return False

    # --- pantallas: inicio -------------------------------------------------
    def _key_inicio(self, key: str) -> None:
        if self.filtrando:
            if key == "BACKSPACE":
                self._fijar_filtro(self.filtro[:-1])
            elif key == "ESC":
                self.filtrando = False
                self._fijar_filtro("")
            elif key == "ENTER":
                self.filtrando = False        # el filtro se queda puesto
            elif key.startswith("char:"):
                char = key[5:]
                if char.isprintable():
                    self._fijar_filtro(self.filtro + char)
            return
        if key == "UP":
            self._mover_cursor(-1)
        elif key == "DOWN":
            self._mover_cursor(1)
        elif key == "PAGEUP":
            self._mover_cursor(-self.pagina)
        elif key == "PAGEDOWN":
            self._mover_cursor(self.pagina)
        elif key == "HOME":
            self.cursor = 0
        elif key == "END":
            self.cursor = max(0, len(self.filas()) - 1)
        elif key in ("LEFT", "RIGHT"):
            self._plegar_grupo_actual()
        elif key == "ENTER":
            if self.path_text:
                self._abrir_ruta()
                return
            fila = self.fila_actual()
            if fila is None:
                self._error("ERR-INP-003", self.tr("tui.msg.no_document"))
            elif fila[0] == "grupo":
                self._alternar_grupo(fila[1])
            else:
                self.source, self.info = fila[1], None
                self.pending = "analyze"

    # --- pantallas: diagnóstico -------------------------------------------
    def _key_diagnostico(self, key: str) -> None:
        if key == "ENTER":
            self.screen, self.option_index = "opciones", 0
        elif key == "ESC":
            self.screen = "inicio"

    # --- pantallas: opciones ----------------------------------------------
    def _key_opciones(self, key: str) -> None:
        if key == "UP":
            self.option_index = max(0, self.option_index - 1)
        elif key == "DOWN":
            self.option_index = min(len(self.option_rows()) - 1, self.option_index + 1)
        elif key == "LEFT":
            self._cambiar_opcion(-1)
        elif key in ("RIGHT", "ENTER"):
            self._cambiar_opcion(1)
        elif key == "ESC":
            self.screen = "inicio"
        elif key == "char:m":
            self.metrics_panel = True
            self.metrics_scroll = 0

    def option_rows(self) -> list[str]:
        """Claves de las filas de Opciones, en orden. La fila ``"_"`` separa."""
        return ([f"fmt:{clave}" for clave, _etiqueta in FORMATS]
                + ["_"]
                + ["out", "keep", "paper", "paper_ebook", "reader", "spread",
                   "theme", "tui_theme"])

    def option_label(self, clave: str) -> tuple[str, str]:
        """``(etiqueta, valor)`` de una fila. Cada valor se lee sin abrir nada."""
        t, s = self.tr, self.state
        if clave.startswith("fmt:"):
            nombre = clave[4:]
            etiqueta = dict(FORMATS).get(nombre, nombre)
            return etiqueta, MARKS["ok"] if s.targets.get(nombre) else MARKS["pending"]
        return {
            "out": (t("tui.opt.out"), s.out),
            "keep": (t("tui.opt.keep"),
                     KEEP_LABELS.get(s.keep, {}).get(self.lang, s.keep)),
            "paper": (t("tui.opt.paper_web"), _papel(s.paper, self.lang)),
            "paper_ebook": (t("tui.opt.paper_ebook"), _papel(s.paper_ebook, self.lang)),
            "reader": (t("tui.opt.reader"),
                       t("tui.state.on") if s.reader else t("tui.state.off")),
            "spread": (t("tui.opt.spread"), _reparto(s.spread, self.lang)),
            "theme": (t("tui.opt.theme"), s.theme),
            "tui_theme": (t("tui.opt.tui_theme"), temas.label(s.tui_theme, self.lang)),
        }.get(clave, (clave, ""))

    def _cambiar_opcion(self, delta: int) -> None:
        claves = self.option_rows()
        if not claves:
            return
        clave = claves[max(0, min(len(claves) - 1, self.option_index))]
        if clave == "_":
            return
        s = self.state
        if clave.startswith("fmt:"):
            nombre = clave[4:]
            s.targets[nombre] = (not s.targets.get(nombre)) if delta > 0 else s.targets.get(nombre, False)
            return
        if clave == "reader":
            s.reader = not s.reader
        elif clave == "theme":
            s.theme = _ciclar(THEMES_DOC, s.theme, delta)
        elif clave == "tui_theme":
            s.tui_theme = temas.cycle(s.tui_theme, delta, self.lang)
        elif clave == "spread":
            s.spread = _ciclar(SPREADS, s.spread, delta)
        elif clave == "keep":
            s.keep = _ciclar(KEEPS, s.keep, delta)
        elif clave == "paper":
            s.paper = _ciclar(PAPERS, s.paper, delta)
        elif clave == "paper_ebook":
            s.paper_ebook = _ciclar(("auto",) + PAPERS, s.paper_ebook, delta)

    def _convertir(self) -> None:
        """Enter/c en Opciones: revisa, pregunta si hace falta y encarga."""
        if not self.state.pedidos():
            self._error("ERR-USE-001", self.tr("tui.msg.no_formats"))
            return
        if self.state.keep == "ask":
            self.confirming_keep, self.answer = True, ""
            self.message = ""
            return
        self._start_conversion()

    def _answer_keep(self, key: str) -> None:
        if key in ("char:s", "char:y", "ENTER"):
            self.state.keep, self.confirming_keep = "yes", False
            self._start_conversion()
        elif key == "char:n":
            self.state.keep, self.confirming_keep = "no", False
            self._start_conversion()
        elif key == "ESC":
            self.confirming_keep = False

    # --- pantallas: config -------------------------------------------------
    def _key_config(self, key: str) -> None:
        if key == "UP":
            self.config_index = max(0, self.config_index - 1)
        elif key == "DOWN":
            self.config_index = min(len(CONFIG_ORDER) - 1, self.config_index + 1)
        elif key in ("LEFT", "RIGHT", "ENTER"):
            nombre = CONFIG_ORDER[self.config_index]
            delta = -1 if key == "LEFT" else 1
            self.config[nombre] = _siguiente(nombre, self.config[nombre], delta)
            self._aplicar_config()
        elif key == "ESC":
            self.screen = self.return_screen
        elif key == "char:s":
            self.config["tui_theme"] = self.state.tui_theme
            self.config["paper"] = self.state.paper
            self.config["theme"] = self.state.theme
            self.config["keep_intermediate"] = self.state.keep
            self.config["out_dir"] = self.state.out
            self.config["reader_panel"] = self.state.reader
            self.config["reader_spread"] = self.state.spread
            if self.on_save_config is not None:
                self.on_save_config(dict(self.config))
            self.message = f"{self.tr('tui.cfg.saved')}: config.json"
            self.message_style = "ok"
            self.screen = self.return_screen

    # --- pantallas: fuentes ------------------------------------------------
    def _key_fuentes(self, key: str) -> None:
        if self.fuentes_editing:
            if key == "BACKSPACE":
                self.fuentes_text = self.fuentes_text[:-1]
            elif key == "ESC":
                self.fuentes_editing, self.fuentes_text = False, ""
            elif key == "ENTER":
                if self.fuentes_text.strip():
                    self.fuentes.append(self.fuentes_text.strip())
                    self.fuentes = sorted(set(self.fuentes))
                    self.message, self.message_style = self.tr("tui.src.added"), "ok"
                self.fuentes_editing, self.fuentes_text = False, ""
            elif key.startswith("char:"):
                char = key[5:]
                if char.isprintable():
                    self.fuentes_text += char
            return
        if key == "UP":
            self.fuentes_cursor = max(0, self.fuentes_cursor - 1)
        elif key == "DOWN":
            self.fuentes_cursor = min(max(0, len(self.fuentes) - 1), self.fuentes_cursor + 1)
        elif key == "char:+":
            self.fuentes_editing, self.fuentes_text = True, ""
        elif key == "DELETE":
            if len(self.fuentes) > 1:
                del self.fuentes[min(self.fuentes_cursor, len(self.fuentes) - 1)]
                self.fuentes_cursor = max(0, self.fuentes_cursor - 1)
                self.message, self.message_style = self.tr("tui.src.removed"), "ok"
            else:
                self.message, self.message_style = self.tr("tui.src.kept_one"), "warn"
        elif key == "char:T":
            ruta = self.fuentes[min(self.fuentes_cursor, len(self.fuentes) - 1)] \
                if self.fuentes else ""
            cuantos = sum(1 for libro in self.files if libro.lugar == ruta)
            self.message = self.tr("tui.src.test", n=cuantos, ruta=ruta)
            self.message_style = "ok"
        elif key == "ENTER":
            ruta = self.fuentes[min(self.fuentes_cursor, len(self.fuentes) - 1)] \
                if self.fuentes else None
            self.plegados = {carpeta for carpeta in
                             {libro.lugar for libro in self.files} if carpeta != ruta}
            self.agrupar = True
            self.screen, self.cursor = "inicio", 0
        elif key == "ESC":
            self.screen = self.return_screen

    def _key_resultado(self, key: str) -> None:
        if key == "ESC":
            self.screen = "inicio"
        elif key == "char:i":
            self.screen = "diagnostico"

    def _key_progreso(self, key: str) -> None:   # pragma: no cover - ocupado
        return

    def _key_metrics(self, key: str) -> str | None:
        if key in ("ESC", "char:q", "ENTER", "char:m"):
            self.metrics_panel = False
            return None
        if key == "UP":
            self.metrics_scroll = max(0, self.metrics_scroll - 1)
        elif key == "DOWN":
            self.metrics_scroll += 1
        elif key == "PAGEUP":
            self.metrics_scroll = max(0, self.metrics_scroll - 5)
        elif key == "PAGEDOWN":
            self.metrics_scroll += 5
        return None

    # --- trabajo -----------------------------------------------------------
    def run_pending(self) -> None:
        """Ejecuta lo pendiente hasta terminar.

        El corredor llama **después** de pintar, así el marco de «analizando…» o
        «convirtiendo 2/4» se ve de verdad y no se salta de golpe al resultado.
        """
        while self.pending:
            self.advance()

    def advance(self) -> bool:
        """Un paso de trabajo. Devuelve ``True`` si queda algo por hacer."""
        if self.pending == "analyze":
            self.pending = None
            self.analyze()
        elif self.pending == "convert":
            self._step_conversion()
        return bool(self.pending)

    def analyze(self) -> None:
        if self.source is None:
            self._error("ERR-INP-003", self.tr("tui.msg.no_document"))
            return
        try:
            self.info = self.backend.analizar(self.source)
        except Exception as exc:                      # el backend puede fallar
            self._error("ERR-EXT-001", f"{type(exc).__name__}: {exc}")
            return
        self.screen = "diagnostico"
        self.message = ""

    def _start_conversion(self) -> bool:
        """Prepara la cola y deja la pantalla de Progreso puesta."""
        if self.source is None:
            self._error("ERR-INP-003", self.tr("tui.msg.no_document"))
            return False
        pedidos = self.state.pedidos()
        if not pedidos:
            self._error("ERR-USE-001", self.tr("tui.msg.no_formats"))
            return False
        self.steps = [Step(nombre) for nombre in pedidos]
        self._cola = list(pedidos)
        self._salidas: list[dict[str, Any]] = []
        self._avisos: list[dict[str, Any]] = []
        self.resultado = None
        self.screen = "progreso"
        self.pending = "convert"
        self.answer = ""
        return True

    def _step_conversion(self) -> None:
        """Convierte **un** formato y anota su marca. Así el progreso avanza."""
        if self.source is None or not self._cola:
            self.resultado = {
                "outputs": list(self._salidas),
                "fidelity": {salida.get("format"): salida.get("fidelity")
                             for salida in self._salidas},
                "warnings": list(self._avisos),
            }
            for paso in self.steps:
                if paso.status != "failed":
                    paso.status = "done"
            self.pending = None
            self.screen = "resultado"
            self.busy = ""
            self.message = ""
            return

        nombre = self._cola[0]
        for paso in self.steps:
            if paso.name == nombre:
                paso.status = "running"
        hechos = len(self.steps) - len(self._cola)
        self.busy = f"{self.tr('tui.busy.converting')} {hechos + 1}/{len(self.steps)}"
        opciones = {
            "targets": {clave: clave == nombre for clave, _ in FORMATS},
            "out": self.state.out, "paper": self.state.paper, "theme": self.state.theme,
            "keep": self.state.keep, "reader": self.state.reader,
            "spread": self.state.spread,
        }
        try:
            resultado = self.backend.convertir(self.source, opciones, lambda *_: None)
        except Exception as exc:
            for paso in self.steps:
                if paso.name == nombre:
                    paso.status = "failed"
            self._cola = []
            self.pending = None
            self._error("ERR-EXT-001", f"{type(exc).__name__}: {exc}")
            return
        self._salidas.extend(resultado.get("outputs", []))
        for aviso in resultado.get("warnings", []):
            if aviso not in self._avisos:
                self._avisos.append(aviso)
        for paso in self.steps:
            if paso.name == nombre:
                paso.status = "done"
        self._cola.pop(0)

    def run_conversion(self) -> None:
        """Convertir de una tirada, sin mirar los marcos intermedios."""
        if self._start_conversion():
            self.run_pending()

    def _error(self, code: str, detail: str) -> None:
        self.message = f"{MARKS['error']} {code} · {detail}"
        self.message_style = "error"

    # --- dibujo ------------------------------------------------------------
    def render(self, width: int = 80, height: int = 24) -> list[str]:
        """Marco completo en texto plano: lo que se compara en las pruebas."""
        canvas = Canvas(width, height, ascii_only=self.ascii_only)
        self.draw(canvas)
        lineas = canvas.lines()
        if self.ascii_only:
            # sustitución 1:1: el ancho del marco no cambia al perder unicode
            lineas = [linea.translate(ASCII_MAP) for linea in lineas]
        return lineas

    def draw(self, canvas: Canvas) -> None:
        """Pinta la pantalla. **El único orden de dibujo** que hay."""
        self._limpiar(canvas)
        self._draw_frame(canvas)
        if self.help_visible:
            self._draw_help(canvas)
        elif self.metrics_panel and self.screen == "opciones":
            self._draw_opciones(canvas)
            self._draw_metrics_panel(canvas)
        else:
            getattr(self, f"_draw_{self.screen}")(canvas)
        self._draw_footer(canvas)

    def _draw_frame(self, canvas: Canvas) -> None:
        version = getattr(self.backend, "version", "1.0.0")
        contrato = getattr(self.backend, "contrato", "")
        titulo = f" {getattr(self.backend, 'nombre_app', 'TUI')} {version}"
        if contrato:
            titulo += f" · {contrato}"
        titulo += " "
        etiqueta = self.tr(SCREEN_KEYS[self.screen])
        # el rótulo de la derecha se reserva primero: así nunca se pisan
        ancho_titulo = max(4, canvas.width - len(etiqueta) - 3)
        canvas.fill(0, 0, canvas.width, 1, "bar")
        canvas.text(0, 0, _fit(titulo, ancho_titulo), "bar")
        canvas.text(canvas.width - len(etiqueta) - 2, 0, etiqueta, "bar")

    def _draw_footer(self, canvas: Canvas) -> None:
        """Barra de acciones: qué teclas hay **y qué hacen**, en esta pantalla."""
        texto = self.tr(f"tui.bar.{self.screen}")
        if len(texto) > canvas.width - 2:
            partes = texto.split(" · ")
            while partes and len(" · ".join(partes)) > canvas.width - 2:
                partes.pop()
            texto = " · ".join(partes) or texto[: canvas.width - 2]
        canvas.fill(0, canvas.height - 1, canvas.width, 1, "bar")
        canvas.text(1, canvas.height - 1, texto, "bar")

    def _body(self, canvas: Canvas) -> tuple[int, int, int, int]:
        """Área de contenido. Debajo quedan dos filas para mensajes y el pie."""
        return 1, 2, canvas.width - 2, canvas.height - 4

    def _limpiar(self, canvas: Canvas) -> None:
        """Borrar antes de escribir: una línea corta no deja cola de la anterior."""
        canvas.fill(0, 1, canvas.width, canvas.height - 2, "")

    def _fila_mensaje(self, canvas: Canvas) -> int:
        return canvas.height - 3

    # --- inicio ------------------------------------------------------------
    def _flecha(self, plegado: bool) -> str:
        """El pliegue se ve también sin dibujo de caja."""
        if self.ascii_only:
            return ">" if plegado else "v"
        return "▸" if plegado else "▾"

    def _draw_inicio(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        filas = self.filas()
        titulo = self.tr("tui.start.documents")
        if self.filtro:
            titulo = (f"{titulo} ({_num(len(self.libros_visibles()), self.lang)} "
                      f"{self.tr('tui.list.of')} {_num(len(self.files), self.lang)} · "
                      f"«{self.filtro}»)")
        elif self.files:
            titulo = f"{titulo} ({_num(len(self.files), self.lang)})"
        canvas.text(x + 1, y, _fit(titulo, ancho - 2), "title")

        fila = y + 2
        if not filas:
            vacio = (self.tr("tui.list.no_match") if self.filtro and self.files
                     else self.tr("tui.start.empty"))
            canvas.text(x + 1, fila, _fit(vacio, ancho - 2), "muted")
            fila += 2
        visible = max(1, limite - fila - 2)
        self.pagina = visible
        desde = _ventana(self.cursor, len(filas), visible)
        for indice in range(desde, min(desde + visible, len(filas))):
            seleccionada = indice == self.cursor
            tipo, dato, cuenta = filas[indice]
            if tipo == "grupo":
                flecha = self._flecha(dato in self.plegados)
                marca = "> " if seleccionada else "  "
                etiqueta = (self.tr("tui.list.one_book") if cuenta == 1
                            else self.tr("tui.list.books"))
                cola = f"  {_num(cuenta, self.lang)} {etiqueta}"
                nombre = _fit(f"{marca}{flecha} {dato}", max(8, ancho - len(cola) - 3))
                canvas.text(x + 1, fila, nombre, "selected" if seleccionada else "title")
                canvas.text(x + canvas.width - len(cola) - 1, fila, cola, "muted")
            else:
                marca = "> " if seleccionada else "  "
                prefijo = {"epub": "EPUB ", "html": "HTML ", "pdf": "     "}.get(
                    dato.formato, "     ")
                # los libros cuelgan de su grupo: dos espacios más, como un árbol
                sangria = "  " if self.agrupar else ""
                cola = f"  {_humano(dato.tamano)}" if self.agrupar else \
                    f"  {dato.lugar} · {_humano(dato.tamano)}"
                nombre = _fit(f"{marca}{sangria}{prefijo}{dato.nombre}",
                              max(8, ancho - len(cola) - 3))
                canvas.text(x + 1, fila, nombre, "selected" if seleccionada else "")
                canvas.text(x + canvas.width - len(cola) - 1, fila, cola, "muted")
            fila += 1
            if fila > limite - 2:
                break

        fila = min(fila + 1, limite - 1)
        if self.filtrando:
            texto = f"{self.tr('tui.list.filter')}: {self.filtro}_"
            canvas.text(x + 1, fila, _fit(texto, ancho - 2), "selected")
        elif self.editing:
            texto = f"{self.tr('tui.start.path')}: {self.path_text}_"
            canvas.text(x + 1, fila, _fit(texto, ancho - 2), "selected")
        elif self.filtro:
            texto = f"{self.tr('tui.list.filter_on')}: «{self.filtro}» · " \
                    f"{self.tr('tui.list.clear')}"
            canvas.text(x + 1, fila, _fit(texto, ancho - 2), "muted")
        else:
            canvas.text(x + 1, fila, _fit(self.tr("tui.start.path_hint"), ancho - 2), "muted")

        if fila + 1 <= limite - 1:
            if self.filtrando:
                estado = self.tr("tui.list.typing")
            elif self.editing:
                estado = self.tr("tui.status.enter_path")
            elif filas:
                actual = self.fila_actual()
                if actual is not None and actual[0] == "grupo":
                    estado = self.tr("tui.list.group_hint").replace("{grupo}", actual[1])
                else:
                    libro = self._libro_elegido()
                    estado = self.tr("tui.status.enter_analyze").replace(
                        "{doc}", libro.nombre if libro else "-")
            else:
                estado = self.tr("tui.status.type_path")
            canvas.text(x + 1, fila + 1, _fit(estado, ancho - 2), "muted")
        if self.message:
            canvas.text(x + 1, self._fila_mensaje(canvas), _fit(self.message, ancho - 2),
                        self.message_style)

    # --- diagnóstico -------------------------------------------------------
    def _draw_diagnostico(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        info = self.info or Analisis()
        nombre = self.source.nombre if self.source else "-"
        canvas.text(x + 1, y, _fit(f"{self.tr('tui.diag.title')}: {nombre}", ancho - 2), "title")

        capa = self.tr("tui.state.on") if info.caracteres else self.tr("tui.state.off")
        if info.caracteres:
            capa += f" ({_num(info.caracteres, self.lang)} {self.tr('tui.diag.chars')})"
        es_epub = info.formato == "epub"
        filas: list[tuple[str, str]] = []
        if info.formato == "html":
            filas.append((self.tr("tui.diag.format"),
                          self.tr("tui.diag.format_html").replace(
                              "{n}", _num(info.paginas, self.lang))))
        elif es_epub:
            filas.append((self.tr("tui.diag.format"),
                          self.tr("tui.diag.format_epub").replace(
                              "{n}", _num(info.paginas, self.lang))))
        else:
            filas.append((self.tr("tui.diag.format"), self.tr("tui.diag.format_pdf")))
        filas.append((self.tr("tui.diag.pages"), _num(info.paginas, self.lang)))
        if not es_epub and info.formato != "html":
            filas.append((self.tr("tui.diag.size"), info.tamano_hoja or "-"))
        filas += [
            (self.tr("tui.diag.encrypted"),
             self.tr("tui.state.on") if info.cifrado else self.tr("tui.state.off")),
            (self.tr("tui.diag.text_layer"), capa),
        ]
        if not es_epub and info.formato != "html":
            filas.append((self.tr("tui.diag.fonts"), _num(info.fuentes, self.lang)))
        filas += [
            (self.tr("tui.diag.images"),
             f"{_num(info.imagenes, self.lang)} ({_num(info.convertibles, self.lang)} "
             f"{self.tr('tui.diag.convertible')})"),
            (self.tr("tui.diag.blocks"), _num(info.bloques, self.lang)),
            (self.tr("tui.diag.warnings"),
             _num(info.avisos, self.lang) if info.avisos else self.tr("tui.state.none")),
        ]
        ancho_etiqueta = max((len(etiqueta) for etiqueta, _ in filas), default=1) + 1
        fila = y + 2
        for etiqueta, valor in filas:
            if fila > limite - 1:
                break
            canvas.text(x + 2, fila, _fit(f"{etiqueta:<{ancho_etiqueta}}", ancho_etiqueta),
                        "muted")
            canvas.text(x + 3 + ancho_etiqueta, fila,
                        _fit(valor, ancho - ancho_etiqueta - 4), "")
            fila += 1
        canvas.text(x + 1, min(fila + 1, limite),
                    _fit(f"{MARKS['ok']} {self.tr('tui.hint.confirm')}", ancho - 2), "muted")
        if self.message:
            canvas.text(x + 1, self._fila_mensaje(canvas), _fit(self.message, ancho - 2),
                        self.message_style)

    # --- opciones ----------------------------------------------------------
    def _draw_opciones(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        claves = self.option_rows()
        pedidos = " · ".join(dict(FORMATS).get(n, n) for n in self.state.pedidos()) or "—"
        canvas.text(x + 1, y, _fit(f"{self.tr('tui.opt.title')} · {self.tr('tui.opt.outputs')}: "
                                   f"{pedidos}", ancho - 2), "title")
        primera = y + 2
        visible = max(1, limite - primera - 2)
        desde = _ventana(self.option_index, len(claves), visible)
        for posicion, clave in enumerate(claves[desde:desde + visible], start=desde):
            fila = primera + (posicion - desde)
            if clave == "_":
                canvas.rule(x + 1, fila, ancho - 2, "muted")
                continue
            etiqueta, valor = self.option_label(clave)
            seleccionada = posicion == self.option_index
            marca = "> " if seleccionada else "  "
            estilo = "selected" if seleccionada else ""
            canvas.text(x + 1, fila, _fit(f"{marca}{etiqueta:<22}", 24), estilo)
            canvas.text(x + 25, fila, _fit(valor, ancho - 26), estilo)
        if desde > 0:
            canvas.text(x + ancho - 2, primera - 1, "^", "muted")
        if desde + visible < len(claves):
            canvas.text(x + ancho - 1, limite, "v", "muted")

        actual = claves[min(self.option_index, len(claves) - 1)]
        ayuda = self.tr(f"tui.opt.help.{actual.replace('fmt:', 'fmt.')}")
        libre = primera + min(len(claves) - desde, visible) + 1
        if not ayuda.startswith("tui.opt.help."):
            canvas.text(x + 1, libre, _fit(ayuda, ancho - 2), "muted")
            libre += 1
        self._draw_book(canvas, libre)
        mensaje = self._fila_mensaje(canvas)
        if self.confirming_keep:
            canvas.text(x + 1, mensaje, _fit(self.tr("tui.ask.keep"), ancho - 2), "warn")
            canvas.text(x + 1, mensaje + 1, _fit(self.tr("tui.ask.why"), ancho - 2), "muted")
        elif self.message:
            canvas.text(x + 1, mensaje, _fit(self.message, ancho - 2), self.message_style)

    def _draw_book(self, canvas: Canvas, fila: int) -> None:
        """«El libro»: lo que se va a convertir, medido. Cifras, no adjetivos."""
        x, _y, ancho, limite = self._body(canvas)
        if fila >= limite - 1 or self.source is None:
            return
        datos = self._medidas()
        if not datos:
            return
        canvas.text(x + 1, fila, _fit(self.tr("tui.book.title"), ancho - 2), "title")
        fila += 1
        piezas = [
            f"{_num(datos.get('words', 0), self.lang)} {self.tr('tui.book.words').lower()}",
            f"{_num(datos.get('pages', 0), self.lang)} {self.tr('tui.book.pages_short')}",
            f"{_num(datos.get('chapters', 0), self.lang)} "
            f"{self.tr('tui.book.chapters').lower()}",
            f"{_num(datos.get('reading', 0), self.lang)} {self.tr('tui.book.minutes')}",
        ]
        renglones = canvas.wrap(ancho - 4, " · ".join(piezas))
        for renglon in renglones[: max(0, limite - fila)]:
            canvas.text(x + 2, fila, renglon, "")
            fila += 1
        if renglones and fila <= limite:
            cola = (f"{self.tr('tui.book.profile')}: {datos.get('profile', '-')} · "
                    f"{_num(datos.get('per_page', 0), self.lang)} "
                    f"{self.tr('tui.book.per_page').lower()}")
            canvas.text(x + 2, fila, _fit(cola, ancho - 4), "muted")

    def _medidas(self) -> dict[str, Any]:
        """Medido una vez por documento: dibujar no debe costar trabajo."""
        if self.source is None:
            return {}
        clave = (str(self.source.ruta), self.state.paper)
        if self._medidas_cache[0] != clave:
            try:
                datos = dict(self.backend.medir(self.source))
            except Exception:
                datos = {}
            self._medidas_cache = (clave, datos)
        return self._medidas_cache[1]

    def _draw_metrics_panel(self, canvas: Canvas) -> None:
        """Modal de métricas: mientras está abierto, el teclado es suyo."""
        ancho = min(canvas.width - 6, 56)
        alto = min(canvas.height - 4, 12)
        x = (canvas.width - ancho) // 2
        y = (canvas.height - alto) // 2
        # se tapa el fondo: un modal no deja leer lo de debajo a medias
        canvas.fill(x, y, ancho, alto, "overlay")
        canvas.box(x, y, ancho, alto, self.tr("tui.panel.metrics"), "overlay")
        datos = self._medidas()
        renglones = [
            f"{self.tr('tui.book.words')}: {_num(datos.get('words', 0), self.lang)}",
            f"{self.tr('tui.book.pages')}: {_num(datos.get('pages', 0), self.lang)}",
            f"{self.tr('tui.book.chapters')}: {_num(datos.get('chapters', 0), self.lang)}",
            f"{self.tr('tui.book.reading')}: {_num(datos.get('reading', 0), self.lang)}",
            f"{self.tr('tui.book.per_page')}: {_num(datos.get('per_page', 0), self.lang)}",
            f"{self.tr('tui.book.profile')}: {datos.get('profile', '-')}",
        ]
        visible = max(1, alto - 3)
        desde = min(self.metrics_scroll, max(0, len(renglones) - visible))
        for indice, renglon in enumerate(renglones[desde:desde + visible]):
            canvas.text(x + 2, y + 1 + indice, _fit(renglon, ancho - 4), "")
        pista = self.tr("tui.panel.scroll")
        if len(renglones) > visible:
            pista = f"{pista} · {desde + 1}-{min(len(renglones), desde + visible)}/{len(renglones)}"
        canvas.text(x + 2, y + alto - 2, _fit(pista, ancho - 4), "muted")

    # --- progreso y resultado ---------------------------------------------
    def _draw_progreso(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        canvas.text(x + 1, y, _fit(self.tr("tui.prog.title"), ancho - 2), "title")
        fila = y + 2
        for paso in self.steps:
            if fila > limite:
                break
            marca = {"done": MARKS["ok"], "running": MARKS["pending"],
                     "failed": MARKS["error"], "pending": MARKS["pending"]}[paso.status]
            canvas.text(x + 2, fila, f"{marca} {paso.name}",
                        "ok" if paso.status == "done" else
                        ("error" if paso.status == "failed" else ""))
            fila += 1
        if self.busy:
            canvas.text(x + 1, min(fila + 1, limite), _fit(self.busy, ancho - 2), "muted")

    def _draw_resultado(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        canvas.text(x + 1, y, _fit(self.tr("tui.res.title"), ancho - 2), "title")
        fila = y + 2
        datos = self.resultado or {}
        canvas.text(x + 1, fila, _fit(self.tr("tui.res.outputs"), ancho - 2), "title")
        fila += 1
        for salida in datos.get("outputs", []):
            if fila > limite - 3:
                break
            fidelidad = salida.get("fidelity")
            marca = MARKS["ok"] if (fidelidad or 0) >= 0.999 else MARKS["warn"]
            etiqueta = dict(FORMATS).get(salida.get("format"), salida.get("format", "?"))
            canvas.text(x + 2, fila, f"{marca} {etiqueta:<9}", "")
            canvas.text(x + 16, fila, _fit(str(salida.get("path", "")), ancho - 34), "")
            canvas.text(x + ancho - 12, fila, _fit(_humano(int(salida.get("bytes", 0))), 10), "muted")
            fila += 1

        fidelidades = datos.get("fidelity") or {}
        if fidelidades:
            fila += 1
            texto = " · ".join(f"{clave} {valor:.4f}" for clave, valor in fidelidades.items())
            canvas.text(x + 1, fila, _fit(f"{self.tr('tui.res.fidelity')}: {texto}", ancho - 2),
                        "ok" if all(valor >= 0.999 for valor in fidelidades.values()) else "warn")
            fila += 2

        avisos = datos.get("warnings") or []
        canvas.text(x + 1, min(fila, limite), _fit(self.tr("tui.res.warnings"), ancho - 2), "title")
        fila += 1
        if not avisos:
            canvas.text(x + 2, fila, self.tr("tui.res.none"), "muted")
        for aviso in avisos[: max(0, limite - fila)]:
            canvas.text(x + 2, fila, _fit(f"{MARKS['warn']} {aviso.get('code', '')} · "
                                          f"{aviso.get('message', '')}", ancho - 3), "warn")
            fila += 1
        if self.message:
            canvas.text(x + 1, self._fila_mensaje(canvas), _fit(self.message, ancho - 2),
                        self.message_style)

    # --- config ------------------------------------------------------------
    def _draw_config(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        canvas.text(x + 1, y, _fit(self.tr("tui.cfg.title"), ancho - 2), "title")
        fila = y + 2
        for indice, nombre in enumerate(CONFIG_ORDER):
            if fila > limite - 2:
                break
            seleccionada = indice == self.config_index
            marca = "> " if seleccionada else "  "
            canvas.text(x + 1, fila, _fit(f"{marca}{nombre:<20}", 22),
                        "selected" if seleccionada else "")
            canvas.text(x + 23, fila, _fit(_valor_config(nombre, self.config.get(nombre),
                                                         self.lang), ancho - 24),
                        "selected" if seleccionada else "")
            fila += 1
        canvas.text(x + 1, self._fila_mensaje(canvas), _fit(self.tr("tui.cfg.hint"), ancho - 2),
                    "muted")

    # --- fuentes -----------------------------------------------------------
    def _draw_fuentes(self, canvas: Canvas) -> None:
        x, y, ancho, limite = self._body(canvas)
        canvas.text(x + 1, y, _fit(self.tr("tui.src.title"), ancho - 2), "title")
        fila = y + 2
        if not self.fuentes:
            canvas.text(x + 2, fila, _fit(self.tr("tui.src.empty"), ancho - 3), "muted")
            fila += 2
        for indice, ruta in enumerate(self.fuentes):
            if fila > limite - 4:
                break
            seleccionada = indice == self.fuentes_cursor
            marca = "> " if seleccionada else "  "
            cuantos = sum(1 for libro in self.files if libro.lugar == ruta)
            etiqueta = (self.tr("tui.src.row_none") if not cuantos else
                        (self.tr("tui.src.row_one") if cuantos == 1
                         else self.tr("tui.src.row", n=cuantos)))
            cola = f"  {etiqueta}"
            canvas.text(x + 1, fila, _fit(f"{marca}{ruta}", max(8, ancho - len(cola) - 3)),
                        "selected" if seleccionada else "")
            canvas.text(x + canvas.width - len(cola) - 1, fila, cola, "muted")
            fila += 1
        fila += 1
        if self.fuentes_editing:
            canvas.text(x + 1, fila, _fit(f"{self.tr('tui.src.prompt')}: "
                                          f"{self.fuentes_text}_", ancho - 2), "selected")
        else:
            canvas.text(x + 1, fila, _fit(self.tr("tui.src.help"), ancho - 2), "muted")
        fila += 2
        canvas.text(x + 1, fila, _fit(self.tr("tui.src.list"), ancho - 2), "title")
        fila += 1
        for libro in self.libros_visibles()[: max(0, limite - fila - 1)]:
            canvas.text(x + 2, fila, _fit(f"{libro.lugar}/{libro.nombre}", ancho - 3), "")
            fila += 1
        canvas.text(x + 1, self._fila_mensaje(canvas),
                    _fit(self.tr("tui.src.footer", n=len(self.fuentes), m=len(self.files)),
                         ancho - 2), "muted")

    # --- ayuda -------------------------------------------------------------
    def _draw_help(self, canvas: Canvas) -> None:
        ancho = min(canvas.width - 4, 62)
        alto = min(canvas.height - 2, 13)
        x = (canvas.width - ancho) // 2
        y = (canvas.height - alto) // 2
        canvas.fill(x, y, ancho, alto, "overlay")
        canvas.box(x, y, ancho, alto, self.tr("tui.help.title"), "overlay")
        claves = ("tui.key.up", "tui.key.change", "tui.key.enter", "tui.key.esc",
                  "tui.key.filter", "tui.key.fold", "tui.key.page", "tui.key.help",
                  "tui.key.quit")
        for indice, clave in enumerate(claves[: alto - 3]):
            canvas.text(x + 2, y + 2 + indice, _fit(self.tr(clave), ancho - 4), "")
        canvas.text(x + 2, y + alto - 2, _fit("F1 · Esc", ancho - 4), "muted")


# --- utilidades ------------------------------------------------------------

def _ventana(indice: int, total: int, visible: int) -> int:
    if total <= visible:
        return 0
    mitad = visible // 2
    return max(0, min(total - visible, indice - mitad))


def _fit(texto: str, ancho: int, marca: str = "…") -> str:
    if ancho <= 0:
        return ""
    texto = str(texto)
    if len(texto) <= ancho:
        return texto
    if ancho == 1:
        return marca
    return texto[: ancho - 1] + marca


def _num(valor: Any, lang: str = "es") -> str:
    """Cifra con separador de miles: 13.586 en español, 13,586 en inglés."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return str(valor if valor is not None else "-")
    separador = "." if lang == "es" else ","
    return f"{numero:,}".replace(",", separador)


def _humano(bytes_: int) -> str:
    if bytes_ >= 1_048_576:
        return f"{bytes_ / 1_048_576:.1f} MB"
    if bytes_ >= 1024:
        return f"{bytes_ / 1024:.0f} KB"
    return f"{bytes_} B"


def _papel(valor: str, lang: str = "es") -> str:
    return PAPER_LABELS.get(valor, {}).get(lang, valor)


def _reparto(valor: str, lang: str = "es") -> str:
    return SPREAD_LABELS.get(valor, {}).get(lang, valor)


def _ciclar(valores: tuple[str, ...], actual: str, delta: int) -> str:
    try:
        indice = valores.index(actual)
    except ValueError:
        indice = 0
    return valores[(indice + delta) % len(valores)]


def _siguiente(nombre: str, actual: Any, delta: int) -> Any:
    """El valor siguiente de una clave de configuración, con su vocabulario."""
    if nombre == "theme":
        return _ciclar(THEMES_DOC, str(actual), delta)
    if nombre == "tui_theme":
        return temas.cycle(str(actual), delta)
    if nombre == "paper":
        return _ciclar(PAPERS, str(actual), delta)
    if nombre == "keep_intermediate":
        return _ciclar(KEEPS, str(actual), delta)
    if nombre == "reader_spread":
        return _ciclar(SPREADS, str(actual), delta)
    if nombre == "log_level":
        return _ciclar(("error", "warn", "info", "debug"), str(actual), delta)
    if nombre == "lang":
        return _ciclar(("es", "en"), str(actual), delta)
    if nombre == "words_per_page":
        return _ciclar(("200", "250", "300", "350", "400"), str(actual), delta)
    if nombre in ("overwrite",):
        return not bool(actual)
    if nombre == "out_dir":
        return _ciclar(("output", "junto-al-pdf", ""), str(actual), delta)
    return actual


def _valor_config(nombre: str, valor: Any, lang: str = "es") -> str:
    """Un valor de configuración en palabras, no en clave interna."""
    t = Translator(lang)
    if nombre == "tui_theme":
        return temas.label(str(valor), lang)
    if nombre == "paper":
        return _papel(str(valor), lang)
    if nombre == "keep_intermediate":
        return KEEP_LABELS.get(str(valor), {}).get(lang, str(valor))
    if nombre == "reader_spread":
        return _reparto(str(valor), lang)
    if isinstance(valor, bool):
        return t("tui.state.on") if valor else t("tui.state.off")
    if valor == "":
        return "—"
    return str(valor)
