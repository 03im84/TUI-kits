# -*- coding: utf-8 -*-
"""Pack educativo TUI — Parte III (patrones), IV (implementación) y V (síntesis)."""

FIG_FICHA = """
<table class="ficha">
<thead><tr><th style="width:26%">Ficha de composición</th><th>Contenido</th></tr></thead>
<tbody>
<tr><td><b>Reutiliza del núcleo</b></td><td>{reutiliza}</td></tr>
<tr><td><b>Lo que añade</b></td><td>{anade}</td></tr>
<tr><td><b>Teclas nuevas</b></td><td>{teclas}</td></tr>
<tr><td><b>Estados obligatorios</b></td><td>{estados}</td></tr>
<tr><td><b>Su límite</b></td><td>{limite}</td></tr>
</tbody>
</table>
"""


def ficha(reutiliza, anade, teclas, estados, limite):
    return FIG_FICHA.format(reutiliza=reutiliza, anade=anade, teclas=teclas,
                            estados=estados, limite=limite)


parte3 = """
<section class="parte">
<span class="num">Parte III</span>
<h2 class="sec">Las particularidades: siete patrones de pantalla</h2>
<p class="lead">Un patrón no es un diseño nuevo: es una <b>composición</b> de piezas del núcleo con un añadido pequeño y propio. Si al leer un patrón no reconoces de dónde viene cada parte, no lo has entendido todavía.</p>

<div class="box">
<div class="box-t">Cómo se lee cada patrón</div>
<p>Siempre igual, en cinco líneas: <b>cuándo se usa</b> (y cuándo no), <b>anatomía</b> con un boceto, <b>reglas</b> que no se negocian, <b>ficha de composición</b> —qué reutiliza del núcleo, qué añade, qué teclas estrena, qué estados necesita y dónde está su límite— y <b>los tres errores</b> que se cometen siempre con ese patrón.
Los siete patrones cubren, sumados, casi cualquier herramienta de terminal que vayas a necesitar: panel, tabla, formulario, asistente, proceso por lotes, diálogo y visor de registros.</p>
</div>
</section>
"""

p1 = """
<section>
<span class="num">15 · Patrón P1</span>
<h2 class="sec">Panel de estado</h2>
<p class="lead">Una pantalla que responde a «¿cómo está esto?» en menos de tres segundos, sin que el usuario tenga que hacer nada.</p>

<h3>15.1 Cuándo se usa (y cuándo no)</h3>
<table class="compact">
<tbody>
<tr><td style="width:33%"><b>Se usa</b></td><td>Cuando hay entre cuatro y nueve cifras que se miran a diario, cuando el valor está en detectar lo anómalo, cuando el usuario es el mismo todos los días y ya sabe leer la pantalla.</td></tr>
<tr><td><b class="no">No se usa</b></td><td>Si hay que actuar sobre registros concretos —eso es una tabla—, si hay más de nueve métricas (entonces hay una jerarquía mal hecha, no un panel), o si el usuario es ocasional: un panel que hay que interpretar es una tabla mal diseñada.</td></tr>
</tbody>
</table>

<h3>15.2 Anatomía</h3>
<pre class="fig">┌ SERVICIO · api-interno ─────────────────────────────── última: 14:02:11 ┐
│                                                                        │
│  PETICIONES / MIN        LATENCIA P95         ERRORES 5 MIN            │
│        1.284                  312 ms              0.8 %               │
│        ▲ +6 % vs ayer         ▁▂▃▅▂▁▂▃            ▲ +0.2                │
│                                                                        │
│  COLA DE TRABAJO         DISCO                  CERTIFICADO            │
│        37 pendientes         68 % usado          caduca en 12 d        │
│        ████████░░░░ 8/20     12 GB libres        [renovar]             │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ r refrescar   Enter detalle   f periodo   ? ayuda   q salir            │
└────────────────────────────────────────────────────────────────────────┘</pre>

<h3>15.3 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Una cifra por tarjeta, y su unidad siempre visible.</b> «312» no dice nada; «312 ms» sí. La unidad no se abrevia hasta perder significado.</td></tr>
<tr><td class="sem">2</td><td><b>Cada cifra lleva comparación.</b> Un número sin referencia no es información: «+6 % vs ayer», «de 20», «▲». Sin comparación, el usuario no sabe si preocuparse.</td></tr>
<tr><td class="sem">3</td><td><b>Mismo ancho y misma retícula para todas las tarjetas.</b> Tres columnas iguales, no anchos «según el contenido». La comparación visual se hace por posición.</td></tr>
<tr><td class="sem">4</td><td><b>Lo más importante, arriba a la izquierda</b>, porque es donde cae la mirada primero y donde no hay nada más que leer.</td></tr>
<tr><td class="sem">5</td><td><b>Marca de tiempo de los datos, siempre.</b> Un panel sin hora miente por omisión: el usuario cree estar viendo el presente.</td></tr>
<tr><td class="sem">6</td><td><b>Si el dato es viejo, se dice.</b> «última: hace 40 min» en ámbar junto al bloque afectado. Es la diferencia entre un panel y una ilusión.</td></tr>
</tbody>
</table>

""" + ficha(
    "N1 rejilla · N3 jerarquía · N4 roles de color · N5 estados · N8 barra de estado · L1 layout de tres bandas",
    "La <b>retícula de tarjetas</b> y la regla de comparación por posición. El bloque de tendencia opcional (una línea de ▁▂▃).",
    "r refrescar · f cambiar periodo · Enter abrir el detalle de la tarjeta activa",
    "Vacío (sin datos aún: explica qué se medirá) · cargando (mantiene la última cifra y su hora) · error (conserva lo viejo, marcado) · éxito (por defecto)",
    "No sirve para series largas ni para actuar sobre elementos. Con más de nueve métricas deja de ser panel y pasa a ser una tabla con filtros.") + """

<h3>15.4 Los tres errores de siempre</h3>
<div class="cols2">
<div><b>1. Decorar antes de informar.</b> Marcos dobles, colores vivos y un logo de tres líneas: el 40 % de la pantalla gasta en estética y queda sitio para cuatro cifras.</div>
<div><b>2. Cifras sin comparación.</b> «Usuarios: 8.412» no dice si es bueno. Con «+12 % esta semana» se convierte en información.</div>
<div><b>3. Refrescar sin avisar.</b> La pantalla cambia bajo los ojos mientras el usuario lee. Se marca la actualización y se evita mover lo que no ha cambiado.</div>
</div>
</section>
"""

