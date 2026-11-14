# -*- coding: utf-8 -*-
"""Pack educativo: interfaces de terminal (TUI) — idealizar, diseñar, implementar.
Genera HTML navegable y PDF imprimible desde el mismo contenido."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tui_pack_b import PARTS_B

OUT = "/home/user/03_Pack_TUI/TUI_Pack_Educativo"

CSS = """
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


FIG_MAPA = """
<pre class="fig">  PARTE I · IDEALIZAR                    PARTE II · EL NÚCLEO
  ¿debe existir? pros y contras          N1 rejilla      N2 marcos y layouts
  qué género de TUI es                   N3 jerarquía    N4 color
  el contrato antes del boceto           N5 estados      N6 foco
                                         N7 teclas       N8 barra de estado
                    │                    N9 mensajes
                    └──────────┬─────────┘
                               ▼
              PARTE III · PARTICULARIDADES
              P1 panel · P2 tabla · P3 formulario · P4 asistente
              P5 cola de trabajo · P6 diálogos · P7 registros
                               ▼
              PARTE IV · IMPLEMENTAR      PARTE V · SÍNTESIS
              estado/render/entrada        16 reglas · 6 ejercicios
              sustratos · pruebas          rúbrica · glosario</pre>
"""

portada = """
<div class="cover">
  <div class="cover-top"><div class="sello">Instituto de Aprendizaje Humano · Pack educativo</div></div>
  <div>
    <h1>Interfaces de terminal<br><em>para quien nunca ha diseñado una</em></h1>
    <div class="sub">Idealizar con criterio, diseñar sobre una rejilla, implementar sin frameworks durante las primeras treinta líneas.<br>
    Un núcleo de nueve piezas reutilizables y siete patrones de pantalla que se construyen con ellas.</div>
  </div>
  <div>
    <table class="compact" style="font-size:8.4pt">
      <tr><td style="width:44mm;color:#8a5a2b;font-size:7.2pt;letter-spacing:.14em;text-transform:uppercase">Para quién</td><td>Sin experiencia previa en diseño ni en interfaces</td></tr>
      <tr><td style="color:#8a5a2b;font-size:7.2pt;letter-spacing:.14em;text-transform:uppercase">Cómo está hecho</td><td>Núcleo primero, particularidades después, todo reutilizable</td></tr>
      <tr><td style="color:#8a5a2b;font-size:7.2pt;letter-spacing:.14em;text-transform:uppercase">Al terminar</td><td>Podrás diseñar y construir tus propias TUI, y saber cuándo no conviene</td></tr>
    </table>
  </div>
  <div class="cover-meta">
    <div><b>Parte I</b>Idealizar: pros, contras<br>y elección de género</div>
    <div><b>Parte II</b>El núcleo: nueve piezas<br>transversales</div>
    <div><b>Partes III–V</b>Patrones, código<br>y manual de decisión</div>
  </div>
</div>
"""

mapa = """
<section>
<span class="num">00 · Cómo está organizado</span>
<h2 class="sec">Un pack nuclear: lo común primero, lo particular después</h2>
<p class="lead">La estructura no es decorativa. Cada pieza que aprendas en la parte II se vuelve a usar en la parte III sin cambios: los patrones no son diseños nuevos, son <b>combinaciones</b> del núcleo con un añadido pequeño.</p>

""" + FIG_MAPA + """

<h3>0.1 Las nueve piezas del núcleo</h3>
<table class="compact">
<thead><tr><th style="width:12%">Pieza</th><th style="width:26%">Qué resuelve</th><th>Dónde reaparece</th></tr></thead>
<tbody>
<tr><td><b>N1</b> Rejilla</td><td>La unidad de todo: la celda y sus medidas</td><td>Los siete patrones, sin excepción</td></tr>
<tr><td><b>N2</b> Marcos y layouts</td><td>Reparto del espacio y cinco estructuras base</td><td>P1, P2, P4, P6, P7</td></tr>
<tr><td><b>N3</b> Jerarquía</td><td>Cómo destacar sin tipografías ni tamaños</td><td>Todos</td></tr>
<tr><td><b>N4</b> Color</td><td>Cuatro roles y dos estados, y su alternativa sin color</td><td>Todos</td></tr>
<tr><td><b>N5</b> Estados</td><td>Vacío, cargando, error, éxito, sin permiso</td><td>Todos</td></tr>
<tr><td><b>N6</b> Foco</td><td>Quién recibe las teclas y cómo se ve</td><td>P2, P3, P4, P6, P7</td></tr>
<tr><td><b>N7</b> Teclas</td><td>Mapa canónico y memoria muscular</td><td>Todos</td></tr>
<tr><td><b>N8</b> Barra de estado</td><td>El contrato visible de lo que se puede hacer</td><td>Todos</td></tr>
<tr><td><b>N9</b> Mensajes</td><td>Errores, confirmaciones y avisos en una línea</td><td>P2, P3, P5, P6</td></tr>
</tbody>
</table>

</section>
"""

# ---------------------------------------------------------------- PARTE I
parte1 = """
<section class="parte">
<span class="num">Parte I</span>
<h2 class="sec">Idealizar: decidir antes de dibujar</h2>
<p class="lead">La mayoría de las TUIs malas no fallan al implementarse: fallan al decidirse. Se construyen porque era divertido o porque «el terminal es más rápido», y nadie comprobó antes si el problema pedía una interfaz.</p>
</section>
"""

c01 = """
<section>
<span class="num">01 · Idealizar</span>
<h2 class="sec">Qué es (y qué no es) una interfaz de terminal</h2>
<p class="lead">Una TUI es una aplicación que vive dentro de la terminal: dibuja con caracteres sobre una rejilla fija, se maneja con teclado y no necesita ventanas, ratón ni entorno gráfico.</p>

<h3>1.1 Las cuatro condiciones que la definen</h3>
<table class="compact">
<thead><tr><th style="width:22%">Condición</th><th style="width:34%">Qué significa</th><th>Consecuencia de diseño</th></tr></thead>
<tbody>
<tr><td><b>Rejilla de caracteres</b></td><td>La pantalla es una matriz de celdas iguales, no un lienzo libre.</td><td>Todo se piensa en columnas y filas. El espacio es escaso y contable: se administra, no se rellena.</td></tr>
<tr><td><b>Entrada por teclado</b></td><td>El usuario escribe teclas; puede haber ratón, pero nunca es la única vía.</td><td>El mapa de teclas es parte del diseño, no un detalle de implementación.</td></tr>
<tr><td><b>Dentro de un terminal</b></td><td>Comparte espacio con otros programas, se accede por SSH y convive con el prompt.</td><td>La aplicación tiene que poder entrar y salir limpia; y a menudo se usa en pantallas de 40 columnas.</td></tr>
<tr><td><b>Sin imágenes ni tipografías</b></td><td>Una sola familia monoespaciada; color limitado; sin transparencias.</td><td>La jerarquía se construye con espacio, mayúsculas, posición y símbolos.</td></tr>
</tbody>
</table>

<h3>1.2 Lo que una TUI no es</h3>
<table class="compact">
<tbody>
<tr><td style="width:34%"><b>No es «una web en gris»</b></td><td>Un formulario web trasladado a caracteres pierde todo lo que la web hacía bien (jerarquía, ayuda contextual, validación suave) y conserva lo malo (densidad, dependencia del ratón).</td></tr>
<tr><td><b>No es una herramienta de segunda</b></td><td>Para vigilar servicios, procesar lotes, explorar registros o trabajar por SSH, una TUI es a menudo <b>mejor</b> que una interfaz gráfica: arranca en milisegundos y funciona donde no hay pantalla.</td></tr>
<tr><td><b>No es una salida de consola</b></td><td>Imprimir líneas y terminar no es una interfaz: es un registro. La diferencia es que la TUI <b>mantiene un estado</b> y responde a teclas sin volver a ejecutarse.</td></tr>
</tbody>
</table>

<div class="box">
<div class="box-t">La definición operativa del pack</div>
<p style="margin-bottom:0">Una TUI es <b>una aplicación con estado que dibuja una rejilla de caracteres y responde a teclas</b>. Todo lo que se construya bajo esa definición entra en el pack; todo lo que no mantenga estado (un comando que imprime y sale) necesita otras reglas, que no son estas.</p>
</div>
</section>
"""

