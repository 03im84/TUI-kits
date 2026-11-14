#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye el compilatorio: HTML y PDF.

    python3 04_Compilatorio/compilatorio.py

Las figuras no son dibujos: se leen de los `.txt` que generan las propias
series. Si una pantalla cambia, el compilatorio deja de coincidir con ella.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))

from estilo import CSS as CSS_BASE  # noqa: E402  (copiada del pack, ver estilo.py)
from fichas_a import SERIES_A  # noqa: E402
from fichas_b import SERIES_B  # noqa: E402

SERIES = SERIES_A + SERIES_B

#: cómo se pide a cada colección que se pinte en ANSI (para la figura con color)
ANSI_CMD = {
    "cyberpunk": ["cyberpunk/cyberpunk.py", "--ansi"],
    "minority": ["minority/minority.py", "--ansi"],
    "juego": ["juego/juego.py", "--ansi"],
    "pipboy": ["pipboy/pipboy.py", "--ansi"],
    "reactor": ["reactor/reactor.py", "--ansi"],
    "nier": ["nier/nier.py", "--ansi"],
    "pragmata": ["pragmata/pragmata.py", "--ansi"],
    "tui": ["tui/series.py", "--ansi", "btop"],
}

#: color de la pantalla cuando el generador no pinta el fondo en cada celda
FONDOS = {
    "cyberpunk": "#04070c", "minority": "#02060d", "juego": "#131f2d",
    "pipboy": "#102e16", "reactor": "#090d18", "nier": "#c3bea6",
    "pragmata": "#0b151d", "tui": "#011627",
}

#: de qué fichero .txt se saca la figura de cada colección y qué pantalla
FIGURAS = {
    "cyberpunk": ("cyberpunk/cyberpunk.txt", "01"),
    "minority": ("minority/minority.txt", "01"),
    "juego": ("juego/juego.txt", "01"),
    "pipboy": ("pipboy/pipboy.txt", "01"),
    "reactor": ("reactor/reactor.txt", "01"),
    "nier": ("nier/nier.txt", "01"),
    "pragmata": ("pragmata/pragmata.txt", "01"),
    "tui": ("tui/btop.txt", "01"),
}

SEGUNDA_FIGURA = {
    "reactor": ("reactor/reactor-ascii.txt", "01"),
    "tui": ("tui/ncdu.txt", "01"),
}

CSS_EXTRA = """
@page { @bottom-left { content: "Compilatorio de plantillas · interfaces de terminal"; } }
@page :first { @bottom-left { content: ""; } }
.ficha { border-top: .8pt solid #d8d2c4; border-bottom: .8pt solid #d8d2c4;
         padding: 3mm 0; margin: 0 0 5mm; }
.ficha td { border: 0; padding: .7mm 0; vertical-align: top; }
.ficha td.k { width: 26mm; color: #8a5a2b; font-size: 7.4pt; letter-spacing: .06em;
              text-transform: uppercase; }
.paleta { display: flex; flex-wrap: wrap; gap: 2.2mm; margin: 2mm 0 4mm; }
.chip { width: 26mm; border: .4pt solid #cfc8b8; border-radius: .8mm; overflow: hidden;
        page-break-inside: avoid; }
.chip .c { height: 9mm; }
.chip .t { font-family: "DejaVu Sans Mono", monospace; font-size: 5.6pt; padding: .8mm 1mm;
           background: #faf8f3; color: #3a352c; line-height: 1.25; }
.chip .t b { display: block; font-family: Georgia, serif; font-size: 6.4pt; font-weight: 600; }
.orden { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; color: #8a5a2b;
         border: .5pt solid #d8cdb8; border-radius: .8mm; padding: .6mm 1.8mm; }
.toc a { color: #23211d; text-decoration: none; }
.toc li { list-style: none; margin: 0 0 1.1mm; font-size: 9pt; }
.toc li a::after { content: target-counter(attr(href), page); float: right;
                   font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; color: #8a8378; }
.toc ul { padding: 0; margin: 0 0 5mm; }
.toc .g { font-size: 7.6pt; letter-spacing: .1em; text-transform: uppercase; color: #8a5a2b;
          margin: 4mm 0 1.6mm; }
.dos { display: flex; gap: 6mm; }
.dos > div { flex: 1; }
.mini { font-size: 8.2pt; }
.cifras { width: 100%; border: 0; border-collapse: collapse; margin: 8mm 0 0; }
.cifras td { border: 0; border-top: .8pt solid #23211d; padding: 3mm 0 0; width: 25%; }
.fig-braille { font-size: 8.4pt; line-height: 1.02; }
.cifras b { display: block; font-size: 26pt; font-weight: 400; line-height: 1; }
.cifras span { font-size: 7.4pt; letter-spacing: .1em; text-transform: uppercase; color: #8a5a2b; }
.mini td { padding: .9mm 1.4mm; }
"""


# --------------------------------------------------------------------------- #
# figuras: leer la pantalla del .txt, que es la salida real del generador
# --------------------------------------------------------------------------- #
_ESC = re.compile(r"\x1b\[([0-9;]*)m")


def ansi_a_html(texto: str, fondo: str) -> str:
    """Convierte una pantalla pintada en ANSI a spans con color de verdad.

    Se lee **lo que el generador pinta**, no una reconstrucción: si la serie
    cambia un color, la figura cambia. Los escapes se traducen a estilo CSS.
    """
    salida = []
    estilo = {"fg": None, "bg": fondo, "negrita": False, "subrayado": False}
    pos = 0
    for m in _ESC.finditer(texto):
        trozo = texto[pos:m.start()]
        if trozo:
            salida.append(_span(trozo, estilo))
        codigos = [int(x) for x in m.group(1).split(";") if x] or [0]
        i = 0
        while i < len(codigos):
            c = codigos[i]
            if c == 0:
                estilo = {"fg": None, "bg": fondo, "negrita": False, "subrayado": False}
            elif c == 1:
                estilo["negrita"] = True
            elif c == 4:
                estilo["subrayado"] = True
            elif c == 38 and i + 1 < len(codigos) and codigos[i + 1] == 2:
                estilo["fg"] = "#%02x%02x%02x" % tuple(codigos[i + 2:i + 5])
                i += 4
            elif c == 48 and i + 1 < len(codigos) and codigos[i + 1] == 2:
                estilo["bg"] = "#%02x%02x%02x" % tuple(codigos[i + 2:i + 5])
                i += 4
            i += 1
        pos = m.end()
    if texto[pos:]:
        salida.append(_span(texto[pos:], estilo))
    return "".join(salida)