p2 = """
<section>
<span class="num">16 · Patrón P2</span>
<h2 class="sec">Tabla y explorador de datos</h2>
<p class="lead">El patrón más usado y el que más se estropea: una lista de elementos con un detalle al lado, filtro, orden y una fila que siempre está activa.</p>

<h3>16.1 Cuándo se usa</h3>
<p>Cuando el usuario tiene que <b>encontrar uno entre muchos</b> y después hacer algo con él. Si siempre es el mismo elemento, no hace falta tabla; si hay que mirar veinte a la vez para comparar, probablemente sea un panel. Si la acción es sobre un solo elemento y siempre igual, quizá baste una lista simple con Enter.</p>

<h3>16.2 Anatomía: tres zonas y una fila activa</h3>
<pre class="fig">┌ PACIENTES ── /ins · 12 resultados ──────────────────────────────────────┐
│ ID    NOMBRE              EDAD   MOTIVO            ESTADO     ÚLTIMA    │
│ 001   Álvarez, Marta        34   insomnio          activo     04 nov    │
│▶002   Bravo, Julio          51   ansiedad          activo     06 nov    │
│ 003   Cano, Rosa            29   duelo             alta       12 oct    │
│ 004   Díaz, Andrés          47   insomnio          en espera  30 oct    │
│ ...                                                                     │
├───────────────────────────────────┬─────────────────────────────────────┤
│ 12 registros · orden: última ▼    │ FICHA 002 · Bravo, Julio            │
│ filtro: insomnio                  │ Edad 51 · derivado por su médico    │
│                                   │ [e] editar  [d] borrar  [Enter] ver │
├───────────────────────────────────┴─────────────────────────────────────┤
│ / buscar  ↑↓ mover  o ordenar  f filtrar  Enter abrir  ? ayuda  q salir │
└─────────────────────────────────────────────────────────────────────────┘</pre>

<h3>16.3 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Seis columnas visibles como máximo.</b> Si necesitas más, el detalle es el sitio para el resto. Cada columna que se añade resta un 10 % de legibilidad a todas las demás.</td></tr>
<tr><td class="sem">2</td><td><b>La primera columna es el identificador</b> y siempre está: corto, único, estable. Es a lo que el usuario se referirá al hablar de la fila.</td></tr>
<tr><td class="sem">3</td><td><b>Los números se alinean a la derecha, el texto a la izquierda.</b> Es la única forma de comparar 1.284 con 96 sin leer dígito a dígito.</td></tr>
<tr><td class="sem">4</td><td><b>La fila activa se marca con un símbolo además del color</b> (<span class="mono">▶</span> en el margen). Sin color, sin señalar: quien no distingue el resaltado pierde el cursor de la interfaz.</td></tr>
<tr><td class="sem">5</td><td><b>Se trunca con puntos suspensivos, no se parte la palabra</b> ni se deja que empuje la columna siguiente. El ancho de cada columna se decide en el diseño, no por el dato más largo.</td></tr>
<tr><td class="sem">6</td><td><b>Contador siempre visible:</b> «12 resultados». Es lo que evita la pregunta «¿y esto es todo?».</td></tr>
<tr><td class="sem">7</td><td><b>El filtro se ve.</b> Un filtro aplicado y no mostrado es la primera causa de «faltan datos» en una herramienta interna.</td></tr>
</tbody>
</table>

""" + ficha(
    "N1 rejilla · N2 marcos y bandas · N4 color (estado y selección) · N5 estados · N6 foco · N7 teclas · N8 barra de estado · L3 master-detail",
    "El <b>modelo de columnas</b> (ancho, tipo, alineación, orden) y el ciclo de filtro. Es el añadido más pequeño de todos los patrones y el más rentable.",
    "/ buscar · f filtrar · o ordenar · Espacio seleccionar · * seleccionar todo · Enter abrir · g/G ir a principio/final · n/N siguiente/anterior resultado",
    "Vacío (<b>con la acción que lo llena</b>: «crea el primer registro con n») · filtro sin resultados («quitar filtro con Esc») · cargando (filas esqueleto) · error de lectura (mantener lo cacheado y avisar) · éxito",
    "Por encima de unos cientos de filas sin virtualización se nota el tirón; con miles hay que paginar o virtualizar. Y no es un editor: si hay que cambiar muchas celdas, es otro patrón.") + """

<h3>16.4 Los tres errores de siempre</h3>
<div class="cols2">
<div><b>1. Selección invisible al perder el foco.</b> El usuario abre un diálogo y ya no sabe qué fila estaba activa. La fila activa conserva su marca aunque el foco esté en otro sitio.</div>
<div><b>2. Ordenar por la columna equivocada.</b> Se ordena por la fecha mostrada en formato «04 nov» y no por la fecha real. Se ordena siempre por el dato, nunca por su representación.</div>
<div><b>3. Barra de estado que no cambia.</b> La barra muestra todas las teclas siempre. Debe mostrar solo las que funcionan <i>ahora</i>.</div>
</div>
</section>
"""

p3 = """
<section>
<span class="num">17 · Patrón P3</span>
<h2 class="sec">Formulario y validación</h2>
<p class="lead">Aquí se pierde más tiempo que en ningún otro patrón: no por escribir, sino por corregir errores que la interfaz pudo evitar.</p>

<h3>17.1 Anatomía</h3>
<pre class="fig">┌ NUEVO REGISTRO ─────────────────────────────────────────────────────────┐
│                                                                        │
│  Nombre *      ▏Marta Álvarez Ruiz                                     │
│                                                                        │
│  Edad *        ▏34                                                     │
│                entre 18 y 99                                           │
│                                                                        │
│  Motivo        ▏insomnio                                               │
│                ┌──────────────────────────────┐                        │
│                │ insomnio                     │ ← sugerencias          │
│                │ insomnio crónico             │                        │
│                │ insomnio de conciliación     │                        │
│                └──────────────────────────────┘                        │
│                                                                        │
│  Correo        ▏marta@ejemplo                                          │
│                ✗ falta el dominio después de la arroba                 │
│                                                                        │
│  * obligatorio                                                         │
├────────────────────────────────────────────────────────────────────────┤
│ Tab siguiente  Shift-Tab anterior  Enter guardar  Esc cancelar         │
└────────────────────────────────────────────────────────────────────────┘</pre>

<h3>17.2 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Validar al salir del campo, no al teclear.</b> Corregir mientras se escribe es una forma elegante de insultar al usuario. La excepción son los contadores («23/200»).</td></tr>
<tr><td class="sem">2</td><td><b>El error va pegado al campo</b>, debajo, con una marca (<span class="mono">✗</span>) y una frase que diga <b>cómo arreglarlo</b>: «falta el dominio después de la arroba», no «correo no válido».</td></tr>
<tr><td class="sem">3</td><td><b>Nunca se borra lo escrito.</b> Jamás. Ni al fallar, ni al cambiar de paso, ni al irse y volver.</td></tr>
<tr><td class="sem">4</td><td><b>El ancho del campo insinúa el contenido</b>: edad estrecha, correo ancho. Un campo de 40 columnas para un año es una promesa falsa.</td></tr>
<tr><td class="sem">5</td><td><b>Enter guarda y Esc cancela</b>, siempre, en toda la aplicación. Si en esta pantalla Enter significa otra cosa, hay que decirlo en la barra.</td></tr>
<tr><td class="sem">6</td><td><b>Al guardar, se bloquea y se dice qué está pasando</b>: «guardando…». Un campo que acepta más escritura mientras guarda produce duplicados.</td></tr>
<tr><td class="sem">7</td><td><b>Cancelar con cambios pide confirmación; salir sin cambios, no.</b> La confirmación se gasta solo en lo que se pierde.</td></tr>
</tbody>
</table>

""" + ficha(
    "N1 rejilla · N3 jerarquía · N4 color (error y foco) · N5 estados · N6 foco · N7 teclas (Tab/Shift-Tab) · N9 línea de mensajes",
    "El <b>modelo de campo</b> (etiqueta, tipo, ancho, obligatoriedad, ayuda, validador) y la lista de sugerencias.",
    "Tab / Shift-Tab navegar · Enter guardar · Esc cancelar · Ctrl-Z deshacer en el campo",
    "Vacío (valores por defecto razonables) · editando · error por campo · error global (arriba, si hay varios) · guardando · guardado (mensaje de confirmación breve)",
    "Con más de siete u ocho campos en pantallas de 24 filas no cabe: hay que pasar a P4 (asistente por pasos). Y si el formulario es de texto largo, se abre en <span class='mono'>$EDITOR</span>.") + """
</section>
"""

