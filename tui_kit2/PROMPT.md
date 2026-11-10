# Prompt: construye una TUI de siete pantallas, pura y determinista

> Este documento es una especificación autosuficiente. Quien lo reciba **no
> necesita ver el código original ni el producto al que sirve**: con lo que hay
> aquí se puede escribir la interfaz entera desde cero y comprobarla.
>
> Léelo completo antes de escribir la primera línea. Los criterios de aceptación
> del final no son sugerencias: son la definición de «terminado».

---

## 1. Qué vas a construir

Una interfaz de terminal, en **Python 3.11+ y solo biblioteca estándar**, para un
conversor de libros (PDF/EPUB → HTML, Markdown, EPUB, ebook). Siete pantallas,
navegación con flechas, dos modales y una barra de acciones al pie.

Tres propiedades mandan sobre todas las demás:

1. **Pureza.** La aplicación no imprime, no lee del teclado, no abre archivos y
   no consulta el tamaño del terminal. Recibe **teclas** y devuelve **marcos de
   texto**:
   ```python
   app.handle("DOWN")            # procesa una tecla
   lineas = app.render(92, 26)   # lista de 26 cadenas de ≤92 caracteres
   ```
   Todo lo que huela a aparato (modo crudo, `select`, secuencias ANSI) vive en
   un **corredor** aparte.
2. **Determinismo.** Las mismas teclas, en el mismo orden, producen los mismos
   marcos byte a byte. Sin reloj, sin azar, sin sistema de archivos, sin estado
   global. Dos ejecuciones del mismo guion deben ser idénticas (`==`).
3. **El color nunca informa solo.** Cada estado lleva además una marca textual y
   un puntero. Con todos los estilos vacíos la pantalla sigue siendo legible y
   completa.

Lo que convierte, mide o lee libros **no está aquí**: está detrás de un
`Protocol` de cuatro métodos. La interfaz pide; otro responde.

### Prohibiciones explícitas

- No importes nada del producto al que sirve la TUI (ni su CLI, ni su conversor,
  ni su módulo de temas). Si lo haces, la réplica deja de ser una réplica.
- No imprimas desde la aplicación. Ni `print`, ni `sys.stdout`, ni `input`.
- No metas cadenas visibles en las pantallas: **el texto va por claves** (§6).
- No uses reloj, `random`, ni `os.listdir` dentro de la aplicación.
- No dependas de `colorama`, `rich`, `blessed`, `curses`. Nada.
- No inventes colores nuevos por pantalla: los temas son siete y están en §7.

---

## 2. Estructura de archivos

```
tuikit/
├── __init__.py     exporta App, SCREENS, Canvas, Translator, Backend, DemoBackend, Libro, Analisis
├── keys.py         bytes del terminal → nombres de tecla
├── screen.py       Canvas (rejilla de celdas), MARKS, dibujo de caja
├── term.py         modo crudo, tamaño, pantalla alternativa, ANSI
├── theme.py        7 paletas, styles(), label(), cycle()
├── i18n.py         catálogo es/en + Translator
├── backend.py      Libro, Analisis, Protocol Backend, DemoBackend
├── app.py          las siete pantallas, el teclado y el dibujo
└── demo.py         corredor de marcos (guion) y corredor interactivo
main.py             lanzador de la demostración
tests/test_replica.py
```

Regla de oro de la separación: **`app.py` no sabe dibujar en un terminal y
`screen.py` no sabe qué es una pantalla.** `app.py` escribe celdas; `screen.py`
las guarda; `demo.py` las vuelca.

---

## 3. Las piezas de abajo

### 3.1 `screen.py` — el lienzo

```python
UNICODE_SET = {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│",
               "tee_l": "├", "tee_r": "┤"}
ASCII_SET   = {todas las claves: "+", salvo "h": "-", "v": "|"}
MARKS = {"ok": "[OK]", "warn": "[!]", "error": "[x]", "pending": "[ ]"}

@dataclass
class Cell:
    char: str = " "
    style: str = ""

class Canvas:
    def __init__(self, width, height, *, ascii_only=False)   # mínimo 20×6
    def clear(self)
    def text(self, x, y, value, style="")      # recorta fuera de la rejilla, nunca lanza
    def fill(self, x, y, width, height, style="")
    def box(self, x, y, width, height, title="", style="")   # título en x+2 del borde superior
    def rule(self, x, y, width, style="")
    def wrap(self, width, value) -> list[str]   # por palabras; parte palabras larguísimas
    def paragraph(self, x, y, width, value, style="", max_lines=None) -> int
    def lines(self) -> list[str]                # texto plano, rstrip por línea
```

Detalles que importan: `text()` **ignora** lo que caiga fuera (no lanza, no
envuelve); `lines()` hace `rstrip()` de cada fila, así un marco es comparable
sin espacios a la derecha; `wrap()` nunca devuelve una lista vacía (devuelve
`[""]`).