c02 = """
<section>
<span class="num">02 · Idealizar</span>
<h2 class="sec">Cuándo una TUI es la respuesta correcta</h2>
<p class="lead">Antes de elegir TUI hay que ganársela. Esta es la conversación honesta que hay que tener con uno mismo, con los pros y los contras puestos en la misma tabla.</p>

<h3>2.1 Ventajas reales (no entusiasmo, ventajas)</h3>
<table class="compact">
<tbody>
<tr><td style="width:32%"><b>Arranca en milisegundos</b></td><td>No hay motor de render, ni capa gráfica, ni fuentes que cargar. Para herramientas que se abren veinte veces al día, esto es una diferencia de uso, no de rendimiento.</td></tr>
<tr><td><b>Funciona por SSH y sin escritorio</b></td><td>Es la única interfaz posible en un servidor, en un contenedor o en una conexión mala. Y la misma herramienta sirve en local y en remoto.</td></tr>
<tr><td><b>Se puede automatizar y componer</b></td><td>Convive con tuberías, <span class="mono">tmux</span>, <span class="mono">grep</span>, scripts y tareas programadas. Una interfaz gráfica vive aislada; una TUI es una pieza más del sistema.</td></tr>
<tr><td><b>Es barata de distribuir</b></td><td>Un binario o un paquete. Sin instaladores, sin dependencias de sistema, sin actualizaciones de escritorio.</td></tr>
<tr><td><b>La rejilla obliga a priorizar</b></td><td>Con 80 columnas no cabe lo accesorio. Muchas TUIs son más claras que su equivalente gráfica porque no tuvieron sitio para el desorden.</td></tr>
<tr><td><b>Es accesible por defecto… si se hace bien</b></td><td>Todo texto, todo teclado: funciona con lectores de pantalla y sin ratón. La accesibilidad es una consecuencia del medio, no un añadido (§14).</td></tr>
</tbody>
</table>

<h3>2.2 Desventajas que hay que aceptar por escrito</h3>
<table class="compact">
<tbody>
<tr><td style="width:32%"><b>Público limitado</b></td><td>Quien no vive en la terminal no la va a usar. Si el usuario final es administrativo, clínico o de dirección, la TUI casi nunca es la respuesta.</td></tr>
<tr><td><b>Sin imágenes ni gráficos</b></td><td>Nada de fotografías, mapas, iconos ricos ni curvas. Series temporales como mucho en una línea.</td></tr>
<tr><td><b>Depende del terminal del otro</b></td><td>Tamaño, colores, Unicode, teclas modificadoras: cada terminal es un mundo. Hay que degradar y probar (§25).</td></tr>
<tr><td><b>La curva de entrada es alta</b></td><td>Sin ratón y sin botones evidentes, el usuario tiene que aprender teclas. Si la herramienta se usa una vez al mes, esa curva no se amortiza.</td></tr>
<tr><td><b>Las animaciones cuestan</b></td><td>Y por SSH cuestan tráfico. La sensación de inmediatez exige cuidado con el refresco (§24).</td></tr>
<tr><td><b>Más difícil de testear visualmente…</b></td><td>…pero más fácil de testear que una interfaz gráfica, si el render es una función pura (§22, §25). Con criterio, la desventaja se vuelve ventaja.</td></tr>
</tbody>
</table>

<h3>2.3 La prueba de las seis preguntas</h3>
<p>Si contestas «no» a alguna de las tres primeras, la TUI no es el medio. Si contestas «sí» a todas, el género está claro.</p>
<table class="compact">
<thead><tr><th style="width:8%">#</th><th style="width:52%">Pregunta</th><th>Si la respuesta es «no»</th></tr></thead>
<tbody>
<tr><td class="sem">1</td><td>¿El usuario trabaja ya en la terminal o por SSH?</td><td>Haz una interfaz web. En serio.</td></tr>
<tr><td class="sem">2</td><td>¿La tarea se repite, o al menos se usa con frecuencia?</td><td>Un comando con buenos argumentos y buena salida es mejor que una TUI.</td></tr>
<tr><td class="sem">3</td><td>¿La información es sobre todo texto, números y estados?</td><td>Si hay mapas, imágenes o geometría, es otro medio.</td></tr>
<tr><td class="sem">4</td><td>¿Se puede manejar todo con teclado y sin color?</td><td>Rediseña antes de programar: algo está apoyado en lo visual.</td></tr>
<tr><td class="sem">5</td><td>¿Funciona en 80×24 y se degrada en 40 columnas?</td><td>Aún no está diseñada, solo bocetada.</td></tr>
<tr><td class="sem">6</td><td>¿Sabes qué teclas usa y dónde se ven?</td><td>No hay interfaz: hay dibujo.</td></tr>
</tbody>
</table>

<div class="regla">La TUI es la elección correcta cuando <b>el coste de abrir la herramienta es el problema</b> y el contenido es texto: vigilar, explorar, procesar, revisar. Es la elección equivocada cuando el problema es convencer a alguien que no ha abierto una terminal en su vida.</div>
</section>
"""