p4 = """
<section>
<span class="num">18 · Patrón P4</span>
<h2 class="sec">Asistente por pasos</h2>
<p class="lead">Un formulario largo convertido en una conversación corta. Su valor no está en dividir, sino en <b>decidir por el usuario</b> lo que no necesita decidir.</p>

<h3>18.1 Anatomía</h3>
<pre class="fig">┌ IMPORTAR PACIENTES ─────────────────────────────────────────────────────┐
│                                                                        │
│   (1) Origen  ────  (2) Columnas  ────  (3) Revisión  ────  (4) Listo   │
│        ✓               ✓                 ●                             │
│   ───────────────────────────────────────────────────────────────────  │
│                                                                        │
│   PASO 3 DE 4 · Revisión                                                │
│                                                                        │
│   Se importarán 218 registros.                                          │
│   3 filas se descartarán por falta de nombre.                           │
│   ─────────────────────────────────────────────────────────────────    │
│   001  Álvarez, Marta      34   insomnio                                │
│   002  Bravo, Julio        51   ansiedad                                │
│   003  Cano, Rosa          29   duelo                                   │
│                                                                        │
│   ¿Qué quieres hacer con las 3 filas incompletas?                       │
│   ▸ omitirlas          guardarlas para revisar          cancelar todo   │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ Enter continuar  ← atrás  g guardar borrador  Esc salir  ? ayuda        │
└────────────────────────────────────────────────────────────────────────┘</pre>

<h3>18.2 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Cinco pasos como máximo</b>, y cada paso responde una sola pregunta. Si un paso tiene dos decisiones, son dos pasos.</td></tr>
<tr><td class="sem">2</td><td><b>El paso actual se ve, y también lo ya hecho</b> (✓ en los completados). El usuario tiene que saber cuánto falta para decidir si sigue.</td></tr>
<tr><td class="sem">3</td><td><b>Volver atrás no pierde nada.</b> Nunca. Y el paso final es un <b>resumen editable</b>: es la última red antes del desastre.</td></tr>
<tr><td class="sem">4</td><td><b>Se puede salir y reanudar.</b> Borrador guardado con <span class="mono">g</span> y recuperado al volver. Un asistente que se pierde a mitad es un asistente que nadie usa dos veces.</td></tr>
<tr><td class="sem">5</td><td><b>Los valores por defecto hacen el 80 % del trabajo.</b> El mejor paso es el que no aparece porque había una opción evidente ya marcada.</td></tr>
</tbody>
</table>

""" + ficha(
    "N1 rejilla · N2 marcos · N3 jerarquía · N5 estados · N6 foco · N7 teclas · N8 barra de estado",
    "El <b>stepper</b> (indicador de pasos), la validación por paso y el borrador persistente.",
    "Enter siguiente · ← atrás · g guardar borrador · s saltar el paso (si es opcional)",
    "Borrador pendiente al abrir · validación fallida en el paso · revisión final · proceso en curso (tras confirmar) · resultado con recuento (importados / descartados)",
    "No sirve para tareas diarias repetidas: si alguien hace esto cinco veces al día, un asistente de cuatro pasos es fricción pura. Para eso, formulario único con opciones recordadas.") + """
</section>
"""

p5 = """
<section>
<span class="num">19 · Patrón P5</span>
<h2 class="sec">Cola de trabajo y progreso</h2>
<p class="lead">Lo que el usuario no ve, no existe; y si lo ve mal, no se fía. El problema no es dibujar una barra, es <b>decir la verdad sobre el tiempo</b>.</p>

<h3>19.1 Anatomía</h3>
<pre class="fig">┌ PROCESAR LOTES ─────────────────────────────────────────────────────────┐
│ Progreso global  ███████████████░░░░░░░░░░░░  62 %  ·  quedan ~1 min 40 │
│ 218 de 351 · 4 con error                                                │
│                                                                        │
│ ESTADO    ARCHIVO                 TAMAÑO    TIEMPO    RESULTADO         │
│ hecho     lote-001.csv             2.1 MB     0.4 s   218 filas         │
│ hecho     lote-002.csv             1.9 MB     0.5 s   351 filas         │
│ en curso  lote-003.csv             2.4 MB      ----    leyendo…         │
│ pendiente lote-004.csv             2.0 MB               -               │
│ error     lote-005.csv             0.9 MB     0.2 s   ✗ línea 42: sin ID│
│ ...                                                                     │
├────────────────────────────────────────────────────────────────────────┤
│ p pausar  c cancelar  e reintentar errores  l ver registro  q salir     │
└────────────────────────────────────────────────────────────────────────┘</pre>

<h3>19.2 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>El progreso es monótono y honesto.</b> Nunca vuelve atrás, nunca se queda en 99 % dos minutos. Si no se puede calcular, se muestra el recuento («218 de 351») y no un porcentaje inventado.</td></tr>
<tr><td class="sem">2</td><td><b>El tiempo restante solo se muestra si es fiable</b> —tamaños homogéneos, ritmo estable—. Un «quedan 2 s» que se convierte en tres minutos destruye la confianza más que no dar estimación.</td></tr>
<tr><td class="sem">3</td><td><b>Cada elemento tiene su estado visible</b>: pendiente, en curso, hecho, error. La barra global sin detalle no permite saber qué falló.</td></tr>
<tr><td class="sem">4</td><td><b>Cancelar funciona de verdad y dice qué pasó</b> con lo ya procesado: «se canceló tras 218 de 351; lo procesado se conserva».</td></tr>
<tr><td class="sem">5</td><td><b>Los errores no se pierden al terminar:</b> quedan en una lista final con su acción de reintento. Un proceso que acaba «con 4 errores» y sin decir cuáles es un proceso roto.</td></tr>
<tr><td class="sem">6</td><td><b>La interfaz no secuestra la terminal:</b> Ctrl-C siempre responde, y el proceso deja un registro en un archivo para poder mirarlo después.</td></tr>
</tbody>
</table>

""" + ficha(
    "N1 rejilla · N4 color por estado · N5 estados ampliados (4 + error por elemento) · N8 barra de estado · L3 master-detail",
    "El <b>modelo de elemento</b> con su estado propio, el recuento global y la política de refresco (una actualización por segundo, no por evento).",
    "p pausar · c cancelar · e reintentar solo los errores · l abrir el registro completo",
    "Sin trabajo en cola (vacío) · en curso · pausado · cancelado · terminado con errores · terminado limpio",
    "En terminales remotas, repintar toda la tabla en cada evento satura la conexión: se refresca el conjunto como mucho una vez por segundo y se escribe solo lo que cambió (§24).") + """
</section>
"""

