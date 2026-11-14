# Brief de entrega · Pack educativo de TUI

Documento de traspaso para el agente que lleva el trabajo de interfaces de terminal. Contiene el encargo tal como se formuló, las decisiones tomadas y por qué, el estado real del material, las trampas técnicas que ya se pisaron y lo que queda abierto.

**Paquete completo:** `Entrega_Pack_TUI_Agente.zip` (en esta misma carpeta) — contiene el HTML, el PDF y los dos generadores.
**Copia de trabajo:** `/home/user/03_Pack_TUI/` (HTML y PDF) y `/home/user/src/tui_pack.py` + `tui_pack_b.py` (generadores).

---

## 1. El encargo original

> «Pack educativo-instructivo acerca de cómo **idealizar** (tomando en cuenta pros y contras), **diseñar** (tomando en cuenta UX/UI) e **implementar** estos TUIs, incluyendo el cómo de los elementos que son **transversales a todos primero**, y luego avanzando a sus **particularidades**. Al final el receptor del material debe ser capaz de crear sus propias interfaces a través del entendimiento de sus **alcances y limitaciones**.»

Aclaraciones dadas al arrancar, que son restricciones firmes:

| Pregunta | Respuesta |
|---|---|
| ¿Qué significa TUI? | **Terminal User Interface** (no tangible, no impresa) |
| ¿Formato? | **HTML + PDF**, con ejemplos, y **trabajo nuclear**: que los elementos comunes se reutilicen en los pasos avanzados |
| ¿Para quién? | **Desde cero**: nunca ha diseñado ni programado interfaces |

---

## 2. Las decisiones estructurales (y su motivo)

1. **Cinco partes, treinta capítulos.** I Idealizar · II El núcleo · III Particularidades · IV Implementar · V Síntesis.
2. **El núcleo es explícito y numerado: N1–N9.** Rejilla, marcos y layouts, jerarquía, color, estados, foco, teclas, barra de estado, mensajes. Numerarlo no es adorno: permite que cada patrón declare **qué piezas reutiliza** y convierte la promesa de «nuclear» en algo verificable.
3. **Cada patrón de la parte III lleva una «ficha de composición»** de cinco filas: *reutiliza del núcleo · lo que añade · teclas nuevas · estados obligatorios · su límite*. Regla editorial: **un patrón solo puede añadir una cosa**; si añade dos, está mal descompuesto.
4. **Un generador, dos formatos.** `src/tui_pack.py` contiene CSS (pantalla + impresión), portada, índice, partes I y II, y ensambla `tui_pack_b.py` (partes III–V). Cualquier cambio de contenido se propaga al HTML y al PDF con una sola ejecución.
5. **Las figuras son capturas de terminal, no dibujos de interfaz.** Todos los bocetos son `pre` con caracteres de caja: el documento practica el medio que enseña.
6. **El contenido es decidible, no inspiracional.** Cada capítulo termina en reglas numeradas o en una prueba ejecutable por el lector («imprime la pantalla sin color: ¿se distingue el foco?»).

---

## 3. Estado actual

- **PDF:** 35 páginas A4. Sin páginas huérfanas (QA: todas las páginas con más de 230 palabras salvo la portada).
- **HTML:** archivo único autocontenido, sin recursos externos, con índice lateral de 30 enlaces a anclas.
- **Índice del contenido:** ver §6 de este brief.
- **QA hecho:** revisión visual página a página renderizando con `pymupdf` a 58 dpi y ampliando zonas a 150–200 dpi; comprobación de anclas del HTML; comprobación de que no hay `http://` ni `src=` externos.

---

## 4. La duda que quedó abierta: los modales

**Pregunta recibida:** «no hay modales, ¿cuál es la razón, si la hubiese?».

**Respuesta corta:** sí los hay, en dos sitios, y su escasez es intencionada.

| Dónde | Qué dice el pack |
|---|---|
| §06, tabla de layouts (**L5**) | «Modal sobre pantalla» existe como **estructura**, con dos avisos: nunca anidar modales, y en 40 columnas el modal mínimo ocupa toda la pantalla |
| §20 (**P6**) | Patrón completo: confirmación, diálogo de acción breve y paleta de comandos; con seis reglas, entre ellas «Esc cierra siempre» y «no se anidan diálogos» |
| §10 (foco) | El «foco fantasma»: al abrir un modal, el fondo debe desactivarse visualmente |
| §13 (mensajes) | Las confirmaciones de éxito **no** usan modal: van a la línea de mensajes |

**La razón de que sean escasos, por si hay que justificarla o ampliarla:**

1. **Rompen el flujo de teclado**, que es la única entrada fiable del medio. Cada modal es un cambio de contexto que el usuario no pidió.
2. **En este medio cuestan la pantalla entera.** Lo que en una interfaz gráfica es una caja de 400×300 px, en 40 columnas es toda la vista: se pierde el contexto que justificaba el modal.
3. **Interrumpen sin poder deshacerse con ratón.** No hay clic fuera para cerrar ni gesto de descarte: solo Esc, que hay que conocer.
4. **Casi siempre hay una solución mejor:** la acción en línea en la propia fila, la línea de mensajes con deshacer, o una pantalla entera cuando de verdad hace falta contexto.
5. **Por eso el pack los reserva a lo destructivo o irreversible**, y nombra el objeto y la cantidad («borrar 3 registros»), con el foco inicial fuera de la acción peligrosa.