### 3.2 `keys.py` — de bytes a teclas

`decode(data: bytes) -> list[str]` produce:

```
UP DOWN LEFT RIGHT HOME END PAGEUP PAGEDOWN ENTER ESC TAB BACKSPACE DELETE F1 CTRL_C
char:<c>
```

Secuencias: `\x1b[A|B|C|D` y `\x1bOA|OB|OC|OD` para flechas; `\x1b[H`/`\x1b[1~`
Inicio; `\x1b[F`/`\x1b[4~` Fin; `\x1b[3~` Supr; `\x1b[5~`/`\x1b[6~` RePág/AvPág;
`\x1bOP`/`\x1b[11~` F1; `\r`/`\n` Enter; `\t` Tab; `\x7f`/`\x08` Retroceso;
`\x03` Ctrl+C; `\x1b` suelto Escape. Todo lo demás, si es imprimible, `char:<c>`.

**`PAGEUP` y `PAGEDOWN` deben existir de verdad.** Es fácil escribir la pantalla
que los usa y olvidar producirlos: entonces la tecla está documentada y muerta.

### 3.3 `term.py` — el aparato

`habilitar_ansi(salida=Tty) -> bool` (activa VT en Windows), `Teclado(entrada)`
como gestor de contexto (modo `cbreak` en POSIX, restaura al salir; `leer(espera)
-> bytes` con `select` + `os.read`, **no** `read()` con búfer), `es_terminal(flujo)`,
`pantalla_alternativa(salida, entrar=True)`, `tamano(defecto=(80,24)) -> (ancho, alto)`
con mínimos 20×8.

`leer()` devuelve `b""` si no hay tecla. Nunca bloquea más de `espera` segundos.

---

## 4. El mundo, detrás del `Protocol`

```python
@dataclass
class Libro:
    ruta: Path
    nombre: str
    lugar: str = ""            # la carpeta, tal cual se muestra en el grupo
    formato: str = "pdf"       # "pdf" | "epub" | "html"
    peso: int | None = None    # tamaño conocido; si es None se pregunta al disco

    @property
    def tamano(self) -> int    # peso si está, si no ruta.stat().st_size, si falla 0

@dataclass
class Analisis:
    formato: str = "pdf"; paginas: int = 0; tamano_hoja: str = ""
    cifrado: bool = False; caracteres: int = 0; fuentes: int = 0
    imagenes: int = 0; convertibles: int = 0; bloques: int = 0; avisos: int = 0
    palabras: int = 0; capitulos: int = 0; paginas_lectura: int = 0; perfil: str = "limpio"

class Backend(Protocol):
    nombre_app: str
    version: str
    def libros(self) -> list[Libro]: ...
    def analizar(self, libro: Libro) -> Analisis: ...
    def medir(self, libro: Libro) -> dict:        # words, pages, chapters, reading, per_page, profile
    def convertir(self, libro: Libro, opciones: dict,
                  progreso: Callable[[str, int, int], None]) -> dict:
        # -> {"outputs": [{"format","path","bytes","fidelity"}, ...],
        #     "fidelity": {formato: float}, "warnings": [{"code","message"}, ...]}
```

`opciones` que recibe `convertir`: `targets` (dict formato→bool con **un solo
formato encendido** cuando la aplicación convierte paso a paso), `out`, `paper`,
`theme`, `keep`, `reader`, `spread`.

`DemoBackend` es el mundo de mentira obligatorio para pruebas y demostración:
8 libros repartidos en las carpetas `ensayo` (3), `manuales` (2), `novela` (2) y
`salida` (1), con tamaños fijos, `analizar`/`medir` deterministas y un
`convertir` que informa de cada paso y devuelve fidelidad `1.0` y un aviso
`W-META-DUMMY`. `nombre_app = "Incunable"`, `version = "1.12.0"`,
`contrato = "1.17"` (el marco enseña `Incunable 1.12.0 · 1.17`).

---

## 5. La aplicación

### 5.1 Estado (todo en un sitio, todo inspeccionable)

```
screen            una de SCREENS
return_screen     a dónde vuelve Configuración o Fuentes
quit_requested    la tecla q lo pone; el corredor pregunta
help_visible      modal de teclas
metrics_panel     modal de métricas; mientras está abierto, el teclado es suyo
metrics_scroll
message           última línea útil: aviso, error o confirmación
message_style     "" | "muted" | "ok" | "warn" | "error"
pending           None | "analyze" | "convert"   ← trabajo pendiente
busy              texto del marco ocupado («Convirtiendo… 2/3»)

files, cursor, plegados(set), agrupar, filtrando, filtro, editing, path_text, pagina
source, info, resultado, steps(list[Step])
state             ConvertState: targets, paper, paper_ebook, theme, tui_theme, keep,
                  out, reader, spread
option_index, config(dict), config_index
fuentes(list), fuentes_editing, fuentes_text, fuentes_cursor
```