p6 = """
<section>
<span class="num">20 · Patrón P6</span>
<h2 class="sec">Diálogos, menús y paleta de comandos</h2>
<p class="lead">Todo lo que interrumpe. Bien usado, protege; mal usado, es la razón por la que la gente odia las interfaces de texto.</p>

<h3>20.1 Los tres tipos y cuándo usar cada uno</h3>
<table class="compact">
<thead><tr><th style="width:22%">Tipo</th><th style="width:32%">Para qué</th><th>Regla</th></tr></thead>
<tbody>
<tr><td><b>Confirmación</b></td><td>Acción destructiva o irreversible</td><td>Solo entonces. Se nombra el objeto y la cantidad: «borrar 3 registros», no «¿estás seguro?». La acción destructiva nunca es la opción por defecto.</td></tr>
<tr><td><b>Diálogo de acción breve</b></td><td>Pedir un dato sin salir de la pantalla (renombrar, mover)</td><td>Un campo, dos botones, Esc cancela. Si necesita dos campos, casi siempre es mejor un formulario completo.</td></tr>
<tr><td><b>Paleta de comandos</b></td><td>Funciones que se usan poco y no caben en la barra</td><td>Se abre con <span class="mono">Ctrl-K</span> o <span class="mono">:</span>, busca por nombre y muestra la tecla de cada comando. Sustituye a los menús largos.</td></tr>
</tbody>
</table>

<h3>20.2 Anatomía</h3>
<pre class="fig">        ┌ BORRAR REGISTROS ──────────────────────────────┐
        │                                                │
        │  Se van a borrar 3 registros seleccionados.     │
        │  Esta acción no se puede deshacer.              │
        │                                                │
        │  Escribe  borrar  para confirmar:               │
        │  ▏                                              │
        │                                                │
        │        [ cancelar ]            ( borrar )       │
        └────────────────────────────────────────────────┘

┌ PALETA DE COMANDOS ─────────────────────────── Ctrl-K ─┐
│ ▏exp                                                    │
│  exportar csv                    Ctrl-E                 │
│  exportar json                   Ctrl-J                 │
│  expandir todo                   z                      │
└─────────────────────────────────────────────────────────┘</pre>

<h3>20.3 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>Esc cierra siempre</b>, desde cualquier diálogo, y no ejecuta nada.</td></tr>
<tr><td class="sem">2</td><td><b>No se anidan diálogos.</b> Si aparece un error mientras hay una confirmación abierta, el error va a la línea de mensajes, no encima.</td></tr>
<tr><td class="sem">3</td><td><b>El foco inicial no está en la acción destructiva.</b> Empieza en «cancelar» o en el campo vacío.</td></tr>
<tr><td class="sem">4</td><td><b>Se dice qué se va a hacer y a cuántos.</b> La cantidad es información, no adorno.</td></tr>
<tr><td class="sem">5</td><td><b>En 40 columnas, el diálogo mínimo ocupa toda la pantalla.</b> Se diseña para que quepa en 36 columnas o se degrada conscientemente a pantalla completa.</td></tr>
</tbody>
</table>

""" + ficha(
    "N2 marcos (borde con título) · N4 color (destructivo) · N6 foco (modal) · N7 teclas (Esc, Ctrl-K) · N9 línea de mensajes",
    "El <b>bloqueo modal</b> del resto de la pantalla y el componente de búsqueda incremental.",
    "Esc cerrar · Enter confirmar · Ctrl-K abrir paleta · Tab alternar botones",
    "Diálogo abierto sobre pantalla con selección previa · campo de confirmación vacío · error de validación de la confirmación",
    "No es sitio para información: si hay que leer más de cuatro líneas, no es un diálogo, es una pantalla.") + """
</section>
"""

p7 = """
<section>
<span class="num">21 · Patrón P7</span>
<h2 class="sec">Registro, detalle y visor de eventos</h2>
<p class="lead">La pantalla que se usa cuando algo ha ido mal, y por tanto la que menos margen tiene para estar mal diseñada.</p>

<h3>21.1 Anatomía</h3>
<pre class="fig">┌ EVENTOS ── nivel: ≥ aviso ── 1.284 líneas ──────────────────────────────┐
│ 14:02:11  INFO   conexión establecida con api-interno:443              │
│ 14:02:14  INFO   lote-001.csv procesado (218 filas)                     │
│ 14:02:15  WARN   latencia 812 ms por encima del umbral                  │
│▶14:02:19  ERROR  lote-005.csv línea 42: falta el campo ID               │
│                  ↳ fila: 005;nombre=Cano, Rosa;edad=29                  │
│ 14:02:20  INFO   reintento 1/3 en 2 s                                   │
├────────────────────────────────────────────────────────────────────────┤
│ ↑↓ mover  f filtrar nivel  / buscar  t seguir  y copiar  e editor  q    │
└────────────────────────────────────────────────────────────────────────┘</pre>

<h3>21.2 Reglas que no se negocian</h3>
<table class="compact">
<tbody>
<tr><td style="width:8%" class="sem">1</td><td><b>El nivel se escribe además de colorearse</b> (INFO / WARN / ERROR). El color no puede ser el único portador de la información (§8).</td></tr>
<tr><td class="sem">2</td><td><b>Hora alineada a la izquierda en columna fija</b>, siempre el mismo formato, siempre con segundos si el diagnóstico importa.</td></tr>
<tr><td class="sem">3</td><td><b>El mensaje no se trunca si es un error.</b> Si hay que cortarlo, se parte en dos líneas con sangría, como en el ejemplo: primero el hecho, después el contexto.</td></tr>
<tr><td class="sem">4</td><td><b>Seguir el final es una tecla, no un comportamiento permanente.</b> Si el usuario sube a leer, la vista no se mueve sola; se avisa: «3 nuevas líneas ↓».</td></tr>
<tr><td class="sem">5</td><td><b>Se puede copiar y abrir en el editor</b> del usuario. Una interfaz que no deja sacar el texto obliga a repetir el trabajo a mano.</td></tr>
</tbody>
</table>

""" + ficha(
    "N1 rejilla · N3 jerarquía (nivel en caja alta) · N4 color por nivel · N6 foco · N7 teclas · N8 barra de estado",
    "El <b>buffer de líneas</b> con scroll, el filtro por nivel y el modo «seguir».",
    "f filtrar por nivel · t seguir el final · y copiar al portapapeles · e abrir en $EDITOR",
    "Sin eventos (vacío con la explicación de qué se registrará) · filtro sin resultados · en pausa (lectura manual) · error de lectura del archivo de registro",
    "No es un editor ni un visor de texto largo. Para analizar en serio, se exporta: la TUI sirve para detectar, no para estudiar.") + """
</section>
"""

