# -*- coding: utf-8 -*-
"""Fichas de las series 1–4: cyberpunk, minority, juego y pipboy.

Cada ficha es un dict con lo que la página necesita: identidad, paleta con
procedencia, inventario de pantallas, la técnica que la distingue, qué copiar,
qué no copiar y un fragmento real de su código.
"""

SERIES_A = [
    # ------------------------------------------------------------------ 1
    {
        "clave": "cyberpunk",
        "orden": "01",
        "nombre": "Cyberpunk",
        "lema": "Neón sobre negro, y la primera piedra del motor",
        "script": "cyberpunk/cyberpunk.py",
        "genera": "cyberpunk.html · cyberpunk.txt (6 pantallas, 100×30)",
        "origen": "inventada",
        "unidad": "celda",
        "colores": [
            ("fondo", "#04070c", "inventado"), ("texto", "#9fe8ff", "inventado"),
            ("tenue", "#4a7f8f", "inventado"), ("fantasma", "#26404a", "inventado"),
            ("rejilla", "#17414f", "inventado"), ("título", "#00f0ff", "inventado"),
            ("magenta", "#ff2ec4", "inventado"), ("ok", "#39ff88", "inventado"),
            ("aviso", "#ffd400", "inventado"), ("error", "#ff2e63", "inventado"),
        ],
        "variantes": "5 paletas: neón · magenta · fósforo · ámbar · mono",
        "pantallas": [
            ("01", "Arranque", "Logo en fuente de bloques, autodiagnóstico y biométrica."),
            ("02", "Intrusión", "Rejilla de pares hexadecimales; el camino se marca invirtiendo el fondo."),
            ("03", "Diagnóstico", "Barras horizontales y una serie temporal de un renglón."),
            ("04", "Mercado negro", "Tabla con columnas a la derecha y panel de detalle."),
            ("05", "Comms", "Tres paneles; el texto sin descifrar son `▒` de verdad."),
            ("06", "Visualizador", "62 columnas de espectro con `█` y remates `▁▂▃▄▅▆▇`."),
        ],
        "idea": """Nació fuera del proyecto de FFmpeg, como diversión, y se convirtió en el
        origen de todo lo demás: de aquí salió <b>el motor de celdas</b> que hoy comparten
        las ocho colecciones. Su regla de honestidad está en la cabecera del fichero: si
        algo se ve en la pantalla, se puede escribir con <span class="mono">sys.stdout.write</span>.
        No hay imágenes, ni transparencias, ni fuentes especiales.""",
        "tecnica": """El truco que la identifica es <b>la fuente de bloques del logo</b>: ocho
        glifos de 5 × 7 dibujados con <span class="mono">█</span> y un espacio, escritos a mano
        en un diccionario de cuarenta líneas. Es el ejemplo más limpio de que un logotipo en
        terminal no es una imagen: es una tabla de caracteres.
        <br><br>El segundo truco es de disciplina: <b>el color nunca informa solo</b>. Cada barra
        lleva su porcentaje escrito al lado; la fila elegida, además del fondo invertido, cambia
        de color de texto. Si mañana se imprime en un papel, la pantalla sigue diciendo lo mismo.""",
        "copiar": [
            "La fuente de bloques: 8 glifos, 40 líneas, sirve para cualquier logotipo corto.",
            "Las series de un renglón con <span class=\"mono\">▁▂▃▄▅▆▇█</span>: un gráfico temporal sin ejes.",
            "La selección por fondo invertido, que funciona incluso sin color.",
        ],
        "evitar": [
            "Inventar la paleta y presentarla como si fuera un dato. Aquí es legítimo porque es ficción declarada; en una herramienta real, no.",
            "El neón como sustituto de la jerarquía: el estilo tiene cuatro colores de acento y solo se sostiene porque cada uno tiene un papel fijo.",
        ],
        "fragmento": '''FUENTE = {
    "N": ["█  █", "██ █", "█ ██", "█  █", "█  █"],
    "E": ["████", "█   ", "███ ", "█   ", "████"],
    "U": ["█  █", "█  █", "█  █", "█  █", "████"],
    "R": ["████", "█  █", "███ ", "█ █ ", "█  █"],
}
# el logo se compone pegando cada glifo fila a fila''',
    },
    # ------------------------------------------------------------------ 2
    {
        "clave": "minority",
        "orden": "02",
        "nombre": "Minority Report",
        "lema": "Cristal: la jerarquía por el hueco y el trazo discontinuo",
        "script": "minority/minority.py",
        "genera": "minority.html · minority.txt (6 pantallas, 100×30)",
        "origen": "inventada",
        "unidad": "celda",
        "colores": [
            ("fondo", "#02060d", "inventado"), ("texto", "#dceaf7", "inventado"),
            ("tenue", "#7e9aae", "inventado"), ("filete", "#1d3346", "inventado"),
            ("cristal", "#0a161f", "inventado"), ("título", "#bfe6ff", "inventado"),
            ("hielo", "#e8f6ff", "inventado"), ("alerta", "#ff5d6c", "inventado"),
            ("ok", "#7ef0c0", "inventado"), ("aviso", "#ffc163", "inventado"),
        ],
        "variantes": "4 paletas: cristal · crepúsculo · óxido · mono",
        "pantallas": [
            ("01", "Sala de mando", "Predicciones del día, precog y actividad cortical."),
            ("02", "Scrub", "La línea temporal se recorre moviendo un cursor."),
            ("03", "Dosier cruzado", "Dos registros comparados campo a campo."),
            ("04", "Visión", "La predicción como fotograma: bloques y siluetas."),
            ("05", "Despacho", "Mapa de la ciudad con unidades desplegadas."),
            ("06", "Archivo", "La pantalla que se permite dudar: cifras y una serie."),
        ],
        "idea": """El segundo estilo y la prueba de que el motor era reutilizable: no se copió
        ni una línea, se importó. Donde cyberpunk pone neón sobre negro, aquí hay <b>paneles
        de cristal pálido flotando en una sala a oscuras</b>: marcos discontinuos
        <span class="mono">╌</span>, esquinas sueltas, tramas tenues y mucho aire.""",
        "tecnica": """La técnica es <b>separar sin cerrar</b>. Un marco continuo dice «esto es
        una caja»; un marco de guiones dice «esto flota». El <span class="mono">╌</span> deja
        pasar la mirada y aun así ordena. Las esquinas se dibujan una a una, sin lados: el panel
        se sugiere, no se encierra.
        <br><br>Y una corrección que quedó en el código: la trama <span class="mono">░</span>
        por todo el interior del panel <b>competía con el texto</b>. Hoy el relleno es plano y
        la trama solo aparece en los bordes. Es la regla de siempre: la legibilidad gana a la
        decoración.""",
        "copiar": [
            "El marco discontinuo <span class=\"mono\">╌</span> para paneles que no deben encerrar.",
            "El aire como jerarquía: dos columnas separadas por tres espacios leen mejor que dos columnas separadas por un marco.",
            "La cifra con su unidad siempre juntas (<span class=\"mono\">92 lpm</span>), que evita el error clásico de leer un número sin saber de qué.",
        ],
        "evitar": [
            "La trama de cristal sobre el texto: se probó, competía, se quitó.",
            "Los marcos de cristal en pantallas densas: con más de tres paneles, el hueco desaparece y solo queda ruido.",
        ],
        "fragmento": '''c.texto(x, y, "┌", estilo)                  # esquina suelta
c.texto(x + ancho - 1, y, "┐", estilo)
for columna in range(x + 1, x + ancho - 1):
    c.texto(columna, y, "╌", estilo)          # el lado no se cierra
c.texto(x + 2, y, f" {titulo} ", "title")''',
    },
    # ------------------------------------------------------------------ 3
    {
        "clave": "juego",
        "orden": "03",
        "nombre": "Juego / consola",
        "lema": "Del botón biselado al glifo de caja: vocabulario gráfico traducido",
        "script": "juego/juego.py",
        "genera": "juego.html · juego.txt (6 pantallas, 100×30)",
        "origen": "medida",
        "unidad": "celda",
        "colores": [
            ("fondo", "#131f2d", "medido"), ("panel", "#082873", "medido"),
            ("borde", "#1f6fac", "medido"), ("azul", "#0d90fa", "medido"),
            ("cian", "#44c8f9", "medido"), ("amarillo", "#e5d818", "medido"),
            ("rosa", "#da1e7d", "medido"), ("verde", "#05b769", "medido"),
            ("rojo", "#fd4299", "medido"),
        ],
        "variantes": "sin variantes: la paleta medida se usa tal cual",
        "pantallas": [
            ("01", "Acceso", "Menú con botones de tres filas y estado de recursos."),
            ("02", "Perfil", "Estadísticas en barras segmentadas, con leyenda."),
            ("03", "Tienda", "Rejilla de objetos; el precio y lo que se puede pagar."),
            ("04", "Mapa", "Rejilla de rutas con nodos `▣` y el jugador `►`."),
            ("05", "HUD de combate", "La más densa: vida, energía y daño a la vez."),
            ("06", "Pausa", "El menú modal sobre la partida congelada."),
        ],
        "idea": """La paleta <b>no está inventada</b>: sale de muestrear nueve regiones de una
        pieza vectorial de la serie «UI sci-fi» de Alamy (el enlace que pasó el usuario daba 404
        y se midió la pieza hermana). Es el primer ejercicio de este corpus en el que un color
        tiene un número detrás y no una opinión.""",
        "tecnica": """El trabajo real de esta serie fue <b>traducir vocabulario</b>. Una
        ilustración de interfaz tiene botones con bisel, barras con segmentos y marcos con doble
        trazo; en una terminal eso son tres decisiones concretas: marco
        <span class="mono">╔═╗</span>, botón de tres filas
        <span class="mono">▛▀▜ / ▌ ▐ / ▙▄▟</span> y barra <span class="mono">▮▯</span>.
        <br><br>La lección que queda es que <b>casi todo el vocabulario gráfico tiene un
        equivalente en glifos de caja</b>, y que el equivalente no es una imitación: es una regla
        que se aplica igual en las seis pantallas.""",
        "copiar": [
            "El botón de tres filas completo, con su versión enfocada y su versión pulsada.",
            "Las barras segmentadas <span class=\"mono\">▮▯</span>: se leen mejor que las continuas cuando hay pocos niveles.",
            "La leyenda explícita del mapa: ninguna forma se explica sola.",
        ],
        "evitar": [
            "Medir una ilustración y llamarlo «paleta de producto». Sirve para estudiar; una app real lee su tema.",
            "El rosa como color de «vida» sin comprobarlo en escala de grises: en este caso el rosa y el rojo tienen casi la misma luminancia.",
        ],
        "fragmento": '''MUESTRAS = {
    "fondo":  "#131f2d",   # región 1: el fondo
    "panel":  "#082873",   # región 2: el panel interior
    "borde":  "#1f6fac",   # región 3: el trazo luminoso
    "azul":   "#0d90fa",   # … nueve regiones, nueve números
}''',
    },
    # ------------------------------------------------------------------ 4
    {
        "clave": "pipboy",
        "orden": "04",
        "nombre": "Pip-Boy",
        "lema": "Un solo fósforo y cinco brillos: la restricción como sistema",
        "script": "pipboy/pipboy.py",
        "genera": "pipboy.html · pipboy.txt (6 pantallas, 100×30)",
        "origen": "medida",
        "unidad": "celda",
        "colores": [
            ("fondo", "#102e16", "medido"), ("tenue", "#1c5626", "medido"),
            ("medio", "#3d8a55", "medido"), ("claro", "#64b887", "medido"),
            ("pico", "#63e59f", "medido"),
        ],
        "variantes": "sin variantes: cinco niveles y ninguno más",
        "pantallas": [
            ("01", "STATS", "El muñeco de habilidades y la barra PWR con escala."),
            ("02", "ITEMS", "Inventario con peso, valor y detalle con barras."),
            ("03", "DATA", "Misiones con casillas `[ ] [>]` y barra de avance."),
            ("04", "RADIO", "Emisoras, sintonía y nivel de señal."),
            ("05", "STATUS", "Estado de las extremidades, salud y radiación."),
            ("06", "Arranque", "La pantalla de encendido del tubo."),
        ],
        "idea": """Cinco verdes medidos sobre una captura real del Pip-Boy 3000. Y eso es
        <b>todo</b> el sistema de color: no hay un solo acento ajeno. La jerarquía se hace
        subiendo o bajando el brillo, como en un tubo de rayos catódicos de verdad, donde no
        existe otro canal que la intensidad del haz.""",
        "tecnica": """Es el mejor ejemplo del corpus de que <b>la restricción produce carácter</b>.
        Cinco niveles obligan a decidir qué es cada cosa: el fondo no compite, el tenue es
        mobiliario, el medio es texto, el claro es énfasis y el pico es el único que grita. Todo
        lo demás —corchetes solo en los extremos, títulos con filetes
        <span class="mono">━━━ STATS ━━━</span>, pestañas con la activa en vídeo inverso, reglas
        de escala <span class="mono">└──┴──┘</span>— son formas, no colores.""",
        "copiar": [
            "Los cinco niveles como escala declarada: un solo matiz, cinco papeles.",
            "La regla de escala <span class=\"mono\">└──┴──┘</span> con su marca de porcentaje: da referencia sin barras.",
            "El vídeo inverso para la pestaña activa, que sobrevive al blanco y negro.",
        ],
        "evitar": [
            "Usar el brillo para codificar <i>categorías</i>: cinco brillos dicen importancia, no dicen «esto es un error y aquello una advertencia». Para eso hace falta forma o texto.",
            "Añadir un sexto verde para «destacar algo»: rompe el sistema entero.",
        ],
        "fragmento": '''FOSFORO = {
    "fondo": "#102e16",   # el tubo apagado
    "tenue": "#1c5626",   # mobiliario: filetes y marcos
    "medio": "#3d8a55",   # texto
    "claro": "#64b887",   # énfasis
    "pico":  "#63e59f",   # el único que grita
}''',
    },
]