def _span(trozo: str, estilo: dict) -> str:
    css = []
    if estilo["fg"]:
        css.append(f"color:{estilo['fg']}")
    if estilo["bg"]:
        css.append(f"background:{estilo['bg']}")
    if estilo["negrita"]:
        css.append("font-weight:700")
    if estilo["subrayado"]:
        css.append("text-decoration:underline")
    contenido = html.escape(trozo).replace(" ", "&nbsp;")
    if not css:
        return contenido
    return f'<span style="{";".join(css)}">{contenido}</span>'


def figura_color(clave: str, clase: str = "fig") -> str:
    """La primera pantalla de una colección, pintada por ella misma."""
    resultado = subprocess.run([sys.executable, *ANSI_CMD[clave]], cwd=RAIZ,
                               capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"{clave}: {resultado.stderr[-400:]}")
    lineas = resultado.stdout.splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.startswith("── "))
    # 26 y no 30: con 30 el bloque no cabe en el hueco de una página y se sale
    cuerpo = lineas[inicio + 1:inicio + 27]
    fondo = FONDOS[clave]
    html_lineas = [ansi_a_html(linea, fondo) for linea in cuerpo]
    while html_lineas and not html_lineas[-1].strip():
        html_lineas.pop()
    return (f'<pre class="{clase}" style="background:{fondo}">'
            + "\n".join(html_lineas) + "</pre>")


def figura_plantilla() -> str:
    """Las tres pantallas de la plantilla mínima, pintadas por ella misma.

    Van en tres bloques y no en uno: 95 líneas seguidas no caben en una página,
    y una figura que no cabe se sale del papel o deja media página en blanco.
    """
    resultado = subprocess.run([sys.executable, "04_Compilatorio/plantilla_tui.py", "--ansi"],
                               cwd=RAIZ, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr[-400:])
    lineas = resultado.stdout.splitlines()
    fondo, bloques, i = "#101418", [], 0
    while i < len(lineas):
        if lineas[i].startswith("── "):
            titulo = lineas[i][3:].strip(" ─")  # noqa: F841
            cuerpo = lineas[i + 1:i + 31]
            while cuerpo and not cuerpo[-1].strip():
                cuerpo.pop()
            pintado = "\n".join(ansi_a_html(linea, fondo) for linea in cuerpo)
            bloques.append(f'<pre class="fig" style="background:{fondo}">{pintado}</pre>')
            i += 31
            continue
        i += 1
    return "\n".join(bloques)


def pantalla(ruta: str, numero: str) -> str:
    texto = (RAIZ / ruta).read_text(encoding="utf-8")
    bloques = re.split(r"^=== ", texto, flags=re.M)
    for bloque in bloques:
        if bloque.startswith(f"{numero} "):
            lineas = bloque.splitlines()[1:]
            while lineas and not lineas[-1].strip():
                lineas.pop()
            return "\n".join(linea.rstrip() for linea in lineas)
    raise KeyError(f"{ruta}: pantalla {numero}")


def fig(texto: str, clase: str = "fig") -> str:
    return f'<pre class="{clase}">{html.escape(texto)}</pre>'


# --------------------------------------------------------------------------- #
# piezas de página
# --------------------------------------------------------------------------- #
def portada() -> str:
    return f"""
<section class="portada">
  <div class="sello">Instituto de Aprendizaje Humano · material de estudio</div>
  <h1>Plantillas de interfaz de terminal</h1>
  <p class="sub">Compilatorio de las ocho colecciones construidas después de la TUI de
  FFmpeg: <b>63 pantallas</b>, siete estilos de ficción y siete aplicaciones que existen,
  todas sobre el mismo motor de celdas.<br>
  Para estudiar, copiar y rehacer — no para mirar.</p>
  <table class="meta">
    <tr><td>QUÉ ES</td><td>Un catálogo de plantillas ejecutables, con su paleta, su técnica y sus límites</td></tr>
    <tr><td>CÓMO SE LEE</td><td>Una ficha por colección: idea, paleta, pantallas, técnica, qué copiar y qué no</td></tr>
    <tr><td>AL TERMINAR</td><td>Podrás copiar una plantilla y cambiarla sin romperla</td></tr>
  </table>
  <table class="cifras">
    <tr><td><b>8</b><span>colecciones</span></td>
        <td><b>63</b><span>pantallas</span></td>
        <td><b>1</b><span>motor de celdas</span></td>
        <td><b>0</b><span>dependencias</span></td></tr>
  </table>
</section>"""


