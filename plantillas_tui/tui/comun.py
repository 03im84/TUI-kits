#!/usr/bin/env python3
"""Emisor común para la serie de siete TUIs reales.

Cada app define su paleta, sus tres pantallas y de dónde sale cada color. Este
módulo se encarga de todo lo demás: verificar bordes y anchuras, escribir el
.txt sin un solo escape, montar el HTML con su tabla de color y pintar en ANSI.

La diferencia con las series anteriores es de criterio, no de código: estas apps
existen, así que su paleta no se inventa ni se mide a ojo — se **lee** del
fichero de tema de la app (btop trae 29) o se saca del histograma de una captura
real, que en una TUI plana sí funciona.
"""

from __future__ import annotations

import html
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402

ANCHO, ALTO = 100, 30


# ---------------------------------------------------------------------------
# mobiliario compartido
# ---------------------------------------------------------------------------
def caja(c: Lienzo, x: int, y: int, ancho: int, alto: int, titulo: str = "",
         estilo: str = "borde", titulo_estilo: str = "titulo") -> None:
    """Caja de una línea con el título incrustado en el borde superior."""
    c._paneles.append(c._registro(x, y, ancho, alto, titulo,
                                  "┌", "┐", "└", "┘", "─", "│"))
    cuerpo = "─" * (ancho - 2)
    if titulo:
        etiqueta = f" {titulo} "
        cuerpo = "─" + etiqueta + "─" * (ancho - 3 - len(etiqueta))
    c.texto(x, y, "┌" + cuerpo + "┐", estilo)
    for fila in range(y + 1, y + alto - 1):
        c.texto(x, fila, "│", estilo)
        c.texto(x + ancho - 1, fila, "│", estilo)
    c.texto(x, y + alto - 1, "└" + "─" * (ancho - 2) + "┘", estilo)
    if titulo:
        c.texto(x + 2, y, f" {titulo} ", titulo_estilo)


def barra(c: Lienzo, x: int, y: int, ancho: int, valor: float, estilo: str,
          vacio: str = "tenue", lleno: str = "█") -> None:
    dentro = round(max(0.0, min(1.0, valor)) * ancho)
    c.texto(x, y, lleno * dentro, estilo)
    c.texto(x + dentro, y, "·" * (ancho - dentro), vacio)


def pie(c: Lienzo, teclas: list[tuple[str, str]], estilo: str = "tecla",
        texto: str = "texto", y: int = 28) -> None:
    x = 1
    for tecla, accion in teclas:
        c.texto(x, y, tecla, estilo)
        c.texto(x + len(tecla) + 1, y, accion + "  ", texto)
        x += len(tecla) + len(accion) + 4


def titulo_ventana(c: Lienzo, texto: str, estilo: str = "titulo") -> None:
    c.texto(1, 0, texto, estilo)


# ---------------------------------------------------------------------------
# una app: paleta + pantallas + procedencia de cada color
# ---------------------------------------------------------------------------
@dataclass
class App:
    clave: str
    nombre: str
    comando: str
    descripcion: str
    fuente: str
    paleta: dict[str, str]
    origen: dict[str, str]
    uso: dict[str, str]
    pantallas: list[tuple[str, str, str, Callable[[Lienzo], None]]]
    variantes: dict[str, dict[str, str]] = field(default_factory=dict)


BASES = {
    "borde": ("caja", "tenue", "texto"),
    "tecla": ("acento", "titulo", "texto"),
    "rojo": ("metodo_del", "alerta", "tenue"),
}
INVERTIDOS = {"inverso"}


def es_fondo(estilo: str) -> bool:
    """Un estilo que pinta fondo y no texto: vídeo inverso y las píldoras de estado."""
    return estilo in INVERTIDOS or estilo.endswith("_pildora")


_USADOS: dict[int, set[str]] = {}


def usados(app: App) -> set[str]:
    """Estilos que las pantallas pintan de verdad. Un color que nadie usa no es
    un color de la app: no se enseña en la tabla."""
    clave = id(app)
    if clave not in _USADOS:
        estilos: set[str] = set()
        for _, _, _, lienzo in construir(app):
            estilos |= {celda.estilo for fila in lienzo.rejilla
                        for celda in fila if celda.estilo}
        _USADOS[clave] = estilos
    return _USADOS[clave]


