#!/usr/bin/env python3
"""Las otras tres: posting, castero y fx."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402
from tui.comun import App, barra, caja, pie, titulo_ventana  # noqa: E402


# ---------------------------------------------------------------------------
# posting · paleta MEDIDA de una captura
# ---------------------------------------------------------------------------
def posting_peticion(c: Lienzo) -> None:
    """La barra de pestañas arriba, la URL y el título; debajo, las cabeceras a la
    izquierda y la descripción de la petición a la derecha."""
    c.texto(0, 0, " atlas-api", "titulo")
    c.texto(70, 0, "◆ local", "metodo_get")
    c.texto(82, 0, "you@devbox", "tenue")

    for indice, (metodo, nombre, activo) in enumerate((("GET", "List users", True),
                                                      ("POS", "Create user", False),
                                                      ("DEL", "Delete user", False))):
        x = 1 + indice * 22
        c.texto(x, 2, f" {metodo} {nombre} ", "pestana_activa" if activo else "tenue")

    c.texto(1, 4, "GET", "metodo_get")
    c.texto(5, 4, "${BASE_URL}/users?page=1&per_page=20", "texto")
    c.relleno(70, 4, 7, 1, "estado_pildora")
    c.texto(71, 4, "200", "estado_ok")
    c.relleno(78, 4, 5, 1, "estado_pildora")
    c.texto(88, 4, " Send ", "boton_enviar")
    c.texto(6, 5, "→ http://localhost:8000/users?page=1&per_page=20", "tenue")

    for indice, (nombre, activo) in enumerate((("Headers", True), ("Body", False),
                                              ("Path", False), ("Query", False),
                                              ("Auth", False), ("Options", False))):
        c.texto(1 + indice * 9, 7, nombre, "titulo" if activo else "tenue")

    caja(c, 0, 8, 70, 20, "Headers")
    cabeceras = [("[x]", "Accept", "application/json"),
                 ("[x]", "Authorization", "Bearer ${API_TOKEN}"),
                 ("[x]", "User-Agent", "Posting/3.0"),
                 ("[x]", "Cache-Control", "no-cache"),
                 ("[x]", "X-Request-ID", "${uuid}"),
                 ("[x]", "X-Client-Version", "2026.10"),
                 ("[x]", "Origin", "https://app.example.com"),
                 ("[ ]", "Accept-", "← escribiendo")]
    for indice, (marca, nombre, valor) in enumerate(cabeceras):
        fila = 9 + indice
        if indice == 3:
            c.relleno(1, fila, 68, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(2, fila, marca, "metodo_get" if indice != 7 else "tenue")
        c.texto(6, fila, nombre, estilo)
        c.texto(24, fila, valor, estilo)
        c.texto(66, fila, "×", "tenue")
    c.texto(2, 18, "sugerencias", "tenue")
    c.texto(14, 18, "Accept-Charset  Accept-Encoding", "acento")
    c.texto(2, 20, "8 cabeceras · 1 desactivada", "tenue")
    c.texto(2, 22, "Ctrl+Space alterna · ^j envía · ^s guarda", "tenue")
    c.texto(2, 24, "↑↓ mover · ^d duplicar · ⌫ borrar", "tenue")

    caja(c, 72, 8, 28, 20, "Request")
    c.texto(74, 9, "método", "tenue")
    c.texto(74, 10, "GET", "metodo_get")
    c.texto(74, 12, "estado", "tenue")
    c.texto(74, 13, "200 OK", "estado_ok")
    c.texto(74, 15, "guardada en", "tenue")
    c.texto(74, 16, "users/", "texto")
    c.texto(74, 17, "  list-users.yaml", "texto")
    c.texto(74, 21, "Peticiones = ficheros:", "tenue")
    c.texto(74, 22, "se versionan con git.", "tenue")
    c.texto(74, 24, "× cierra la pestaña", "tenue")
    pie(c, [("^s", "guardar"), ("^j", "enviar"), ("^p", "comandos"), ("F1", "ayuda")])


def posting_respuesta(c: Lienzo) -> None:
    c.texto(0, 0, " atlas-api", "titulo")
    c.texto(70, 0, "◆ local", "metodo_get")
    c.texto(88, 0, "200 OK", "estado_ok")

    for indice, (nombre, activo) in enumerate((("Body", True), ("Headers", False),
                                              ("Cookies", False), ("Trace", False))):
        c.texto(1 + indice * 10, 2, nombre, "titulo" if activo else "tenue")
    c.texto(60, 2, "335 B en 42.00 ms", "tenue")
    c.relleno(84, 2, 8, 1, "estado_pildora")
    c.texto(85, 2, "200 OK", "estado_ok")

    caja(c, 0, 3, 100, 24, "")
    # cada línea se compone de tres piezas: sangría, clave y valor
    lineas = [(0, "{", None, "llave"),
              (2, '"users": [', None, "llave"),
              (4, "{", None, "llave"),
              (6, '"id":', "42", "numero"),
              (6, '"name":', '"Ada Lovelace"', "cadena"),
              (6, '"email":', '"ada@example.com"', "cadena"),
              (6, '"role":', '"admin"', "cadena"),
              (6, '"active":', "true", "numero"),
              (6, '"tags":', '["math", "code"]', "cadena"),
              (4, "},", None, "llave"),
              (4, "{", None, "llave"),
              (6, '"id":', "43", "numero"),
              (6, '"name":', '"Grace Hopper"', "cadena"),
              (6, '"email":', '"grace@example.com"', "cadena"),
              (6, '"role":', '"admin"', "cadena"),
              (6, '"active":', "false", "numero"),
              (6, '"tags":', '["navy", "cobol"]', "cadena"),
              (4, "}", None, "llave"),
              (2, "],", None, "llave"),
              (2, '"total":', "2", "numero"),
              (2, '"next":', "null", "tenue"),
              (0, "}", None, "llave")]
    for indice, (sangria, clave, valor, estilo) in enumerate(lineas):
        fila = 4 + indice
        c.texto(2 + sangria, fila, clave, "llave" if valor else estilo)
        if valor:
            c.texto(2 + sangria + len(clave) + 1, fila, valor, estilo)
    c.texto(2, 25, 'application/json · 22 líneas · 2 objetos · claves coloreadas por tipo', "tenue")
    pie(c, [("↑↓", "línea"), ("/", "buscar"), ("y", "copiar"), ("F1", "ayuda")])


def posting_coleccion(c: Lienzo) -> None:
    c.texto(0, 0, " atlas-api", "titulo")
    c.texto(74, 0, "Requests · History", "tenue")

    caja(c, 0, 2, 44, 26, "Requests")
    c.texto(2, 3, "/ buscar petición", "tenue")
    # (profundidad, nombre o None si es carpeta, método)
    arbol = [(0, "auth/", None), (1, "Current user", "GET"), (1, "Login", "POS"),
             (1, "Refresh session", "POS"), (1, "Revoke session", "DEL"),
             (0, "projects/", None), (1, "Get project", "GET"),
             (1, "List projects", "GET"), (1, "Create project", "POS"),
             (0, "teams/", None), (1, "List teams", "GET"), (1, "Team members", "GET"),
             (0, "users/", None), (1, "Get user", "GET"), (1, "List users", "GET"),
             (1, "Delete user", "DEL")]
    for indice, (nivel, nombre, metodo) in enumerate(arbol):
        fila = 4 + indice
        if nombre == "List projects":
            c.relleno(1, fila, 42, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        if metodo is None:
            c.texto(2, fila, "▾ " + nombre, "titulo")
        else:
            c.texto(2, fila, metodo, f"metodo_{metodo.lower()}" if estilo == "texto" else estilo)
            c.texto(6, fila, nombre, estilo)
            c.texto(39, fila, "→", "tenue")

    caja(c, 46, 2, 54, 26, "GET List users")
    c.texto(48, 3, "GET ${BASE_URL}/users?page=1", "texto")
    c.texto(48, 5, "Headers", "titulo")
    c.texto(58, 5, "8", "numero")
    c.texto(48, 6, "Authorization  Bearer ${API_TOKEN}", "texto")
    c.texto(48, 7, "Accept  application/json", "texto")
    c.texto(48, 9, "Respuesta", "titulo")
    c.texto(48, 10, "200 OK · 335 B · 42.00 ms", "estado_ok")
    c.texto(48, 12, "Última vez", "titulo")
    c.texto(48, 13, "hoy 22:31:04", "texto")
    c.texto(48, 15, "Guardada en", "titulo")
    c.texto(48, 16, "users/list-users.yaml", "cadena")
    c.texto(48, 18, "El árbol son ficheros YAML:", "tenue")
    c.texto(48, 19, "se editan con cualquier editor", "tenue")
    c.texto(48, 20, "y se versionan con git.", "tenue")
    c.texto(48, 22, "Verbos", "titulo")
    c.texto(56, 22, "GET", "metodo_get")
    c.texto(61, 22, "POS", "metodo_pos")
    c.texto(66, 22, "DEL", "metodo_del")
    c.texto(48, 24, "El color del verbo es lo único", "tenue")
    c.texto(48, 25, "que distingue una fila de otra.", "tenue")
    pie(c, [("↑↓", "petición"), ("⏎", "abrir"), ("^n", "nueva"), ("F1", "ayuda")])


POSTING = App(
    clave="posting",
    nombre="posting",
    comando="posting",
    descripcion="Cliente HTTP en el terminal: guarda cada llamada como un YAML, las organiza "
    "en árbol y muestra la respuesta con el JSON coloreado. Es el más denso de los siete y "
    "el que mejor enseña la regla: **el color va al verbo HTTP** —verde GET, naranja POST, "
    "rojo DELETE— y al tipo del valor JSON, no al marco.",
    fuente="**Medido** en un fotograma del GIF de presentación: fondo `#11131d` (47 % de "
    "los píxeles), barra lateral `#211e38`, campos `#282441` y `#3e3162`, rosa `#ff69b4` del "
    "botón Send y teal `#68f2d5` del código de respuesta con su fondo `#195552`. Los colores "
    "de sintaxis del JSON y los de cada verbo son **derivados** de esos acentos: en la "
    "captura se ven el rosa y el teal, no la escala entera.",
    paleta={"fondo": "#11131d", "texto": "#d5d6e0", "titulo": "#c8c9e8",
            "borde": "#3e3162", "tenue": "#9192aa", "pestana_activa": "#3e3162",
            "seleccion": "#3e3162", "sel_fg": "#ffffff", "acento": "#ff69b4",
            "metodo_get": "#68f2d5", "metodo_pos": "#ffb86c", "metodo_del": "#ff6e6e",
            "estado_ok": "#68f2d5", "estado_pildora": "#195552", "boton_enviar": "#ff69b4",
            "llave": "#8f8fa8", "cadena": "#9ece6a", "numero": "#ffb86c"},
    origen={"fondo": "medido", "texto": "derivado", "titulo": "medido", "borde": "medido",
            "tenue": "medido", "pestana_activa": "medido", "acento": "medido",
            "metodo_get": "derivado", "metodo_pos": "derivado", "metodo_del": "derivado",
            "estado_ok": "medido", "estado_pildora": "medido", "boton_enviar": "medido", "llave": "derivado",
            "cadena": "derivado", "numero": "derivado"},
    uso={"fondo": "fondo", "texto": "texto", "titulo": "pestaña activa y cabeceras",
         "borde": "marco de las cajas", "tenue": "ayudas", "acento": "autocompletado",
         "metodo_get": "GET", "metodo_pos": "POST", "metodo_del": "DELETE",
         "estado_ok": "código de respuesta", "estado_pildora": "fondo de la píldora 200 OK", "boton_enviar": "botón Send",
         "llave": "claves del JSON", "cadena": "cadenas", "numero": "números y booleanos"},
    pantallas=[("01", "Petición", "Pestañas de petición, la barra del método con su URL y la "
                "tabla de cabeceras con una escribiéndose.", posting_peticion),
               ("02", "Respuesta", "El JSON con su color por tipo de valor, el tamaño y el "
                "tiempo de la respuesta.", posting_respuesta),
               ("03", "Colección", "El árbol de peticiones y el detalle de la elegida. Aquí el "
                "color clasifica verbos.", posting_coleccion)],
)


# ---------------------------------------------------------------------------
# castero · paleta MEDIDA (One Dark, el tema que usa)
# ---------------------------------------------------------------------------
def castero_feeds(c: Lienzo) -> None:
    c.texto(0, 0, "castero · Paused [00:12:32/00:38:26]: Buying Attention (+5 in queue)",
            "titulo")

    for x, ancho, nombre in ((0, 32, "Feeds"), (33, 44, "Episodes"), (78, 22, "Metadata")):
        c.texto(x, 2, nombre, "titulo")
    c.texto(0, 3, "─" * 100, "tenue")

    feeds = ["Embedded", "NPR Politics Podcast", "Bullseye with Jesse Thorn", "Hidden Brain",
             "Invisibilia", "Tiny Desk Concerts", "Alt.Latino", "Song Travels Express",
             "How To Do Everything", "Crosscurrents", "Planet Money", "Radiolab",
             "99% Invisible", "The Daily", "Reply All", "Switched on Pop",
             "Song Exploder", "Code Switch"]
    for indice, nombre in enumerate(feeds):
        fila = 4 + indice
        if indice == 3:
            c.relleno(0, fila, 32, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(0, fila, nombre, estilo)

    episodios = ["Tunnel Vision", "Crickets and Cannibals", "The Lonely American Man",
                 "Radio Replay: The Mind of the Village", "Think Fast with Daniel Kahneman",
                 "Men: 45, Women: 0", "Counting Other People's Blessings",
                 "When Did Marriage Become So Hard?", "Why Now?", "Lost in Translation",
                 "Radio Replay: The Power Hour", "Give Me Your Tired...",
                 "The Science of Grit", "Peak Performance", "The Value of Solitude",
                 "Fighting the Status Quo", "The Benefits of Not Belonging",
                 "What Makes a Good Life?"]
    for indice, nombre in enumerate(episodios):
        fila = 4 + indice
        if indice == 9:
            c.relleno(33, fila, 44, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(33, fila, nombre[:44], estilo)

    c.texto(78, 4, "Buying Attention", "jugando")
    c.texto(78, 5, "Mon, 01 Jan 2018", "texto")
    c.texto(78, 4 + 2, "", "texto")
    c.texto(78, 7, "Description:", "titulo")
    for indice, linea in enumerate(("Have you ever opened", "your computer with the",
                                    "intention of sending", "one email - only to",
                                    "spend an hour scrolling", "through social media?")):
        c.texto(78, 8 + indice, linea, "texto")
    c.texto(78, 15, "Copyright:", "titulo")
    c.texto(78, 16, "2015 NPR", "texto")
    c.texto(78, 18, "Duración:", "titulo")
    c.texto(78, 19, "00:38:26", "texto")
    c.texto(78, 21, "Descargado:", "titulo")
    c.texto(78, 22, "sí · 24,1 MiB", "verde")
    c.texto(0, 24, "↑↓ feed · ⇥ episodios · ⏎ reproducir · d descargar", "tenue")
    c.texto(0, 25, "r marcar escuchado · u actualizar feeds · / buscar", "tenue")
    c.texto(0, 29, "Processed 25 feeds with 2687 total episodes -- Press h for help", "texto")


def castero_reproductor(c: Lienzo) -> None:
    c.texto(0, 0, "castero · Reproduciendo", "titulo")
    c.texto(70, 0, "volumen 72 %", "tenue")

    caja(c, 0, 2, 100, 12, "Buying Attention")
    c.texto(2, 3, "Hidden Brain · Mon, 01 Jan 2018 21:00:00 -0500", "tenue")
    c.texto(2, 5, "00:12:32", "texto")
    barra(c, 11, 5, 70, 0.33, "naranja")
    c.texto(82, 5, "00:38:26", "texto")
    c.texto(2, 7, "▶", "jugando")
    c.texto(4, 7, "reproduciendo", "jugando")
    c.texto(20, 7, "· velocidad 1.0×", "tenue")
    c.texto(2, 9, "Espacio pausa · ← → 30 s · d descarga · q salir", "tenue")
    c.texto(2, 11, "Descripción:", "titulo")
    c.texto(2, 12, "Have you ever opened your computer with the intention of sending one", "texto")

    caja(c, 0, 15, 60, 13, "Cola · 5 episodios")
    cola = [("1", "Radio Replay: Fresh Starts", "00:41:02"),
            ("2", "I'm Right, You're Wrong", "00:35:18"),
            ("3", "Radio Replay: Don't Panic!", "00:38:44"),
            ("4", "Never Go To Vegas", "00:29:51"),
            ("5", "Kinder-Gardening", "00:33:07")]
    for indice, (numero, titulo, duracion) in enumerate(cola):
        fila = 16 + indice
        c.texto(2, fila, numero, "tenue")
        c.texto(4, fila, titulo, "texto")
        c.texto(50, fila, duracion, "tenue")
    c.texto(2, 23, "q quitar · J/K mover · ⏎ reproducir", "tenue")

    caja(c, 62, 15, 38, 13, "Progreso")
    c.texto(64, 16, "escuchado", "tenue")
    c.texto(76, 16, "12:32", "texto")
    c.texto(64, 17, "restante", "tenue")
    c.texto(76, 17, "25:54", "texto")
    c.texto(64, 19, "marcas de posición", "tenue")
    c.texto(64, 20, "◇◇◇◇◆◇◇◇◇◇", "naranja")
    c.texto(64, 22, "guardado en", "tenue")
    c.texto(64, 23, "~/.local/share/castero", "texto")
    c.texto(0, 29, "[h] ayuda · [q] salir · [p] pausa", "texto")


def castero_descargas(c: Lienzo) -> None:
    c.texto(0, 0, "castero · Descargas", "titulo")
    c.texto(72, 0, "2 en curso · 1 en cola", "tenue")

    caja(c, 0, 2, 100, 10, "En curso")
    for indice, (nombre, porcentaje, resto) in enumerate((("Buying Attention.mp3", 0.62, "14:42"),
                                                          ("Fresh Starts.mp3", 0.18, "33:31"))):
        fila = 3 + indice * 3
        c.texto(2, fila, nombre, "texto")
        c.texto(40, fila, "1,2 MiB/s" if indice == 0 else "0,4 MiB/s", "tenue")
        c.texto(52, fila, "quedan 00:" + resto, "tenue")
        c.texto(70, fila, "de 24,1 MiB", "tenue")
        barra(c, 2, fila + 1, 66, porcentaje, "naranja")
        c.texto(70, fila + 1, f"{int(porcentaje * 100):3d} %", "texto")


    caja(c, 0, 13, 100, 8, "Terminadas")
    for indice, (nombre, duracion) in enumerate((("Tunnel Vision.mp3", "00:34:18"),
                                                 ("Crickets and Cannibals.mp3", "00:34:18"),
                                                 ("The Lonely American Man.mp3", "00:35:02"))):
        fila = 14 + indice
        c.texto(2, fila, "[ok]", "verde")
        c.texto(7, fila, nombre, "texto")
        c.texto(42, fila, duracion, "tenue")
        c.texto(56, fila, "8,1 MiB", "tenue")

    caja(c, 0, 22, 100, 6, "En cola")
    c.texto(2, 23, "1", "tenue")
    c.texto(5, 23, "Why Now?.mp3", "texto")
    c.texto(42, 23, "esperando turno", "tenue")
    c.texto(66, 23, "0 %", "tenue")
    c.texto(2, 25, "Solo se descarga uno a la vez: la cola respeta el orden del feed.", "tenue")
    c.texto(0, 28, "d descargar · x cancelar · h ayuda".ljust(100), "tenue")


CASTEREO = App(
    clave="castero",
    nombre="castero",
    comando="castero",
    descripcion="Cliente de podcasts con tres columnas —feeds, episodios, metadatos— que "
    "copia deliberadamente el diseño de las primeras versiones de iTunes. Usa el tema One "
    "Dark y **casi no tiene color propio**: un naranja para los títulos y las barras, y "
    "todo lo demás es texto.",
    fuente="**Medido** de una captura: es One Dark otra vez (`#282c34` de fondo, `#d19a66` "
    "naranja para títulos y progreso, `#abb2bf` de texto, `#5c6370` de metadatos). castero "
    "no inventa paleta, usa la del tema: el color solo aparece donde hay algo que señalar.",
    paleta={"fondo": "#282c34", "texto": "#abb2bf", "titulo": "#d19a66",
            "tenue": "#5c6370", "naranja": "#d19a66", "jugando": "#e5c07b",
            "verde": "#98c379", "seleccion": "#d19a66", "sel_fg": "#282c34"},
    origen={"fondo": "medido", "texto": "medido", "titulo": "medido", "tenue": "medido",
            "naranja": "medido", "jugando": "medido", "verde": "derivado"},
    uso={"fondo": "fondo", "texto": "texto", "titulo": "cabeceras de columna",
         "tenue": "metadatos", "naranja": "progreso y barra", "jugando": "lo que suena",
         "verde": "descarga completa"},
    pantallas=[("01", "Feeds", "Las tres columnas de Castero, con el feed y el episodio "
                "elegidos en naranja.", castero_feeds),
               ("02", "Reproductor", "Lo que suena, su progreso y la cola.", castero_reproductor),
               ("03", "Descargas", "La cola de descargas con sus barras.", castero_descargas)],
)


# ---------------------------------------------------------------------------
# fx · sin paleta propia: hereda la del terminal
# ---------------------------------------------------------------------------
def fx_arbol(c: Lienzo) -> None:
    c.texto(0, 0, "fx respuesta.json", "titulo")
    c.texto(60, 0, "JSON · 29 líneas · modo interactivo", "tenue")

    caja(c, 0, 2, 100, 24, "")
    lineas = [
        (" 1", "{", "llave"),
        (" 2", '  "users": [', "llave"),
        (" 3", "    {", "llave"),
        (" 4", '      "id": 42,', "clave"),
        (" 5", '      "name": "Ada Lovelace",', "clave"),
        (" 6", '      "email": "ada@example.com",', "clave"),
        (" 7", '      "role": "admin",', "clave"),
        (" 8", '      "active": true,', "clave"),
        (" 9", '      "tags": ["math", "code"],', "clave"),
        ("10", "    },", "llave"),
        ("11", "    {", "llave"),
        ("12", '      "id": 43,', "clave"),
        ("13", '      "name": "Grace Hopper",', "clave"),
        ("14", '      "email": "grace@example.com",', "clave"),
        ("15", '      "role": "admin",', "clave"),
        ("16", '      "active": false,', "clave"),
        ("17", '      "tags": ["navy", "cobol"],', "clave"),
        ("18", "    }", "llave"),
        ("19", "  ],", "llave"),
        ("20", '  "total": 2,', "clave"),
        ("21", '  "next": null', "clave"),
        ("22", "}", "llave"),
    ]
    for indice, (numero, texto, estilo) in enumerate(lineas):
        fila = 3 + indice
        if indice == 12:
            c.relleno(1, fila, 98, 1, "seleccion")
            estilo = "seleccion"
        c.texto(1, fila, numero.rjust(3), "tenue")
        c.texto(6, fila, texto, estilo)
    c.texto(1, 26, "↑↓ mover · ⏎ plegar · / buscar · . script · q salir", "tenue")


def fx_busqueda(c: Lienzo) -> None:
    c.texto(0, 0, "fx respuesta.json", "titulo")
    c.texto(1, 2, "/", "titulo")
    c.texto(3, 2, "admin", "cadena")
    c.texto(9, 2, "  7 coincidencias en 3 claves", "tenue")

    caja(c, 0, 4, 100, 17, "Resultados")
    resultados = [("1", "users[0].role", "admin", "12"),
                  ("2", "users[1].role", "admin", "28"),
                  ("3", "users[2].role", "admin", "44"),
                  ("4", "users[0].email", "ada@example.com", "13"),
                  ("5", "users[1].email", "grace@example.com", "29"),
                  ("6", "users[3].email", "linus@example.com", "45"),
                  ("7", "meta.roles[]", "admin · editor · reader", "61")]
    for indice, (numero, ruta, valor, linea) in enumerate(resultados):
        fila = 5 + indice * 2
        if indice == 1:
            c.relleno(1, fila, 98, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(2, fila, numero, "tenue")
        c.texto(5, fila, ruta, "clave" if estilo == "texto" else estilo)
        c.texto(32, fila, valor, "cadena" if estilo == "texto" else estilo)
        c.texto(70, fila, f"línea {linea}", "tenue")
    c.texto(2, 19, "↑↓ mover · ⏎ saltar a la línea · esc cerrar", "tenue")

    caja(c, 0, 22, 100, 7, "Contexto")
    c.texto(2, 23, '      "role": "admin",', "clave")
    c.texto(2, 25, "La búsqueda no filtra el documento: salta a la línea.", "tenue")
    c.texto(2, 26, "n siguiente · N anterior · esc cerrar", "tenue")


def fx_script(c: Lienzo) -> None:
    c.texto(0, 0, "fx respuesta.json", "titulo")
    c.texto(72, 0, "pipeline · 3 pasos", "tenue")

    caja(c, 0, 2, 100, 9, "Entrada")
    c.texto(2, 3, "users", "clave")
    c.texto(8, 3, "· 4 objetos · 24 campos", "tenue")
    for indice, (nombre, correo, activo) in enumerate((("Ada Lovelace", "ada@example.com", "true"),
                                                      ("Grace Hopper", "grace@example.com", "false"),
                                                      ("Linus Torvalds", "linus@example.com", "true"),
                                                      ("Margaret Hamilton", "mh@example.com", "true"))):
        fila = 5 + indice
        c.texto(2, fila, str(indice + 1), "tenue")
        c.texto(5, fila, nombre.ljust(20), "texto")
        c.texto(26, fila, correo.ljust(20), "cadena")
        c.texto(48, fila, "activo " + activo, "numero")

    caja(c, 0, 12, 100, 7, "Script")
    c.texto(2, 13, ".users", "clave")
    c.texto(10, 13, ".filter(u => u.active)", "cadena")
    c.texto(38, 13, ".map(u => u.name)", "cadena")
    c.texto(2, 15, "▲ los tres pasos se aplican sin volver a leer el fichero", "tenue")
    c.texto(2, 16, "  el resultado se puede guardar como nuevo JSON", "tenue")

    caja(c, 0, 20, 100, 8, "Salida")
    c.texto(2, 21, "[", "llave")
    c.texto(2, 22, '  "Ada Lovelace",', "cadena")
    c.texto(2, 23, '  "Linus Torvalds",', "cadena")
    c.texto(2, 24, '  "Margaret Hamilton"', "cadena")
    c.texto(2, 25, "]", "llave")
    c.texto(2, 26, "3 de 4 · Grace Hopper se descarta por active: false", "tenue")


FX = App(
    clave="fx",
    nombre="fx",
    comando="fx respuesta.json",
    descripcion="Navegador de JSON con JavaScript: pliega y despliega, busca, y transforma con "
    "una línea de script sin salir del fichero. **No trae paleta**: usa los colores de tu "
    "terminal, que es exactamente el argumento de ncdu llevado al otro extremo.",
    fuente="Aquí no hay nada medido y conviene decirlo: de `fx` no teníamos captura y la app "
    "no define colores propios, así que la paleta es **derivada** del esquema por defecto del "
    "terminal del autor (One Dark). Es la única de las siete cuyo color no procede ni de un "
    "fichero ni de un píxel.",
    paleta={"fondo": "#282c34", "texto": "#abb2bf", "titulo": "#61afef",
            "tenue": "#5c6370", "llave": "#abb2bf", "clave": "#61afef",
            "cadena": "#98c379", "numero": "#d19a66",
            "seleccion": "#3e4451", "sel_fg": "#ffffff"},
    origen={"fondo": "derivado", "texto": "derivado", "titulo": "derivado", "tenue": "derivado",
            "llave": "derivado", "clave": "derivado", "cadena": "derivado", "numero": "derivado",
            "seleccion": "derivado"},
    uso={"fondo": "fondo", "texto": "llaves y puntuación", "titulo": "barra de estado",
         "tenue": "números de línea", "clave": "claves y rutas", "cadena": "valores",
         "numero": "números y booleanos"},
    pantallas=[("01", "Árbol", "El documento con números de línea, plegable y con la fila "
                "elegida marcada. Sin adornos: es JSON.", fx_arbol),
               ("02", "Búsqueda", "Una búsqueda con sus coincidencias y el contexto. fx no "
                "filtra: salta a la línea.", fx_busqueda),
               ("03", "Script", "Entrada, script y salida: la ventaja real de fx sobre un "
                "visor de JSON.", fx_script)],
)

APPS2 = [POSTING, CASTEREO, FX]