def indice() -> str:
    def grupo(titulo, items):
        filas = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in items)
        return f'<div class="g">{titulo}</div><ul>{filas}</ul>'

    return f"""
<section class="toc">
  <span class="num">Índice</span>
  <h2 class="sec">Lo que hay dentro</h2>
  {grupo("Antes de empezar", [
      ("p00", "00 · Cómo se usa este compilatorio"),
      ("p01", "01 · El método: cuatro capas y una regla")])}
  {grupo("Las siete series de estilo", [
      ("s1", "02 · Cyberpunk: neón sobre negro"),
      ("s2", "03 · Minority Report: cristal"),
      ("s3", "04 · Juego: vocabulario gráfico traducido"),
      ("s4", "05 · Pip-Boy: un solo fósforo"),
      ("s5", "06 · Reactor: el chaflán y el ASCII"),
      ("s6", "07 · NieR: matriz de puntos"),
      ("s7", "08 · Pragmata: el color que trabaja")])}
  {grupo("Cuando la aplicación existe", [
      ("p09", "09 · Las siete apps reales"),
      ("p10", "10 · Las ocho colecciones comparadas")])}
  {grupo("Para construir la tuya", [
      ("p11", "11 · La plantilla mínima"),
      ("p12", "12 · Ficheros, comandos y verificación"),
      ("pa", "A · Todas las paletas"),
      ("pb", "B · Qué no demuestra este compilatorio")])}
</section>"""


def capitulo_00() -> str:
    filas = "".join(
        f"<tr><td><b>{s['orden']}</b></td><td><b>{s['nombre']}</b><br>"
        f"<span class='mono'>{s['script']}</span></td>"
        f"<td>{len(s['pantallas'])}</td><td>{s['origen']}</td>"
        f"<td>{s['unidad']}</td></tr>"
        for s in SERIES)
    return f"""
<section id="p00">
<span class="num">00</span>
<h2 class="sec">Cómo se usa este compilatorio</h2>
<p class="lead">Esto no es un tutorial. El tutorial es el <i>pack</i>: núcleo de nueve
piezas, siete patrones y un manual de decisión. Esto es el <b>catálogo de lo construido</b>
con ese método, ordenado para que se pueda estudiar, copiar y rehacer.</p>

<h3>00.1 Tres formas de leerlo</h3>
<table class="compact">
<tbody>
<tr><td style="width:22%"><b>Estudiar</b></td><td>Una colección por sesión. Mira la figura, lee la técnica, y <b>antes de pasar página</b> intenta decir en voz alta por qué esa pantalla se reconoce. Si no puedes, la técnica es la que viene escrita debajo.</td></tr>
<tr><td><b>Copiar</b></td><td>El capítulo 11 trae la plantilla mínima (<span class="mono">plantilla_tui.py</span>, 3 pantallas, 9 colores). Se copia, se cambian los datos y ya hay una TUI propia. Las fichas dicen qué piezas se pueden injertar de cada serie.</td></tr>
<tr><td><b>Rehacer</b></td><td>Cada colección es un generador: <span class="mono">python3 cyberpunk/cyberpunk.py</span> reescribe su HTML y su TXT. Cambia una pantalla, vuelve a ejecutar y mira qué se rompe. Eso enseña más que leer.</td></tr>
</tbody>
</table>

<h3>00.2 El inventario completo</h3>
<table class="compact">
<thead><tr><th style="width:7%">nº</th><th style="width:38%">colección</th><th style="width:9%">pantallas</th><th style="width:22%">paleta</th><th>unidad de dibujo</th></tr></thead>
<tbody>{filas}
<tr><td><b>—</b></td><td><b>Plantilla mínima</b><br><span class="mono">04_Compilatorio/plantilla_tui.py</span></td><td>3</td><td>derivada y declarada</td><td>celda</td></tr>
</tbody></table>
<p class="nota-txt">Las siete primeras colecciones son <b>estilos</b>: ficción, con paleta
inventada o medida. La octava es distinta en especie: son aplicaciones que existen y su paleta
se lee. Esa diferencia es el argumento del capítulo 09.</p>

<h3>00.3 Lo que este documento no es</h3>
<div class="alerta">
<p style="margin:0 0 2mm">Las 63 pantallas son <b>imágenes estáticas</b>, no programas. No hay
teclado, ni estado, ni bucle: cada pantalla es una función que dibuja sobre una rejilla y
devuelve texto. Esa es la parte que falta para convertirlas en herramientas, y el capítulo 11
dice exactamente cuál es y dónde está explicada.</p>
<p style="margin:0">Tampoco es una galería de arte: cada colección existe para enseñar <b>una
decisión concreta</b>. Si una ficha no te deja una regla que puedas aplicar mañana, esa ficha
está mal escrita, no el diseño.</p>
</div>
</section>"""


def capitulo_01() -> str:
    return f"""
<section id="p01">
<span class="num">01</span>
<h2 class="sec">El método: cuatro capas y una regla</h2>
<p class="lead">Las ocho colecciones se ven muy distintas y se construyen igual. Cuatro capas,
siempre en el mismo orden. Cuando algo falla, falla en una de las cuatro, y saber cuál ahorra
la mitad del trabajo.</p>

<table class="compact">
<thead><tr><th style="width:20%">Capa</th><th style="width:30%">Qué resuelve</th><th>Dónde vive</th></tr></thead>
<tbody>
<tr><td><b>1 · Motor</b></td><td>La rejilla de celdas: escribir en una coordenada, rellenar, comprobar bordes.</td><td><span class="mono">mockups/celdas.py</span> — 200 líneas, compartido por las ocho</td></tr>
<tr><td><b>2 · Paleta</b></td><td>Qué colores hay, qué papel tiene cada uno y de dónde sale.</td><td>Un diccionario por colección, con su procedencia escrita</td></tr>
<tr><td><b>3 · Composición</b></td><td>Dónde va cada cosa: cabecera, cuerpo, pie, paneles.</td><td>Una función por pantalla; ninguna mide texto a mano</td></tr>
<tr><td><b>4 · Salida</b></td><td>Tres destinos para el mismo dibujo: HTML con color, TXT sin un escape, ANSI para el terminal.</td><td><span class="mono">construir_html()</span> · escritura directa · <span class="mono">pintar()</span></td></tr>
</tbody>
</table>

<h3>01.1 La regla que hace todo lo demás posible</h3>
<div class="regla">Todo lo que se ve en cualquiera de estas pantallas <b>se puede escribir con
<span class="mono">sys.stdout.write</span></b>: texto y color, nada más. No hay imágenes, ni
transparencias, ni fuentes especiales, ni cursores gráficos.</div>
<p>Esa regla es la que convierte un mockup en una plantilla. Si el dibujo depende de algo que
una terminal no tiene, no se puede copiar: se puede imitar. Y una plantilla que no se puede
copiar no sirve para estudiar.</p>

<h3>01.2 Lo que cambia y lo que no</h3>
<div class="dos">
<div>
<p><b>Cambia</b>, en cada colección:</p>
<ul class="lista">
<li>la paleta y su procedencia;</li>
<li>el vocabulario de glifos (marcos discontinuos, doble línea, braille, bloques);</li>
<li>la unidad de dibujo — celda, punto o bloque;</li>
<li>la densidad: de 5 colores a 19.</li>
</ul>
</div>
<div>
<p><b>No cambia</b>, en ninguna:</p>
<ul class="lista">
<li>la rejilla de 100 × 30 y la medida en columnas;</li>
<li>el texto como única fuente de información;</li>
<li>el pie con las teclas visibles;</li>
<li>la verificación de anchura, marcos y estilos.</li>
</ul>
</div>
</div>

<div class="box">
<div class="box-t">Por qué esto es un compilatorio y no una galería</div>
<p style="margin:0">Porque las ocho comparten motor y reglas, y difieren solo en las decisiones
que el pack llama <i>particularidades</i>. Estudiar ocho galerías enseña ocho estilos; estudiar
este compilatorio enseña <b>qué palanca mueve qué</b>.</p>
</div>
</section>"""