parte3 += p1 + p2 + p3 + p4 + p5 + p6 + p7


# ---------------------------------------------------------------- PARTE IV
parte4 = """
<section class="parte">
<span class="num">Parte IV</span>
<h2 class="sec">Implementar: del boceto a la herramienta</h2>
<p class="lead">Aquí se descubre lo que ningún boceto cuenta: una TUI es un <b>bucle</b>. Todo lo demás —marcos, colores, tablas— es consecuencia de tres decisiones que se toman una vez.</p>
</section>
"""

i1 = """
<section>
<span class="num">22 · Implementación</span>
<h2 class="sec">La arquitectura mínima: estado, render, entrada</h2>
<p class="lead">Si el código de una TUI está bien organizado, se puede dibujar cualquier pantalla sin tocar la lógica. Si está mal, cada pantalla nueva rompe las anteriores.</p>

<h3>22.1 Las cuatro piezas</h3>
<table class="compact">
<thead><tr><th style="width:20%">Pieza</th><th style="width:34%">Qué es</th><th>Regla</th></tr></thead>
<tbody>
<tr><td><b>Estado</b></td><td>Una estructura de datos que contiene todo lo que la pantalla necesita mostrar: lista, selección, filtro, mensaje, modo.</td><td>Una sola fuente de verdad. Si algo se dibuja, está en el estado; si no está en el estado, no se dibuja.</td></tr>
<tr><td><b>Render</b></td><td>Una función que recibe el estado y devuelve la pantalla completa (una rejilla de caracteres o una lista de líneas).</td><td><b>Función pura</b>: sin leer archivos, sin consultar la hora, sin red. Mismo estado, misma pantalla. Esto es lo que hace testeable la interfaz.</td></tr>
<tr><td><b>Entrada</b></td><td>Traduce la tecla pulsada en un cambio de estado.</td><td>La entrada no dibuja nunca. Solo cambia el estado y deja que el bucle repinte.</td></tr>
<tr><td><b>Bucle</b></td><td>Espera un evento → actualiza estado → repinta → repite. Más un manejador de cambio de tamaño.</td><td>Un solo hilo para la interfaz. El trabajo pesado va fuera y comunica resultados al estado.</td></tr>
</tbody>
</table>

<pre class="fig">        ┌───────────────┐   tecla    ┌──────────────┐
        │   ENTRADA     │───────────▶│              │
        └───────────────┘            │    ESTADO    │
        ┌───────────────┐  resultado │  (una sola   │
        │ TRABAJO ASÍNC.│───────────▶│   verdad)    │
        └───────────────┘            └──────┬───────┘
                                            │ render(estado)
                                            ▼
        ┌───────────────┐   celdas   ┌──────────────┐
        │   TERMINAL    │◀───────────│   REJILLA    │
        └───────────────┘  (diff)    └──────────────┘</pre>

<h3>22.2 Los cuatro errores que arruinan una TUI</h3>
<table class="compact">
<tbody>
<tr><td style="width:32%"><b>Dibujar y decidir a la vez</b></td><td>El código que pinta la tabla también consulta la base de datos. Resultado: pantallas que se congelan y errores imposibles de reproducir. Se separa en render puro y acciones.</td></tr>
<tr><td><b>No manejar el cambio de tamaño</b></td><td>La terminal se redimensiona y el marco se rompe. Se debe escuchar el evento (SIGWINCH o equivalente) y volver a calcular el layout; y fijar un <b>mínimo</b> por debajo del cual se muestra un aviso en lugar de basura.</td></tr>
<tr><td><b>Repintar todo en cada tecla</b></td><td>Funciona en local y parpadea por SSH. Se repinta solo lo que cambió, o se limita la frecuencia a 10–15 fps.</td></tr>
<tr><td><b>No restaurar la terminal al salir</b></td><td>El usuario acaba con el cursor invisible y el eco desactivado. Toda salida —incluido Ctrl-C y las excepciones— pasa por una limpieza registrada al arrancar.</td></tr>
</tbody>
</table>
</section>
"""