c03 = """
<section>
<span class="num">03 · Idealizar</span>
<h2 class="sec">Los cinco géneros y cómo elegir el tuyo</h2>
<p class="lead">Casi toda herramienta de terminal es una variante de cinco formas. Reconocer la forma antes de dibujar evita el error más caro: inventar una pantalla que ya existe y funciona peor.</p>

<table class="compact">
<thead><tr><th style="width:20%">Género</th><th style="width:26%">Pregunta que responde</th><th style="width:22%">Pieza central</th><th>Patrón del pack</th></tr></thead>
<tbody>
<tr><td><b>Vigilancia</b></td><td>«¿Cómo está esto ahora mismo?»</td><td>Tarjetas con cifra y comparación</td><td>P1 panel de estado</td></tr>
<tr><td><b>Exploración</b></td><td>«¿Dónde está el que busco y qué tiene?»</td><td>Lista + detalle + filtro</td><td>P2 tabla y explorador</td></tr>
<tr><td><b>Captura</b></td><td>«¿Cómo meto este dato sin equivocarme?»</td><td>Campos con validación</td><td>P3 formulario · P4 asistente</td></tr>
<tr><td><b>Proceso</b></td><td>«¿Cómo va esto y qué ha fallado?»</td><td>Cola con estados y progreso</td><td>P5 cola de trabajo</td></tr>
<tr><td><b>Diagnóstico</b></td><td>«¿Qué pasó exactamente?»</td><td>Registro con filtro y detalle</td><td>P7 registros</td></tr>
</tbody>
</table>

<h3>3.1 Cómo se elige (y cómo se combinan)</h3>
<p>Se elige por la <b>acción principal</b> del usuario, no por el tipo de datos. Una herramienta de pacientes puede ser exploración (buscar y abrir) o captura (dar de alta); son dos pantallas distintas del mismo producto, y cada una tiene su género. Lo normal en una herramienta madura es <b>dos o tres géneros combinados</b> con una tecla que los une, nunca cinco amontonados en una sola pantalla.</p>

<table class="compact">
<tbody>
<tr><td style="width:30%"><b>Un género por pantalla</b></td><td>El usuario sabe siempre qué está mirando. Cambiar de género es cambiar de pantalla, con una tecla estable (<span class="mono">1</span>, <span class="mono">2</span>, <span class="mono">3</span> o <span class="mono">Tab</span> entre secciones).</td></tr>
<tr><td><b>Combinación típica</b></td><td>Vigilancia + diagnóstico: el panel detecta, <span class="mono">Enter</span> abre los registros de esa métrica. Es la combinación más útil de todas y la que menos se implementa.</td></tr>
<tr><td><b class="no">Lo que no funciona</b></td><td>Una pantalla que intenta vigilar, explorar y capturar a la vez. El usuario acaba con veinte teclas y ninguna segura.</td></tr>
</tbody>
</table>

<div class="panel-nota"><b>Prueba de humo:</b> escribe en una frase la acción principal de tu herramienta. Si la frase tiene dos verbos («ver y editar», «buscar y procesar»), tienes dos pantallas, no una. Ese es el reparto que hay que hacer antes de dibujar nada.</div>
</section>
"""

c04 = """
<section>
<span class="num">04 · Idealizar</span>
<h2 class="sec">El contrato antes del boceto</h2>
<p class="lead">Diseñar una TUI es responder seis preguntas por escrito. Lo que no se responde antes se decide por accidente durante la implementación, y ahí ya no se decide: se improvisa.</p>

<table class="compact">
<thead><tr><th style="width:8%">#</th><th style="width:26%">Pregunta</th><th style="width:30%">Qué produce</th><th>Si no se responde</th></tr></thead>
<tbody>
<tr><td class="sem">1</td><td><b>¿Quién y en qué condiciones?</b></td><td>Ancho mínimo, si hay color, si hay prisa, si hay conexión mala.</td><td>Se diseña para uno mismo en una pantalla grande y no funciona para nadie más.</td></tr>
<tr><td class="sem">2</td><td><b>¿Cuál es la tarea principal, en un verbo?</b></td><td>El género (§03) y la pantalla de arranque.</td><td>La herramienta abre en una pantalla que no es la que se usa.</td></tr>
<tr><td class="sem">3</td><td><b>¿Con qué frecuencia se usa?</b></td><td>Cuánto puede exigir la curva de teclas.</td><td>Atajos para una herramienta mensual, o menús para una que se usa cada hora.</td></tr>
<tr><td class="sem">4</td><td><b>¿Qué error es caro?</b></td><td>Dónde van las confirmaciones, los deshacer y las validaciones.</td><td>Se protege lo barato y se deja suelto lo grave (§13).</td></tr>
<tr><td class="sem">5</td><td><b>¿De dónde vienen los datos y qué pasa si fallan?</b></td><td>Los estados de error y la política de datos obsoletos (§09).</td><td>La pantalla se queda en blanco y el usuario cree que no hay datos.</td></tr>
<tr><td class="sem">6</td><td><b>¿Cómo se sale y qué queda hecho?</b></td><td>Teclas de salida, limpieza de terminal y confirmación de estado.</td><td>El usuario sale con la terminal rota y sin saber si su acción se guardó.</td></tr>
</tbody>
</table>

<h3>4.1 El contrato en cinco líneas (plantilla para copiar)</h3>
<pre class="code">HERRAMIENTA:      ______________________  (un sustantivo concreto)
USUARIO:          ________________  en  ______ columnas, con/sin color
TAREA PRINCIPAL:  ______________________  (un verbo: vigilar | explorar |
                                           capturar | procesar | diagnosticar)
FRECUENCIA:       ______ veces al ______
ERROR CARO:       ______________________  ->  protección: ______
DATOS:            origen ______  si falla: ______
SALIDA:           tecla ______  deja hecho: ______  restaura: ______</pre>

<h3>4.2 Alcances y limitaciones: lo que hay que aceptar de entrada</h3>
<table class="compact">
<thead><tr><th style="width:50%">Alcance (lo que este medio hace mejor)</th><th>Limitación (lo que no se negocia)</th></tr></thead>
<tbody>
<tr><td>Densidad de información por pantalla</td><td>Sin imágenes, iconos ricos ni gráficos; series como mucho de una línea</td></tr>
<tr><td>Velocidad de arranque y de interacción con teclado</td><td>Sin ratón como vía principal, sin <i>hover</i>, sin arrastrar y soltar</td></tr>
<tr><td>Funcionar por SSH, en contenedores y en servidores</td><td>Depende del tamaño, del color y del juego de caracteres del terminal ajeno</td></tr>
<tr><td>Componerse con otros programas y automatizarse</td><td>No hay integración con el escritorio: portapapeles y archivos, según terminal</td></tr>
<tr><td>Accesibilidad de base (todo texto, todo teclado)</td><td>Solo si no se depende del color ni del Unicode (§14)</td></tr>
<tr><td>Coste de distribución casi nulo</td><td>Público limitado a quien ya vive en la terminal</td></tr>
</tbody>
</table>

<h3>4.3 El contrato, resuelto: un ejemplo completo</h3>
<pre class="code">HERRAMIENTA:      lista de pacientes en espera
USUARIO:          terapeuta · 100+ columnas · a veces por SSH y sin color
TAREA PRINCIPAL:  explorar
FRECUENCIA:       15 veces al día
ERROR CARO:       borrar una ficha  ->  confirmar escribiendo el nombre,
                                        papelera de 30 días, nunca borrado real
DATOS:            base local  ·  si falla: última copia con su hora, marcada
SALIDA:           q  ·  deja hecho: la selección se recuerda al volver
                  ·  restaura: cursor, eco y pantalla</pre>

<table class="compact">
<thead><tr><th style="width:30%">Respuesta</th><th>Consecuencia directa en el diseño</th></tr></thead>
<tbody>
<tr><td>«Explorar», 15 veces al día</td><td>Género P2 (tabla + detalle) como pantalla de arranque. No hay panel: nadie abre una herramienta quince veces para mirar cifras.</td></tr>
<tr><td>«Por SSH, sin color»</td><td>La selección se marca con <span class="mono">▶</span>; los estados llevan palabra. El color es un extra, no un requisito.</td></tr>
<tr><td>«Borrar es caro»</td><td>La única confirmación de la aplicación, y con el nombre escrito a mano. Todo lo demás se hace sin interrumpir.</td></tr>
<tr><td>«Base local que puede fallar»</td><td>Estado de error con datos de la última copia y su hora. La pantalla nunca se queda en blanco.</td></tr>
</tbody>
</table>

<div class="alerta"><b>El límite que más se ignora:</b> una TUI no compite con una aplicación de escritorio; compite con un comando, un archivo de texto y un <span class="mono">grep</span>. Si tu TUI no es más clara o más rápida que esa combinación, no hay razón para construirla. Y no pasa nada: la mitad de las ideas de TUI se caen en esta comprobación, y caerse ahí es un éxito del método.</div>
</section>
"""