def capitulo_serie(s, ancla: str) -> str:
    colores = "".join(
        f'<div class="chip"><div class="c" style="background:{hexa}"></div>'
        f'<div class="t"><b>{rol}</b>{hexa}<br>{origen}</div></div>'
        for rol, hexa, origen in s["colores"])
    pantallas = "".join(
        f"<tr><td class='mono' style='width:7%'>{n}</td><td style='width:24%'><b>{t}</b></td>"
        f"<td>{nota}</td></tr>"
        for n, t, nota in s["pantallas"])
    copiar = "".join(f"<li>{x}</li>" for x in s["copiar"])
    evitar = "".join(f"<li>{x}</li>" for x in s["evitar"])
    ruta, numero = FIGURAS[s["clave"]]
    figura = (figura_color(s["clave"], "fig fig-braille" if s["clave"] == "nier" else "fig")
              if s["clave"] in ANSI_CMD else fig(pantalla(ruta, numero)))
    extra = ""
    if s["clave"] in SEGUNDA_FIGURA:
        ruta2, num2 = SEGUNDA_FIGURA[s["clave"]]
        extra = f"""
<h3>{s['orden']}.5 La segunda figura</h3>
<p>La misma colección, en su otra cara: {'la versión en ASCII de 7 bits, sin un solo glifo de dibujo de cajas y sin tildes' if s['clave'] == 'reactor' else 'la app con cero colores propios, donde la identidad la hace la tipografía'}.</p>
{fig(pantalla(ruta2, num2))}"""
    return f"""
<section id="{ancla}">
<span class="num">{s['orden']} · Serie</span>
<h2 class="sec">{s['nombre']}</h2>
<p class="lead">{s['lema']}.</p>

<table class="ficha">
<tr><td class="k">Generador</td><td><span class="mono">{s['script']}</span></td></tr>
<tr><td class="k">Produce</td><td>{s['genera']}</td></tr>
<tr><td class="k">Paleta</td><td><b>{s['origen']}</b> · {len(s['colores'])} roles · {s['variantes']}</td></tr>
<tr><td class="k">Unidad</td><td>{s['unidad']} · rejilla 100 × 30</td></tr>
</table>

<h3>{s['orden']}.1 La idea</h3>
<p>{s['idea']}</p>

<h3>{s['orden']}.2 La paleta, con su procedencia</h3>
<div class="paleta">{colores}</div>
<p class="nota-txt">Cada ficha lleva el mismo dato: <b>rol, valor y origen</b>. Un color sin
origen es una opinión; con origen, es una decisión que se puede revisar.</p>

<h3>{s['orden']}.3 Una pantalla, tal como sale</h3>
{figura}
<p class="nota-txt">Figura pintada por <span class="mono">{s['script'].split(' · ')[0]} --ansi</span> y
traducida a color: cada color es el que el generador escribe, no una aproximación. Si cambia la
paleta, cambia la figura. Se muestran las primeras 26 de las 30 filas: la pantalla completa está
en <span class="mono">{s['genera'].split(' ')[0]}</span>.</p>

<h3>{s['orden']}.4 La técnica</h3>
<p>{s['tecnica']}</p>
{extra}

<h3>{s['orden']}.{'6' if extra else '5'} Qué copiar y qué no</h3>
<div class="dos">
<div><p class="mini"><b>Copiar</b></p><ul class="lista">{copiar}</ul></div>
<div><p class="mini"><b>No copiar</b></p><ul class="lista">{evitar}</ul></div>
</div>

<h3>{s['orden']}.{'7' if extra else '6'} El fragmento</h3>
<pre class="code">{html.escape(s['fragmento'])}</pre>

<h3>{s['orden']}.{'8' if extra else '7'} El inventario de sus seis pantallas</h3>
<table class="compact mini">
<thead><tr><th>nº</th><th>pantalla</th><th>qué resuelve</th></tr></thead>
<tbody>{pantallas}</tbody>
</table>
</section>"""