`SCREENS = ("inicio", "diagnostico", "opciones", "progreso", "resultado", "config", "fuentes")`

### 5.2 El bucle de trabajo — esto es lo que hay que copiar bien

`handle(tecla)` **no hace el trabajo**. Deja `pending` y vuelve:

```python
def run_pending(self):          # el corredor llama DESPUÉS de pintar
    while self.pending:
        self.advance()

def advance(self) -> bool:      # un paso; True si queda algo
    if self.pending == "analyze":
        self.pending = None; self.analyze()
    elif self.pending == "convert":
        self._step_conversion()
    return bool(self.pending)
```

Y la conversión avanza **un formato por paso**: `_start_conversion()` arma la cola
(`steps`, `_cola`), pone `screen = "progreso"` y `pending = "convert"`; cada
`_step_conversion()` convierte el primero de la cola con `targets = {solo ese}`,
lo marca `done`, lo saca y deja `busy = "Convirtiendo… k/n"`. Cuando la cola se
vacía: `pending = None`, `busy = ""`, `screen = "resultado"` y `resultado` queda
con `outputs`, `fidelity` y `warnings` fusionados.

Consecuencia visible y obligatoria: **existe un marco de progreso con unas marcas
hechas y otras pendientes**. Si tu implementación convierte de una tirada, has
perdido la pantalla de Progreso aunque la tengas dibujada.

### 5.3 Teclado

Orden de despacho en `handle()` — **el orden es parte de la especificación**:

```
Ctrl+C                      → "quit" (código de salida 0 del corredor)
metrics_panel               → el modal se lo come todo (Esc, q, Enter, m cierran; ↑↓ PgUp PgDn desplazan)
F1 o char:?                 → abre/cierra la ayuda
help_visible                → cualquier tecla cierra la ayuda
confirming_keep             → s/y/Enter = conservar · n = no · Esc = cancelar
fuentes_editing             → edición de una ruta de Fuentes
filtrando                   → edición del filtro de la lista
editing                     → edición de la ruta escrita en Inicio
char:<c> (sin edición)      → atajos globales; si el atajo no aplica, sigue
pantalla                    → _key_<pantalla>(tecla)
```

Atajos globales (`_shortcut`), y a qué pantalla aplican:

| tecla | efecto | dónde |
|---|---|---|
| `q` | `quit_requested = True` | siempre |
| `r` | editar ruta a mano | inicio |
| `b` | buscar (filtro) | inicio |
| `f` | Fuentes | inicio, config |
| `s` | Configuración (guarda `return_screen`) | cualquiera menos config |
| `i` | analizar el libro elegido | cualquiera |
| `o` | Opciones | inicio, diagnóstico, resultado |
| `c` | convertir: si estás en Opciones arranca; si no, lleva a Opciones | inicio, diagnóstico, resultado, opciones |

Teclas por pantalla:

- **inicio**: `↑↓` una fila · `PgUp/PgDn` una pantalla (`pagina` = filas visibles) ·
  `Inicio/Fin` extremos · `←→` pliegan/despliegan el grupo de la fila actual ·
  `Enter` sobre carpeta = plegar; `Enter` sobre libro = analizar; `Enter` con ruta
  escrita = analizar esa ruta.
- **diagnóstico**: `Enter` → Opciones · `Esc` → Inicio.
- **opciones**: `↑↓` mover · `←→`/`Enter` cambiar el valor de la fila · `c`
  convertir · `m` métricas · `Esc` → Inicio.
- **progreso**: nada (se está trabajando).
- **resultado**: `Esc` → Inicio · `i` → diagnóstico.
- **config**: `↑↓` mover · `←→`/`Enter` cambiar · `s` guardar y volver a
  `return_screen` · `Esc` volver sin guardar.
- **fuentes**: `↑↓` mover · `+` añadir ruta (edición) · `Supr` quitar (nunca la
  última: avisa) · `T` probar (cuenta libros) · `Enter` abrir esa fuente (pliega
  las demás) · `Esc` volver.

### 5.4 Navegación de la lista (Inicio)

- Agrupada por carpeta (`agrupar=True`), grupos ordenados alfabéticamente; dentro
  de cada grupo, los libros como vienen del backend.
- El cursor recorre **filas** (grupos y libros), no solo libros.
- `←→` plegar/desplegar no pierde al usuario: tras plegar, el cursor queda en la
  fila del grupo.
- El filtro compara **sin mayúsculas y sin tildes** (`Saint` encuentra
  `Saint-Exupéry`; `principito` encuentra `el-principito.pdf`).
- `Enter` sobre una carpeta **no** es un error: pliega. Y pulsar `i` con una
  carpeta elegida actúa sobre **el primer libro de esa carpeta** — concesión
  deliberada, documentada, determinista.
- `_ventana(cursor, total, visible)` centra el cursor con `mitad = visible // 2`
  y nunca deja huecos al final.

---

## 6. El dibujo: reglas que se pueden comprobar