parte1 += c01 + c02 + c03 + c04

# ---------------------------------------------------------------- PARTE II
parte2 = """
<section class="parte">
<span class="num">Parte II</span>
<h2 class="sec">El núcleo: nueve piezas que se repiten siempre</h2>
<p class="lead">Estas nueve piezas son el vocabulario del medio. Se aprenden una vez y se usan en cualquier pantalla: son las que hacen que dos herramientas distintas parezcan del mismo autor, y las que permiten diseñar rápido sin copiar.</p>
</section>
"""

n1 = """
<section>
<span class="num">05 · Núcleo N1</span>
<h2 class="sec">La celda y la rejilla</h2>
<p class="lead">Todo lo demás se apoya aquí. Si la rejilla está mal pensada, ninguna otra pieza puede salvarlo: es el equivalente a una retícula tipográfica en papel.</p>

<h3>5.1 Las medidas que hay que saber de memoria</h3>
<table class="compact">
<thead><tr><th style="width:26%">Medida</th><th style="width:24%">Valor</th><th>Por qué</th></tr></thead>
<tbody>
<tr><td><b>Pantalla mínima</b></td><td>80 × 24</td><td>El tamaño clásico de terminal y el mínimo razonable. Todo tiene que caber aquí sin cortarse.</td></tr>
<tr><td><b>Degradación</b></td><td>40 columnas</td><td>Móvil, panel dividido, ventana estrecha. O funciona, o muestra un aviso claro: nunca dibujo roto.</td></tr>
<tr><td><b>Margen interior</b></td><td>1 columna</td><td>Nada pegado al borde. Un carácter de aire alrededor de todo cambia por completo la legibilidad.</td></tr>
<tr><td><b>Sangría de nivel</b></td><td>2 columnas</td><td>Jerarquía por posición: cada nivel de anidamiento, dos columnas.</td></tr>
<tr><td><b>Ancho de columna de texto</b></td><td>≤ 72 columnas</td><td>Más allá, la vista pierde el salto de línea. En pantallas anchas, el texto se centra o se divide en dos columnas.</td></tr>
<tr><td><b>Filas de contenido</b></td><td>3 bandas</td><td>Cabecera + cuerpo + pie. Deja 20 filas útiles en una pantalla de 24: ese es el presupuesto real.</td></tr>
</tbody>
</table>

<h3>5.2 El presupuesto de espacio, contado</h3>
<pre class="fig">80 x 24  ──────────────────────────────────────────────────────────────
 fila 1      ┌ CABECERA: título + contexto (1 fila) ──────────────────┐
 filas 2-3   │ margen + subtítulo opcional                           │
 filas 4-21  │                                                       │
             │        CUERPO: 18 filas útiles de contenido           │
             │                                                       │
 fila 22     ├───────────────────────────────────────────────────────┤
 fila 23     │ BARRA DE ESTADO: teclas disponibles ahora             │
 fila 24     │ línea de mensajes (errores, confirmaciones)           │
             └───────────────────────────────────────────────────────┘
 Si necesitas más filas para el cuerpo, quítalas de la cabecera:
 nunca de la barra de estado ni de la línea de mensajes.</pre>

<h3>5.3 Las cuatro reglas de N1</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Los anchos se deciden en el diseño, no por el contenido.</b> Una columna no crece porque un dato sea largo: se trunca (§16). Si el contenido no cabe, el diseño estaba mal.</td></tr>
<tr><td class="sem">2</td><td><b>Todo se mide en columnas, nunca en píxeles ni en porcentajes.</b> «La columna de estado ocupa 12 columnas», no «un 15 %».</td></tr>
<tr><td class="sem">3</td><td><b>El contenido se alinea a la rejilla, no al gusto.</b> Bordes en la misma columna, cifras en la misma posición, etiquetas de la misma longitud.</td></tr>
<tr><td class="sem">4</td><td><b>Se prueba en tres anchos: 80, 60 y 40.</b> Un diseño que solo funciona en 80 no está terminado; es un boceto grande.</td></tr>
</tbody>
</table>
</section>
"""

n2 = """
<section>
<span class="num">06 · Núcleo N2</span>
<h2 class="sec">Marcos, bandas y los cinco layouts</h2>
<p class="lead">Cinco estructuras cubren casi todo. No hay que inventar layouts: hay que reconocer cuál de estos cinco es el problema y aplicarlo entero.</p>

<h3>6.1 Los cinco layouts</h3>
<table class="compact">
<thead><tr><th style="width:14%">Código</th><th style="width:24%">Estructura</th><th style="width:28%">Cuándo</th><th>Riesgo típico</th></tr></thead>
<tbody>
<tr><td><b>L1</b> Tres bandas</td><td>Cabecera · cuerpo · barra de estado</td><td>Cualquier pantalla simple y todas las de vigilancia</td><td>Cabecera demasiado alta: se come el cuerpo</td></tr>
<tr><td><b>L2</b> Dos columnas</td><td>Reparto vertical 40/60 o 30/70</td><td>Lista + detalle cuando no hay filtros</td><td>Columnas que cambian de ancho según el contenido</td></tr>
<tr><td><b>L3</b> Master-detail</td><td>Lista arriba o izquierda, detalle al lado, pie común</td><td>Exploración con acción sobre un elemento</td><td>El detalle roba espacio a la lista hasta hacerla ilegible</td></tr>
<tr><td><b>L4</b> Asistente</td><td>Stepper · paso · pie con navegación</td><td>Captura de varios pasos</td><td>Pasos que no caben y se cortan por abajo</td></tr>
<tr><td><b>L5</b> Modal sobre pantalla</td><td>Pantalla base + caja centrada</td><td>Decisión breve o confirmación</td><td>Anidar modales; en 40 columnas se convierte en toda la pantalla</td></tr>
</tbody>
</table>

<h3>6.2 Los marcos: la única decoración con función</h3>
<pre class="fig">  simple            doble             banda              sin marco
 ┌──────────┐      ╔══════════╗      ┌ TÍTULO ─────┐     TÍTULO
 │          │      ║          ║      │             │     ─────────────
 └──────────┘      ╚══════════╝      └─────────────┘     contenido

  Regla: un solo estilo por pantalla. El doble marca lo activo o lo modal,
  no lo importante. Todo lo demás, simple. Y si la pantalla está apretada,
  el marco es lo primero que se quita: la banda de título basta.</pre>

<h3>6.3 Las cinco reglas de N2</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Un layout por pantalla.</b> Combinar L3 con L4 dentro de la misma vista es la forma más rápida de perder al usuario.</td></tr>
<tr><td class="sem">2</td><td><b>La barra de estado y la línea de mensajes no se mueven nunca</b>: siempre las dos últimas filas. Es el ancla espacial de la aplicación.</td></tr>
<tr><td class="sem">3</td><td><b>Los bordes se dibujan con Unicode o con ASCII, y se elige antes de empezar.</b> Media aplicación con <span class="mono">┌</span> y media con <span class="mono">+</span> parece un descuido.</td></tr>
<tr><td class="sem">4</td><td><b>El título de la caja dice qué contiene, no dónde estás.</b> «PACIENTES», no «Pantalla 2 de 5».</td></tr>
<tr><td class="sem">5</td><td><b>Al reducir el ancho, primero se estrecha el detalle, después se oculta, y solo al final se avisa.</b> Ese es el orden de prioridades del layout.</td></tr>
</tbody>
</table>
</section>
"""

