# Compilatorio de plantillas de interfaz de terminal

Once colecciones de interfaz construidas en el workspace, reunidas como material
de estudio: se estudian, se copian y se rehacen. No es un tutorial —el tutorial
es el *pack* de `03_Pack_TUI/`—; esto es el catálogo de lo que se construyó con
su método.

## Qué hay

| Fichero | Qué es |
|---|---|
| `Compilatorio_TUI.pdf` | El documento, 29 páginas, con las figuras en color real |
| `Compilatorio_TUI.html` | El mismo documento, navegable, sin recursos externos |
| `plantilla_tui.py` | **La plantilla mínima**: 3 pantallas, 9 colores, un verificador. Se copia y se cambia |
| `plantilla.txt` / `plantilla.html` | La salida de la plantilla |
| `compilatorio.py` | El generador de este documento |
| `fichas_a.py` / `fichas_b.py` | Las fichas de las ocho colecciones (datos, paletas, técnicas) |

## Lo que contiene el documento

| Cap. | Contenido |
|---|---|
| 00–01 | Cómo usarlo y el método: cuatro capas, una regla |
| 02–08 | Las **siete series de estilo**: cyberpunk, Minority Report, juego, Pip-Boy, reactor, NieR, Pragmata. Una ficha por serie: idea, paleta con procedencia, pantalla real en color, técnica, qué copiar, qué no, fragmento de código e inventario |
| 09–10 | Las **siete apps reales** (21 pantallas, 91 colores con su origen) y la tabla comparada de las ocho colecciones |
| 11 | La **plantilla mínima**, sus cinco decisiones, cómo copiarla en cuatro pasos y las doce comprobaciones |
| 12 | Ficheros, comandos y las tres capas de verificación |
| A–B | Todas las paletas, y lo que el compilatorio **no** demuestra |

**63 pantallas** en total: 6 × 7 series de estilo + 21 de las apps reales.

Además, al principio del documento, un apartado **00.3** y el capítulo 01 explican
las cuatro capas comunes (motor, paleta, composición, salida). Las figuras de las
fichas muestran las primeras 26 de las 30 filas de cada pantalla: la pantalla
completa está siempre en el `.txt` que cita cada ficha.

## Reproducir

```bash
# cada colección escribe sus .html y .txt
python3 cyberpunk/cyberpunk.py
python3 minority/minority.py
python3 juego/juego.py
python3 pipboy/pipboy.py
python3 reactor/reactor.py
python3 nier/nier.py
python3 pragmata/pragmata.py
python3 tui/series.py

# la plantilla: se verifica y se pinta
python3 04_Compilatorio/plantilla_tui.py --test
python3 04_Compilatorio/plantilla_tui.py --ansi

# el documento
python3 04_Compilatorio/compilatorio.py     # necesita weasyprint para el PDF
```

## Cómo se generan las figuras

No son capturas de pantalla ni dibujos: el compilatorio **ejecuta cada generador
con `--ansi`**, captura lo que escribe y traduce los colores ANSI a HTML. Si una
colección cambia un color, la figura del PDF cambia sola. Es la misma idea que el
resto del proyecto: la figura es la salida real, no una ilustración de ella.

Excepción: la versión ASCII de reactor y la pantalla de ncdu se leen de su `.txt`,
porque el interés de esas dos figuras es justamente que no tienen color.

## Estado de verificación

- `plantilla_tui.py --test` → **0 problemas** · la prueba negativa detecta las
  averías plantadas (un estilo sin declarar y una celda sobre el borde).
- Los ocho generadores se ejecutaron en esta sesión y escribieron sus ficheros
  (6 pantallas × 7 series + 21 pantallas de apps).
- El documento se regeneró con esas salidas; las 29 páginas se revisaron como
  imagen (portada, fichas, capítulos 09–12, apéndices).

## Dos cosas que aparecieron construyendo esto

1. **El corpus 08 no se pintaba nunca en ANSI.** `pintar()` reventaba con
   `KeyError: 'inverso'` en las seis apps que no declaran ese rol (solo ncdu lo
   tiene). Estaba ahí desde el principio y nadie lo había ejecutado con `--ansi`.
   Arreglado en `tui/comun.py` con una caída a `seleccion` y luego a `titulo`.
2. **NieR declara un color y pinta otro.** El docstring de `nier.py` dice papel
   `#c7c2aa` y el diccionario `PAPEL` aplica `#c3bea6`; manda el diccionario,
   porque es el que se pinta. Queda anotado en la ficha (06.5) en vez de
   corregir el original: es su decisión, y el compilatorio no reescribe las
   colecciones.
3. **Un verificador que no registra el panel no verifica nada.** La primera
   versión de `plantilla_tui.py` dibujaba las cajas con una función propia y el
   verificador daba cero. Se descubrió al plantar una avería a propósito. Ahora
   la plantilla usa `Lienzo.caja()` —que sí registra— y el test exige que la
   prueba negativa detecte al menos dos averías.