Marco de 92×26 de referencia. **Filas**: `0` barra de título · `1` en blanco ·
`2` título de pantalla · `3` en blanco · `4…(alto-4)` contenido ·
`alto-3` mensaje · `alto-2` segunda línea de mensaje · `alto-1` barra de acciones.

1. **Barra superior**: fondo estilo `bar`; a la izquierda ` App versión · contrato `
   recortado a `ancho-12`; a la derecha el nombre de la pantalla, a `ancho - len - 2`.
2. **Cuerpo**: `x=2`, `ancho = canvas.width - 2`, `limite = canvas.height - 4`.
3. **Mensajes**: fila `alto-3` (y `alto-2` si son dos líneas). Nunca se escribe
   encima del contenido y nunca se deja cola de un mensaje anterior: **cada
   pantalla limpia su área antes de pintar** (`fill` de la fila 1 a la `alto-2`).
4. **Pie**: fondo `bar`; texto de `tui.bar.<pantalla>` empezando en la columna 1.
   Si no cabe, se recortan **frases completas** por el separador ` · `; si ni así
   cabe, se corta en seco. Nunca se parte una frase por la mitad.
5. **Recorte**: `_fit(texto, ancho)` deja el texto tal cual si cabe; si no,
   `texto[:ancho-1] + "…"`. Con `ancho == 1` devuelve `…`.
6. **Cifras**: agrupadas por miles según el idioma — `13.586` en español,
   `13,586` en inglés (`_num`). A la derecha en las columnas de tamaño.
7. **Tamaños**: `_humano(bytes)` → `512 B`, `214 KB`, `1.0 MB`.
8. **Alineación**: etiqueta en una columna de ancho fijo calculado con la
   etiqueta más larga del bloque (`max(len)+1` o `+2`), valor a continuación. En
   Opciones la columna de etiqueta es de 22 caracteres y el valor empieza en la
   columna 25 del cuerpo.
9. **Marcas**: `[OK]` hecho/encendido · `[!]` aviso · `[x]` error · `[ ]`
   pendiente/apagado. El puntero es `> ` en la columna del cuerpo; las filas no
   seleccionadas llevan `  ` (mismo ancho, para que nada baile).
10. **Modales** (ayuda y métricas): **tapan el fondo** (`fill` con estilo
    `overlay` y luego `box` con título); centrados; ancho `min(ancho-6, 56)` para
    métricas y `min(ancho-4, 62)` para ayuda; si el contenido no cabe, se
    desplaza y se dice en qué tramo estás (`2-7/12`).
11. **Modo ASCII**: `ascii_only` cambia el dibujo de caja a `+ - |`, las flechas
    del árbol a `>`/`v` y, al final del `render`, traduce 1:1 los glifos que
    vengan de los textos (`↑↓←→«»×—’·`). **El ancho no cambia**: la sustitución
    es de un carácter por uno. Las tildes se quedan (el ASCII es del marco, no
    del idioma).

### 6.1 Qué enseña cada pantalla

**Inicio** (`tui.screen.start` → «Inicio»)

```
 Documentos encontrados (8)          ← con filtro: (2 de 8 · «pri»)
  > ▾ ensayo                                   3 libros
           el-principito.pdf                   1.0 MB
      EPUB fahrenheit-451.epub                500 KB
  Ruta: (pulsa [r])                 ← estado, o «Buscar: pri_» o «Ruta: /tmp/x_»
  Enter: analizar el-principito.pdf ← qué pasará si pulsas Enter
```
- Prefijo de formato en los libros: `EPUB `, `HTML `, `     ` (PDF sin marca),
  alineado a la izquierda de la columna del nombre; los libros van sangrados dos
  espacios más que su grupo.
- Grupo: `▾` desplegado, `▸` plegado; a la derecha `N libros` / `1 libro`.
- Vacío: `tui.start.empty` explica dónde poner libros o que escribas una ruta.
- Sin coincidencias: `tui.list.no_match`.

**Diagnóstico** (`tui.screen.diagnosis`): una línea de título con el nombre del
libro y un bloque etiqueta/valor con Formato, Páginas, Tamaño (solo PDF), Cifrado,
Capa de texto (`sí (74.312 caracteres)`), Fuentes (solo PDF), Imágenes
(`9 (9 convertibles)`), Bloques, Avisos. Cierra con `[OK] Enter continuar`.
Para EPUB no se enseña tamaño de hoja ni fuentes; para HTML el formato dice
`HTML (N capítulos)` y las páginas son capítulos.

**Opciones** (`tui.screen.options`): título `Opciones de conversión · Salidas: …`.
Cinco filas de formato con `[OK]`/`[ ]`, una **regla** de separación, y luego
Carpeta de salida, HTML intermedio, Papel · HTML, Papel · ebook, Cuaderno,
Reparto, Tema, Tema de la terminal. Debajo, la ayuda de la fila elegida
(`tui.opt.help.<fila>`, una frase) y el bloque **El libro** con las cifras
medidas (`13.586 palabras · 53 páginas · 27 capítulos · 45 min de lectura` y
`Perfil del texto: limpio · 302 por página`). Si `keep_intermediate == "ask"`,
al convertir se pregunta en la franja de mensajes: `¿Conservar también el HTML
intermedio? [s/n]` y, debajo, por qué se pregunta.