i2 = """
<section>
<span class="num">23 · Implementación</span>
<h2 class="sec">Del boceto al código: cuatro sustratos</h2>
<p class="lead">Se puede empezar por un framework o por el sustrato. Con lo primero se llega antes; con lo segundo se entiende por qué el framework existe. Recomendación honesta: escribir <b>una vez</b> la versión de treinta líneas y luego no volver a hacerlo nunca.</p>

<h3>23.1 Nivel 0 · ANSI puro (Python, sin dependencias)</h3>
<pre class="code">import sys, tty, termios, select

def leer_tecla():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

def dibujar(estado):
    # mueve el cursor al origen y pinta la pantalla completa
    filas = []
    filas.append("┌─ TAREAS " + "─" * 60 + "┐")
    for i, t in enumerate(estado["items"][:8]):
        marca = "▶" if i == estado["sel"] else " "
        filas.append("│" + (marca + " " + t).ljust(70)[:70] + "│")
    filas.append("├" + "─" * 70 + "┤")
    filas.append("│ ↑↓ mover   q salir".ljust(71) + "│")
    filas.append("└" + "─" * 70 + "┘")
    sys.stdout.write("\\x1b[H" + "\\n".join(filas))   # H = ir a 1,1
    sys.stdout.flush()

def main():
    estado = {"items": ["comprar pan", "llamar a Ana", "revisar informe"],
              "sel": 0}
    fd = sys.stdin.fileno()
    viejo = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)                      # sin eco, sin espera de Enter
        sys.stdout.write("\\x1b[?25l")        # oculta el cursor
        while True:
            dibujar(estado)
            k = leer_tecla()
            if k == "q":
                break
            elif k == "j" and estado["sel"] < len(estado["items"]) - 1:
                estado["sel"] += 1
            elif k == "k" and estado["sel"] > 0:
                estado["sel"] -= 1
    finally:
        sys.stdout.write("\\x1b[?25h")        # muestra el cursor
        termios.tcsetattr(fd, termios.TCSADRAIN, viejo)

main()</pre>
<p class="nota-txt">Treinta líneas y ya están las cuatro piezas: estado, render puro, lectura de tecla y limpieza garantizada. Todo lo que venga después es esto con más comodidad.</p>

<h3>23.2 Nivel 1 · Framework (Python / Textual)</h3>
<pre class="code">from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, ListItem, ListView, Static

class Tareas(App):
    CSS = "ListView { border: round $accent; height: 1fr; }"
    TITULO = "TAREAS"

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(*[ListItem(Static(t)) for t in
                         ["comprar pan", "llamar a Ana", "revisar informe"]])
        yield Footer()

Tareas().run()</pre>
<p class="nota-txt">El framework aporta lo que cuesta escribir bien y no enseña nada: foco, scroll, redimensionado, diff de pantalla, barra de estado con teclas, temas. Lo que <b>no</b> aporta es la decisión de diseño: eso lo sigues poniendo tú.</p>

<h3>23.3 Los otros dos sustratos, en una línea cada uno</h3>
<table class="compact">
<thead><tr><th style="width:16%">Sustrato</th><th style="width:28%">Cuándo elegirlo</th><th>Qué cambia respecto a los anteriores</th></tr></thead>
<tbody>
<tr><td><b>Ink</b> (JS/TS)</td><td>Ya hay un equipo de JavaScript o la herramienta se distribuye por <span class="mono">npx</span>.</td><td>Modelo de componentes con reconcilización, como React, pero dibujando en la terminal. Ecosistema de CLIs muy maduro.</td></tr>
<tr><td><b>ratatui</b> (Rust)</td><td>La herramienta tiene que ser un único binario, muy rápida, y distribuirse sin runtime.</td><td>Control fino del búfer y del diff; más ceremonia para lo mismo. Ideal si el rendimiento es un requisito, no una esperanza.</td></tr>
</tbody>
</table>

<div class="box">
<div class="box-t">Regla de elección (para no perder una semana)</div>
<p style="margin-bottom:0">Si la TUI es una herramienta interna de un equipo → el lenguaje que ya usa el equipo, con su framework. Si es una herramienta que se va a distribuir → un binario o <span class="mono">npx</span>, porque pedirle a alguien que instale un entorno para ver una tabla es el primer abandono.
Y si es para aprender → el nivel 0 primero, sin excusas.</p>
</div>
</section>
"""

i3 = """
<section>
<span class="num">24 · Implementación</span>
<h2 class="sec">Rendimiento y límites reales</h2>
<p class="lead">La terminal es rápida en local y lenta por red. Casi todos los problemas de «va a tirones» son de ancho de banda, no de CPU.</p>

<h3>24.1 La aritmética que conviene tener en la cabeza</h3>
<table class="compact">
<tbody>
<tr><td style="width:34%"><b>Una pantalla de 80×24</b></td><td>1.920 celdas. Repintarla entera son unos pocos kilobytes: irrelevante en local, notable por SSH a 30 fps.</td></tr>
<tr><td><b>Regla práctica</b></td><td>Refresco máximo de 10–15 fps para datos y 1 fps para procesos largos. Por encima, el ojo no gana nada y la conexión sufre.</td></tr>
<tr><td><b>Lo que cuesta de verdad</b></td><td>No es pintar: es <b>consultar</b>. Si el refresco dispara una consulta a la base de datos, el problema es de arquitectura, no de dibujo.</td></tr>
<tr><td><b>Objetivo medible</b></td><td>Arranque por debajo de 200 ms y primer frame por debajo de 100 ms. Si tarda más, el usuario cree que no funciona y pulsa dos veces.</td></tr>
</tbody>
</table>

<h3>24.2 Lo que una TUI no puede hacer (y su alternativa)</h3>
<table class="compact">
<thead><tr><th style="width:26%">No se puede</th><th style="width:34%">Por qué</th><th>Qué se hace en su lugar</th></tr></thead>
<tbody>
<tr><td><b>Imágenes y gráficos ricos</b></td><td>La unidad es el carácter. Hay protocolos de imagen, pero dependen del terminal.</td><td>Tablas, sparklines de una línea, cifras bien alineadas. Y exportar la imagen a un archivo.</td></tr>
<tr><td><b>Ratón como entrada principal</b></td><td>Existe, pero no es fiable ni accesible; y quien usa la herramienta por SSH no lo espera.</td><td>Todo alcanzable con teclado. El ratón, si se añade, es un extra que nunca es la única vía.</td></tr>
<tr><td><b>Tipografía y jerarquía fina</b></td><td>Una sola familia monoespaciada; negrita, caja alta y espacio son todo el repertorio.</td><td>Jerarquía por posición, espacio en blanco y mayúsculas (§7).</td></tr>
<tr><td><b>Scroll nativo</b></td><td>La aplicación controla la pantalla; el scroll puede romper el dibujo.</td><td>Scroll propio con <span class="mono">↑↓</span>, y modo de pantalla alternativa bien gestionado al salir.</td></tr>
<tr><td><b>Animaciones continuas</b></td><td>Cuestan tráfico y CPU, y marean en un entorno de trabajo.</td><td>Solo transiciones de estado (progreso, spinner de carga) y con un motivo.</td></tr>
</tbody>
</table>
</section>
"""

