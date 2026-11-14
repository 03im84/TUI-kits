#!/usr/bin/env python3
"""La serie de siete: construye todas, verifica y escribe.

    python3 tui/series.py              # los 7 html, los 7 txt y el índice
    python3 tui/series.py --ansi btop  # una app pintada en el terminal
    python3 tui/series.py --lista      # qué hay y de dónde sale cada paleta

Las siete son apps que existen: ncdu, btop, bagels, posting, fx, castero y
gitui. La diferencia con las series anteriores no es de código sino de criterio:
aquí la paleta no se inventa ni se mide a ojo — se lee del fichero de tema de la
app o se saca del histograma de una captura, que en una TUI plana sí funciona.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from tui.apps1 import APPS1  # noqa: E402
from tui.apps2 import APPS2  # noqa: E402
from tui.comun import (ANCHO, ALTO, App, construir, escribir, marcas, paleta, pintar,  # noqa: E402
                       verificar)

APPS: list[App] = [*APPS1, *APPS2]

CSS_INDICE = """
:root{--fondo:#0a0b0f;--texto:#c9d1d9;--tenue:#7d8996;--acento:#addb67;
 --mono:"Cascadia Mono","JetBrains Mono","Consolas","DejaVu Sans Mono",Menlo,monospace;
 --sans:"Segoe UI",system-ui,-apple-system,Arial,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);font-family:var(--sans);padding:0 0 80px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