**Progreso** (`tui.screen.progress`): `Convirtiendo`, una línea por formato con
su marca, y el texto `Convirtiendo… k/n`. El pie dice que no hay teclas que
valgan.

**Resultado** (`tui.screen.result`): `Resultado`, `Artefactos` con una línea por
salida — `[OK] EPUB     ruta/al/archivo.epub    143 KB` —, `Fidelidad: html
1.0000 · md 1.0000 · epub 1.0000` (marca `[!]` en vez de `[OK]` si alguna baja de
0.999) y `Avisos` con `[!] W-META-DUMMY · mensaje` o `ninguno`.

**Configuración** (`tui.screen.config`): once claves en orden fijo — `lang`,
`theme`, `tui_theme`, `paper`, `out_dir`, `keep_intermediate`, `reader_panel`,
`reader_spread`, `words_per_page`, `log_level`, `overwrite` — con el valor **en
palabras** (`Carta · 215,9×279,4 mm`, `una hoja`, `preguntar`, `sí`/`no`, `Alto
contraste`), no en clave interna. Al pie: `Los cambios se aplican al guardar`.

**Fuentes** (`tui.screen.sources`): carpetas con `N libros` a la derecha, la ayuda
`+ añadir · Supr quitar · T probar · Enter ver los libros`, la lista de libros
encontrados y, al pie, `Entrada: 4 fuentes · 8 libros`.

**Ayuda** (modal, `tui.help.title` → «Teclas»): nueve renglones con las teclas
(`↑/↓ elegir`, `←/→ o espacio cambiar valor`, `Enter confirmar`, `Esc volver /
cancelar la edición`, `b buscar en la lista · Esc limpia`, `←/→ plegar y
desplegar el grupo`, `PgUp/PgDn una pantalla · Inicio/Fin los extremos`, `F1 o ?
esta ayuda`, `q salir · Ctrl+C cancelar (código 5)`).

**Métricas** (modal, `tui.panel.metrics` → «Métricas del libro»): palabras,
páginas, capítulos, páginas de lectura, por página y perfil. Al pie, `↑↓
desplazar` y el tramo visible.

### 6.2 Errores: códigos y dónde se ven

Los errores **no abren otra pantalla**: escriben en la franja de mensajes con
marca `[x]` y estilo `error`.

| código | cuándo | texto |
|---|---|---|
| `ERR-INP-003` | no hay documento elegido | `Elige un documento primero.` |
| `ERR-USE-001` | ningún formato encendido | `No hay ningún formato marcado en Opciones.` |
| `ERR-EXT-001` | el backend lanza | `[x] ERR-EXT-001 · TipoDeError: mensaje` |

Un fallo durante la conversión marca el paso como `failed` **y deja la pantalla
de Progreso con la marca visible**: no se miente diciendo que terminó.

---

## 7. Temas: siete, ni uno más

`PALETTES` mapea nombre → `{token: (código ANSI 256, negrita)}`; cada paleta
define su propio `fg` y los tokens. Estilos con nombre que la aplicación usa:
`title`, `muted`, `ok`, `warn`, `error`, `selected`, `bar`, `overlay`.

```python
styles(nombre, no_color=False) -> dict[str, str]   # estilo "" siempre presente y vacío
label(nombre, lang) -> str                          # «Alto contraste» / «High contrast»
cycle(nombre, delta, lang) -> str                   # recorrido circular, determinista
canonical(valor) -> str                             # valor válido o DEFAULT
```

Los siete: `high_contrast` (por defecto), `amber`, `phosphor`, `phosphor_color`,
`warm_white`, `dim_green`, `colorblind`. `bar` y `overlay` se construyen con
`\x1b[7m` (vídeo inverso) más su color. Con `no_color=True` **todos** los estilos
son `""`. `cycle` recorriendo `len(PALETTES)` veces vuelve al punto de partida.

---

## 8. Textos: claves, no literales

`i18n.py` expone `ES` y `EN`, diccionarios **con el mismo juego de claves**, y:

```python
class Translator:
    def __init__(self, lang="es")   # idioma desconocido → "es"
    def __call__(self, key, **kwargs)  # clave ausente → devuelve la clave; formato tolerante
```

Reglas:
- Toda cadena visible es `tui.*`. **Ninguna pantalla contiene texto en español ni
  en inglés**: pide la clave.
- Marcadores con nombre: `{n}`, `{doc}`, `{grupo}`, `{m}`, `{ruta}`. Con `{}` no:
  se rompe al traducir.