def capitulo_09() -> str:
    return f"""
<section id="p09">
<span class="num">09</span>
<h2 class="sec">Las siete apps reales: cuando la paleta se lee</h2>
<p class="lead">Las siete series anteriores son ficción: su color se inventa o se mide de una
imagen. Esta es la única colección donde el color <b>se copia de un fichero que la aplicación
publica</b>. Cambia el criterio entero, no el código.</p>

<h3>09.1 Siete respuestas distintas a las mismas nueve preguntas</h3>
<table class="compact">
<thead><tr><th style="width:14%">app</th><th style="width:30%">Su decisión de diseño</th><th>Lo que aporta</th></tr></thead>
<tbody>
<tr><td><b>btop</b></td><td>Degradado como información: verde, ámbar y rojo según carga.</td><td>El único caso que <b>lee</b> su paleta de 29 ficheros de tema. Es la procedencia en su forma más limpia.</td></tr>
<tr><td><b>ncdu</b></td><td>Identidad tipográfica: columnas fijas y barras de <span class="mono">#</span>.</td><td>El caso de <b>cero color propio</b>: hereda los del terminal. Una TUI puede tener carácter sin paleta.</td></tr>
<tr><td><b>gitui</b></td><td>El color clasifica estados de git; el conflicto se lee en el texto.</td><td>El límite del color: hay información que <b>no puede</b> ir solo en color.</td></tr>
<tr><td><b>bagels</b></td><td>Calendario y barras: el color hace de leyenda.</td><td>Jerarquía sin tipografía, con un solo acento y un fondo de panel.</td></tr>
<tr><td><b>posting</b></td><td>El color va al verbo HTTP y al tipo del valor JSON.</td><td>La paleta más densa del corpus: 19 roles y aun así cuatro familias de significado.</td></tr>
<tr><td><b>castero</b></td><td>Tres columnas, herencia de iTunes.</td><td>Reparto del espacio sin marcos: la separación la hace la tipografía.</td></tr>
<tr><td><b>fx</b></td><td>Ni paleta ni cromo: el JSON y los números de línea.</td><td>El caso en que la <b>procedencia es una suposición</b> y hay que decirlo.</td></tr>
</tbody>
</table>

<h3>09.2 btop: cuando el color <i>es</i> el dato</h3>
<p>Cada núcleo tiene su barra y su color; el degradado no decora, <b>clasifica la carga</b>. Un
rojo en la fila 5 no es énfasis: es un umbral. La figura sale del motor con los valores de
<span class="mono">night-owl.theme</span> leídos del disco.</p>
{figura_color("tui")}

<h3>09.3 ncdu: la identidad sin paleta</h3>
<p>Mismo motor, cero colores propios, y aun así se reconoce. La fila elegida no es un color: es
<b>vídeo inverso</b>, y el tamaño se comunica con una barra de <span class="mono">#</span> entre
corchetes. Es la prueba de que la rejilla y la jerarquía hacen más trabajo que el color.</p>
{fig(pantalla("tui/ncdu.txt", "01"))}

<h3>09.4 Las cifras de la colección</h3>
<p>El <span class="mono">verificar()</span> del motor recorre las 21 pantallas —63 000
celdas— y no encuentra un solo aviso. Y el recuento de color queda así:</p>
<pre class="code">7 apps · 21 pantallas · 100×30 · 91 colores
leídos 11 · medidos 30 · derivados 29 · heredados 21

leído      copiado de night-owl.theme: main_bg, main_fg, title, hi_fg
medido     histograma de una captura: #300a24 al 80,3 % de los píxeles
derivado   verde/rojo del diff: no había diff en la captura
heredado   borde = atenuado; la app no declara color de marco</pre>
<p class="nota-txt">Los 21 heredados no son un defecto: son la deuda que el motor cubre cuando
la app no declara ese rol. Lo que sería un defecto es no contarlos.</p>

<div class="regla">La lección de la colección 08: <b>una paleta inventada se defiende, una
paleta medida se mide, una paleta leída se copia</b>. Mezclar las tres y llamarlo todo «diseño»
es lo que hace que después nadie sepa por qué un gris es ese gris.</div>
</section>"""


