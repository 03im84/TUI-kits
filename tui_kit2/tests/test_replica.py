"""Pruebas de la réplica: lo que se puede afirmar de un marco de texto.

No hay terminal aquí. Todo se comprueba pidiendo marcos: mismo guion, mismos
bytes. Si algo cambia de aspecto sin querer, estas pruebas lo dicen.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from tuikit.app import SCREENS, App
from tuikit.backend import Analisis, DemoBackend, Libro
from tuikit.demo import GUION, storyboard
from tuikit.i18n import CATALOGOS, Translator
from tuikit import theme


def app(lang: str = "es", **kwargs) -> App:
    return App(DemoBackend(), lang=lang, **kwargs)


def recorrer(app_: App, teclas: list[str]) -> None:
    for tecla in teclas:
        app_.handle(tecla)
        app_.run_pending()


# --- las siete pantallas ---------------------------------------------------

def test_hay_siete_pantallas():
    assert SCREENS == ("inicio", "diagnostico", "opciones", "progreso",
                       "resultado", "config", "fuentes")


def test_el_guion_pasa_por_las_siete_pantallas():
    vistas = set()
    a = app()
    for _titulo, tecla in GUION:
        if tecla:
            a.handle(tecla)
        vistas.add(a.screen)
        while a.pending:
            vistas.add(a.screen)
            a.advance()
        vistas.add(a.screen)
    assert vistas == set(SCREENS)


def test_el_guion_es_determinista():
    uno = storyboard()
    otro = storyboard()
    assert uno == otro
    assert len(uno) > len(GUION)


# --- el marco --------------------------------------------------------------

@pytest.mark.parametrize("ancho,alto", [(40, 12), (60, 18), (92, 26), (120, 40)])
def test_ninguna_linea_se_pasa_del_ancho(ancho, alto):
    for _titulo, lineas in storyboard(width=ancho, height=alto):
        assert len(lineas) == alto
        for linea in lineas:
            assert len(linea) <= ancho, f"«{linea}» mide {len(linea)}"


def test_ascii_puro_no_usa_dibujo_de_caja():
    for _titulo, lineas in storyboard(ascii_only=True):
        texto = "\n".join(lineas)
        assert not set(texto) & set("┌┐└┘─│├┤▸▾")


def test_ascii_conserva_el_ancho_y_el_marco():
    for _titulo, lineas in storyboard(width=76, height=20, ascii_only=True):
        assert len(lineas) == 20
        for linea in lineas:
            assert len(linea) <= 76
            # ASCII es para el marco, no para el idioma: las tildes se quedan
            assert not set(linea) & set("┌┐└┘─│├┤▸▾↑↓←→«»")


def test_el_color_nunca_es_el_unico_portador():
    # cada salida y cada paso llevan marca textual, no solo estilo
    a = app()
    recorrer(a, ["DOWN", "ENTER", "char:o", "char:c", "char:s"])
    resultado = "\n".join(a.render(92, 26))
    assert "[OK]" in resultado
    assert "1.0000" in resultado


def test_el_pie_dice_las_teclas_de_la_pantalla():
    a = app()
    for pantalla in SCREENS:
        a.screen = pantalla
        pie = a.render(100, 26)[-1]
        assert pie.strip(), pantalla
        assert "tui.bar." not in pie, f"clave sin traducir en {pantalla}"


# --- teclado ---------------------------------------------------------------

def test_atajos_globales():
    a = app()
    a.handle("char:s")
    assert a.screen == "config"
    a.handle("char:p")            # una letra suelta no navega
    assert a.screen == "config"
    a.handle("ESC")
    assert a.screen == "inicio"
    assert a.handle("char:q") == "quit"
    assert a.handle("CTRL_C") == "quit"


def test_buscar_filtra_y_esc_limpia():
    a = app()
    a.handle("char:b")
    for letra in "pri":
        a.handle(f"char:{letra}")
    assert [libro.nombre for _tipo, libro, _n in a.filas() if _tipo == "libro"] == [
        "el-principito.pdf", "el-principito.html"]
    a.handle("ESC")
    assert a.filtro == ""
    assert len(a.libros_visibles()) == len(a.files)


def test_plegar_y_desplegar_grupo():
    a = app()
    a.handle("DOWN")
    a.handle("LEFT")
    assert a.plegados
    a.handle("LEFT")
    assert not a.plegados


def test_enter_analiza_y_diagnostica():
    a = app()
    a.handle("DOWN")
    a.handle("ENTER")
    assert a.pending == "analyze"
    assert a.screen == "inicio"          # el trabajo se hace tras pintar
    a.run_pending()
    assert a.screen == "diagnostico"
    assert "Páginas" in "\n".join(a.render())


def test_ruta_escrita_a_mano_se_analiza():
    a = app()
    a.handle("char:r")
    for letra in "/tmp/otro.epub":
        a.handle(f"char:{letra}")
    a.handle("ENTER")
    a.run_pending()
    assert a.source is not None and a.source.nombre == "otro.epub"
    assert a.source.formato == "epub"


def test_editar_ruta_admite_borrado_y_cancelacion():
    a = app()
    a.handle("char:r")
    for letra in "abc":
        a.handle(f"char:{letra}")
    a.handle("BACKSPACE")
    assert a.path_text == "ab"
    a.handle("ESC")
    assert a.path_text == "" and not a.editing


def test_sin_formatos_avisa_y_no_convierte():
    a = app()
    a.handle("DOWN")
    a.handle("ENTER")
    a.run_pending()
    a.handle("char:o")
    a.state.screen = "opciones"
    a.state.targets = {clave: False for clave in a.state.targets}
    a.handle("char:c")
    assert a.pending is None
    assert "ERR-USE-001" in "\n".join(a.render())


def test_pregunta_por_el_html_intermedio():
    a = app()
    recorrer(a, ["DOWN", "ENTER", "char:o", "char:c"])
    assert a.confirming_keep
    assert "s/n" in "\n".join(a.render())
    a.handle("char:n")
    assert not a.confirming_keep
    assert a.state.keep == "no"
    assert a.pending == "convert"


def test_el_progreso_avanza_formato_a_formato():
    a = app()
    recorrer(a, ["DOWN", "ENTER", "char:o"])
    a.handle("char:c")
    a.handle("char:s")
    vistas = []
    while a.pending:
        a.advance()
        vistas.append((a.screen, [paso.status for paso in a.steps]))
    assert a.screen == "resultado"
    assert any("running" not in estados and "done" in estados and "pending" in estados
               for _pantalla, estados in vistas)
    assert all(paso.status == "done" for paso in a.steps)


def test_el_panel_de_metricas_se_abre_y_se_cierra():
    a = app()
    recorrer(a, ["DOWN", "ENTER", "char:o"])
    a.handle("char:m")
    assert a.metrics_panel
    marco = "\n".join(a.render())
    assert "Métricas" in marco and "13.586" in marco
    a.handle("DOWN")
    a.handle("ESC")
    assert not a.metrics_panel


def test_config_guarda_y_vuelve():
    guardado = {}
    a = App(DemoBackend(), on_save_config=guardado.update)
    a.handle("char:s")
    a.handle("DOWN")
    a.handle("RIGHT")                     # theme: auto → light
    assert a.config["theme"] == "light"
    a.handle("char:s")
    assert a.screen == "inicio"
    assert guardado["theme"] == "light"


def test_fuentes_anaden_y_quitan():
    a = app()
    a.handle("char:f")
    assert a.screen == "fuentes"
    antes = len(a.fuentes)
    a.handle("char:+")
    for letra in "/srv/libros":
        a.handle(f"char:{letra}")
    a.handle("ENTER")
    assert len(a.fuentes) == antes + 1
    a.handle("DELETE")
    assert len(a.fuentes) == antes


def test_la_ayuda_es_un_modal_de_una_tecla():
    a = app()
    a.handle("F1")
    assert a.help_visible
    a.handle("ESC")
    assert not a.help_visible
    a.handle("char:?")
    assert a.help_visible


# --- idioma y temas --------------------------------------------------------

def test_los_dos_idiomas_tienen_las_mismas_claves():
    assert set(CATALOGOS["es"]) == set(CATALOGOS["en"])


def test_ningun_texto_visible_es_una_clave():
    for lang in ("es", "en"):
        for _titulo, lineas in storyboard(lang=lang, height=30):
            texto = "\n".join(lineas)
            assert "tui." not in texto, lang
            assert "{n}" not in texto and "{doc}" not in texto, lang


def test_el_ingles_cambia_las_palabras_no_las_teclas():
    es = "\n".join(storyboard(lang="es")[0][1])
    en = "\n".join(storyboard(lang="en")[0][1])
    assert "Documentos encontrados" in es
    assert "found" in en.lower() or "Documents" in en
    for tecla in ("[b]", "[i]", "[c]", "q"):
        assert tecla in es and tecla in en


def test_los_valores_se_traducen_no_solo_las_etiquetas():
    es = "\n".join(lineas for _t, lineas in storyboard(lang="es") for lineas in lineas)
    en = "\n".join(lineas for _t, lineas in storyboard(lang="en") for lineas in lineas)
    assert "Carta" in es and "Carta" not in en
    assert "una hoja" in es and "una hoja" not in en
    assert "US Letter" in en


@pytest.mark.parametrize("nombre", list(theme.PALETTES))
def test_cada_tema_pinta_y_cambia_de_color(nombre):
    estilos = theme.styles(nombre)
    assert estilos["title"] and estilos["bar"]
    assert theme.styles(nombre, no_color=True)["title"] == ""


def test_los_temas_se_recorren_sin_perderse():
    actual = theme.DEFAULT
    vistos = set()
    for _ in range(len(theme.PALETTES)):
        vistos.add(actual)
        actual = theme.cycle(actual, 1)
    assert actual == theme.DEFAULT
    assert vistos == set(theme.PALETTES)


# --- el backend ------------------------------------------------------------

def test_el_backend_de_mentira_cumple_la_forma():
    backend = DemoBackend()
    assert backend.libros()
    libro = backend.libros()[0]
    assert isinstance(libro, Libro) and libro.formato in ("pdf", "epub", "html")
    assert isinstance(backend.analizar(libro), Analisis)
    medidas = backend.medir(libro)
    assert {"words", "pages", "chapters", "reading"} <= set(medidas)
    pasos = []
    salida = backend.convertir(libro, {"targets": {"html": True, "epub": True}, "out": "x"},
                               lambda nombre, i, total: pasos.append((nombre, i, total)))
    assert pasos == [("html", 1, 2), ("epub", 2, 2)]
    assert len(salida["outputs"]) == 2 and salida["fidelity"]["epub"] == 1.0


def test_la_aplicacion_no_conoce_el_mundo_real():
    # la TUI no importa nada del producto: solo tuikit
    fuente = (Path(__file__).resolve().parents[1] / "tuikit" / "app.py").read_text()
    assert "incunable" not in fuente
    assert "pdfminer" not in fuente and "pypdf" not in fuente


def test_el_traductor_no_revienta_con_claves_raras():
    t = Translator("es")
    assert t("tui.no.existe") == "tui.no.existe"
    assert t("tui.list.of") == "de"
    assert Translator("fr").lang == "es"