- Los nombres de teclas, comandos, formatos (`HTML`, `EPUB`), rutas y códigos de
  error **no se traducen**: son contrato.
- Los nombres de archivo y carpeta tampoco: vienen del backend.
- Interpolación tolerante: si falta el argumento, devuelve la plantilla sin
  reventar.

El catálogo completo, con los textos exactos en español que se usan como
referencia, está en el **Anexo A**. En inglés, traduce; no reescribas la
interfaz: los `[OK]`, los `[b]` del pie y el orden de las frases se mantienen.

---

## 9. Corredores

Dos, en `demo.py`, y ninguno sabe nada de las pantallas:

**`storyboard(width, height, lang, ascii_only, backend, guion) -> [(título, marco)]`**
recorre un guion de `(título, tecla)`; tras cada tecla añade el marco y, mientras
haya `pending`, llama a `advance()` añadiendo **un marco por paso**. Es la
herramienta de pruebas y la vista previa de la documentación.

Guion obligatorio (pasa por las siete pantallas y los dos modales):

```
("inicio",""), ("inicio · bajar","DOWN") ×2, ("diagnóstico","ENTER"),
("opciones","char:o"), ("opciones · bajar","DOWN") ×2,
("opciones · encender EPUB","ENTER"), ("opciones · bajar","DOWN"),
("opciones · métricas","char:m"), ("opciones · cerrar métricas","ESC"),
("convertir","char:c"), ("convertir · ¿conservar el HTML?","char:s"),
("resultado",""), ("configuración","char:s"), ("fuentes","char:f"),
("ayuda","F1"), ("fuentes · cerrar la ayuda","ESC"), ("inicio","ESC")
```

Con ese guion salen **24 marcos**. Si salen menos, o falta `progreso` entre los
títulos de las pantallas visitadas, el bucle de trabajo está mal (§5.2).

**`run(...)`** es el interactivo: si no hay terminal, vuelca el guion y sale con
0; si la hay, entra en pantalla alternativa, lee con `Teclado`, traduce con
`decode`, pinta agrupando celdas del mismo estilo (una secuencia ANSI por tramo,
no por celda) y restaura al salir.

Lanzador `main.py`:

```
python3 main.py [--guion] [--lang es|en] [--size 92x26] [--ascii]
                [--solo PANTALLA] [--out ARCHIVO] [--tema NOMBRE]
```

---

## 10. Criterios de aceptación

Todo esto se comprueba **sin terminal**, pidiendo marcos. Si algo falla, no está
terminado.

1. `SCREENS` tiene exactamente las siete pantallas y el guion las visita todas.
2. El guion es determinista: dos ejecuciones dan listas iguales (`==`), y hay más
   marcos que pasos (los intermedios existen).
3. Para 40×12, 60×18, 76×20, 92×26 y 120×40: **ninguna línea supera el ancho** y
   hay exactamente `alto` líneas.
4. Con `ascii_only` no aparece ningún glifo de dibujo de caja ni flecha unicode
   (`┌┐└┘─│├┤▸▾↑↓←→«»`) y el ancho se conserva.
5. `[OK]`, `[ ]`, `[x]`, `[!]` y `>` están presentes donde toca: quitando el color
   se sigue entendiendo la pantalla.
6. El pie de cada pantalla no está vacío y no contiene claves sin traducir.
7. `set(ES) == set(EN)`; en los marcos no aparece nunca `tui.` ni `{n}`; en
   inglés cambian las palabras y **no** las teclas (`[b]`, `[i]`, `[c]`, `q`).
8. Los siete temas pintan (`title` y `bar` no vacíos) y con `no_color` todo es
   `""`; `cycle` vuelve al inicio.
9. `App` no menciona el producto ni sus dependencias (`incunable`, `pdfminer`,
   `pypdf`): la comprobación es leer el propio `app.py`. `DemoBackend` cumple el
   `Protocol`, informa de los pasos con `(nombre, i, total)` y devuelve fidelidad
   y avisos.
10. Flujos comprobables con teclas: `Enter` en la lista deja `pending="analyze"`
    y la pantalla sigue en Inicio **hasta** que el corredor llama a
    `run_pending()`; `r` + texto + `Enter` analiza la ruta escrita (y
    `Backspace`/`Esc` funcionan); `b` filtra sin tildes y `Esc` limpia;
    `←`/`→` pliegan y despliegan; sin formatos, `c` escribe `ERR-USE-001` y no
    convierte; con `keep == "ask"`, `c` pregunta y `s`/`n` arrancan la cola;
    `m` abre el modal y `Esc` lo cierra; `s` en Configuración guarda por
    `on_save_config` y vuelve; en Fuentes `+`/`Supr` añaden y quitan (nunca la
    última); `F1` y `?` abren la ayuda y cualquier tecla la cierra.
11. La conversión deja marcas `done`/`pending` visibles en algún marco
    intermedio y todas `done` al final; el resultado lleva `outputs`, `fidelity`
    y `warnings`.