i4 = """
<section>
<span class="num">25 · Implementación</span>
<h2 class="sec">Pruebas y calidad: cómo saber que funciona</h2>
<p class="lead">Una TUI se puede testear mejor que una interfaz gráfica, porque su render es texto. Es una de sus ventajas grandes y casi nadie la aprovecha.</p>

<h3>25.1 La prueba de instantánea (snapshot)</h3>
<p>Como el render es una función pura de estado a texto, se guarda la salida esperada de un estado concreto en un archivo («dorado») y se compara en cada cambio. Si el resultado cambia, se revisa si es intencionado. Con tres estados bien elegidos —lleno, vacío, error— se cubre el 80 % de los fallos visuales.</p>

<h3>25.2 Simulación de teclas</h3>
<p>Se aplican secuencias de teclas al estado y se comprueba el resultado: <span class="mono">↓ ↓ Enter Esc</span> debe dejar la selección, el detalle abierto y el detalle cerrado, sin efectos colaterales. Estas pruebas detectan el bug más común de todas las TUIs: la tecla que hace cosas distintas según el historial de navegación.</p>

<h3>25.3 La lista de comprobación de veinte puntos</h3>
<table class="compact doscol">
<tbody>
<tr><td>1. Cabe en 80×24 sin cortarse</td><td>11. Cambiar de tamaño no rompe el dibujo</td></tr>
<tr><td>2. Es usable en 40 columnas o avisa</td><td>12. El foco siempre es visible</td></tr>
<tr><td>3. Se entiende sin color</td><td>13. Esc siempre vuelve atrás</td></tr>
<tr><td>4. Funciona sin Unicode (<span class="mono">+--+</span>)</td><td>14. Ctrl-C sale limpio y restaura la terminal</td></tr>
<tr><td>5. Funciona con <span class="mono">TERM=dumb</span></td><td>15. Cancelar no deja datos a medias</td></tr>
<tr><td>6. Estado vacío con la acción que lo llena</td><td>16. Los errores dicen cómo arreglarlos</td></tr>
<tr><td>7. Estado de carga sin bloquear</td><td>17. Filtro aplicado siempre visible</td></tr>
<tr><td>8. Error de red sin perder lo cacheado</td><td>18. Cifras alineadas a la derecha</td></tr>
<tr><td>9. Diez mil filas sin tirón</td><td>19. Las teclas están en la ayuda (<span class="mono">?</span>)</td></tr>
<tr><td>10. Textos largos truncados con …</td><td>20. Arranque por debajo de 200 ms</td></tr>
</tbody>
</table>

<div class="panel-nota">Los puntos 3, 4 y 5 son los que separan una herramienta profesional de una demostración. Probarla en una terminal de 40 columnas sin colores y con Unicode desactivado cuesta diez minutos y descubre más que una tarde de revisión de código.</div>
</section>
"""

i5 = """
<section>
<span class="num">26 · Implementación</span>
<h2 class="sec">Entregar y mantener</h2>
<p class="lead">Una TUI que no se puede instalar ni recordar no existe. El último kilómetro también se diseña.</p>

<table class="compact">
<tbody>
<tr><td style="width:30%"><b>Instalación</b></td><td>Un comando, sin entorno previo: <span class="mono">pipx install</span>, <span class="mono">npx</span> o un binario. Cada paso extra de instalación pierde la mitad de los usuarios.</td></tr>
<tr><td><b><span class="mono">--help</span> completo</b></td><td>Con las teclas, no solo los argumentos. Y la pantalla <span class="mono">?</span> dentro de la aplicación, siempre actualizada con la barra de estado.</td></tr>
<tr><td><b>Configuración</b></td><td>Archivo en el sitio estándar del sistema (XDG). Nada de configuración solo por variables de entorno, y nunca configuración obligatoria para empezar.</td></tr>
<tr><td><b>Detección de capacidades</b></td><td>Comprobar color y UTF-8 al arrancar y degradar: sin color, con ASCII. Nunca asumir truecolor.</td></tr>
<tr><td><b>Temas</b></td><td>Claro y oscuro como mínimo. Un tema oscuro forzado en una terminal clara es ilegible.</td></tr>
<tr><td><b>Compatibilidad de teclas</b></td><td>Nunca se cambia una tecla sin avisar en el registro de cambios. Las teclas son memoria muscular: cambiarlas es romper el teclado de otro.</td></tr>
</tbody>
</table>

<h3>26.1 La lista de publicación (diez puntos)</h3>
<table class="compact doscol">
<tbody>
<tr><td>1. Se instala con un comando, sin entorno previo</td><td>6. El color y el Unicode se detectan al arrancar</td></tr>
<tr><td>2. <span class="mono">--help</span> documenta las teclas, no solo los argumentos</td><td>7. Hay tema claro y oscuro</td></tr>
<tr><td>3. <span class="mono">--version</span> responde sin abrir la interfaz</td><td>8. El registro de cambios avisa de cualquier tecla movida</td></tr>
<tr><td>4. La configuración vive en el sitio estándar del sistema</td><td>9. Existe un modo no interactivo para scripts</td></tr>
<tr><td>5. La pantalla <span class="mono">?</span> está actualizada con la barra de estado</td><td>10. El README muestra la herramienta en una captura de texto</td></tr>
</tbody>
</table>

<div class="regla">Una TUI se juzga en los primeros treinta segundos: instalarla, abrirla y saber qué hacer sin leer nada más que la barra de estado. Todo lo de esta página existe para que esos treinta segundos salgan bien.</div>
</section>
"""

parte4 += i1 + i2 + i3 + i4 + i5


# ---------------------------------------------------------------- PARTE V
parte5 = """
<section class="parte">
<span class="num">Parte V</span>
<h2 class="sec">El manual de decisión</h2>
<p class="lead">Todo el pack condensado en una página, seis ejercicios y un glosario. Si tienes que repasar antes de empezar un proyecto, esta es la parte que se relee.</p>
</section>
"""

r16 = """
<section>
<span class="num">27 · Síntesis</span>
<h2 class="sec">Las dieciséis reglas nucleares</h2>

<div class="reglas">
<div><b>Del núcleo</b>
<ol>
<li>La unidad es la celda: piensa en columnas, no en píxeles.</li>
<li>Diseña para 80×24 y comprueba en 40 columnas.</li>
<li>Un margen de una columna alrededor de todo. Siempre.</li>
<li>Tres roles de color como máximo, más dos estados.</li>
<li>Nunca uses el color como única señal.</li>
<li>Cinco estados por pantalla: vacío, cargando, error, éxito, sin permiso.</li>
<li>Un solo foco visible en cada momento.</li>
<li>Enter avanza, Esc vuelve, q sale. En todas las pantallas.</li>
<li>La barra de estado muestra solo lo que funciona ahora.</li>
<li>Jerarquía con mayúsculas, espacio y posición, no con adornos.</li>
</ol></div>
<div><b>De la decisión</b>
<ol start="11">
<li>Si el usuario tiene que actuar sobre un registro, no es un panel: es una tabla.</li>
<li>Los números, a la derecha; el texto, a la izquierda.</li>
<li>El progreso se dice con recuento o no se dice.</li>
<li>Las acciones destructivas se nombran con su cantidad.</li>
<li>El render es una función pura del estado: sin red, sin reloj, sin disco.</li>
<li>Si algo no se puede hacer con teclado y sin color, no está terminado.</li>
</ol></div>
</div>

<div class="regla">Y la que resume todas: <b>una TUI no es una interfaz gráfica en blanco y negro</b>. Es otra gramática —rejilla, teclas, densidad— y quien la trata como una versión pobre de una ventana hace herramientas que nadie quiere usar.</div>
</section>
"""