def paleta(app: App) -> dict[str, str]:
    """Paleta declarada + los estilos de base que todas las pantallas usan.

    `borde`, `tecla`, `inverso` y `rojo` no se declaran app por app: se toman
    del color que cada app ya tiene para ese papel. Si no hay ninguno, es un
    error de la app, no un color por defecto inventado.
    """
    vista = dict(app.paleta)
    usados_ahora = usados(app)
    for clave, candidatos in BASES.items():
        if clave in vista or clave not in usados_ahora:
            continue
        for candidato in candidatos:
            if candidato in vista:
                vista[clave] = vista[candidato]
                app.origen.setdefault(clave, "heredado de " + candidato)
                break
    # fuera lo que no se pinta (sel_fg es el texto de la selección, no un relleno)
    return {k: v for k, v in vista.items()
            if k in usados_ahora or k in ("fondo", "texto", "sel_fg")}


def construir(app: App) -> list[tuple[str, str, str, Lienzo]]:
    salida = []
    for numero, nombre, nota, funcion in app.pantallas:
        lienzo = Lienzo(ANCHO, ALTO)
        funcion(lienzo)
        salida.append((numero, nombre, nota, lienzo))
    return salida


def verificar(app: App) -> list[str]:
    problemas = []
    for numero, _, _, lienzo in construir(app):
        for problema in lienzo.comprobar():
            problemas.append(f"[{app.clave} {numero}] {problema}")
        for fila in lienzo.lineas():
            if len(fila) != ANCHO:
                problemas.append(f"[{app.clave} {numero}] fila de {len(fila)}")
        validos = set(paleta(app)) - {"sel_fg"}
        usados = {celda.estilo for fila in lienzo.rejilla for celda in fila if celda.estilo}
        usados = {e for e in usados if not es_hex(e)}
        for estilo in sorted(usados - validos):
            problemas.append(f"[{app.clave} {numero}] estilo {estilo!r} no está en la paleta")
    return problemas


# ---------------------------------------------------------------------------
# salida
# ---------------------------------------------------------------------------
def es_hex(estilo: str) -> bool:
    """Un estilo puede ser un color literal: '#22da6e'. Sirve para los gradientes
    de btop, que no son un color de la paleta sino tres que se mezclan."""
    return estilo.startswith("#") and len(estilo) in (4, 7)


def mezcla(a: str, b: str, t: float) -> str:
    """Interpola dos colores #rrggbb. t=0 → a, t=1 → b."""
    x, y = (int(a[i:i + 2], 16) for i in (1, 3, 5)), (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(i + (j - i) * t):02x}" for i, j in zip(x, y))


def rampa(colores: list[str], pasos: int) -> list[str]:
    """Reparte `pasos` colores a lo largo de una lista de extremos."""
    if pasos <= 1:
        return [colores[0]] * pasos
    tramos = len(colores) - 1
    salida = []
    for paso in range(pasos):
        posicion = paso / (pasos - 1) * tramos
        tramo = min(int(posicion), tramos - 1)
        salida.append(mezcla(colores[tramo], colores[tramo + 1], posicion - tramo))
    return salida


def spans(fila) -> str:
    trozos, actual, buffer = [], None, ""
    for celda in fila:
        if celda.estilo != actual:
            if buffer:
                texto = html.escape(buffer)
                if actual and es_hex(actual):
                    trozos.append(f'<span style="color:{actual}">{texto}</span>')
                elif actual:
                    trozos.append(f'<span class="c-{actual}">{texto}</span>')
                else:
                    trozos.append(texto)
            actual, buffer = celda.estilo, celda.char
        else:
            buffer += celda.char
    if buffer:
        texto = html.escape(buffer)
        if actual and es_hex(actual):
            trozos.append(f'<span style="color:{actual}">{texto}</span>')
        elif actual:
            trozos.append(f'<span class="c-{actual}">{texto}</span>')
        else:
            trozos.append(texto)
    return "".join(trozos)


def marcas(texto: str) -> str:
    """Texto plano con dos marcas: `código` y **negrita**. Todo lo demás se escapa."""
    trozos = texto.split("`")
    salida = []
    for i, trozo in enumerate(trozos):
        if i % 2:
            salida.append(f"<code>{html.escape(trozo)}</code>")
        else:
            partes = trozo.split("**")
            salida.append("".join(f"<strong>{html.escape(t)}</strong>" if j % 2
                                  else html.escape(t) for j, t in enumerate(partes)))
    return "".join(salida)