12. El resultado de `render()` es texto plano: sin secuencias ANSI. El color solo
    lo pone el corredor al volcar celdas.

---

## 11. Cómo se trabaja (si eres un modelo con herramientas)

1. Escribe `screen.py`, `keys.py`, `term.py` primero: no dependen de nada.
2. `theme.py` e `i18n.py` después: son datos.
3. `backend.py` con `DemoBackend` completo; pruébalo solo.
4. `app.py` **pantalla a pantalla**, comprobando marcos con `render()` después de
   cada una. No sigas hasta que la anterior no se salga del ancho a 40×12.
5. `demo.py` y el guion; exige que salgan las siete pantallas y 24 marcos.
6. Las pruebas del §10 enteras antes de decir que está.
7. Guarda dos volcados del guion en `docs/` (92×26 y 60×18 en ASCII): son la
   prueba visual y lo que se enseña al usuario.

Si algo de lo que dice este documento choca con tu gusto, gana el documento.
Si choca con la comodidad de quien lee la pantalla a las dos de la mañana, gana
la comodidad: y entonces cambia el documento, no la pantalla a escondidas.

---

## Anexo A — catálogo en español (referencia de forma)

Las 135 claves, con el texto exacto. En inglés: mismas claves, mismo orden de
ideas, teclas y nombres propios intactos.