def capitulo_10() -> str:
    filas = "".join(
        f"<tr><td><b>{s['orden']}</b> {s['nombre']}</td><td class='sem'>{len(s['colores'])}</td>"
        f"<td>{s['origen']}</td><td>{s['unidad']}</td>"
        f"<td>{s.get('_glifo', '')}</td></tr>"
        for s in SERIES)
    return f"""
<section id="p10">
<span class="num">10</span>
<h2 class="sec">Las ocho colecciones, comparadas</h2>
<p class="lead">Puestas en una tabla, las ocho dicen mucho más que por separado: aparecen tres
ejes que no se ven leyendo una sola ficha.</p>

<table class="compact">
<thead><tr><th style="width:32%">colección</th><th style="width:9%">colores</th>
<th style="width:20%">procedencia</th><th style="width:16%">unidad</th><th>glifo dominante</th></tr></thead>
<tbody>
<tr><td><b>01</b> Cyberpunk</td><td class="sem">10</td><td>inventada</td><td>celda</td><td><span class="mono">█ ▓ ░</span></td></tr>
<tr><td><b>02</b> Minority Report</td><td class="sem">10</td><td>inventada</td><td>celda</td><td><span class="mono">╌ ░</span></td></tr>
<tr><td><b>03</b> Juego</td><td class="sem">9</td><td>medida</td><td>celda</td><td><span class="mono">╔ ═ ▮</span></td></tr>
<tr><td><b>04</b> Pip-Boy</td><td class="sem">5</td><td>medida</td><td>celda</td><td><span class="mono">━ ▓ ▒</span></td></tr>
<tr><td><b>05</b> Reactor</td><td class="sem">11</td><td>medida + derivada</td><td>celda</td><td><span class="mono">╲ ╱ ◤</span></td></tr>
<tr><td><b>06</b> NieR</td><td class="sem">9</td><td>medida + derivada</td><td><b>punto</b></td><td><span class="mono">⣿ ⠿</span></td></tr>
<tr><td><b>07</b> Pragmata</td><td class="sem">12</td><td>medida</td><td>celda</td><td><span class="mono">╱ ╲ ◉</span></td></tr>
<tr><td><b>08</b> Apps reales</td><td class="sem">91</td><td><b>leída y medida</b></td><td>celda</td><td>el de cada app</td></tr>
</tbody></table>

<h3>10.1 Tres ejes que aparecen al comparar</h3>
<table class="compact">
<tbody>
<tr><td style="width:24%"><b>Invención → lectura</b></td><td>Es un eje, no una jerarquía. Inventar (01, 02) es legítimo en ficción; leer (08) es obligatorio cuando la app existe. Lo que nunca es legítimo es <b>inventar y presentarlo como medido</b>.</td></tr>
<tr><td><b>Cuántos colores</b></td><td>De 5 a 19, con 91 en el agregado. El número no mide calidad: Pip-Boy con 5 hace más trabajo de jerarquía que Pragmata con 12, porque el brillo es un sistema y el arcoíris no.</td></tr>
<tr><td><b>Unidad de dibujo</b></td><td>Siete colecciones dibujan en celdas; NieR dibuja en puntos (4× más resolución) y paga el precio: el texto deja de ser texto. Cambiar de unidad cambia la categoría del resultado.</td></tr>
</tbody>
</table>

<h3>10.2 Los pares que enseñan más</h3>
<div class="dos">
<div>
<p class="mini"><b>Pip-Boy / Pragmata</b></p>
<p class="nota-txt">5 colores contra 12. En Pip-Boy el color dice <i>cuánto importa</i>; en
Pragmata dice <i>qué es</i>. Son dos usos distintos del mismo canal y no se pueden mezclar sin
que la pantalla mienta.</p>
</div>
<div>
<p class="mini"><b>Cyberpunk / NieR</b></p>
<p class="nota-txt">Bloques contra puntos. Los dos dibujan «fuera» de la tipografía normal, pero
NieR cambia la resolución del medio y cyberpunk solo cambia el glifo. El coste de NieR es que
nada de su texto se puede copiar.</p>
</div>
</div>

<div class="box">
<div class="box-t">Qué haría distinta esta tabla con una colección más</div>
<p style="margin:0">Si añadieras una novena, la pregunta útil no es «¿qué estilo es?» sino
<b>«¿qué casilla de esta tabla mueve?»</b>. Si no mueve ninguna, no es una colección nueva: es
una pantalla nueva de una que ya existe.</p>
</div>
</section>"""


def capitulo_11() -> str:
    return f"""
<section id="p11">
<span class="num">11</span>
<h2 class="sec">La plantilla mínima: cómo se hace la tuya</h2>
<p class="lead">Ocho colecciones están muy bien para estudiar, pero nadie empieza copiando
setenta pantallas. Se empieza con tres. <span class="mono">plantilla_tui.py</span> es eso: tres
pantallas, nueve colores y un verificador, en un solo fichero que se ejecuta.</p>

<h3>11.1 Las cinco decisiones y ninguna más</h3>
<table class="compact">
<tbody>
<tr><td style="width:22%"><b>1 · Rejilla</b></td><td>100 × 30 celdas y una sola función que mide: <span class="mono">ancho()</span>, que cuenta <b>columnas</b>, no caracteres. Todo lo demás pasa por ella.</td></tr>
<tr><td><b>2 · Paleta</b></td><td>Nueve roles, cada uno con su procedencia escrita en un diccionario paralelo. Si un rol no tiene origen, no se pinta.</td></tr>
<tr><td><b>3 · Composición</b></td><td>Cabecera, cuerpo y pie de teclas. El mobiliario —caja, pie, cabecera— son tres funciones de quince líneas.</td></tr>
<tr><td><b>4 · Estados</b></td><td>Lista, detalle y diálogo. Son los tres que necesita cualquier utilidad, y son el 90 % de las pantallas de las ocho colecciones.</td></tr>
<tr><td><b>5 · Verificación</b></td><td>Ancho exacto, marcos intactos, estilos declarados — y una <b>prueba negativa</b>: si el verificador no detecta dos averías plantadas, el test falla.</td></tr>
</tbody>
</table>

<h3>11.2 El esqueleto, en treinta líneas</h3>
<pre class="code">ANCHO, ALTO = 100, 30

PALETA = {{"fondo": "#101418", "texto": "#d8dee6", "tenue": "#7c8894",
          "titulo": "#8fd6ff", "borde": "#2c3946", "acento": "#4fb3e8",
          "ok": "#5fd39a", "aviso": "#e8b455", "error": "#e06c75"}}

def pantalla_lista(c):                      # una función por pantalla
    cabecera(c, "copias", "5 carpetas")
    caja(c, 1, 3, 62, 22, "carpetas")
    for i, (ruta, cuenta, estado) in enumerate(FILAS):
        if i == 1:                          # el relleno, ANTES que el texto
            c.relleno(2, 4 + i * 2, 60, 1, "acento")
        c.texto(3, 4 + i * 2, ajustar(ruta, 34), "texto")
    pie(c, [("↑↓", "mover"), ("⏎", "abrir"), ("q", "salir")])

PANTALLAS = [("01", "Lista", "…", pantalla_lista), …]</pre>

<h3>11.3 Copiarla y hacerla tuya, en cuatro pasos</h3>
<pre class="code">1. cp -r mockups 04_Compilatorio/plantilla_tui.py  mi_proyecto/
2. cambia FILAS por tus datos y PALETA por tus colores (con su ORIGEN)
3. python3 mi_proyecto/plantilla_tui.py --test     # tiene que salir 0
4. python3 mi_proyecto/plantilla_tui.py            # escribe .txt y .html</pre>

<h3>11.4 La prueba negativa: lo que este corpus aprendió a la mala</h3>
<p>Mientras se construía esta plantilla aparecieron dos cosas que valen más que el código:</p>
<table class="compact">
<tbody>
<tr><td style="width:26%"><b>El verificador que no verifica</b></td><td>La primera versión dibujaba las cajas con una función propia que <b>no registraba el panel</b>. El verificador daba cero problemas porque no tenía nada que comprobar. Se descubrió plantando una avería a propósito: el test falló, y con él la ilusión de que el código estaba bien.</td></tr>
<tr><td><b>El pasillo de dos columnas</b></td><td>El motor exige <b>dos columnas libres a la derecha de cada panel</b>. Un panel que empieza justo donde acaba el anterior hace saltar 22 avisos de «el contenido se sale por la derecha». No es un capricho: es el espacio que necesita el marco para no pegarse a lo siguiente.</td></tr>
</tbody>
</table>

<h3>11.5 Del mockup a la herramienta: lo que falta</h3>
<table class="compact">
<tbody>
<tr><td style="width:24%"><b>Estado</b></td><td>Una estructura con lo que la pantalla necesita: lista, selección, filtro, mensaje. Una sola fuente de verdad.</td></tr>
<tr><td><b>Render puro</b></td><td>La función que ya tienes, pero recibiendo el estado en vez de leer constantes del módulo.</td></tr>
<tr><td><b>Entrada</b></td><td>Leer teclas y traducirlas a cambios de estado. Incluye las secuencias de escape de las flechas y la tecla Esc.</td></tr>
<tr><td><b>Bucle</b></td><td>Esperar → actualizar → repintar. Y un manejador de cambio de tamaño.</td></tr>
<tr><td><b>Terminal</b></td><td>Pantalla alternativa, cursor oculto, restaurar <i>siempre</i> — también al salir por excepción.</td></tr>
<tr><td><b>Diferencial</b></td><td>Escribir solo las celdas que cambiaron. Con 100 × 30 no hace falta; con 10 000 filas, sí.</td></tr>
</tbody>
</table>
<p class="nota-txt">La parte IV del pack desarrolla estos seis puntos con código. Este
compilatorio se detiene donde empieza el bucle a propósito: una plantilla que ya no es estática
deja de poder compararse con una figura.</p>

<h3>11.6 La plantilla, tal como sale</h3>
<p>Las tres pantallas de <span class="mono">plantilla_tui.py</span>, pintadas por ella misma
(<span class="mono">--ansi</span>) con sus nueve colores:</p>
{figura_plantilla()}

<h3>11.7 La lista de doce comprobaciones</h3>
<pre class="code">Antes de decir que una plantilla está terminada:

  1. cada fila mide exactamente el ancho de la rejilla
  2. ningún contenido pisa un borde
  3. todo estilo pintado existe en la paleta
  4. todo color de la paleta se usa en alguna pantalla
  5. el relleno se pinta antes que el texto
  6. ningún texto se recorta a media palabra
  7. la selección se distingue sin color (forma o marca)
  8. cada cifra lleva su unidad al lado
  9. el pie dice qué teclas hay, y son las que funcionan
 10. hay al menos una pantalla vacía y una de error
 11. el .txt se lee sin una sola secuencia de escape
 12. el verificador falla cuando se le planta una avería</pre>

<div class="regla">Una plantilla no está terminada cuando se ve bien: está terminada cuando
<b>se puede romper a propósito y el test lo dice</b>.</div>
</section>"""