def _css(app: App) -> str:
    col = paleta(app)
    variables = "\n ".join(f"--{k}:{v};" for k, v in col.items()
                           if k not in ("fondo", "sel_fg"))
    clases = "\n".join(f".c-{k}{{color:var(--{k})}}" for k in col
                       if k not in ("fondo", "seleccion", "sel_fg") and not es_fondo(k))
    clases += "\n.c-seleccion{background:var(--seleccion);color:var(--sel_fg)}"
    clases += "\n.c-inverso{background:var(--inverso);color:var(--fondo)}"
    clases += "\n.c-fondo{background:var(--fondo)}"
    clases += "".join(f"\n.c-{k}{{background:var(--{k})}}" for k in col
                      if es_fondo(k) and k != "inverso")
    variantes = ""
    for nombre, cambios in app.variantes.items():
        decl = ";".join(f"--{k}:{v}" for k, v in cambios.items())
        variantes += f'html[data-pal="{nombre}"]{{{decl}}}'
    return f"""
:root{{{variables}--sel_fg:{col.get('sel_fg', col['texto'])};
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}}
{variantes}
*{{box-sizing:border-box}}
body{{margin:0;background:#0a0b0f;color:#c9d1d9;font-family:var(--sans);padding:0 0 80px}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 22px}}
header{{padding:34px 0 22px;border-bottom:1px solid #1b2130;margin-bottom:26px}}
h1{{margin:0 0 8px;font-size:26px;letter-spacing:-.02em}}
h1 span{{color:var(--titulo);font-family:var(--mono)}}
.sub{{color:#7d8996;font-size:15px;line-height:1.68;margin:0;max-width:84ch}}
.controls{{display:flex;gap:18px;align-items:center;margin-top:16px;font-size:13px;color:#7d8996;flex-wrap:wrap}}
select{{font-family:var(--mono);font-size:12.5px;background:#0f1420;color:#c9d1d9;border:1px solid #24303f;border-radius:7px;padding:6px 9px}}
section{{margin:0 0 44px}}
.head{{display:flex;align-items:baseline;gap:12px;margin-bottom:5px}}
.num{{font-family:var(--mono);font-size:11px;color:var(--titulo);border:1px solid #24303f;border-radius:5px;padding:4px 7px}}
h2{{font-size:18px;margin:0;font-weight:600}}
.nota{{color:#7d8996;font-size:13.5px;line-height:1.65;margin:0 0 12px;max-width:92ch}}
.nota code{{font-family:var(--mono);background:#0f1420;border:1px solid #1e2836;border-radius:4px;padding:0 4px;color:#9fd0e0}}
.term{{background:var(--fondo);border-radius:7px;padding:12px 14px;overflow-x:auto;
 box-shadow:0 0 0 1px #1e2836, 0 24px 55px -34px #000}}
.term pre{{margin:0;font-family:var(--mono);font-size:12.5px;line-height:1.3;white-space:pre;color:var(--texto)}}
{clases}
footer{{color:#7d8996;font-size:13.5px;line-height:1.75;border-top:1px solid #1b2130;padding-top:20px}}
footer code{{font-family:var(--mono);background:#0f1420;border:1px solid #1e2836;border-radius:4px;padding:1px 5px;color:#a9b6c9}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}}
th,td{{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #1b2130;vertical-align:top}}
th{{color:#7d8996;font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}}
td code{{font-family:var(--mono);color:#d8e2e6;font-size:12.5px}}
.swatch{{display:inline-block;width:13px;height:13px;border-radius:3px;vertical-align:-2px;margin-right:7px;box-shadow:0 0 0 1px #ffffff18}}
.aviso{{background:#0d1420;border-left:3px solid var(--titulo);padding:13px 16px;border-radius:0 7px 7px 0;
 color:#96a4b2;font-size:13.5px;line-height:1.68;margin-top:16px}}
"""


