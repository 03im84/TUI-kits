# tuikit — réplica desacoplada de la TUI de Incunable

Siete pantallas, teclas de verdad, marcos de texto. Sin terminal para probarla y
sin nada del producto debajo: el mundo exterior está detrás de un `Protocol`.

```
tui_replica/
├── main.py                 lanzador (guion o interactivo)
├── tuikit/
│   ├── app.py              las siete pantallas y el teclado  (~1.240 líneas)
│   ├── backend.py          Libro · Analisis · Protocol Backend · DemoBackend
│   ├── screen.py           Canvas de celdas, MARKS, dibujo de caja
│   ├── keys.py             bytes → nombres de tecla
│   ├── term.py             modo crudo, tamaño, pantalla alternativa, ANSI
│   ├── theme.py            7 paletas de terminal · styles() · cycle() · label()
│   ├── i18n.py             135 claves × 2 idiomas (es, en) + Translator
│   └── demo.py             corredor de marcos (guion) y corredor real
├── tests/test_replica.py   39 pruebas, sin terminal
└── docs/
    ├── marcos-92x26.txt        los 24 marcos del guion, 92×26
    └── marcos-60x18-ascii.txt  los mismos, apretados y en ASCII
```

## Probar

```bash
cd tui_replica
python3 -m pytest -q tests          # 39 passed
python3 main.py --guion             # vuelca el guion de marcos
python3 main.py                     # interactivo, si hay terminal
python3 main.py --guion --lang en --size 60x18 --ascii --out /tmp/m.txt
```

Solo biblioteca estándar. No necesita `incunable` instalado ni el paquete de
1.12.0: **no toca el producto**.

## Lo que hace

| pantalla | tecla | qué pasa |
|---|---|---|
| **inicio** | `↑↓` `PgUp/PgDn` `Inicio/Fin` · `←→` plegar · `Enter` analizar · `b` buscar · `r` ruta | lista de libros agrupada por carpeta, con tamaño |
| **diagnóstico** | `Enter` seguir · `Esc` volver | formato, páginas, cifrado, capa de texto, fuentes, imágenes, bloques, avisos |
| **opciones** | `↑↓` mover · `←→`/`Enter` cambiar · `c` convertir · `m` métricas · `Esc` | cinco formatos, carpeta, HTML intermedio, papel HTML/ebook, cuaderno, reparto, temas |
| **progreso** | — | una marca por formato: `[ ]` → `[OK]`, con «Convirtiendo… 2/3» |
| **resultado** | `i` · `c` · `Esc` | artefactos con bytes, fidelidad a cuatro decimales, avisos de metadatos |
| **config** | `↑↓` `←→` · `s` guardar | once claves con sus valores en palabras, no en clave interna |
| **fuentes** | `↑↓` · `+` `Supr` · `T` probar · `Enter` · `Esc` | carpetas de las que salen los libros |

Globales: `q` salir · `Ctrl+C` salir · `F1`/`?` ayuda modal · `s` ajustes · `f`
fuentes · `o` opciones · `i` inspeccionar · `c` convertir.

## Las ideas que se conservan

1. **La aplicación es pura.** `App.render(ancho, alto) -> list[str]`. No imprime,
   no lee, no espera. Todo lo demás (terminal, `select`, ANSI) es del corredor.
2. **El trabajo se hace después de pintar.** `handle()` deja `pending`; el
   corredor pinta el marco ocupado y solo entonces llama a `run_pending()`. Por
   eso el progreso se ve avanzar en vez de saltar al resultado.
3. **El color nunca informa solo.** Hay marcas `[OK]` `[!]` `[x]` `[ ]` y un
   puntero `>`. Con el tema apagado (`no_color`) se sigue entendiendo todo.
4. **Los textos no viven en las pantallas.** Las pantallas piden claves
   `tui.*`; el catálogo tiene español e inglés con **el mismo juego de claves**
   (una prueba lo comprueba).
5. **El determinismo es una propiedad, no una intención.** Mismo guion, mismos
   marcos, byte a byte (`test_el_guion_es_determinista`).
6. **Nada se sale del ancho.** Probado a 40, 60, 76, 92 y 120 columnas; a 40×12
   se recorta con `…`, no se rompe la línea.
7. **El pie dice qué hace cada tecla** en la pantalla en la que estás, y en
   terminales estrechas se recorta por el separador ` · ` sin dejar frases a
   medias.

## Las adaptaciones (esto es una réplica, no el producto)

| producto | aquí | por qué |
|---|---|---|
| `app.py` importa `cli`, `converter`, `theme` del paquete | `app.py` habla con `Backend` (`Protocol`) | la TUI no sabe convertir ni leer PDF: solo pide |
| textos en `resources/i18n/*.json` | `i18n.py`, catálogo en el módulo | un solo archivo, sin ruta de recursos |
| `Config` del producto con carga/guarda real | `dict` de configuración con `on_save_config` | guardar es del corredor |
| `theme.py` del producto con 10 paletas de documento | `theme.py` con las **7 paletas de terminal** (`high_contrast`, `amber`, `phosphor`, `phosphor_color`, `warm_white`, `dim_green`, `colorblind`) | son las que la TUI usa de verdad |
| lista de libros del sistema de archivos | `DemoBackend` con 8 libros fijos | determinismo y cero E/S |
| `keys.py`, `screen.py`, `term.py` | **copiados tal cual** | son la parte que no depende del producto |

Las pruebas lo vigilan: `app.py` no menciona `incunable`, ni `pdfminer`, ni
`pypdf` (`test_la_aplicacion_no_conoce_el_mundo_real`).

## Lo que no es

- No es una etapa de Incunable: no cambia versión, contrato ni paquete.
- No empaqueta nada y no entra en `release/`.
- No discute el criterio de la etapa en curso (el EPUB de 1.12.0, la
  universalidad, `XXXX` fuera del libro). Es un paréntesis aparte.

El guion completo, marco a marco, está en `docs/marcos-92x26.txt`. La
especificación para reconstruir todo esto desde cero, sin ver este código, está
en [`PROMPT.md`](PROMPT.md).