n3 = """
<section>
<span class="num">07 · Núcleo N3</span>
<h2 class="sec">Jerarquía sin tipografía</h2>
<p class="lead">No hay tamaños, ni pesos finos, ni familias distintas. Quedan cinco herramientas, y con cinco se construye toda la jerarquía que hace falta.</p>

<h3>7.1 El repertorio completo</h3>
<table class="compact">
<thead><tr><th style="width:22%">Herramienta</th><th style="width:34%">Uso</th><th>Límite</th></tr></thead>
<tbody>
<tr><td><b>Mayúsculas</b></td><td>Títulos de zona y etiquetas de columna. Grita, así que se usa poco.</td><td>Un bloque de más de seis palabras en mayúsculas se lee peor que en caja baja.</td></tr>
<tr><td><b>Negrita</b></td><td>El dato, el nombre, la cifra que importa en la fila.</td><td>Si hay tres negritas en una fila, no hay ninguna.</td></tr>
<tr><td><b>Sangría (2 col.)</b></td><td>Anidamiento, jerarquía de árbol, continuación de un mensaje.</td><td>Más de tres niveles en 80 columnas es ilegible: replantea el contenido.</td></tr>
<tr><td><b>Espacio en blanco</b></td><td>Separar bloques, agrupar por proximidad.</td><td>Es la herramienta más potente y la que menos se usa.</td></tr>
<tr><td><b>Símbolos</b></td><td><span class="mono">▶</span> foco · <span class="mono">✓</span> hecho · <span class="mono">✗</span> error · <span class="mono">◆ ● ○</span> progreso · <span class="mono">▲▼</span> orden</td><td>Un símbolo por significado, y el mismo en toda la aplicación. Nunca dos símbolos para lo mismo.</td></tr>
</tbody>
</table>

<h3>7.2 El mismo dato, con y sin jerarquía</h3>
<pre class="fig"> SIN JERARQUÍA                          CON JERARQUÍA
 001 Alvarez Marta 34 insomnio activo   001  Álvarez, Marta      34  insomnio   activo
 002 Bravo Julio 51 ansiedad activo     ▶002  Bravo, Julio        51  ansiedad   activo
 003 Cano Rosa 29 duelo alta            003  Cano, Rosa          29  duelo      alta

 Lo que ha cambiado: una columna de separación, anchos fijos,
 números a la derecha, un marcador de foco. Nada más.</pre>

<h3>7.3 Las cuatro reglas de N3</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Una jerarquía de tres niveles como máximo</b>: zona, bloque, dato. Cuatro niveles en una rejilla de caracteres no se distinguen.</td></tr>
<tr><td class="sem">2</td><td><b>El énfasis se gana, no se reparte.</b> En cada fila, un solo elemento en negrita: el que el usuario viene a buscar.</td></tr>
<tr><td class="sem">3</td><td><b>La separación va antes que la decoración.</b> Antes de añadir un marco, añade una línea en blanco; casi siempre resuelve más.</td></tr>
<tr><td class="sem">4</td><td><b>Consistencia absoluta:</b> si «ERROR» va en mayúsculas en una pantalla, va en mayúsculas en todas. La inconsistencia se percibe como error aunque no lo sea.</td></tr>
</tbody>
</table>
</section>
"""

n4 = """
<section>
<span class="num">08 · Núcleo N4</span>
<h2 class="sec">Color: cuatro roles, dos estados y un plan B</h2>
<p class="lead">El color en una TUI no es decoración ni marca: es una señal de estado. Cuatro roles bastan, y todos tienen que funcionar también sin color.</p>

<h3>8.1 La paleta funcional</h3>
<table class="compact">
<thead><tr><th style="width:18%">Rol</th><th style="width:22%">Se usa para</th><th style="width:26%">Alternativa sin color</th><th>Error frecuente</th></tr></thead>
<tbody>
<tr><td><b>Fondo / neutro</b></td><td>Todo el texto normal</td><td>—</td><td>Texto gris claro «elegante» que es ilegible en un proyector</td></tr>
<tr><td><b>Acento</b></td><td>Una sola cosa: el foco, o el dato principal de la pantalla</td><td>Marcador <span class="mono">▶</span>, negrita</td><td>Usar el acento en cinco sitios: deja de señalar</td></tr>
<tr><td><b>Éxito</b></td><td>Confirmaciones y estados correctos</td><td>Palabra «OK» / «✓»</td><td>Verde para todo lo que no es un error</td></tr>
<tr><td><b>Alerta / error</b></td><td>Fallos y riesgo. El rojo se gasta poco o no significa nada</td><td>Palabra «ERROR» / «✗»</td><td>Rojo para avisos informativos</td></tr>
<tr><td><b>Estado: selección</b></td><td>La fila activa</td><td>Símbolo en el margen + negrita</td><td>Selección solo con fondo de color</td></tr>
<tr><td><b>Estado: deshabilitado</b></td><td>Lo que no está disponible ahora</td><td>Paréntesis o nota «(no disponible)»</td><td>Gris que se confunde con texto normal</td></tr>
</tbody>
</table>

<h3>8.2 Las cinco reglas de N4</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Nunca el color como única señal.</b> Cada color lleva palabra, símbolo o posición. Es el requisito de accesibilidad más importante del medio.</td></tr>
<tr><td class="sem">2</td><td><b>Contraste antes que armonía.</b> Texto sobre fondo con diferencia clara; nada de grises intermedios para información.</td></tr>
<tr><td class="sem">3</td><td><b>Funciona en 16 colores</b> aunque el terminal soporte millones. El terminal del otro no es el tuyo.</td></tr>
<tr><td class="sem">4</td><td><b>Respeta el tema del usuario</b>: no fijes fondo blanco ni negro absolutos salvo que sea imprescindible.</td></tr>
<tr><td class="sem">5</td><td><b>Pruébalo en daltonismo</b>: verde y rojo son el par que más se confunde. Si tu pantalla depende de distinguirlos, está mal diseñada.</td></tr>
</tbody>
</table>

<div class="panel-nota">Prueba de una sola línea: imprime la pantalla sin colores y pide a alguien que diga cuál es el elemento activo y cuál es el error. Si no puede, el diseño dependía del color.</div>
</section>
"""