**Si se quiere ampliar** (recomendación, no hecho): añadir a P6 una subsección «Cuándo un modal es la respuesta equivocada» con tres casos y su alternativa (edición en línea, deshacer en la barra de mensajes, panel lateral en lugar de modal). No hace falta tocar nada más del pack: P6 ya tiene el hueco natural.

---

## 5. Trampas técnicas ya resueltas (no repetirlas)

- **Páginas huérfanas.** Con una sección por página forzada salían 44 páginas y siete casi vacías. Solución aplicada: las secciones **fluyen** (`page-break-before: auto`, con regla superior fina), solo las partes fuerzan salto (`section.parte`) y el índice tiene `page-break-after: always`. Con eso bajó a 35 páginas sin huecos.
- **`h2` y `h3` con `page-break-after: avoid`**, o quedan títulos al pie de página.
- **Tablas con `table-layout: fixed` y anchos en %**; nunca en mm.
- **Comillas escapadas dentro de las cadenas Python:** los `<span class="mono">` van con comillas simples (`class='mono'`) cuando están dentro de literales de doble comilla. Ya hubo un `SyntaxError` por eso.
- **WeasyPrint no está instalado por defecto** en este entorno: `pip install weasyprint pymupdf` antes de generar.
- **El texto de las figuras se ve «pegado» a 58 dpi** y está bien: comprobar siempre ampliando a 150 dpi antes de tocar nada.
- **Regenerar:** `python3 src/tui_pack.py` (escribe en `/home/user/03_Pack_TUI/`).

---

## 6. Índice del pack (para no duplicar capítulos)

**Parte 0 · Índice y cómo leerlo.** Índice impreso en dos columnas y tabla «cómo se usa el pack» según el perfil del lector.

**Parte I · Idealizar**
01 Qué es (y qué no es) una TUI · 02 Cuándo una TUI es la respuesta correcta (pros/contras + prueba de seis preguntas) · 03 Los cinco géneros · 04 El contrato antes del boceto (seis preguntas, plantilla, ejemplo resuelto, alcances y límites).

**Parte II · El núcleo**
05 N1 celda y rejilla · 06 N2 marcos, bandas y cinco layouts · 07 N3 jerarquía sin tipografía · 08 N4 color: cuatro roles y dos estados · 09 N5 los cinco estados · 10 N6 foco · 11 N7 mapa de teclas · 12 N8 barra de estado · 13 N9 línea de mensajes · 14 densidad, números y accesibilidad.

**Parte III · Particularidades** (cada uno con ficha de composición)
15 P1 panel de estado · 16 P2 tabla y explorador · 17 P3 formulario y validación · 18 P4 asistente por pasos · 19 P5 cola de trabajo y progreso · 20 P6 diálogos y paleta de comandos · 21 P7 registro y visor de eventos.

**Parte IV · Implementar**
22 Estado, render, entrada (arquitectura y cuatro errores) · 23 Cuatro sustratos: ANSI puro, Textual, Ink, ratatui · 24 Rendimiento y límites reales · 25 Pruebas (instantáneas, teclas simuladas, 20 comprobaciones) · 26 Entregar y mantener (diez puntos de publicación).

**Parte V · Síntesis**
27 Las dieciséis reglas nucleares · 28 Seis ejercicios con rúbrica de cuatro niveles · 29 Glosario y para seguir.

---

## 7. Estilo del material (mantener la coherencia)

- **Paleta:** tinta `#16262b`, bronce `#8a5a2b`, papel `#faf8f3`, borde `#d9d2c5`, alerta `#a63d2f`.
- **Tipografía:** Georgia para texto; `DejaVu Sans Mono` para figuras y código.
- **Figuras:** fondo tinta, texto papel, tamaño 6.7 pt, `white-space: pre`; **sin** caracteres decorativos que no sean de caja.
- **Numeración:** cada capítulo es un `§` con dos dígitos; las piezas del núcleo se citan como **N1–N9** y los patrones como **P1–P7** en todas partes.
- **Estructura de capítulo:** `lead` en cursiva → tablas cortas (≤ 7 filas) → reglas numeradas → cierre con regla o nota. Nunca un capítulo solo de prosa.
- **Tono:** segunda persona, frases cortas, sin adjetivos de entusiasmo. Cada afirmación acompañada de su consecuencia práctica o de su límite.

---

## 8. Lo que queda abierto (candidatos, sin priorizar)

1. **Cuaderno de ejercicios** independiente: los seis enunciados en hojas imprimibles con la rúbrica para autocorregirse.
2. **Plantilla de código del ejercicio 3** (tabla master-detail) lista para clonar, con el render puro separado y pruebas de instantánea.
3. **Ampliación de P6** con «cuándo un modal es la respuesta equivocada» (ver §4).
4. **Ejemplos ejecutables** de los cuatro sustratos en un repositorio aparte, uno por carpeta.
5. **Versión inglesa** del pack: el contenido ya está separado del CSS, así que es sustituir cadenas.

---

## 9. Cómo continuar sin romper lo que funciona

- **No cambiar la arquitectura de cinco partes ni la numeración N/P**: es lo que hace que el pack sea «nuclear» y reutilizable.
- **Antes de añadir contenido a un capítulo**, comprobar que no empuja una página a quedar medio vacía: regenerar y mirar los recuentos de palabras por página con `pymupdf` (por debajo de ~230 palabras en una página que no sea portada o cierre de parte, hay que revisar).
- **Cualquier figura nueva va como captura ASCII**, nunca como imagen.
- **Si se toca el CSS**, tocar también el bloque `@media screen`: el HTML y el PDF comparten hoja de estilos y el HTML es la versión que se lee en pantalla.