def construir_html(app: App, href_indice: str = "indice.html") -> str:
    pantallas = construir(app)
    secciones = []
    for numero, nombre, nota, lienzo in pantallas:
        filas = "\n".join(spans(fila) for fila in lienzo.rejilla)
        secciones.append(f"""
<section>
  <div class="head"><span class="num">{numero}</span><h2>{html.escape(nombre)}</h2></div>
  <p class="nota">{marcas(nota)}</p>
  <div class="term"><pre>{filas}</pre></div>
</section>""")

    filas_color = ""
    for clave, hexa in paleta(app).items():
        if clave in ("seleccion", "sel_fg"):
            continue
        filas_color += (f'<tr><td><span class="swatch" style="background:{hexa}"></span>'
                        f'<code>{hexa}</code></td><td>{clave}</td>'
                        f'<td>{app.uso.get(clave, "")}</td>'
                        f'<td>{app.origen.get(clave, "medido")}</td></tr>')

    opciones = "".join(f'<option value="{v}">{v}</option>'
                       for v in ("original", *app.variantes))
    return f"""<!DOCTYPE html>
<html lang="es" data-pal="original">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(app.nombre)} · TUI real</title>
<style>{_css(app)}</style></head>
<body>
<div class="wrap">
<header>
  <h1>{html.escape(app.nombre)} <span>· TUI real, tres pantallas</span></h1>
  <p class="sub">{marcas(app.descripcion)}</p>
  <div class="controls">
    <label>Paleta <select id="pal">{opciones}</select></label>
    <span><code>{html.escape(app.comando)}</code></span>
  </div>
  <div class="aviso"><strong>De dónde sale el color.</strong> {marcas(app.fuente)}</div>
</header>
{"".join(secciones)}
<section>
  <div class="head"><span class="num">04</span><h2>El color, y de dónde sale</h2></div>
  <table>
    <tr><th>Color</th><th>Nombre</th><th>Uso</th><th>Origen</th></tr>
    {filas_color}
  </table>
</section>
<footer>
  Generado por <code>tui/</code> · motor de celdas en <code>mockups/celdas.py</code> ·
  <a href="{href_indice}" style="color:var(--titulo)">volver al índice de la serie</a>
</footer>
</div>
<script>
const pal=document.getElementById('pal');
pal.addEventListener('change',e=>document.documentElement.dataset.pal=e.target.value);
</script>
</body></html>"""


def _rgb(hexa: str) -> str:
    return f"{int(hexa[1:3], 16)};{int(hexa[3:5], 16)};{int(hexa[5:7], 16)}"


def pintar(app: App, lienzo: Lienzo, fondo: str | None = None) -> str:
    col = paleta(app)
    base = fondo or col["fondo"]
    ansi = {k: f"\x1b[38;2;{_rgb(v)};48;2;{_rgb(base)}m"
            for k, v in col.items() if k not in ("seleccion", "sel_fg") and not es_fondo(k)}
    # no todas las apps declaran un rol `inverso`: ncdu sí, las otras seis no.
    # Sin esta caída, `--ansi` revienta solo en las que no lo declaran.
    _inverso = col.get("inverso") or col.get("seleccion") or col["titulo"]
    ansi["inverso"] = f"\x1b[38;2;{_rgb(base)};48;2;{_rgb(_inverso)}m"
    for k in col:
        if es_fondo(k) and k != "inverso":
            ansi[k] = f"\x1b[38;2;{_rgb(base)};48;2;{_rgb(col[k])}m"
    ansi_extra: dict[str, str] = {}
    ansi["seleccion"] = (f"\x1b[38;2;{_rgb(col.get('sel_fg', col['texto']))}"
                         f";48;2;{_rgb(col['seleccion'])}m")
    salida = []
    for fila in lienzo.rejilla:
        actual, buffer = None, ""
        for celda in fila:
            if celda.estilo != actual:
                if buffer:
                    salida.append(f"{ansi.get(actual, '')}{buffer}\x1b[0m")
                actual, buffer = celda.estilo, celda.char
            else:
                buffer += celda.char
        if buffer:
            if actual and es_hex(actual):
                if actual not in ansi_extra:
                    ansi_extra[actual] = f"\x1b[38;2;{_rgb(actual)};48;2;{_rgb(base)}m"
                salida.append(f"{ansi_extra[actual]}{buffer}\x1b[0m")
            else:
                salida.append(f"{ansi.get(actual, '')}{buffer}\x1b[0m")
        salida.append("\n")
    return "".join(salida)


def escribir(app: App, destino: Path) -> tuple[str, str]:
    pantallas = construir(app)
    html_ = construir_html(app)
    (destino / f"{app.clave}.html").write_text(html_, encoding="utf-8")
    ruta_txt = destino / f"{app.clave}.txt"
    with open(ruta_txt, "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            etiqueta = f"=== {numero} · {nombre} "
            fh.write("\n" + etiqueta + "=" * max(0, ANCHO - len(etiqueta)) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    return str(destino / f"{app.clave}.html"), str(ruta_txt)