n5 = """
<section>
<span class="num">09 · Núcleo N5</span>
<h2 class="sec">Los cinco estados de toda pantalla</h2>
<p class="lead">El caso feliz se dibuja solo. El oficio está en los otros cuatro: vacío, cargando, error y sin permiso. Son los que separan una herramienta de una demostración.</p>

<table class="compact">
<thead><tr><th style="width:16%">Estado</th><th style="width:30%">Qué ve el usuario</th><th>Qué debe poder hacer</th></tr></thead>
<tbody>
<tr><td><b>Vacío</b></td><td>Una frase que explica qué aparecerá aquí <b>y cómo llenarlo</b>: «Aún no hay registros. Crea el primero con <span class="mono">n</span>.»</td><td>La acción que lo llena, sin salir de la pantalla.</td></tr>
<tr><td><b>Cargando</b></td><td>Estructura visible (filas esqueleto o cabeceras) y un indicador discreto. Si hay datos anteriores, se muestran con su hora.</td><td>Seguir navegando por lo ya cargado; cancelar.</td></tr>
<tr><td><b>Error</b></td><td>Qué falló, de dónde venía el dato y qué se conserva: «No se pudo actualizar. Se muestran los datos de las 14:02.»</td><td>Reintentar con una tecla; seguir trabajando con lo cacheado.</td></tr>
<tr><td><b>Sin permiso</b></td><td>Que no es un fallo técnico: «Tu cuenta no tiene acceso a esta sección.»</td><td>Saber a quién pedirlo; volver.</td></tr>
<tr><td><b>Éxito</b></td><td>La pantalla con el resultado y una confirmación breve en la línea de mensajes.</td><td>Continuar; y deshacer, si la acción lo permite.</td></tr>
</tbody>
</table>

<h3>9.1 Cómo se escribe cada estado</h3>
<table class="compact">
<tbody>
<tr><td style="width:26%"><b>Vacío útil</b></td><td>Explica el futuro, no la ausencia: «Aquí aparecerán los lotes procesados» + acción. Nunca «No hay datos» a secas, y nunca una pantalla en blanco.</td></tr>
<tr><td><b>Cargando honesto</b></td><td>El indicador dura lo que dura la carga real. Si tarda más de un segundo, se añade el recuento («leyendo 40 de 218»).</td></tr>
<tr><td><b>Error accionable</b></td><td>Tres piezas: qué pasó, qué se conserva y qué tecla reintenta. Sin las tres, no es un mensaje de error: es una queja.</td></tr>
<tr><td><b>Sin permiso distinto de error</b></td><td>Mezclarlos hace que el usuario intente arreglar por su cuenta lo que solo puede arreglar un administrador.</td></tr>
<tr><td><b>Éxito breve</b></td><td>Una línea, tres segundos, sin diálogo que hay que cerrar. Los mensajes de éxito no interrumpen.</td></tr>
</tbody>
</table>

<div class="regla">Regla de los cinco estados: <b>ninguna pantalla se considera terminada hasta que existen las cinco versiones</b>. Y la prueba de fuego es el estado vacío: es el primero que ve un usuario nuevo, y el que casi nadie diseña.</div>
</section>
"""

n6 = """
<section>
<span class="num">10 · Núcleo N6</span>
<h2 class="sec">El foco: quién recibe las teclas</h2>
<p class="lead">En una interfaz sin ratón, el foco <i>es</i> el cursor del usuario. Si no se ve, la aplicación es inutilizable por muy bien dibujada que esté.</p>

<h3>10.1 Las cuatro reglas del foco</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Un solo foco, siempre visible.</b> Nunca dos elementos que parecen activos. Y visible sin color: marcador en el margen, subrayado o negrita.</td></tr>
<tr><td class="sem">2</td><td><b>El foco se conserva al cambiar de contexto.</b> Si el usuario abre un detalle y lo cierra, vuelve a la misma fila, no al principio de la lista.</td></tr>
<tr><td class="sem">3</td><td><b>Tab y Shift-Tab recorren las zonas</b> en un orden que sigue la lectura: izquierda a derecha, arriba a abajo. Nunca un orden arbitrario.</td></tr>
<tr><td class="sem">4</td><td><b>Al abrir una pantalla, el foco está donde está la tarea</b>, no en una cabecera inerte.</td></tr>
</tbody>
</table>

<h3>10.2 Cómo se ve el foco sin color</h3>
<pre class="fig">  sin foco visible          con foco en la fila 2
  001  Álvarez, Marta        001  Álvarez, Marta
  002  Bravo, Julio          ▶002  Bravo, Julio        ← marcador en el margen
  003  Cano, Rosa            003  Cano, Rosa

  Y con el foco en un campo de texto:
  Nombre   ▏Marta Álvarez      ← barra de inserción visible
  Correo   │marta@ejemplo       ← campos no activos sin barra</pre>

<h3>10.3 El error clásico: el foco fantasma</h3>
<p>Ocurre cuando se abre un diálogo y la pantalla de fondo conserva su resaltado. El usuario pulsa <span class="mono">↓</span> esperando moverse por el diálogo y mueve la lista de detrás. Solución: al activar un modo modal, el foco de fondo <b>se desactiva visualmente</b> aunque la selección se recuerde para cuando se cierre.</p>
</section>
"""

n7 = """
<section>
<span class="num">11 · Núcleo N7</span>
<h2 class="sec">El mapa de teclas</h2>
<p class="lead">Las teclas son la mitad de la interfaz. Un mapa mal elegido no se arregla con ayuda: se arregla cambiando el mapa antes de publicar.</p>

<h3>11.1 El mapa canónico</h3>
<table class="compact">
<thead><tr><th style="width:22%">Tecla</th><th style="width:34%">Significado</th><th>Nota</th></tr></thead>
<tbody>
<tr><td><span class="mono">↑ ↓ ← →</span> / <span class="mono">k j h l</span></td><td>Mover el foco</td><td>Las flechas para todos; <span class="mono">hjkl</span> como alias para expertos. Nunca solo <span class="mono">hjkl</span>.</td></tr>
<tr><td><span class="mono">Enter</span></td><td>Avanzar, abrir, confirmar</td><td>El «sí» universal. Nunca lo uses para borrar.</td></tr>
<tr><td><span class="mono">Esc</span></td><td>Volver, cerrar, cancelar</td><td>El «no» universal. Siempre disponible, en toda pantalla.</td></tr>
<tr><td><span class="mono">Tab</span> / <span class="mono">Shift-Tab</span></td><td>Cambiar de zona</td><td>Orden de lectura.</td></tr>
<tr><td><span class="mono">/</span></td><td>Buscar o filtrar</td><td>Estándar de facto: no lo cambies.</td></tr>
<tr><td><span class="mono">?</span></td><td>Ayuda con el mapa completo</td><td>Debe existir siempre y estar actualizada.</td></tr>
<tr><td><span class="mono">q</span></td><td>Salir</td><td>Con confirmación solo si hay trabajo sin guardar.</td></tr>
<tr><td><span class="mono">Ctrl-C</span></td><td>Interrumpir</td><td>Nunca lo bloquees. Si hay un proceso, pregunta y cancela limpio.</td></tr>
<tr><td><span class="mono">g</span> / <span class="mono">G</span></td><td>Ir al principio / al final</td><td>Convención heredada de <span class="mono">vi</span>, muy extendida.</td></tr>
<tr><td><span class="mono">n</span> / <span class="mono">N</span></td><td>Siguiente / anterior resultado</td><td>Solo si hay búsqueda activa; si no, no hacen nada.</td></tr>
</tbody>
</table>

<h3>11.2 Las cuatro reglas de N7</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Una tecla, un significado en toda la aplicación.</b> Si <span class="mono">d</span> borra en una pantalla, no puede duplicar en otra.</td></tr>
<tr><td class="sem">2</td><td><b>Nada imprescindible vive en una combinación con Ctrl</b>, salvo lo global (salir, buscar). Las combinaciones son para expertos, no para la tarea principal.</td></tr>
<tr><td class="sem">3</td><td><b>Nunca se cambia una tecla sin avisar</b> en el registro de cambios: las teclas son memoria muscular.</td></tr>
<tr><td class="sem">4</td><td><b>La letra de la tecla se elige por su nombre en el idioma del usuario</b>: <span class="mono">e</span> de editar, <span class="mono">b</span> de borrar, <span class="mono">f</span> de filtrar. Y se muestra siempre junto a la palabra (§12).</td></tr>
</tbody>
</table>
</section>
"""

