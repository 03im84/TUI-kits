# plantillas_tui · compilatorio de interfaces de terminal

Paquete autocontenido con **once colecciones de interfaz de terminal** y el
documento que las explica: **63 pantallas**, un solo motor de celdas y cero
dependencias para dibujar.

Se estudia, se copia y se rehace. No es un tutorial —el tutorial es el pack de
`03_Pack_TUI`—; esto es el catálogo de lo construido con su método.

- **Versión del paquete:** 1.0 · 2026-11-09
- **Lenguaje:** Python 3.10+ · solo biblioteca estándar (el PDF necesita `weasyprint`)
- **Probado en:** Linux x86-64 · Python 3.13

---

## Empezar en treinta segundos

```bash
cd plantillas_tui
python3 04_Compilatorio/plantilla_tui.py --test    # tiene que imprimir «ok»
python3 04_Compilatorio/plantilla_tui.py --ansi    # la pinta en tu terminal
```

Eso es una TUI de tres pantallas funcionando. El documento completo, sin
ejecutar nada, está en `04_Compilatorio/Compilatorio_TUI.pdf`.

---

## Qué hay dentro

| Fichero | Qué es |
|---|---|
| **`04_Compilatorio/Compilatorio_TUI.pdf`** | **El documento, 29 páginas**, con las figuras en color real |
| `04_Compilatorio/Compilatorio_TUI.html` | El mismo documento, navegable, sin recursos externos |
| `04_Compilatorio/plantilla_tui.py` | **La plantilla mínima**: 3 pantallas, 9 colores, un verificador |
| `04_Compilatorio/plantilla.txt` · `.html` | Su salida |
| `mockups/celdas.py` | El motor compartido: 200 líneas, lo usan las ocho colecciones |
| `refs/btop/*.theme` | 29 temas reales de btop: la fuente de la paleta leída |
| `cyberpunk/` · `minority/` · `juego/` · `pipboy/` · `reactor/` · `nier/` · `pragmata/` | Las siete series de estilo, cada una con su `.py`, `.html` y `.txt` |
| `tui/` | Las siete apps reales (btop, ncdu, gitui, bagels, posting, castero, fx): 21 pantallas |

### Las ocho colecciones

| | Colección | Paleta | Unidad | Pantallas |
|---|---|---|---|---|
| 01 | Cyberpunk | inventada | celda | 6 |
| 02 | Minority Report (cristal) | inventada | celda | 6 |
| 03 | Juego / consola | medida | celda | 6 |
| 04 | Pip-Boy | medida (5 verdes) | celda | 6 |
| 05 | Reactor (+ versión ASCII de 7 bits) | medida | celda | 6 |
| 06 | NieR: Automata | medida | **punto braille** | 6 |
| 07 | Pragmata (+ paleta para deuteranopía) | medida | celda | 6 |
| 08 | Las siete apps reales | **leída** del `.theme` | celda | 21 |

Más la plantilla mínima, con 3 pantallas: **63 en total**.

---

## Regenerarlo todo

```bash
cd plantillas_tui

# cada colección escribe sus .html y .txt
python3 cyberpunk/cyberpunk.py
python3 minority/minority.py
python3 juego/juego.py
python3 pipboy/pipboy.py
python3 reactor/reactor.py
python3 nier/nier.py
python3 pragmata/pragmata.py
python3 tui/series.py

# la plantilla: se verifica, se pinta, se escribe
python3 04_Compilatorio/plantilla_tui.py --test
python3 04_Compilatorio/plantilla_tui.py --ansi
python3 04_Compilatorio/plantilla_tui.py

# el documento (necesita weasyprint solo para el PDF)
python3 04_Compilatorio/compilatorio.py
```

Opciones comunes a todas las colecciones:

```bash
python3 <serie>.py            # escribe el HTML y el TXT
python3 <serie>.py --ansi     # las pinta en tu terminal, con color de verdad
python3 reactor/reactor.py --ascii   # la versión de 7 bits
python3 nier/nier.py --png    # vistas previas (esta sí necesita Pillow)
```

---

## Cómo se generan las figuras del documento

No son capturas ni dibujos: `compilatorio.py` **ejecuta cada generador con
`--ansi`**, captura lo que escribe y traduce los colores ANSI a HTML. Si una
colección cambia un color, la figura del PDF cambia sola.

Excepción: la versión ASCII de reactor y la pantalla de ncdu se leen de su `.txt`,
porque el interés de esas dos figuras es justamente que **no** tienen color.

---

## Ética del paquete: qué está verificado y qué no

**Verificado en esta entrega**

- Los ocho generadores se ejecutaron dentro de esta misma carpeta, sin acceso al
  resto del proyecto: escriben sus ficheros y no tienen rutas externas.
- `plantilla_tui.py --test` → **0 problemas**, y su **prueba negativa** detecta las
  averías plantadas (un estilo sin declarar, una celda sobre el borde).
- `verificar()` del motor sobre las 21 pantallas de `tui/` → **0 avisos** en 63 000
  celdas.
- El documento se regeneró con estas salidas y sus 29 páginas se revisaron como
  imagen.

**No verificado**

- **No son aplicaciones:** son pantallas estáticas. No hay teclado, ni estado, ni
  bucle de eventos. El capítulo 11 del documento dice qué falta para convertirlas
  en herramientas.
- **Un solo tamaño:** todo se compone a 100 × 30. Ninguna pantalla está probada a
  80 × 24 ni a 40 columnas.
- **Contraste sin comprobar:** ninguna de las ocho paletas pasó por el cálculo
  WCAG. Varias probablemente no cumplirían AA en sus colores tenues.
- **Accesibilidad parcial:** solo Pragmata trae alternativa para deuteranopía.
- **Windows sin probar:** el motor es biblioteca estándar, así que debería
  funcionar, pero no se ejecutó fuera de Linux.

---

## Dos cosas que aparecieron construyendo esto

1. **`tui/series.py --ansi` nunca se había ejecutado.** `pintar()` reventaba con
   `KeyError: 'inverso'` en las seis apps que no declaran ese rol (solo ncdu lo
   tiene). Corregido en `tui/comun.py` con una caída a `seleccion` y luego a
   `titulo`.
2. **Un verificador que no registra el panel no verifica nada.** La primera
   versión de `plantilla_tui.py` dibujaba las cajas con una función propia, no
   registraba el panel y por eso daba cero problemas. Se descubrió plantando una
   avería a propósito; ahora el test exige que la prueba negativa detecte al menos
   dos.

Y una discrepancia anotada, no corregida: **NieR declara un color y pinta otro**
(el docstring de `nier.py` dice `#c7c2aa`, el diccionario aplica `#c3bea6`). Manda
el diccionario, porque es el que se pinta. Está anotado en la ficha 06.5 del
documento.

---

## Autoría

Las siete series de estilo, el motor de celdas y la colección de apps reales son
trabajo previo del mismo proyecto; este paquete los reúne, los documenta y añade
la plantilla mínima, el compilatorio y la corrección de `pintar()`. Ninguna
colección se ha reescrito: se importan tal cual.

*Solo biblioteca estándar. Ninguna imagen, ninguna fuente especial, ningún cursor
gráfico: todo lo que se ve se puede escribir con `sys.stdout.write`.*