ejercicios = """
<section>
<span class="num">28 · Práctica</span>
<h2 class="sec">Seis ejercicios, de una pantalla a una herramienta</h2>
<p class="lead">Cada ejercicio añade una pieza del núcleo o un patrón. El criterio de aceptación es lo que decide si está terminado: si no se cumple, no está terminado, aunque se vea bonito.</p>

<table class="compact">
<thead><tr><th style="width:5%">#</th><th style="width:24%">Qué se construye</th><th style="width:22%">Qué se practica</th><th>Criterio de aceptación</th></tr></thead>
<tbody>
<tr><td><b>1</b></td><td>Reloj + estado del equipo (una pantalla, sin interacción)</td><td>N1 rejilla · N3 jerarquía · N4 color</td><td>Cabe en 40 columnas, se entiende sin color y se refresca una vez por segundo.</td></tr>
<tr><td><b>2</b></td><td>Lista de tareas con foco, marcar y borrar</td><td>N5 estados · N6 foco · N7 teclas · N8 barra</td><td>Estado vacío con la acción que lo llena; foco visible sin color; Esc y q coherentes.</td></tr>
<tr><td><b>3</b></td><td>Tabla master-detail con filtro y orden</td><td>P2 + L3 master-detail</td><td>Seis columnas como máximo, contador visible, filtro sin resultados explicado, 10.000 filas sin tirón.</td></tr>
<tr><td><b>4</b></td><td>Formulario con validación y confirmación al salir</td><td>P3 + N9 mensajes</td><td>Valida al salir del campo, no borra lo escrito, error pegado al campo y con instrucción.</td></tr>
<tr><td><b>5</b></td><td>Asistente de cuatro pasos que guarda borrador</td><td>P4 + stepper</td><td>Volver atrás no pierde nada; salir y reanudar funciona; el resumen final es editable.</td></tr>
<tr><td><b>6</b></td><td><b>Procesador por lotes</b>: cola, progreso, errores y registro</td><td>P5 + P7 + arquitectura §22</td><td>Progreso monótono y honesto, errores acumulados con reintento, cancelar dice qué se conservó, render sin bloquear.</td></tr>
</tbody>
</table>

<h3>28.1 Cómo se evalúa un ejercicio (rúbrica de cuatro niveles)</h3>
<table class="compact">
<thead><tr><th style="width:20%">Criterio</th><th style="width:20%">1 · No está</th><th style="width:20%">2 · A medias</th><th style="width:20%">3 · Bien</th><th>4 · Ejemplar</th></tr></thead>
<tbody>
<tr><td><b>Rejilla</b></td><td>Se rompe al redimensionar</td><td>Aguanta 80×24</td><td>Aguanta 40 columnas con aviso por debajo</td><td>Se adapta y prioriza contenido al reducir</td></tr>
<tr><td><b>Estados</b></td><td>Solo el caso feliz</td><td>Vacío y error</td><td>Los cinco del núcleo</td><td>Además, datos obsoletos marcados con su hora</td></tr>
<tr><td><b>Teclado</b></td><td>Solo algunas teclas</td><td>Todas, pero sin ayuda</td><td>Mapa completo en <span class="mono">?</span></td><td>La barra cambia según contexto</td></tr>
<tr><td><b>Arquitectura</b></td><td>Todo en un archivo</td><td>Estado separado</td><td>Render puro y probado con instantáneas</td><td>Además, teclas simuladas en pruebas</td></tr>
</tbody>
</table>
</section>
"""

glosario = """
<section>
<span class="num">29 · Referencia</span>
<h2 class="sec">Glosario y para seguir</h2>

<table class="compact glosario">
<tbody>
<tr><td><b>Rejilla</b></td><td>Retícula de celdas (columnas × filas) sobre la que se dibuja todo.</td></tr>
<tr><td><b>Celda</b></td><td>Un carácter en una posición. La unidad mínima de una TUI.</td></tr>
<tr><td><b>Layout</b></td><td>Reparto del espacio: bandas, columnas, master-detail.</td></tr>
<tr><td><b>Foco</b></td><td>El único elemento que recibe las teclas en este momento.</td></tr>
<tr><td><b>Estado vacío</b></td><td>Pantalla sin datos que explica qué aparecerá y cómo llenarla.</td></tr>
<tr><td><b>Degradación</b></td><td>Lo que se muestra cuando falta color, Unicode o ancho.</td></tr>
<tr><td><b>Diff</b></td><td>Escribir solo las celdas que cambiaron en lugar de repintar todo.</td></tr>
<tr><td><b>Búfer</b></td><td>Memoria intermedia que contiene la pantalla antes de escribirla.</td></tr>
<tr><td><b>Modal</b></td><td>Elemento que bloquea el resto hasta que se resuelve.</td></tr>
<tr><td><b>Snapshot test</b></td><td>Comparar el render de un estado con un archivo de referencia.</td></tr>
<tr><td><b>TUI</b></td><td>Interfaz de usuario de terminal: texto, teclado, rejilla.</td></tr>
<tr><td><b>ANSI / escape</b></td><td>Secuencias de control que mueven el cursor y cambian colores.</td></tr>
<tr><td><b>Stepper</b></td><td>Indicador de pasos de un asistente.</td></tr>
<tr><td><b>Sparkline</b></td><td>Serie temporal dibujada en una sola línea de caracteres.</td></tr>
<tr><td><b>Modalidad de pantalla alternativa</b></td><td>Modo que ocupa toda la terminal y restaura su contenido al salir.</td></tr>
</tbody>
</table>

<h3>29.1 Para seguir</h3>
<table class="compact">
<tbody>
<tr><td style="width:26%"><b>Herramientas</b></td><td>Textual (Python) · Ink (JS/TS) · ratatui (Rust) · blessed/rich (Python) · bubbletea (Go).</td></tr>
<tr><td><b>Lecturas</b></td><td>Las guías de estilo de CLI de <i>clig.dev</i> y de <i>Heroku</i>; los principios de diseño de TUIs de la documentación de Textual; cualquier manual de tipografía aplicado a rejilla fija.</td></tr>
<tr><td><b>Práctica</b></td><td>Leer el código de tres herramientas de terminal que uses a diario y anotar qué teclas usan, cómo marcan el foco y qué hace su barra de estado. Es el mejor curso que existe y es gratis.</td></tr>
</tbody>
</table>

<div class="regla">El objetivo del pack no es que sepas dibujar marcos: es que puedas mirar cualquier TUI —la tuya o la de otro— y decir <b>qué decisiones tomó, cuáles evitó y dónde va a fallar</b>. Eso es criterio, y es lo único que no caduca cuando cambia el framework.</div>
</section>
"""

parte5 += r16 + ejercicios + glosario

PARTS_B = parte3 + parte4 + parte5