n8 = """
<section>
<span class="num">12 · Núcleo N8</span>
<h2 class="sec">La barra de estado como contrato</h2>
<p class="lead">Es el elemento más pequeño del núcleo y el que más rendimiento da: una sola línea que dice <b>qué se puede hacer ahora mismo</b>. Sin ella, el usuario adivina.</p>

<h3>12.1 Anatomía</h3>
<pre class="fig">┌────────────────────────────────────────────────────────────────────────┐
│ ↑↓ mover  Enter abrir  / buscar  f filtrar  o ordenar  ? ayuda  q salir │
└────────────────────────────────────────────────────────────────────────┘
  tecla ─┘        └─ verbo en el mismo orden: tecla primero, acción después

┌────────────────────────────────────────────────────────────────────────┐
│ ESC cerrar   Enter guardar   Tab siguiente  Ctrl-Z deshacer             │
└────────────────────────────────────────────────────────────────────────┘
  En un formulario, la barra CAMBIA: muestra lo que funciona aquí, no el
  mapa completo. El mapa completo vive en la ayuda (?).</pre>

<h3>12.2 Las cinco reglas de N8</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Solo lo que funciona ahora.</b> Si el usuario está en un formulario, no aparecen las teclas de la tabla.</td></tr>
<tr><td class="sem">2</td><td><b>Entre cinco y siete acciones.</b> Más es un menú disfrazado; menos, en la ayuda.</td></tr>
<tr><td class="sem">3</td><td><b>Formato constante:</b> tecla, espacio, verbo en minúsculas. Alineado a la izquierda o repartido, pero siempre igual.</td></tr>
<tr><td class="sem">4</td><td><b>La tecla de salida está en el extremo derecho.</b> Es donde la busca el ojo cuando alguien se atasca.</td></tr>
<tr><td class="sem">5</td><td><b>Si algo está bloqueado, se dice por qué</b>: «Enter guardar (faltan 2 campos)». Ese paréntesis evita la mitad de los atascos.</td></tr>
</tbody>
</table>

<div class="box">
<div class="box-t">La prueba del contrato</div>
<p style="margin-bottom:0">Tapa el resto de la pantalla y deja solo la barra de estado: un usuario nuevo debe poder saber <b>qué puede hacer</b> en esa pantalla. Si no puede, la barra es un adorno y las teclas son un secreto.</p>
</div>
</section>
"""

n9 = """
<section>
<span class="num">13 · Núcleo N9</span>
<h2 class="sec">La línea de mensajes: errores, avisos y confirmaciones</h2>
<p class="lead">Todo lo que la aplicación tiene que decir al usuario pasa por una sola línea. Es poco sitio y por eso obliga a escribir bien: es el mejor corrector de estilo que existe.</p>

<h3>13.1 La plantilla de tres partes</h3>
<table class="compact">
<thead><tr><th style="width:18%">Parte</th><th style="width:34%">Qué dice</th><th>Ejemplo</th></tr></thead>
<tbody>
<tr><td><b>Qué pasó</b></td><td>El hecho, en presente y sin tecnicismos</td><td>«No se pudo guardar el registro.»</td></tr>
<tr><td><b>Qué se conserva</b></td><td>Lo que no se ha perdido (si hay algo)</td><td>«Los datos siguen en el formulario.»</td></tr>
<tr><td><b>Qué hacer</b></td><td>La tecla o el paso concreto</td><td>«Pulsa <span class="mono">r</span> para reintentar.»</td></tr>
</tbody>
</table>

<h3>13.2 Cómo se escriben los mensajes</h3>
<table class="compact">
<tbody>
<tr><td style="width:34%"><b class="no">Mal</b></td><td><b class="si">Bien</b></td></tr>
<tr><td>«Error 500»</td><td>«No se pudo leer la lista (fallo del servidor). Pulsa r para reintentar.»</td></tr>
<tr><td>«¿Estás seguro?»</td><td>«Se van a borrar 3 registros. Escribe "borrar" para confirmar.»</td></tr>
<tr><td>«Operación completada»</td><td>«218 registros importados. 3 omitidos por falta de nombre.»</td></tr>
<tr><td>«No hay datos»</td><td>«Aún no hay registros. Pulsa n para crear el primero.»</td></tr>
<tr><td>«Campo inválido»</td><td>«El correo necesita un dominio después de la arroba.»</td></tr>
</tbody>
</table>

<h3>13.3 Las cinco reglas de N9</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Una línea, o dos como máximo.</b> Si necesita más, es un diálogo o una pantalla, no un mensaje.</td></tr>
<tr><td style="sem">2</td><td><b>Los mensajes se borran solos</b> a los pocos segundos, salvo los errores, que se quedan hasta que se resuelven o se descartan con Esc.</td></tr>
<tr><td style="sem">3</td><td><b>Nunca se culpa al usuario</b>: se describe el hecho y la salida. «Falta el dominio» es un dato; «has escrito mal el correo» es una acusación.</td></tr>
<tr><td class="sem">4</td><td><b>Las confirmaciones no interrumpen</b>: van a la línea de mensajes, no a un diálogo.</td></tr>
<tr><td class="sem">5</td><td><b>El tono es constante</b>: sin exclamaciones, sin humor, sin emojis. La herramienta no es tu amiga; es una herramienta.</td></tr>
</tbody>
</table>
</section>
"""

n10 = """
<section>
<span class="num">14 · Núcleo N10</span>
<h2 class="sec">Densidad, ritmo y números (y la accesibilidad como cierre)</h2>
<p class="lead">Las nueve piezas anteriores describen lo que se ve; esta describe <b>cuánto</b> se ve. La densidad es la decisión que más cambia la sensación de una TUI y la que menos se piensa.</p>

<h3>14.1 El ritmo de la pantalla</h3>
<table class="compact">
<tbody>
<tr><td style="width:32%"><b>Grupos de 5 a 9 elementos</b></td><td>La vista agrupa por proximidad. Un listado de veinte filas se lee como un bloque; se le añaden separadores cada cinco o siete.</td></tr>
<tr><td><b>Una línea en blanco</b></td><td>Entre bloques lógicos. Nunca dos: dos líneas en blanco no separan más, solo gastan.</td></tr>
<tr><td><b>Densidad alta con descanso</b></td><td>Se puede ser denso si hay jerarquía y espacio en los bordes. Lo que cansa no es la densidad: es la ausencia de jerarquía.</td></tr>
<tr><td><b>Repetición exacta</b></td><td>Cada fila del mismo tipo tiene exactamente el mismo formato. La consistencia ahorra la mitad del esfuerzo de lectura.</td></tr>
</tbody>
</table>

<h3>14.2 Los números, que son la mitad del contenido</h3>
<table class="compact">
<tbody>
<tr><td style="width:32%"><b>Alineados a la derecha</b></td><td>Y con los decimales en la misma posición: <span class="mono">1.284,50</span> sobre <span class="mono">96,00</span> alinea las comas y permite comparar de un vistazo.</td></tr>
<tr><td><b>Unidad siempre visible</b></td><td>«312 ms», «68 %», «12 GB». Un número sin unidad no es un dato: es un misterio.</td></tr>
<tr><td><b>Tres cifras significativas</b></td><td>«1.284» antes que «1.283,7»; «0,8 %» antes que «0,7843 %». La precisión falsa es ruido.</td></tr>
<tr><td><b>Comparación junto al número</b></td><td>«+6 %», «de 20», «▲». Un número aislado no dice si hay que preocuparse.</td></tr>
</tbody>
</table>

<h3>14.3 Accesibilidad y degradación: el cierre del núcleo</h3>
<table class="compact">
<thead><tr><th style="width:26%">Condición</th><th>Qué se garantiza</th></tr></thead>
<tbody>
<tr><td><b>Sin color</b></td><td>Todo estado tiene palabra o símbolo. Probado con <span class="mono">NO_COLOR=1</span>.</td></tr>
<tr><td><b>Sin Unicode</b></td><td>Juego alternativo ASCII (<span class="mono">+ - |</span>). Detectado o seleccionable a mano.</td></tr>
<tr><td><b>40 columnas</b></td><td>Una columna de contenido, detalle a pantalla completa, barra reducida a cinco teclas.</td></tr>
<tr><td><b>Lector de pantalla</b></td><td>Orden de lectura lógico; sin depender de la posición del cursor para transmitir información.</td></tr>
<tr><td><b>Teclado solo</b></td><td>Toda acción alcanzable; ninguna exclusiva del ratón.</td></tr>
<tr><td><b>Terminal tonta</b> (<span class="mono">TERM=dumb</span>)</td><td>Modo sin pantalla interactiva: imprime y sale, o avisa de que no puede funcionar.</td></tr>
</tbody>
</table>

<p class="nota-txt" style="margin-top:2mm">Con esto queda cerrado el núcleo: nueve piezas y una regla de densidad. A partir de aquí, <b>cada patrón de la parte III solo añade una cosa</b>; si un patrón necesita más de una, está mal descompuesto.</p>
</section>
"""