- `tui.bar.inicio` — q salir · [b] buscar · [i] inspeccionar · [c] convertir · [o] opciones · [s] ajustes · [r] ruta · [f] fuentes · ←→ plegar · F1
- `tui.bar.diagnostico` — [c] convertir · [o] opciones · [s] ajustes · Esc volver · q salir
- `tui.bar.opciones` — ↑↓ mover · ←→ cambiar · [c] convertir ya · [m] métricas · Esc volver · q salir
- `tui.bar.progreso` — trabajando… espera, no hay teclas que valgan
- `tui.bar.resultado` — [i] inspeccionar · [c] otra conversión · [s] ajustes · Esc inicio · q salir
- `tui.bar.config` — ↑↓ mover · ←→ cambiar · [s] guardar y volver · [f] fuentes · q salir
- `tui.bar.fuentes` — ↑↓ mover · +/Supr editar · T probar · Enter abrir · Esc volver · q salir
- `tui.bar.panel` — Esc o q cerrar
- `tui.screen.start` — Inicio
- `tui.screen.diagnosis` — Diagnóstico
- `tui.screen.options` — Opciones
- `tui.screen.progress` — Progreso
- `tui.screen.result` — Resultado
- `tui.screen.config` — Configuración
- `tui.screen.sources` — Fuentes
- `tui.start.documents` — Documentos encontrados
- `tui.start.empty` — No hay libros a la vista (PDF o EPUB). Copia uno junto a la aplicación, en Descargas, en el Escritorio o en Documentos; o escribe una ruta y pulsa Enter.
- `tui.start.path` — Ruta
- `tui.start.path_hint` — Ruta: (pulsa [r])
- `tui.list.filter` — Buscar
- `tui.list.filter_on` — Filtro
- `tui.list.clear` — Esc limpia
- `tui.list.of` — de
- `tui.list.books` — libros
- `tui.list.one_book` — libro
- `tui.list.no_match` — Ningún libro coincide. Esc limpia el filtro.
- `tui.list.typing` — Escribe para buscar · Enter deja el filtro · Esc limpia
- `tui.list.group_hint` — Grupo «{grupo}»: Enter o ← lo pliega
- `tui.status.enter_analyze` — Enter: analizar {doc}
- `tui.status.enter_path` — Enter: abrir la ruta escrita · Esc cancelar
- `tui.status.type_path` — Pulsa [r] para escribir una ruta
- `tui.status.ask_keep` — Se te preguntará si conservar el HTML intermedio (config: keep_intermediate = ask)
- `tui.diag.title` — Diagnóstico
- `tui.diag.format` — Formato
- `tui.diag.format_pdf` — PDF
- `tui.diag.format_epub` — EPUB · {n} documentos en el spine
- `tui.diag.format_html` — HTML intermedio · {n} páginas
- `tui.diag.pages` — Páginas
- `tui.diag.size` — Tamaño
- `tui.diag.encrypted` — Cifrado
- `tui.diag.text_layer` — Capa de texto
- `tui.diag.chars` — caracteres
- `tui.diag.fonts` — Fuentes
- `tui.diag.images` — Imágenes
- `tui.diag.convertible` — convertibles
- `tui.diag.blocks` — Bloques
- `tui.diag.warnings` — Avisos
- `tui.state.on` — sí
- `tui.state.off` — no
- `tui.state.none` — ninguno
- `tui.hint.confirm` — Enter continuar
- `tui.opt.group.formats` — Formatos
- `tui.opt.group.output` — Salida
- `tui.opt.out` — Carpeta de salida
- `tui.opt.keep` — HTML intermedio
- `tui.opt.paper_web` — Papel · HTML
- `tui.opt.paper_ebook` — Papel · ebook
- `tui.opt.paper` — Papel
- `tui.opt.reader` — Cuaderno
- `tui.opt.spread` — Reparto
- `tui.opt.theme` — Tema
- `tui.opt.tui_theme` — Tema de la terminal
- `tui.opt.paper_none` — no lleva
- `tui.opt.help.out` — Resultado: junto al archivo, en la app o en la ruta que escribas.
- `tui.opt.help.keep` — Conservar el HTML intermedio permite reexportar sin releer el original.
- `tui.opt.help.paper_web` — Papel del HTML, que es lo único que se imprime.
- `tui.opt.help.paper_ebook` — Papel del ebook: «sin papel» por defecto, porque un ebook se lee en un aparato y no en un pliego.
- `tui.opt.help.reader` — Lector en HTML: índice, cronómetro, ppm y temas. Sin red.
- `tui.opt.help.spread` — Reparto: una hoja bajando, una hoja que se pasa, o dos abiertas.
- `tui.opt.help.theme` — Tema de pantalla y documento.
- `tui.opt.help.tui_theme` — Color de la terminal. No cambia el documento.
- `tui.opt.title` — Opciones de conversión
- `tui.opt.outputs` — Salidas
- `tui.opt.help.fmt.html` — HTML semántico: el intermedio del que salen los demás.
- `tui.opt.help.fmt.md` — Markdown: el texto con su estructura, sin adornos.
- `tui.opt.help.fmt.epub` — EPUB 3: el libro para cualquier lector, sin DRM.
- `tui.opt.help.fmt.ebook` — Ebook autocontenido: un solo archivo con lector propio.
- `tui.opt.help.fmt.print` — PDF para imprimir, con el papel elegido.
- `tui.ask.keep` — ¿Conservar también el HTML intermedio? [s/n]
- `tui.ask.why` — Pregunta porque keep_intermediate = ask en config.json
- `tui.book.title` — El libro
- `tui.book.words` — Palabras
- `tui.book.pages_short` — páginas
- `tui.book.minutes` — min de lectura
- `tui.book.pages` — Páginas del PDF
- `tui.book.reading` — Páginas de lectura
- `tui.book.chapters` — Capítulos
- `tui.book.per_page` — Por página
- `tui.book.useful` — útiles
- `tui.book.structural` — estructurales
- `tui.book.profile` — Perfil del texto
- `tui.book.equivalent` — Páginas equiv.
- `tui.book.not_reliable` — promedio poco fiable
- `tui.prog.title` — Convirtiendo
- `tui.busy.analyzing` — Analizando el documento…
- `tui.busy.converting` — Convirtiendo…
- `tui.res.title` — Resultado
- `tui.res.outputs` — Artefactos
- `tui.res.fidelity` — Fidelidad
- `tui.res.warnings` — Avisos
- `tui.res.none` — sin avisos
- `tui.cfg.title` — Configuración
- `tui.cfg.hint` — Los cambios se aplican al guardar
- `tui.cfg.saved` — Guardado en
- `tui.cfg.invalid` — Valor no válido
- `tui.src.title` — Fuentes de entrada
- `tui.src.empty` — Todavía no hay fuentes. Pulsa + para añadir una carpeta.
- `tui.src.prompt` — Carpeta a añadir (vacío = cancelar)
- `tui.src.row` — {n} libros
- `tui.src.row_one` — 1 libro
- `tui.src.row_none` — sin libros
- `tui.src.missing` — no existe
- `tui.src.help` — + añadir · Supr quitar · T probar · Enter ver los libros
- `tui.src.footer` — Entrada: {n} fuentes · {m} libros
- `tui.src.added` — Fuente añadida
- `tui.src.removed` — Fuente quitada
- `tui.src.test` — {n} libros en {ruta}
- `tui.src.testing` — Recorriendo…
- `tui.src.kept_one` — Se conserva al menos una fuente.
- `tui.src.list` — Libros encontrados
- `tui.help.title` — Teclas
- `tui.key.up` — ↑/↓ elegir
- `tui.key.change` — ←/→ o espacio cambiar valor
- `tui.key.enter` — Enter confirmar
- `tui.key.esc` — Esc volver / cancelar la edición
- `tui.key.filter` — b buscar en la lista · Esc limpia
- `tui.key.fold` — ←/→ plegar y desplegar el grupo
- `tui.key.page` — PgUp/PgDn una pantalla · Inicio/Fin los extremos
- `tui.key.help` — F1 o ? esta ayuda
- `tui.key.quit` — q salir · Ctrl+C cancelar (código 5)
- `tui.msg.no_document` — Elige un documento primero.
- `tui.msg.no_formats` — No hay ningún formato marcado en Opciones.
- `tui.msg.error` — No se pudo completar
- `tui.panel.metrics` — Métricas del libro
- `tui.panel.scroll` — ↑↓ desplazar