def capitulo_12() -> str:
    filas = "".join(
        f"<tr><td><b>{s['nombre']}</b></td><td><span class='mono'>python3 {s['script'].split(' · ')[0]}</span></td>"
        f"<td>{s['genera']}</td></tr>"
        for s in SERIES)
    return f"""
<section id="p12">
<span class="num">12</span>
<h2 class="sec">Ficheros, comandos y verificación</h2>
<p class="lead">Todo lo que hay, dónde está y cómo se vuelve a generar. Sin instalación, sin
dependencias, solo biblioteca estándar.</p>

<h3>12.1 Los generadores</h3>
<table class="compact mini">
<thead><tr><th style="width:22%">colección</th><th style="width:30%">comando</th><th>produce</th></tr></thead>
<tbody>{filas}
<tr><td><b>Plantilla</b></td><td><span class="mono">python3 04_Compilatorio/plantilla_tui.py</span></td><td>plantilla.txt · plantilla.html</td></tr>
<tr><td><b>Este documento</b></td><td><span class="mono">python3 04_Compilatorio/compilatorio.py</span></td><td>Compilatorio_TUI.html · .pdf</td></tr>
</tbody></table>

<h3>12.2 Opciones comunes</h3>
<pre class="code">python3 &lt;serie&gt;.py            # escribe el HTML y el TXT de la colección
python3 &lt;serie&gt;.py --ansi     # las pinta en tu terminal, con color de verdad
python3 plantilla_tui.py --test  # se verifica; sale con 0 si está bien
python3 nier/nier.py --png    # vistas previas en nier/vista/ (necesita Pillow)
python3 reactor/reactor.py --ascii   # la versión de 7 bits</pre>

<h3>12.3 La verificación, en tres capas</h3>
<table class="compact">
<tbody>
<tr><td style="width:20%"><b>Verificador</b></td><td>Milisegundos. Ancho exacto, marcos intactos, estilos declarados. Lo trae el motor y lo usa la plantilla.</td></tr>
<tr><td><b>Prueba negativa</b></td><td>Segundos. Se planta una avería y se comprueba que el verificador la ve. Sin esto, el cero no significa nada.</td></tr>
<tr><td><b>El ojo</b></td><td>Minutos. Abrir el HTML y mirar. Caza lo que ninguna cota ve: el hueco, el desequilibrio, lo que sobra.</td></tr>
</tbody>
</table>

<h3>12.4 Mapa de ficheros</h3>
<pre class="code">mockups/celdas.py        el motor compartido: 200 líneas, ocho colecciones
04_Compilatorio/         este documento, la plantilla y sus fichas
cyberpunk/ minority/ juego/ pipboy/ reactor/ nier/ pragmata/ tui/
                         las ocho colecciones, cada una con su .py, .html y .txt
refs/btop/*.theme        29 temas reales: la fuente de la paleta leída
revisar/                 capturas de verificación de la colección 08</pre>

<div class="alerta">
<p style="margin:0"><b>Antes de dar una colección por buena:</b> ejecuta su generador, abre el
HTML, y comprueba que el TXT no lleva ni un <span class="mono">\x1b</span>. Si el TXT lleva
escapes, alguien confundió «sin color» con «con color apagado».</p>
</div>
</section>"""