parte2 += n1 + n2 + n3 + n4 + n5 + n6 + n7 + n8 + n9 + n10

TOC = [
    ("Parte 0", [("00", "Cómo está organizado el pack", "p00")]),
    ("Parte I · Idealizar", [("01", "Qué es (y qué no es) una TUI", "p01"),
                             ("02", "Cuándo una TUI es la respuesta correcta", "p02"),
                             ("03", "Los cinco géneros y cómo elegir", "p03"),
                             ("04", "El contrato antes del boceto", "p04")]),
    ("Parte II · El núcleo", [("05", "N1 · La celda y la rejilla", "p05"),
                              ("06", "N2 · Marcos, bandas y layouts", "p06"),
                              ("07", "N3 · Jerarquía sin tipografía", "p07"),
                              ("08", "N4 · Color: roles y estados", "p08"),
                              ("09", "N5 · Los cinco estados", "p09"),
                              ("10", "N6 · El foco", "p10"),
                              ("11", "N7 · El mapa de teclas", "p11"),
                              ("12", "N8 · La barra de estado", "p12"),
                              ("13", "N9 · La línea de mensajes", "p13"),
                              ("14", "Densidad, números y accesibilidad", "p14")]),
    ("Parte III · Particularidades", [("15", "P1 · Panel de estado", "p15"),
                                      ("16", "P2 · Tabla y explorador", "p16"),
                                      ("17", "P3 · Formulario y validación", "p17"),
                                      ("18", "P4 · Asistente por pasos", "p18"),
                                      ("19", "P5 · Cola de trabajo y progreso", "p19"),
                                      ("20", "P6 · Diálogos y paleta de comandos", "p20"),
                                      ("21", "P7 · Registro y visor de eventos", "p21")]),
    ("Parte IV · Implementar", [("22", "Estado, render, entrada", "p22"),
                                ("23", "Cuatro sustratos, del ANSI al framework", "p23"),
                                ("24", "Rendimiento y límites reales", "p24"),
                                ("25", "Pruebas y calidad", "p25"),
                                ("26", "Entregar y mantener", "p26")]),
    ("Parte V · Síntesis", [("27", "Las dieciséis reglas nucleares", "p27"),
                            ("28", "Seis ejercicios con rúbrica", "p28"),
                            ("29", "Glosario y para seguir", "p29")]),
]


def build_index():
    """Índice imprimible en dos columnas, generado del mismo TOC que la navegación."""
    grupos = [(g, items) for g, items in TOC]
    mitad = 3
    cols = [grupos[:mitad], grupos[mitad:]]

    def render(grupo_items):
        out = []
        for grupo, items in grupo_items:
            out.append(f'<div class="g">{grupo}</div>')
            for num, titulo, _ in items:
                out.append(f'<div class="e"><span>{num}</span>{titulo}</div>')
        return "".join(out)

    return f"""
<section class="page print-only">
<span class="num">Índice</span>
<h2 class="sec">Contenido del pack</h2>
<div class="ix"><div>{render(cols[0])}</div><div>{render(cols[1])}</div></div>
<h3>Cómo se usa el pack</h3>
<table class="compact">
<tbody>
<tr><td style="width:30%"><b>Si vas a empezar un proyecto</b></td><td>Parte I completa, §27 (las dieciséis reglas) y §28 (ejercicios). El núcleo se consulta mientras se construye.</td></tr>
<tr><td><b>Si ya tienes una pantalla y no sabes por qué no funciona</b></td><td>Ve directo al patrón correspondiente en la parte III y a su ficha de composición.</td></tr>
<tr><td><b>Si vienes de programar y quieres criterio</b></td><td>Parte II completa antes de escribir una línea. Es donde está el 80 % del oficio.</td></tr>
<tr><td><b>Si vienes de UX gráfica</b></td><td>§05, §07 y §08 primero: son las tres piezas donde este medio rompe tus hábitos.</td></tr>
</tbody>
</table>

<div class="regla">Regla de lectura: nada de la parte II es opcional. Todo lo de la parte III es <b>consecuencia</b>. Si intentas aprender la parte III sin la II, acabarás copiando pantallas sin entender por qué funcionan, que es exactamente lo que produce las herramientas de terminal feas.</div>

<p class="nota-txt" style="margin-top:6mm">Treinta capítulos en cinco partes. El núcleo (parte II) se lee completo antes de tocar la parte III: los patrones son combinaciones de esas nueve piezas.</p>
</section>
"""


def build_toc():
    out = ['<nav class="tocnav"><div class="toc">']
    for grupo, items in TOC:
        out.append(f'<div class="g">{grupo}</div>')
        for num, titulo, anchor in items:
            out.append(f'<a href="#{anchor}"><span>{num}</span>{titulo}</a>')
    out.append("</div></nav>")
    return "".join(out)


def add_ids(html):
    """Añade anclas a cada section en el orden del índice."""
    anchors = [a for _, items in TOC for _, _, a in items]
    partes = html.split("<section")
    out = [partes[0]]
    i = 0
    for chunk in partes[1:]:
        if i < len(anchors):
            head, sep, rest = chunk.partition(">")
            if 'class="parte"' in head:
                out.append("<section" + chunk)
            else:
                out.append(f'<section id="{anchors[i]}"' + chunk)
                i += 1
        else:
            out.append("<section" + chunk)
    return "".join(out)


def main():
    body = add_ids(portada + build_index() + mapa + parte1 + parte2 + PARTS_B)
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Interfaces de terminal — pack educativo</title>
<style>{CSS}</style></head><body>
<div class="wrap">{build_toc()}{body}</div></body></html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT + ".html", "w", encoding="utf-8").write(html)
    print("HTML:", len(html))
    from weasyprint import HTML
    HTML(string=html, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf(OUT + ".pdf")
    print("PDF listo")


if __name__ == "__main__":
    main()
