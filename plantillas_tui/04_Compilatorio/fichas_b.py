# -*- coding: utf-8 -*-
"""Fichas de las series 5–8: reactor, nier, pragmata y las siete apps reales."""

SERIES_B = [
    # ------------------------------------------------------------------ 5
    {
        "clave": "reactor",
        "orden": "05",
        "nombre": "Reactor",
        "lema": "El chaflán identifica; el ASCII de 7 bits demuestra",
        "script": "reactor/reactor.py",
        "genera": "reactor.html · reactor.txt · reactor-ascii.html · reactor-ascii.txt",
        "origen": "medida",
        "unidad": "celda",
        "colores": [
            ("fondo", "#090d18", "medido"), ("malla", "#0d2a33", "derivado"),
            ("trazo", "#11565e", "derivado"), ("borde", "#14898b", "medido"),
            ("cian", "#1ad3d6", "medido"), ("pico", "#90f4ec", "medido"),
            ("teal", "#25a39f", "medido"), ("naranja", "#f76c0a", "medido"),
            ("rojo", "#f00001", "medido"), ("gris", "#424345", "medido"),
            ("gris2", "#3d4547", "medido"),
        ],
        "variantes": "una sola paleta y una versión entera en ASCII de 7 bits",
        "pantallas": [
            ("01", "Energía", "Cabecera achaflanada, registro del escaneo y 95 % gigante."),
            ("02", "Memoria", "Volcado con barras grises y bloque legible."),
            ("03", "Unidades", "Tarjetas con número de serie y estado."),
            ("04", "Motores", "Cuatro triángulos de aviso, uno por estado."),
            ("05", "Código", "El bloque de código con su retícula de fondo."),
            ("06", "Error", "El único rojo de la serie, y por eso funciona."),
        ],
        "idea": """La referencia que dio el usuario era una pieza de ArtStation de 1800 × 1201 con
        paneles de reactor. Su rasgo más reconocible no es el color: es <b>la forma de la
        cabecera</b>, que sobresale una columna y acaba en diagonal. Y hay un detalle que
        sorprende al medirla: <b>la pieza no tiene blanco</b>. Son tres canales y un gris.""",
        "tecnica": """El chaflán se dibuja con tres líneas: filete superior que acaba en
        <span class="mono">╲</span>, filete inferior que acaba en <span class="mono">╱</span> y
        una placa de número <span class="mono">[00]</span> al principio. Con eso, seis pantallas
        distintas se reconocen como la misma familia aunque cambie todo lo demás.
        <br><br>Y la técnica que debería tener toda serie: <b>una versión completa en ASCII de
        7 bits</b>. <span class="mono">reactor-ascii.html</span> es la misma colección sin un
        solo glifo de dibujo de cajas, sin bloques y sin tildes, con un <span class="mono">.txt</span>
        que no lleva <i>ningún</i> código de escape. Si al quitarle el color y los glifos sigue
        diciendo lo mismo, el diseño estaba en la información.""",
        "copiar": [
            "El chaflán de tres líneas y la placa <span class=\"mono\">[00]</span>: identidad por forma, no por color.",
            "La tabla de degradación <span class=\"mono\">TABLA_ASCII</span> completa: es el ejercicio que casi nadie hace.",
            "Las franjas de peligro a 45°: <span class=\"mono\">╱</span> desplazadas una columna por fila.",
        ],
        "evitar": [
            "Girar un elemento 90° «como en la referencia»: en celdas no se puede, y hay que decirlo en vez de fingir que se hizo.",
            "Confundir el chaflán con un adorno: si se quita, la serie deja de ser reconocible; si se repite en cada borde, cansa.",
        ],
        "fragmento": '''c.texto(x, y, "┌" + "─" * (ancho - 1) + "╲", "borde")      # superior
c.texto(x, y + 2, "└" + "─" * (ancho - 1) + "╱", "borde")    # inferior
c.texto(x + 2, y + 1, "[00]  E N E R G Y   R E A C T O R", "borde")''',
    },
    # ------------------------------------------------------------------ 6
    {
        "clave": "nier",
        "orden": "06",
        "nombre": "NieR: Automata",
        "lema": "Matriz de puntos: cambiar la unidad cambia la categoría",
        "script": "nier/nier.py · nier/braille.py",
        "genera": "nier.html · nier.txt · vista/01–06.png",
        "origen": "medida",
        "unidad": "punto (braille 2×4)",
        "colores": [
            ("papel", "#c3bea6", "medido"), ("tinta", "#504d44", "medido"),
            ("tinta2", "#7e7b6b", "medido"), ("línea", "#d4ceb5", "medido"),
            ("selección", "#49463e", "medido"), ("naranja", "#f1954c", "medido"),
            ("morado", "#451f4e", "medido"), ("blanco", "#dfdcd3", "medido"),
            ("rejilla", "#b1ac96", "derivado"),
        ],
        "variantes": "sin variantes: la primera serie clara del corpus",
        "pantallas": [
            ("01", "Menú (ITEM)", "El menú del juego, con pestañas y lista."),
            ("02", "Hackeo", "El minijuego de 9S: balas y zonas."),
            ("03", "Chips", "Ranuras, coste y descripción."),
            ("04", "Mapa", "El mapa de puntos con el jugador y los objetivos."),
            ("05", "Máquina", "El registro de la máquina, en matriz."),
            ("06", "Título", "El rótulo del juego, dibujado punto a punto."),
        ],
        "idea": """Aquí no se dibuja con celdas: se dibuja con <b>puntos</b>. Una celda con un
        carácter Braille (U+2800–U+28FF) contiene una matriz de 2 × 4 puntos, así que un lienzo
        de 100 × 30 celdas son <b>200 × 120 puntos</b>. Ese es el orden de magnitud de un cartel
        de puntos real, no una imitación a ojo. Es la primera serie clara del corpus: papel
        beige con tinta oscura, sin fósforo ni cristal.""",
        "tecnica": """El cambio de unidad es lo que hace la serie distinta. Con puntos, el texto
        no se puede componer con la fuente del sistema: hay que dibujar una <b>fuente 5 × 7</b>
        propia, sin minúsculas ni tildes, porque los paneles de puntos no tienen tildes.
        <br><br>Y hay tres límites que el medio impone y que el fichero declara en vez de
        disimular: <b>un color por celda</b> (los ocho puntos de una celda comparten color, porque
        en una terminal el color es de la celda); <b>sin fondo encendido</b> (el braille enciende
        puntos sobre vacío, no apaga puntos sobre una superficie luminosa: por eso el vídeo
        inverso se hace apagando puntos dentro de una barra encendida); y <b>no es texto</b>
        (no se selecciona ni se copia).""",
        "copiar": [
            "El mapeo braille: ocho puntos por celda, con su máscara de bits.",
            "La fuente 5×7 escrita como cadenas de <span class=\"mono\">0</span> y <span class=\"mono\">1</span>: legible y editable.",
            "La declaración de límites al principio del módulo: el mejor comentario de todo el corpus.",
        ],
        "evitar": [
            "Usar braille para texto corrido: a 5×7 puntos solo caben rótulos y cifras.",
            "Prometer selección o copia en una pantalla de puntos: es una imagen, no texto.",
            "Escribir un color en dos sitios: el docstring de <span class=\"mono\">nier.py</span> dice <span class=\"mono\">#c7c2aa</span> y el diccionario aplica <span class=\"mono\">#c3bea6</span>. Manda el diccionario, porque es el que se pinta.",
        ],
        "fragmento": '''# una celda braille = 2 × 4 puntos → 100 × 30 celdas = 200 × 120 puntos
BITS = ((0x01, 0x08), (0x02, 0x10), (0x04, 0x20), (0x40, 0x80))

def celda(puntos: set[tuple[int, int]]) -> str:
    valor = 0
    for (x, y) in puntos:
        valor |= BITS[y][x]
    return chr(0x2800 + valor)''',
    },
    # ------------------------------------------------------------------ 7
    {
        "clave": "pragmata",
        "orden": "07",
        "nombre": "Pragmata",
        "lema": "Cuando el color trabaja, hay que resolver el daltonismo",
        "script": "pragmata/pragmata.py",
        "genera": "pragmata.html · pragmata.txt (6 pantallas, 100×30)",
        "origen": "medida",
        "unidad": "celda",
        "colores": [
            ("fondo", "#0b151d", "medido"), ("línea", "#2e596b", "medido"),
            ("cian", "#4d9ec4", "medido"), ("pico", "#94defb", "medido"),
            ("blanco", "#d9efff", "medido"), ("gris", "#7a8ea1", "medido"),
            ("verde EXE", "#69b66e", "medido"), ("amarillo", "#e2d922", "medido"),
            ("ámbar", "#f3b248", "medido"), ("naranja", "#e9983f", "medido"),
            ("rojo", "#d54d59", "medido"), ("morado", "#856ad1", "medido"),
        ],
        "variantes": "2 paletas: la medida y una para deuteranopía",
        "pantallas": [
            ("01", "Combate", "Enemigo con escudo y la rejilla de Diana al lado."),
            ("02", "Hackeo", "El camino de nodo en nodo, que es el juego."),
            ("03", "Unit Printer", "El menú de impresión con sus materiales."),
            ("04", "Diana", "La rejilla a tamaño completo."),
            ("05", "Estación", "Plano de los seis módulos con el apagón en rojo."),
            ("06", "Traje", "Integridad por zonas y selector de armas."),
        ],
        "idea": """A diferencia de las series de fósforo, aquí <b>el color hace un trabajo</b>:
        verde es el nodo meta, amarillo la habilidad elegida, rojo el daño, morado lo raro. Doce
        colores medidos sobre dos capturas del juego. Y como el color codifica, la serie trae una
        <b>segunda paleta para deuteranopía</b> que cambia el par verde/rojo por cian/ámbar.""",
        "tecnica": """El juego ya es una cuadrícula —el hackeo de Diana se juega trazando un
        camino de nodo en nodo— así que la terminal no disfraza la interfaz: <i>es</i> la
        interfaz. Los marcos <span class="mono">╱─ … ─╲</span> toman la diagonal del HUD y las
        cifras llevan su etiqueta al lado.
        <br><br>La lección transferible es la de la accesibilidad: <b>si un color significa algo,
        necesita una alternativa</b>. Aquí la alternativa es una paleta conmutable; en otros
        casos basta con añadir la forma o el texto. Lo que no vale es confiar en que todo el mundo
        distingue el verde del rojo.""",
        "copiar": [
            "El par de paletas conmutables y el conmutador en el propio HTML.",
            "La rejilla de nodos con marcas distintas por tipo (<span class=\"mono\">+ * # %</span>): forma y color a la vez.",
            "La etiqueta de sector y fecha en la cabecera, que da contexto sin ocupar cuerpo.",
        ],
        "evitar": [
            "Usar doce colores porque hay doce cosas: aquí cada color tiene un papel fijo y declarado.",
            "Copiar los valores medidos como relleno: son <i>picos</i> de brillo sobre cristal translúcido, y el color plano real es algo más apagado.",
        ],
        "fragmento": '''PRAG = {"fondo": "#0b151d", "verde": "#69b66e", "rojo": "#d54d59", …}

#: la misma interfaz, sin depender del par verde/rojo
DEUTERANOPIA = {"verde": "#4d9ec4", "rojo": "#f3b248"}''',
    },
    # ------------------------------------------------------------------ 8
    {
        "clave": "tui",
        "orden": "08",
        "nombre": "Las siete apps reales",
        "lema": "Cuando la app existe, la paleta se lee; no se inventa",
        "script": "tui/series.py · tui/apps1.py · tui/apps2.py",
        "genera": "7 HTML · 7 TXT · indice.html · series.txt (21 pantallas)",
        "origen": "leída y medida",
        "unidad": "celda",
        "colores": [
            ("btop", "14 colores", "leídos de night-owl.theme"),
            ("ncdu", "10 colores", "medidos de una captura"),
            ("gitui", "14 colores", "medidos"),
            ("bagels", "13 colores", "medidos"),
            ("posting", "19 colores", "medidos"),
            ("castero", "10 colores", "medidos"),
            ("fx", "11 colores", "suposición declarada"),
        ],
        "variantes": "91 colores: 11 leídos · 30 medidos · 29 derivados · 21 heredados",
        "pantallas": [
            ("01", "btop", "Degradado como información: verde, ámbar y rojo según carga."),
            ("02", "ncdu", "Cero color propio: identidad tipográfica y barras de `#`."),
            ("03", "gitui", "El color clasifica estados de git; el conflicto se lee."),
            ("04", "bagels", "Calendario y barras: el color hace de leyenda."),
            ("05", "posting", "El color va al verbo HTTP y al tipo del valor JSON."),
            ("06", "castero", "Tres columnas sin marcos: el espacio hace la separación."),
            ("07", "fx", "Ni paleta ni cromo: el JSON y los números de línea."),
        ],
        "idea": """La diferencia con las siete series anteriores no es de código sino de
        criterio: <b>estas apps existen</b>, así que su paleta no se inventa ni se mide a ojo —
        se lee del fichero de tema de la app (btop trae 29) o se saca del histograma de una
        captura, que en una TUI plana sí funciona. Tres pantallas por app, veintiuna en total.""",
        "tecnica": """El corpus se organiza alrededor de una pregunta que ninguna de las series
        anteriores se hacía: <b>¿de dónde sale este color?</b> Cada rol lleva su procedencia y
        la frase que la defiende. btop es el caso limpio (se copia el valor del fichero); ncdu es
        el caso cero (no elige colores, hereda los del terminal); fx es el caso incómodo (la
        paleta es una suposición y se declara como tal).
        <br><br>Y una tabla que sirve de examen: cruzar las nueve piezas del núcleo con las siete
        apps. Ninguna puede dejar de decidir en ninguna.""",
        "copiar": [
            "El lector de temas: <span class=\"mono\">parsear</span> un <span class=\"mono\">.theme</span> y construir la paleta desde el fichero.",
            "La tabla de procedencia: rol, valor, uso y origen en la misma fila.",
            "La verificación de que todo estilo pintado existe en la paleta.",
        ],
        "evitar": [
            "Inventar los colores de una app que existe: se lee su tema o se mide su captura.",
            "Usar los valores medidos como si fueran rellenos: en capturas con degradado son picos.",
        ],
        "fragmento": '''def leer_tema(ruta: Path) -> dict[str, str]:
    """btop declara sus colores en `clave = "#rrggbb"`. Se copian, no se estiman."""
    paleta = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if "=" in linea and linea.strip().startswith(("main_bg", "main_fg", "title", "hi_fg")):
            clave, _, valor = linea.partition("=")
            paleta[clave.strip()] = valor.strip().strip('"')
    return paleta''',
    },
]