header{padding:38px 0 24px;border-bottom:1px solid #1b2130;margin-bottom:26px}
h1{margin:0 0 10px;font-size:28px;letter-spacing:-.02em}
h1 span{color:var(--acento);font-family:var(--mono)}
.sub{color:var(--tenue);font-size:15px;line-height:1.7;margin:0;max-width:84ch}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:26px 0}
.card{border:1px solid #1b2130;border-radius:9px;padding:18px 20px;background:#0d1017}
.card h2{margin:0 0 6px;font-size:17px}
.card h2 a{color:var(--texto);text-decoration:none}
.card h2 a:hover{color:var(--acento)}
.cmd{font-family:var(--mono);font-size:12px;color:var(--acento);background:#12161f;
 border:1px solid #1e2836;border-radius:5px;padding:2px 6px}
.card p{color:var(--tenue);font-size:13.5px;line-height:1.6;margin:10px 0 0}
.chips{display:flex;gap:6px;margin-top:12px;flex-wrap:wrap}
.chip{font-family:var(--mono);font-size:11px;color:#9fb0c0;border:1px solid #24303f;
 border-radius:20px;padding:2px 9px}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:4px;vertical-align:-1px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 0}
th,td{text-align:left;padding:8px 14px 8px 0;border-bottom:1px solid #1b2130;vertical-align:top}
th{color:var(--tenue);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
td code{font-family:var(--mono);color:#d8e2e6;font-size:12.5px}
footer{color:var(--tenue);font-size:13.5px;line-height:1.75;border-top:1px solid #1b2130;padding-top:20px}
footer code{font-family:var(--mono);background:#12161f;border:1px solid #1e2836;border-radius:4px;padding:1px 5px}
"""


def plural(n: int, palabra: str) -> str:
    return f"{n} {palabra}" + ("" if n == 1 else "s")


def indice() -> str:
    tarjetas = []
    for app in APPS:
        col = paleta(app)
        muestras = "".join(f'<span class="sw" style="background:{h}" title="{k} {h}"></span>'
                           for k, h in col.items() if k not in ("seleccion", "sel_fg"))
        medidos = sum(1 for k in col if app.origen.get(k) == "medido")
        leidos = sum(1 for k in col if app.origen.get(k) == "leído")
        derivados = sum(1 for k in col if app.origen.get(k) == "derivado")
        heredados = len(col) - medidos - leidos - derivados
        tarjetas.append(f"""
  <div class="card">
    <h2><a href="{app.clave}.html">{html.escape(app.nombre)}</a></h2>
    <span class="cmd">{html.escape(app.comando)}</span>
    <p>{marcas(app.descripcion.split(". ")[0])}.</p>
    <div class="chips">{muestras}</div>
    <div class="chips">
      <span class="chip">{plural(leidos, "leído")}</span>
      <span class="chip">{plural(medidos, "medido")}</span>
      <span class="chip">{plural(derivados, "derivado")}</span>
      {f'<span class="chip">{plural(heredados, "heredado")}</span>' if heredados else ""}
      <span class="chip">3 pantallas</span>
    </div>
  </div>""")

    def cuenta(app):
        col = paleta(app)
        leidos = sum(1 for k in col if app.origen.get(k) == "leído")
        medidos = sum(1 for k in col if app.origen.get(k) == "medido")
        derivados = sum(1 for k in col if app.origen.get(k) == "derivado")
        return leidos, medidos, derivados, len(col) - leidos - medidos - derivados, len(col)

    filas = "".join(
        f"<tr><td><code>{app.clave}</code></td><td>{app.comando}</td>"
        + "".join(f"<td>{n}</td>" for n in cuenta(app)) + "</tr>"
        for app in APPS)

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Siete TUIs reales · índice</title>
<style>{CSS_INDICE}</style></head>
<body>
<div class="wrap">
<header>
  <h1>Siete TUIs reales <span>· 21 pantallas</span></h1>
  <p class="sub">Siete aplicaciones de terminal que existen —las del artículo de How-To Geek—
  dibujadas con el mismo motor de celdas que las otras seis series. Cada una en 100 × 30,
  tres pantallas: lo que hace falta para reconocerla, no un catálogo de funciones.
  La regla de esta serie es distinta: aquí <strong>la paleta no se inventa</strong>. btop
  trae 29 ficheros de tema y los colores se leen; las demás se miden del histograma de una
  captura real, que en una TUI plana sí da el color exacto. Y cuando un color es una
  suposición, lo dice la tabla de cada página.</p>
</header>
<div class="grid">{"".join(tarjetas)}</div>
<section>
  <h2 style="font-size:17px">Procedencia de cada paleta</h2>
  <table>
    <tr><th>app</th><th>comando</th><th>leídos</th><th>medidos</th><th>derivados</th>
    <th>heredados</th><th>colores</th></tr>
    {filas}
  </table>
  <p class="sub" style="margin-top:14px">«Leído» quiere decir copiado de un fichero de tema
  de la propia aplicación. «Medido», sacado de una captura. «Derivado» es una suposición
  razonada —y se marca para que no se confunda con las otras dos. «Heredado» es un color
  que la app no declara pero necesita (el borde de las cajas, el color de las teclas) y que
  se toma de otro color suyo ya justificado; va marcado para que se vea la costura.</p>
</section>
<footer>
  Generado por <code>tui/series.py</code> · 21 pantallas de 100 × 30 ·
  motor de celdas en <code>mockups/celdas.py</code> · solo biblioteca estándar.
</footer>
</div>
</body></html>"""


def main(argv: list[str]) -> int:
    if "--lista" in argv:
        for app in APPS:
            col = paleta(app)
            heredados = sum(1 for k in col if str(app.origen.get(k, "")).startswith("heredado"))
            print(f"{app.clave:9} {app.comando:26} {len(col):2d} colores "
                  f"({heredados} heredados) · {len(app.pantallas)} pantallas")
        return 0

    if "--ansi" in argv:
        clave = argv[argv.index("--ansi") + 1] if len(argv) > argv.index("--ansi") + 1 else "btop"
        app = next((a for a in APPS if a.clave == clave), None)
        if app is None:
            print(f"no existe la app {clave!r}; prueba: {', '.join(a.clave for a in APPS)}",
                  file=sys.stderr)
            return 1
        for numero, nombre, _, lienzo in construir(app):
            print(f"\n── {app.clave} {numero} · {nombre} " + "─" * (ANCHO - len(nombre) - 12))
            sys.stdout.write(pintar(app, lienzo))
        return 0

    problemas = [p for app in APPS for p in verificar(app)]
    if problemas:
        for problema in problemas[:25]:
            print(problema, file=sys.stderr)
        return 1

    destino = Path(__file__).resolve().parent
    for app in APPS:
        escribir(app, destino)
    (destino / "indice.html").write_text(indice(), encoding="utf-8")

    with open(destino / "series.txt", "w", encoding="utf-8") as fh:
        for app in APPS:
            fh.write(f"\n{'#' * 100}\n# {app.nombre.upper()} · {app.comando}\n{'#' * 100}\n")
            for numero, nombre, _, lienzo in construir(app):
                etiqueta = f"=== {numero} · {nombre} "
                fh.write("\n" + etiqueta + "=" * max(0, ANCHO - len(etiqueta)) + "\n")
                fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")

    def total(etiqueta):
        return sum(1 for a in APPS for k in paleta(a) if a.origen.get(k) == etiqueta)

    colores = sum(len(paleta(a)) for a in APPS)
    print(f"{len(APPS)} apps · {len(APPS) * 3} pantallas · {ANCHO}×{ALTO} · "
          f"{colores} colores: leídos {total('leído')} · medidos {total('medido')} · "
          f"derivados {total('derivado')} · heredados "
          f"{colores - total('leído') - total('medido') - total('derivado')} "
          f"→ 7 html, 7 txt, indice.html y series.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