def apendice_paletas() -> str:
    bloques = []
    for s in SERIES:
        chips = "".join(
            f'<div class="chip"><div class="c" style="background:{h}"></div>'
            f'<div class="t"><b>{r}</b>{h}<br>{o}</div></div>'
            for r, h, o in s["colores"])
        bloques.append(f'<h3>{s["orden"]} · {s["nombre"]} <span class="mono" style="font-size:7.5pt">'
                       f'({s["origen"]})</span></h3><div class="paleta">{chips}</div>')
    return f"""
<section id="pa">
<span class="num">Apéndice A</span>
<h2 class="sec">Todas las paletas</h2>
<p class="lead">Las ocho colecciones, color a color, con su rol y su procedencia. Es la página
que se consulta mientras se elige una paleta para algo nuevo.</p>
{"".join(bloques)}
<p class="nota-txt">Las colecciones 03 a 07 nacieron de medir imágenes: sus valores son picos de
brillo o regiones planas, según el caso, y así está declarado en cada fichero. La colección 08 es
la única cuyos valores se copian de un fichero de tema publicado por la aplicación.</p>
</section>"""


def apendice_limites() -> str:
    return f"""
<section id="pb">
<span class="num">Apéndice B</span>
<h2 class="sec">Qué no demuestra este compilatorio</h2>
<p class="lead">Ocho colecciones y 63 pantallas impresionan; conviene saber exactamente qué se
puede concluir de ellas y qué no.</p>

<table class="compact">
<tbody>
<tr><td style="width:26%"><b>No son aplicaciones</b></td><td>Son pantallas. No hay estado, ni teclado, ni bucle de eventos. Todo lo que se ve se dibuja una vez y se guarda.</td></tr>
<tr><td><b>Un solo tamaño</b></td><td>Todo se compone a 100 × 30. No hay una sola pantalla probada a 80 × 24 ni a 40 columnas, que es lo que el pack pide para una herramienta real.</td></tr>
<tr><td><b>El color, medido a ojo de máquina</b></td><td>Las paletas «medidas» salen de histogramas y percentiles de brillo. En capturas con cristal o degradado, el valor plano real es algo más apagado y así se declara.</td></tr>
<tr><td><b>Contraste no comprobado</b></td><td>Ninguna de las ocho paletas se pasó por el cálculo de contraste WCAG. Varias probablemente no cumplirían AA en sus colores tenues. Es la primera comprobación que habría que añadir.</td></tr>
<tr><td><b>Accesibilidad parcial</b></td><td>Solo Pragmata trae una paleta alternativa para deuteranopía. Las otras siete no, y no porque no haga falta.</td></tr>
<tr><td><b>Nada de rendimiento</b></td><td>No hay medidas de latencia ni de dibujado diferencial. El corpus no las necesita; una herramienta real, sí.</td></tr>
</tbody>
</table>

<h3>B.1 Cómo se cierra</h3>
<p>El compilatorio se cierra con la misma regla con la que se abrió, y conviene que quede en la
última página en vez de enterrada: <b>una plantilla no vale por lo que enseña cuando funciona,
sino por lo que deja claro cuando se rompe</b>. Las ocho colecciones están construidas para poder
romperse a propósito: cada una trae su generador, su paleta y su salida, y ninguna depende de
algo que una terminal no tenga.</p>
<p>Lo que queda por hacer es tuyo, y es siempre lo mismo: copiar la plantilla, cambiar los datos,
ejecutar la prueba negativa, añadirle un estado que no exista todavía —el vacío, el error, la
confirmación— y volver a mirarla. La novena colección del corpus será la que construyas.</p>
<div class="regla">Si una de las 63 pantallas te sirve de punto de partida, ha hecho su trabajo. Si
te obliga a decir por qué la tuya es distinta, ha hecho el doble.</div>
</section>"""


# --------------------------------------------------------------------------- #
# ensamblado
# --------------------------------------------------------------------------- #
def construir() -> str:
    anclas = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "sT"]
    cuerpo = [portada(), indice(), capitulo_00(), capitulo_01()]
    for i, serie in enumerate(SERIES_A + SERIES_B):
        cuerpo.append(capitulo_serie(serie, anclas[i]))
    # la colección 08 (apps reales) sustituye su ficha por el capítulo largo
    cuerpo = [c for c in cuerpo if 'id="sT"' not in c]
    cuerpo += [capitulo_09(), capitulo_10(), capitulo_11(), capitulo_12(),
               apendice_paletas(), apendice_limites()]

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plantillas de interfaz de terminal · compilatorio</title>
<style>{CSS_BASE}{CSS_EXTRA}</style></head><body>
<div class="wrap">{''.join(cuerpo)}</div></body></html>"""


def main() -> int:
    documento = construir()
    destino = AQUI / "Compilatorio_TUI"
    (destino.with_suffix(".html")).write_text(documento, encoding="utf-8")
    print(f"HTML  {len(documento):,} caracteres".replace(",", "."))
    from weasyprint import HTML
    HTML(string=documento, base_url=str(RAIZ)).write_pdf(destino.with_suffix(".pdf"))
    print("PDF   generado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
