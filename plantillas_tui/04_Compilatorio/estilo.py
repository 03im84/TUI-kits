# -*- coding: utf-8 -*-
"""La hoja de estilo del documento, copiada del pack educativo.

Se copia aquí para que el compilatorio sea **autocontenido**: no importa
`uploads/pack/tui_pack.py` ni depende de que ese fichero esté al lado. El
aspecto es el mismo que el del pack (Georgia para el texto, DejaVu Sans Mono
para las figuras, tablas con filete) porque el material se lee junto.

    python3 04_Compilatorio/compilatorio.py     # no necesita nada más

Si algún día se cambia la tipografía del pack, esto se vuelve a copiar; no se
edita a mano.
"""

CSS = """\

@page {
  size: A4;
  margin: 18mm 16mm 16mm 16mm;
  @bottom-left { content: "Pack TUI · Instituto de Aprendizaje Humano"; font-family: Georgia, serif; font-size: 7pt; color: #b0a89c; letter-spacing: .06em; }
  @bottom-center { content: counter(page); font-family: Georgia, serif; font-size: 8pt; color: #8a8378; }
  @bottom-right { content: string(seccion); font-family: Georgia, serif; font-size: 7pt; color: #b0a89c; letter-spacing: .06em; text-transform: uppercase; }
}
@page :first { @bottom-left { content: ""; } @bottom-center { content: ""; } @bottom-right { content: ""; } }

* { box-sizing: border-box; }
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 9.4pt; line-height: 1.5; color: #23211d; margin: 0; background: #fff;
}
h1, h2, h3, h4 { margin: 0; font-weight: normal; }
p { margin: 0 0 2.6mm; }
b, strong { color: #16262b; }
i, em { color: #3d382f; }
a { color: #8a5a2b; text-decoration: none; }
.mono, code { font-family: "DejaVu Sans Mono", "Courier New", monospace; font-size: .88em; background: #f2efe8; padding: 0 1mm; border-radius: .6mm; }

/* ---------- portada ---------- */
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: space-between; page-break-after: always; }
.cover-top { border-top: 2.5pt solid #16262b; padding-top: 6mm; }
.sello { font-size: 7.6pt; letter-spacing: .28em; text-transform: uppercase; color: #8a5a2b; }
.cover h1 { font-size: 34pt; line-height: 1.05; margin: 14mm 0 5mm; letter-spacing: -.015em; color: #16262b; }
.cover h1 em { font-style: italic; }
.cover .sub { font-size: 12pt; font-style: italic; color: #5d574d; max-width: 122mm; line-height: 1.45; }
.cover-meta { display: flex; gap: 8mm; border-top: .8pt solid #d9d2c5; padding-top: 5mm; font-size: 8.2pt; color: #5d574d; }
.cover-meta div { flex: 1; }
.cover-meta b { display: block; font-size: 7pt; letter-spacing: .16em; text-transform: uppercase; color: #8a5a2b; margin-bottom: 1.5mm; font-weight: normal; }

/* ---------- estructura ---------- */
section { page-break-before: auto; margin-top: 9mm; }
section:not(.parte):not(.page) { border-top: .5pt solid #e6e0d4; padding-top: 7mm; }
section:first-of-type { border-top: 0; padding-top: 0; }
section.parte { page-break-before: always; padding-top: 40mm; break-before: page; }
section.page { page-break-after: always; break-after: page; }
.num { string-set: seccion content(); font-size: 8pt; letter-spacing: .22em; text-transform: uppercase; color: #8a5a2b; display: block; margin-bottom: 2mm; }
h2.sec { page-break-after: avoid; break-after: avoid; font-size: 21pt; line-height: 1.14; color: #16262b; margin-bottom: 4mm; letter-spacing: -.01em; }
.parte h2.sec { font-size: 27pt; }
h3 { page-break-after: avoid; break-after: avoid; font-size: 11.4pt; color: #16262b; margin: 5mm 0 2.1mm; }
h3:first-of-type { margin-top: 4mm; }
.lead { font-size: 10.3pt; color: #3d382f; font-style: italic; margin-bottom: 5mm; }
p.nota-txt { font-size: 8.4pt; color: #5d574d; font-style: italic; margin-top: -1mm; }

/* ---------- tablas ---------- */
table { page-break-inside: auto; width: 100%; table-layout: fixed; border-collapse: collapse; margin: 3mm 0 4.5mm; font-size: 8.5pt; }
th { background: #16262b; color: #fff; text-align: left; padding: 1.9mm 2mm; font-weight: normal; font-size: 7.4pt; letter-spacing: .07em; text-transform: uppercase; }
td { padding: 1.45mm 2mm; border-bottom: .5pt solid #e3ddd1; vertical-align: top; }
tr { page-break-inside: avoid; }
tbody tr:nth-child(even) td { background: #faf8f3; }
table.compact td, table.compact th { padding: 1.15mm 1.8mm; font-size: 8.1pt; line-height: 1.4; }
table.ficha { margin-top: 5mm; }
table.ficha th { background: #8a5a2b; }
table.ficha td:first-child { background: #f6f2ea; }
table.doscol td { width: 50%; }
table.glosario td:first-child { width: 30%; }
td.sem { background: #eef2f3 !important; font-weight: bold; color: #16262b; text-align: center; }
.no { color: #a63d2f; font-weight: bold; }
.si { color: #2f6b3d; font-weight: bold; }

/* ---------- bloques ---------- */
.box { border: .8pt solid #d9d2c5; background: #faf8f3; padding: 4mm 4.5mm; margin: 4mm 0; page-break-inside: avoid; }
.box-t { font-size: 7.4pt; letter-spacing: .18em; text-transform: uppercase; color: #8a5a2b; margin-bottom: 2mm; }
.box p:last-child { margin-bottom: 0; }
.regla { border-left: 3pt solid #8a5a2b; background: #fdfbf6; padding: 3mm 4mm; margin: 4mm 0; font-style: italic; page-break-inside: avoid; }
.alerta { border-left: 3pt solid #a63d2f; background: #fdf6f4; padding: 3mm 4mm; margin: 4mm 0; page-break-inside: avoid; }
.panel-nota { border-left: 3pt solid #16262b; background: #f4f7f8; padding: 3mm 4mm; margin: 3.5mm 0; font-size: 8.9pt; page-break-inside: avoid; }
.cols2 { display: flex; gap: 6mm; margin: 3mm 0; page-break-inside: avoid; }
.cols2 > div { flex: 1; font-size: 8.6pt; }

/* ---------- figuras y código ---------- */
pre.fig {
  font-family: "DejaVu Sans Mono", monospace; font-size: 6.7pt; line-height: 1.26;
  background: #16262b; color: #e8e3d8; padding: 4mm 4.5mm; margin: 3mm 0 4.5mm;
  white-space: pre; overflow: hidden; page-break-inside: avoid; border-radius: 1mm;
}
pre.code {
  font-family: "DejaVu Sans Mono", monospace; font-size: 7.1pt; line-height: 1.38;
  background: #f6f2ea; color: #26221c; border-left: 2.5pt solid #8a5a2b;
  padding: 3.5mm 4mm; margin: 3mm 0 3mm; white-space: pre-wrap; page-break-inside: avoid;
}
.reglas { display: flex; gap: 7mm; }
.reglas > div { flex: 1; }
.reglas b { display: block; font-size: 8pt; letter-spacing: .14em; text-transform: uppercase; color: #8a5a2b; margin-bottom: 2mm; }
.reglas ol { margin: 0; padding-left: 5mm; font-size: 8.6pt; }
.reglas li { margin-bottom: 1.6mm; }

/* ---------- índice ---------- */
.toc { font-size: 8.8pt; }
.toc .g { font-size: 7.2pt; letter-spacing: .16em; text-transform: uppercase; color: #8a5a2b; margin: 4mm 0 1.6mm; }
.toc a { display: block; padding: .9mm 0; border-bottom: .4pt dotted #ddd6c8; color: #23211d; }
.toc a span { color: #8a5a2b; display: inline-block; width: 11mm; font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; }
.ix { display: flex; gap: 10mm; font-size: 8.6pt; margin-top: 4mm; }
.ix > div { flex: 1; }
.ix .g { font-size: 7pt; letter-spacing: .16em; text-transform: uppercase; color: #8a5a2b; margin: 5mm 0 1.4mm; }
.ix .e { display: flex; border-bottom: .4pt dotted #ddd6c8; padding: 1mm 0; }
.ix .e span { color: #8a5a2b; font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt; width: 10mm; flex: none; }

/* ---------- pantalla ---------- */
@media screen {
  .print-only { display: none; }
  body { background: #f4f1ea; }
  .wrap { display: block; max-width: 900px; margin: 0 auto; padding: 32px 26px 80px; background: #fff; box-shadow: 0 0 40px rgba(0,0,0,.06); }
  section { page-break-before: auto; border-top: 1px solid #e8e2d6; padding-top: 30px; margin-top: 30px; }
  section.parte { padding-top: 40px; }
  .cover { height: auto; padding-bottom: 30px; }
  nav.tocnav { display: none; }
  pre.fig { font-size: 10px; overflow-x: auto; }
  pre.code { font-size: 11px; }
  h2.sec { font-size: 26px; }
  .parte h2.sec { font-size: 32px; }
  table { font-size: 12.5px; }
  table.compact td, table.compact th { font-size: 12px; }
  .lead { font-size: 15px; }
  p { font-size: 14px; line-height: 1.65; }
  .cols2 > div, .reglas ol, .panel-nota { font-size: 13px; }
}
@media print { .tocnav { display: none; } .wrap { display: block; } }

"""
