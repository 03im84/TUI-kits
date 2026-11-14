#!/usr/bin/env python3
"""Cuatro de las siete: btop, ncdu, gitui y bagels."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402
from tui.comun import App, barra, caja, pie, rampa, titulo_ventana  # noqa: E402


# ---------------------------------------------------------------------------
# btop · paleta LEÍDA de los ficheros de tema que trae la propia app
# ---------------------------------------------------------------------------
def btop_panel(c: Lienzo) -> None:
    titulo_ventana(c, "btop++ 1.3.2 · panel", "titulo")
    c.texto(62, 0, "mem 12.4G/31.2G · swap 0B/8.0G", "tenue")

    caja(c, 0, 2, 50, 13, "cpu  ·  amd ryzen 7 5800x")
    nucleos = [0.18, 0.42, 0.77, 0.12, 0.55, 0.91, 0.30, 0.64]
    for indice, carga in enumerate(nucleos):
        fila = 3 + indice
        c.texto(2, fila, f"{indice:2d}", "tenue")
        llenos = round(carga * 30)
        barra(c, 5, fila, 30, carga,
              "cpu_alto" if carga > 0.8 else ("cpu_medio" if carga > 0.4 else "cpu_bajo"))
        c.texto(36, fila, f"{int(carga * 100):3d}%", "texto")
        c.texto(42, fila, "▁▄█▆▂" if carga > 0.5 else "▁▂▁▃▁", "cpu_medio")
    c.texto(2, 11, "cpu", "titulo")
    c.texto(6, 11, "41%", "hi")
    barra(c, 11, 11, 12, 0.41, "hi")
    c.texto(25, 11, "52 °C", "texto")
    c.texto(32, 11, "3.2 GHz", "texto")
    c.texto(40, 11, "16 hilos", "tenue")

    caja(c, 52, 2, 48, 7, "memoria")
    c.texto(54, 3, "usada", "tenue")
    barra(c, 61, 3, 30, 0.40, "hi")
    c.texto(93, 3, "12.4G", "texto")
    c.texto(54, 4, "cache", "tenue")
    barra(c, 61, 4, 30, 0.28, "cpu_medio")
    c.texto(93, 4, "8.7G", "texto")
    c.texto(54, 5, "libre", "tenue")
    barra(c, 61, 5, 30, 0.32, "tenue")
    c.texto(93, 5, "9.9G", "texto")
    c.texto(54, 7, "swap", "tenue")
    c.texto(61, 7, "0B / 8.0G", "texto")

    caja(c, 52, 9, 48, 6, "red  ·  eth0")
    c.texto(54, 10, "▼ baja", "verde")
    c.texto(63, 10, "1.2 MiB/s", "texto")
    c.texto(54, 11, "▲ sube", "rojo")
    c.texto(63, 11, "84 KiB/s", "texto")
    c.texto(54, 12, "▁▂▅▇▅▃▂▁▂▄▆▇▆▃▂▁▁▂▃▅▇▅▂▁▂▃▂▁▄▅▃▂▁▂▃▄▆▅▃", "verde")

    caja(c, 0, 16, 100, 11, "procesos")
    cabecera = f"{'pid':>6} {'programa':<22} {'cpu%':>5} {'mem':>6} {'user':<10} {'estado':<8}"
    c.texto(2, 17, cabecera, "titulo")
    filas = [("1182", "firefox", "31.2", "2.1G", "ana", "running"),
             ("2043", "code", "12.8", "1.4G", "ana", "running"),
             ("88", "systemd", "0.4", "18M", "root", "sleep"),
             ("31005", "btop", "2.1", "12M", "ana", "running"),
             ("1290", "pipewire", "0.9", "9M", "ana", "sleep")]
    for indice, (pid, prog, cpu, mem, user, estado) in enumerate(filas):
        fila = 18 + indice
        if indice == 1:
            c.relleno(1, fila, 98, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(2, fila, f"{pid:>6} {prog:<22} {cpu:>5} {mem:>6} {user:<10} {estado:<8}", estilo)
    c.texto(2, 24, "ordenado por cpu · 214 procesos · 1 102 hilos", "tenue")
    pie(c, [("m", "menú"), ("f", "filtrar"), ("t", "árbol"), ("q", "salir")])


def btop_procesos(c: Lienzo) -> None:
    titulo_ventana(c, "btop++ · detalle de proceso", "titulo")
    c.texto(60, 0, "pid 1182 · firefox", "tenue")

    caja(c, 0, 2, 50, 12, "uso")
    c.texto(2, 3, "cpu", "tenue")
    barra(c, 8, 3, 32, 0.31, "cpu_medio")
    c.texto(42, 3, "31.2 %", "texto")
    c.texto(2, 4, "mem", "tenue")
    barra(c, 8, 4, 32, 0.42, "hi")
    c.texto(42, 4, "2.1 G", "texto")
    c.texto(2, 6, "hilos", "tenue")
    c.texto(2, 7, "62 · 8 corriendo", "texto")
    c.texto(2, 8, "16 % del total de cpu", "tenue")
    c.texto(2, 10, "tiempo", "tenue")
    c.texto(2, 11, "04:12:33", "texto")
    c.texto(14, 11, "abierto por", "tenue")
    c.texto(26, 11, "ana · tty2", "texto")

    caja(c, 52, 2, 48, 12, "gráfica de cpu · 60 s")
    # 20 columnas de 2 celdas; media celda de resolución con '▄'
    for indice, medios in enumerate((4, 5, 8, 6, 12, 15, 9, 14, 16, 17,
                                     16, 13, 11, 15, 17, 14, 12, 9, 6, 4)):
        x = 54 + indice * 2
        completos, resto = divmod(medios, 2)
        for nivel in range(completos):
            c.texto(x, 11 - nivel, "██", "cpu_bajo" if nivel < 4 else
                    ("cpu_medio" if nivel < 7 else "cpu_alto"))
        if resto:
            c.texto(x, 11 - completos, "▄▄", "cpu_bajo" if completos < 4 else
                    ("cpu_medio" if completos < 7 else "cpu_alto"))
    c.texto(54, 12, "0s" + " " * 18 + "30s" + " " * 18 + "60s", "tenue")

    caja(c, 0, 15, 100, 12, "hilos")
    c.texto(2, 16, f"{'tid':>7} {'estado':<10} {'cpu%':>5}  {'tiempo':<10} {'prioridad'}", "titulo")
    for indice, (tid, estado, cpu) in enumerate((("1182", "running", "12.4"), ("1183", "sleep", "3.1"),
                                                 ("1187", "sleep", "0.2"), ("1191", "running", "8.8"),
                                                 ("1195", "sleep", "0.0"), ("1201", "sleep", "0.4"))):
        fila = 17 + indice
        c.texto(2, fila, f"{tid:>7} {estado:<10} {cpu:>5}  {'00:12:41':<10} 0", "texto")
    c.texto(2, 24, "[k] terminar · [s] señales · [←→] hilos", "tenue")
    pie(c, [("esc", "volver"), ("f", "filtrar"), ("q", "salir")])


def btop_temas(c: Lienzo) -> None:
    titulo_ventana(c, "btop++ · temas", "titulo")
    c.texto(56, 0, "29 temas leídos de /usr/share/btop/themes", "tenue")

    caja(c, 0, 2, 100, 24, "temas  ·  los colores son los del fichero, no una copia")
    temas = [
        ("night-owl", "#011627", "#addb67", "#22da6e", "#addb67", "#ef5350"),
        ("monokai", "#060604", "#f92672", "#a6e22e", "#f8f8f2", "#f92672"),
        ("tokyo-night", "#1a1b26", "#7dcfff", "#9ece6a", "#e0af68", "#f7768e"),
        ("gruvbox_dark", "#1d2021", "#d79921", "#b8bb26", "#d79921", "#fb4934"),
        ("dusklight", "#04142e", "#ff7f00", "#00d4ff", "#fff86b", "#ff7f00"),
        ("dracula", "#282a36", "#f8f8f2", "#50fa7b", "#f1fa8c", "#ff5555"),
    ]
    for indice, (nombre, fondo, acento, bajo, medio, alto) in enumerate(temas):
        fila = 3 + indice * 3
        if indice == 0:
            c.relleno(1, fila, 98, 2, "seleccion")
        estilo = "seleccion" if indice == 0 else "texto"
        c.texto(3, fila, nombre.ljust(14), estilo)
        c.texto(18, fila, "fondo", "tenue")
        c.texto(24, fila, fondo, estilo)
        c.texto(34, fila, "acento", "tenue")
        c.texto(41, fila, acento, estilo)
        c.texto(50, fila, "gradiente", "tenue")
        c.texto(60, fila, f"{bajo} {medio} {alto}", estilo)
        # la tira: fondo del tema + el gradiente real, interpolado color a color
        for paso, color in enumerate(rampa([fondo, bajo, medio, alto], 28)):
            c.texto(3 + paso, fila + 1, "█", color)
    c.texto(3, 22, "cada fila es un fichero .theme: main_bg, hi_fg y los tres extremos del gradiente", "tenue")
    c.texto(3, 24, "las tiras son esos mismos valores, interpolados: no hay nada inventado", "verde")
    pie(c, [("↑↓", "tema"), ("⏎", "aplicar"), ("q", "salir")])


BTOP = App(
    clave="btop",
    nombre="btop",
    comando="btop",
    descripcion="Monitor de sistema: CPU por núcleo con medidores, memoria, red y la lista "
    "de procesos. Es el más vistoso de los siete, y el único que se permite gradientes. "
    "Su paleta **no hay que medirla**: btop trae 29 temas en ficheros `.theme` y cada "
    "color está declarado con su nombre. La tabla de abajo está leída de "
    "`/usr/share/btop/themes/night-owl.theme`.",
    fuente="**Leída**, no medida: son las claves `main_bg`, `main_fg`, `title`, `hi_fg`, "
    "`inactive_fg`, `graph_text`, `cpu_start/mid/end`, `proc_misc` y `selected_*` de "
    "`night-owl.theme`, copiado a `refs/btop/`. Las tiras de la pantalla 03 son los tres "
    "extremos `*_start/mid/end` de cada tema interpolados con `rampa()`. Desviación "
    "declarada: btop dibuja sus cajas con `cpu_box` y `mem_box` (`#ffffff`), que a 100 "
    "columnas taparía el contenido; el marco usa `inactive_fg`.",
    paleta={"fondo": "#011627", "texto": "#d6deeb", "titulo": "#ffffff", "hi": "#addb67",
            "tenue": "#575656", "graph": "#585858", "verde": "#22da6e",
            "cpu_bajo": "#22da6e", "cpu_medio": "#addb67", "cpu_alto": "#ef5350",
            "seleccion": "#000000", "sel_fg": "#ffeb95",
            "rojo": "#ef5350", "borde": "#575656", "gradiente_barra": "#addb67"},
    origen={"fondo": "leído", "texto": "leído", "titulo": "leído", "hi": "leído",
            "tenue": "leído", "graph": "leído", "verde": "leído", "cpu_bajo": "leído",
            "cpu_medio": "leído", "cpu_alto": "leído", "rojo": "leído",
            "borde": "leído", "gradiente_barra": "leído"},
    uso={"fondo": "main_bg", "texto": "main_fg", "titulo": "title", "hi": "hi_fg",
         "tenue": "inactive_fg", "graph": "graph_text", "verde": "proc_misc",
         "cpu_bajo": "cpu_start", "cpu_medio": "cpu_mid", "cpu_alto": "cpu_end",
         "gradiente_barra": "hi_fg"},
    variantes={"monokai": {"fondo": "#060604", "texto": "#f8f8f2", "titulo": "#f8f8f2",
                           "hi": "#f92672", "cpu_bajo": "#a6e22e", "cpu_medio": "#f8f8f2",
                           "cpu_alto": "#f92672", "seleccion": "#7a1137"},
               "tokyo-night": {"fondo": "#1a1b26", "texto": "#cfc9c2", "titulo": "#cfc9c2",
                               "hi": "#7dcfff", "cpu_bajo": "#9ece6a", "cpu_medio": "#e0af68",
                               "cpu_alto": "#f7768e", "seleccion": "#414868"},
               "dusklight": {"fondo": "#04142e", "texto": "#99dfff", "titulo": "#99ffff",
                             "hi": "#ff7f00", "cpu_bajo": "#00d4ff", "cpu_medio": "#fff86b",
                             "cpu_alto": "#ff7f00", "seleccion": "#722b01"}},
    pantallas=[("01", "Panel", "Los medidores de CPU por núcleo con el gradiente del tema "
                "—verde, amarillo, rojo según carga—, la memoria y la red.", btop_panel),
               ("02", "Proceso", "El detalle de un proceso: uso, gráfica de 60 s e hilos.",
                btop_procesos),
               ("03", "Temas", "Los temas reales de btop con sus valores reales: la pantalla "
                "que no existía en las otras series, porque aquí la paleta se lee y no se "
                "mide. Las tiras no cambian con el selector de la página: son datos de cada "
                "tema, no cromo de la app.", btop_temas)],
)


# ---------------------------------------------------------------------------
# ncdu · paleta MEDIDA de una captura; ncdu hereda los colores del terminal
# ---------------------------------------------------------------------------
FILAS_NCDU = [
    ("3,6 MiB", 9, "/brltty"), ("1,8 MiB", 5, "/apparmor.d"), ("1,1 MiB", 3, "/ssl"),
    ("636,0 KiB", 1, "/asciidoc"), ("524,0 KiB", 1, "/xdg"), ("496,0 KiB", 1, "/X11"),
    ("404,0 KiB", 1, "/init"), ("392,0 KiB", 1, "/fonts"), ("344,0 KiB", 1, "/ssh"),
    ("332,0 KiB", 1, "/sane.d"), ("328,0 KiB", 1, "/init.d"), ("232,0 KiB", 1, "/ImageMagick-6"),
    ("220,0 KiB", 1, "/dbus-1"), ("168,0 KiB", 1, "/lynx"), ("152,0 KiB", 1, "/java-8-openjdk"),
    ("144,0 KiB", 1, "/console-setup"), ("140,0 KiB", 1, "/default"),
    ("136,0 KiB", 1, "ld.so.cache"),
]


FILAS_NCDU = [("3,6 MiB", 9, "/brltty"), ("1,8 MiB", 4, "/apparmor.d"),
              ("1,1 MiB", 3, "/ssl"), ("636,0 KiB", 2, "/asciidoc"),
              ("524,0 KiB", 2, "/xdg"), ("496,0 KiB", 2, "/X11"),
              ("404,0 KiB", 1, "/init"), ("392,0 KiB", 1, "/fonts"),
              ("344,0 KiB", 1, "/ssh"), ("332,0 KiB", 1, "/sane.d"),
              ("328,0 KiB", 1, "/init.d"), ("232,0 KiB", 1, "/ImageMagick-6"),
              ("220,0 KiB", 1, "/dbus-1"), ("168,0 KiB", 1, "/lynx"),
              ("152,0 KiB", 1, "/java-8-openjdk"), ("144,0 KiB", 1, "/console-setup"),
              ("140,0 KiB", 1, "/default"), ("136,0 KiB", 1, "/ld.so.cache"),
              ("124,0 KiB", 1, "/terminfo"), ("112,0 KiB", 1, "/pam.d"),
              ("96,0 KiB", 1, "/security"), ("88,0 KiB", 1, "/apt"),
              ("76,0 KiB", 1, "/NetworkManager"), ("64,0 KiB", 1, "/pki"),
              ("52,0 KiB", 1, "/cron.d")]


def _barra_ncdu(c: Lienzo, fila: int, tam: str, llenos: int, ruta: str, estilo: str) -> None:
    """La fila de ncdu tal cual: tamaño a la derecha, barra de # entre corchetes, ruta."""
    c.texto(2, fila, f"{tam:>10} [", estilo)
    c.texto(14, fila, "#" * llenos, "barra" if estilo == "texto" else estilo)
    c.texto(14 + llenos, fila, " " * (9 - llenos), estilo)
    c.texto(24, fila, "] " + ruta, estilo)


def ncdu_directorio(c: Lienzo) -> None:
    c.texto(0, 0, " ncdu 1.11 ~ Use the arrow keys to navigate, press ? for help".ljust(100), "inverso")
    c.texto(0, 1, "--- /etc " + "-" * 87, "texto")
    for indice, (tam, llenos, ruta) in enumerate(FILAS_NCDU):
        fila = 2 + indice
        if indice == 2:
            c.relleno(0, fila, 100, 1, "seleccion")
            _barra_ncdu(c, fila, tam, llenos, ruta, "seleccion")
        else:
            _barra_ncdu(c, fila, tam, llenos, ruta, "texto")
    c.texto(0, 28, " Total disk usage:  14,9 MiB   Apparent size:  9,2 MiB   Items: 3311".ljust(100),
            "inverso")


def ncdu_borrar(c: Lienzo) -> None:
    c.texto(0, 0, " ncdu 1.11 ~ Use the arrow keys to navigate, press ? for help".ljust(100), "inverso")
    c.texto(0, 1, "--- /home/ana/Descargas " + "-" * 76, "texto")
    filas = [("2,4 GiB", 9, "videos/"), ("812,3 MiB", 6, "iso/"),
             ("44,1 MiB", 2, "notas.txt"), ("12,0 MiB", 1, "captura.png"),
             ("8,2 MiB", 1, "musica/"), ("4,0 MiB", 1, "fotos/"),
             ("2,1 MiB", 1, "podcast/"), ("900,0 KiB", 1, "cv.pdf"),
             ("412,0 KiB", 1, "factura.pdf"), ("190,0 KiB", 1, "notas-viejas.txt"),
             ("88,0 KiB", 1, "lista.txt"), ("12,0 KiB", 1, "leeme.md"),
             ("4,0 KiB", 1, ".descarga"),
             ("0,0 B", 0, "vacia/")]
    for indice, (tam, llenos, ruta) in enumerate(filas):
        fila = 2 + indice
        if indice == 0:
            c.relleno(0, fila, 100, 1, "seleccion")
            _barra_ncdu(c, fila, tam, llenos, ruta, "seleccion")
        else:
            _barra_ncdu(c, fila, tam, llenos, ruta, "texto")

    # El diálogo de ncdu ocupa el ancho de la lista y tapa lo de debajo.
    c.relleno(0, 14, 100, 11, "fondo")
    c.texto(0, 14, "┌" + "─" * 98 + "┐", "texto")
    for fila in range(15, 24):
        c.texto(0, fila, "│", "texto")
        c.texto(99, fila, "│", "texto")
    c.texto(0, 24, "└" + "─" * 98 + "┘", "texto")
    c.texto(2, 14, " borrar ", "texto")

    c.texto(4, 16, "Are you sure you want to delete", "texto")
    c.texto(4, 17, '"/home/ana/Descargas/videos"', "aviso")
    c.texto(4, 18, "which is 118 files?", "texto")
    c.relleno(40, 21, 6, 1, "seleccion")
    c.texto(41, 21, "yes", "seleccion")
    c.texto(52, 21, "no", "texto")
    c.texto(62, 21, "[cancel]", "texto")
    c.texto(4, 23, "←→ elegir · ⏎ confirmar · esc cancelar", "tenue")
    c.texto(0, 28, " Total disk usage:  3,2 GiB   Apparent size:  3,1 GiB   Items: 4".ljust(100),
            "inverso")


def ncdu_escaneo(c: Lienzo) -> None:
    c.texto(0, 0, " ncdu 1.11 ~ escaneando", "inverso")
    c.texto(2, 2, "escaneando  /usr/lib/x86_64-linux-gnu/", "texto")
    rutas = [(4, "/usr/lib/x86_64-linux-gnu/"), (2, "/usr/lib/x86_64-linux-gnu/libc.so.6"),
             (4, "/usr/share/"), (2, "/usr/share/doc/"), (4, "/usr/share/doc/python3/"),
             (2, "/usr/share/doc/python3/html/"), (1, "/usr/share/doc/python3/html/style.css"),
             (4, "/usr/share/man/"), (2, "/usr/share/man/man1/")]
    for indice, (sangria, ruta) in enumerate(rutas):
        c.texto(sangria, 4 + indice, "▸ " + ruta, "tenue")

    caja(c, 0, 15, 100, 10, "progreso")
    c.texto(2, 16, "ficheros", "tenue")
    c.texto(12, 16, "128 402", "texto")
    c.texto(34, 16, "directorios", "tenue")
    c.texto(47, 16, "9 110", "texto")
    barra(c, 2, 18, 80, 0.71, "barra", lleno="#")
    c.texto(84, 18, "71 %", "titulo")
    c.texto(2, 20, "tiempo", "tenue")
    c.texto(10, 20, "00:00:04 · quedan 2 s", "texto")
    c.texto(2, 23, "[q] cancelar el escaneo", "tenue")
    c.texto(0, 28, " Total disk usage:  14,9 MiB   Apparent size:  9,2 MiB   Items: 3311".ljust(100),
            "inverso")


NCDU = App(
    clave="ncdu",
    nombre="ncdu",
    comando="ncdu /etc",
    descripcion="Espacio en disco: un `du` por el que te mueves con las flechas. Es el más "
    "austero de los siete y el más honesto del grupo: **ncdu no tiene paleta propia**, "
    "hereda los colores del terminal. Su identidad es tipográfica —columnas de ancho fijo, "
    "barras dibujadas con `#`, la fila elegida en vídeo inverso— y eso es justo lo que "
    "nuestras series anteriores no podían permitirse.",
    fuente="**Medida** de una captura, porque aquí no hay nada que leer: ncdu no trae "
    "paleta, hereda la del terminal (aubergine `#300a24`, el esquema clásico de Ubuntu, y "
    "blanco puro para todo el texto). El rojo `#963229` es el del aviso del diálogo. El "
    "`tenue` es una derivación de ese fondo y va marcado como tal. Consecuencia honesta: "
    "ningún color de esta pantalla lo eligió ncdu.",
    paleta={"fondo": "#300a24", "texto": "#ffffff", "titulo": "#ffffff", "tenue": "#a06c92",
            "barra": "#ffffff", "aviso": "#963229",
            "seleccion": "#ffffff", "sel_fg": "#300a24",
            "inverso": "#ffffff", "borde": "#490e24"},
    origen={"fondo": "medido", "texto": "medido", "titulo": "medido", "tenue": "derivado",
            "barra": "medido", "inverso": "medido", "borde": "medido", "aviso": "medido"},
    uso={"fondo": "fondo del terminal", "texto": "todo el texto", "titulo": "énfasis",
         "tenue": "rutas y ayudas", "barra": "barras de tamaño", "aviso": "borrado",
         "inverso": "cabecera y pie a todo el ancho", "borde": "marco del diálogo"},
    pantallas=[("01", "Directorio", "La pantalla principal: tamaño, barra de `#` y ruta, con "
                "la fila elegida en vídeo inverso y el total en la última línea.",
                ncdu_directorio),
               ("02", "Borrar", "El diálogo de borrado, a todo el ancho y tapando la lista: "
                "tres opciones y la elegida en vídeo inverso. Ni un color de más.", ncdu_borrar),
               ("03", "Escaneo", "El escaneo con la ruta que está leyendo en ese momento y el "
                "progreso. Es la pantalla que demuestra que ncdu vive del texto y no del "
                "color.", ncdu_escaneo)],
)


# ---------------------------------------------------------------------------
# gitui · paleta MEDIDA de una captura
# ---------------------------------------------------------------------------
def _gitui_pestanas(c: Lienzo, activa: int) -> None:
    c.texto(0, 0, " gitui", "titulo")
    for indice, nombre in enumerate(("Status", "Log", "Files", "Stashing", "Stashes")):
        x = 8 + indice * 12
        c.texto(x, 0, f" {nombre} [{indice + 1}] ",
                "pestana_activa" if indice == activa else "tenue")


def gitui_status(c: Lienzo) -> None:
    _gitui_pestanas(c, 0)

    caja(c, 0, 1, 55, 12, "Unstaged Changes")
    cambios = [("M", "src/main.rs"), ("M", "src/ui/draw.rs"), ("?", "src/ui/theme.rs"),
               ("M", "Cargo.toml"), ("A", "docs/imagenes.md"), ("M", "src/asyncgit/mod.rs"),
               ("D", "src/viejo.rs"), ("M", "README.md")]
    for indice, (marca, ruta) in enumerate(cambios):
        fila = 2 + indice
        if indice == 1:
            c.relleno(1, fila, 53, 1, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(2, fila, marca, "verde" if indice == 1 else (
            "rojo" if marca in "MD" else "azul" if marca == "?" else "verde"))
        c.texto(4, fila, ruta, estilo)
    c.texto(2, 11, "8 cambios · [space] preparar", "tenue")

    caja(c, 0, 13, 55, 7, "Staged Changes")
    c.texto(2, 14, "M src/main.rs", "verde")
    c.texto(2, 15, "A src/ui/theme.rs", "verde")
    c.texto(2, 17, "2 ficheros listos", "tenue")

    caja(c, 0, 20, 55, 8, "Commit · 1402/1408")
    c.texto(2, 21, "fix: no saludar dos veces", "texto")
    c.texto(2, 22, "en draw()", "texto")
    c.texto(2, 24, "│", "tenue")
    c.texto(2, 25, "amendar con [c] · convención: fix: / feat:", "tenue")

    caja(c, 57, 1, 43, 27, "Diff · src/ui/draw.rs")
    c.texto(58, 2, "@@ -41,7 +41,9 @@ fn draw", "azul")
    c.texto(58, 3, "     let area = self.area();", "texto")
    c.texto(58, 4, "     let buf = &mut self.buf;", "texto")
    c.texto(58, 5, "-    let w = area.width;", "rojo")
    c.texto(58, 6, "+    let w = w.saturating_sub(2);", "verde")
    c.texto(58, 7, "+    let h = h.saturating_sub(2);", "verde")
    c.texto(58, 8, "     buf.set_string(x, y, \"hola\");", "texto")
    c.texto(58, 10, "     // el margen de 2 celdas", "tenue")
    c.texto(58, 11, "     // viene del marco", "tenue")
    c.texto(58, 24, "1 borrado · 2 añadidos · 1 fichero", "tenue")
    pie(c, [("[q]", "quit"), ("[c]", "commit"), ("[a]", "stage"), ("[d]", "diff"),
            ("[?]", "help")], y=28)


def gitui_log(c: Lienzo) -> None:
    _gitui_pestanas(c, 1)

    caja(c, 0, 1, 55, 27, "Log · 1408 commits")
    commits = [("f91c8c3", "2021-08-22", "Stephan Dilly", "fix: tab msg not nagst in taglist"),
               ("c9b8c21", "2021-08-22", "Stephan Dilly", "update profiler dependency"),
               ("1c2b782", "2021-08-22", "Stephan Dilly", "fix: capacity"),
               ("70e4a31", "2021-08-22", "Stephan Dilly", "update changelog"),
               ("49a185f", "2021-08-22", "Stephan Dilly", "dont process abort on input"),
               ("8192f4b", "2021-08-22", "Stephan Dilly", "show subject line of commits"),
               ("3db3b95", "2021-08-22", "Stephan Dilly", "fix order of old/new to compare"),
               ("2f7a1c4", "2021-08-21", "Stephan Dilly", "add diff stat to log"),
               ("8d0e5a2", "2021-08-21", "Stephan Dilly", "fix: clippy warnings"),
               ("5b6c9f1", "2021-08-20", "Stephan Dilly", "bump crossterm to 0.20"),
               ("e4a7d38", "2021-08-20", "Stephan Dilly", "stash: pop by index"),
               ("a1b9c07", "2021-08-19", "Stephan Dilly", "theme: load from file")]
    for indice, (hash_, fecha, autor, asunto) in enumerate(commits):
        fila = 2 + indice * 2
        if indice == 1:
            c.relleno(1, fila, 53, 2, "seleccion")
            estilo = "seleccion"
        else:
            estilo = "texto"
        c.texto(2, fila, hash_, "hash" if indice != 1 else estilo)
        c.texto(10, fila, fecha, "tenue" if indice != 1 else estilo)
        c.texto(21, fila, autor, estilo)
        c.texto(2, fila + 1, asunto[:52], estilo)
    c.texto(2, 26, "1408 commits · rama master · ↑2 ↓0", "tenue")

    caja(c, 57, 1, 43, 27, "detalle")
    c.texto(59, 2, "author", "tenue")
    c.texto(59, 3, "Stephan Dilly <dilly@stan..>", "texto")
    c.texto(59, 5, "date", "tenue")
    c.texto(59, 6, "2021-08-22 17:23:06", "texto")
    c.texto(59, 8, "commit", "tenue")
    c.texto(59, 9, "c9b8c2133741aa0d3e4b8f9c1d2a", "texto")
    c.texto(59, 11, "message", "tenue")
    c.texto(59, 12, "update profiler dependency", "titulo")
    c.texto(59, 14, "files", "tenue")
    for indice, (marca, ruta) in enumerate((("M", "CHANGELOG.md"), ("M", "Cargo.lock"),
                                            ("M", "Cargo.toml"), ("M", "src/asyncgit"))):
        c.texto(59, 15 + indice, marca, "verde")
        c.texto(61, 15 + indice, ruta, "texto")
    c.texto(59, 21, "stats", "tenue")
    c.texto(59, 22, "+18 −4 · 4 ficheros", "texto")
    c.texto(59, 24, "body", "tenue")
    c.texto(59, 25, "Bumps the profiler so the log", "texto")
    c.texto(59, 26, "no longer blocks the ui thread.", "texto")
    pie(c, [("[q]", "quit"), ("[⏎]", "detalle"), ("[b]", "ramas"), ("[?]", "help")], y=28)


def gitui_conflicto(c: Lienzo) -> None:
    _gitui_pestanas(c, 0)


    caja(c, 0, 1, 55, 12, "Unstaged Changes · conflicto")
    for indice, ruta in enumerate(("src/ui/theme.rs", "src/main.rs", "src/ui/nuevo.rs")):
        c.texto(2, 2 + indice, "UU", "rojo")
        c.texto(5, 2 + indice, ruta, "rojo")
    c.texto(2, 6, "git no deja preparar un fichero con", "tenue")
    c.texto(2, 7, "marcadores dentro: primero se resuelve.", "tenue")

    caja(c, 0, 13, 55, 15, "Resolución")
    c.texto(2, 14, "[o] quedarse con HEAD", "texto")
    c.texto(2, 15, "[t] quedarse con la rama", "texto")
    c.texto(2, 16, "[e] editar a mano", "texto")
    c.texto(2, 18, "Los marcadores son de git, no de gitui:", "tenue")
    c.texto(2, 19, "<<<<<<<  =======  >>>>>>>", "verde")
    c.texto(2, 21, "No hay color que resuelva el conflicto.", "tenue")
    c.texto(2, 22, "Se lee en el texto o no se resuelve.", "tenue")

    caja(c, 57, 1, 43, 27, "Diff · src/ui/theme.rs")
    c.texto(58, 2, "@@ -12,7 +12,11 @@", "azul")
    c.texto(58, 3, " let acento =", "texto")
    c.texto(58, 4, "<<<<<<< HEAD", "amarillo")
    c.texto(58, 5, "   Color::Rgb(122,162,247)", "rojo")
    c.texto(58, 6, "=======", "amarillo")
    c.texto(58, 7, "   Color::Rgb(187,154,247)", "verde")
    c.texto(58, 8, ">>>>>>> feature/tema", "amarillo")
    c.texto(58, 10, " // el resto del fichero sigue", "tenue")
    c.texto(58, 12, " // igual: un conflicto no es un", "tenue")
    c.texto(58, 13, " // error de formato, es una", "tenue")
    c.texto(58, 14, " // decisión que hay que tomar.", "tenue")
    c.texto(58, 24, "3 ficheros en conflicto", "rojo")
    pie(c, [("[q]", "quit"), ("[o]", "ours"), ("[t]", "theirs"), ("[?]", "help")], y=28)


GITUI = App(
    clave="gitui",
    nombre="gitui",
    comando="gitui",
    descripcion="Git en el terminal: pestañas arriba, dos listas de cambios a la izquierda y "
    "el diff a la derecha. Su virtud es que **el color clasifica estados de git** —verde "
    "añadido, rojo borrado, amarillo marcador, azul cabecera de hunk— y no decora nada.",
    fuente="Fondo `#232c31`, fila elegida `#484d79`, atenuado `#7f8887` y el `#0d1b23` de "
    "los huecos: **medidos** del histograma de una captura, leyendo solo el rectángulo de "
    "la ventana porque el escritorio se cuela por los bordes. Los colores de diff son "
    "**derivados**: la captura era de la pestaña Status y no había diff que medir.",
    paleta={"fondo": "#232c31", "texto": "#c3cccf", "titulo": "#d6deeb", "tenue": "#7f8887",
            "pestana_activa": "#484d79", "seleccion": "#484d79", "sel_fg": "#ffffff",
            "verde": "#7ac8a0", "rojo": "#e06c75", "amarillo": "#e5c07b",
            "azul": "#61afef", "hash": "#e5c07b", "autor": "#7ac8a0"},
    origen={"fondo": "medido", "texto": "derivado", "titulo": "medido", "tenue": "medido",
            "pestana_activa": "medido", "verde": "derivado", "rojo": "derivado",
            "amarillo": "derivado", "azul": "derivado", "hash": "derivado",
            "autor": "derivado"},
    uso={"fondo": "fondo", "texto": "texto normal", "titulo": "títulos y pestaña activa",
         "tenue": "metadatos", "pestana_activa": "pestaña y fila elegidas",
         "verde": "añadido", "rojo": "borrado", "amarillo": "marcadores de conflicto",
         "azul": "cabecera de hunk", "hash": "hash de commit", "autor": "autor"},
    pantallas=[("01", "Status", "Los cambios sin preparar y preparados, el diff al lado y la "
                "caja de commit debajo: la pantalla del día a día.", gitui_status),
               ("02", "Log", "El historial de commits y el detalle del seleccionado.",
                gitui_log),
               ("03", "Conflicto", "Una fusión atascada: los marcadores de conflicto son "
                "texto, no color, y por eso se leen igual en una terminal de un tono.",
                gitui_conflicto)],
)


# ---------------------------------------------------------------------------
# bagels · paleta MEDIDA (es el tema tokyo-night de btop, pero eso da igual aquí)
# ---------------------------------------------------------------------------
def _cabecera_bagels(c: Lienzo, pestana: str = "Home") -> None:
    c.texto(0, 0, " ➜Bagels 0.3.2", "titulo")
    for indice, nombre in enumerate(("Home", "Manager")):
        x = 16 + indice * 10
        c.texto(x, 0, f" {nombre} ", "pestana_activa" if nombre == pestana else "tenue")
    c.texto(88, 0, "instance", "tenue")


def bagels_registro(c: Lienzo) -> None:
    _cabecera_bagels(c)

    caja(c, 0, 2, 18, 6, "Accounts")
    c.texto(2, 3, "Bank", "texto")
    c.texto(10, 3, "4924.5", "texto")
    c.texto(2, 5, "Card", "texto")
    c.texto(10, 5, "80.0", "texto")

    caja(c, 20, 2, 24, 6, "View and add")
    c.texto(23, 3, "Expense", "titulo")
    c.texto(35, 3, "Income", "tenue")
    c.texto(23, 5, "<<< 17-23 Nov >>>", "texto")

    caja(c, 46, 2, 54, 6, "Templates")
    for indice, (nombre, atajo) in enumerate((("Home-Uni", "1"), ("Monthly Rent", "2"),
                                              ("Netflix", "3"), ("Weekly shop", "4"))):
        c.texto(48 + indice * 13, 3, nombre, "texto")
        c.texto(48 + indice * 13, 4, atajo, "tenue")

    caja(c, 0, 9, 100, 19, "Records")
    c.texto(2, 10, "Category", "titulo")
    c.texto(22, 10, "Amount", "titulo")
    c.texto(34, 10, "Label", "titulo")
    c.texto(62, 10, "Account", "titulo")

    registros = [("Salary", "+", "1200.0", "Wage pay", "Bank", "verde"),
                 ("Restaurants", "-", "50.0", "Dinner with Sarah", "Bank", "texto"),
                 ("  × Sarah", "+", "25.0", "—", "—", "tenue"),
                 ("  Self total", "=", "25.0", "—", "—", "tenue"),
                 ("Rent", "-", "1200.0", "Monthly Rent", "Bank", "texto"),
                 ("Public Transport", "-", "10.0", "Home → School", "Card", "texto"),
                 ("Snacks", "-", "2.5", "Bagels", "Bank", "texto"),
                 ("Home-Uni", "-", "14.0", "Weekly ticket", "Card", "texto"),
                 ("Groceries", "-", "62.5", "Weekly shop", "Bank", "texto"),
                 ("Netflix", "-", "12.99", "Suscripción", "Card", "texto"),
                 ("Café", "-", "3.2", "Con Ana", "Bank", "texto"),
                 ("Regalo", "-", "25.0", "Cumpleaños", "Bank", "texto")]
    for indice, (cat, signo, cantidad, etiqueta, cuenta, estilo) in enumerate(registros):
        fila = 11 + indice
        if indice == 1:
            c.relleno(1, fila, 98, 1, "seleccion")
            estilo = "seleccion"
        elif estilo != "tenue":
            estilo = "texto"
        if not cat.startswith("  "):
            # el punto dice el signo del dinero, no la categoría: verde entra, naranja sale
            c.texto(2, fila, "●", "verde" if signo == "+" else "naranja")
        c.texto(4, fila, cat, estilo)
        c.texto(22, fila, signo, "verde" if signo == "+" else estilo)
        c.texto(24, fila, cantidad, "verde" if signo == "+" else estilo)
        c.texto(34, fila, etiqueta, estilo)
        c.texto(62, fila, cuenta, estilo)
    c.texto(2, 24, "12 registros · filtro: 17-23 Nov", "tenue")
    c.texto(2, 25, "↑↓ elegir · ⏎ editar · / buscar · tab cambia de panel", "tenue")
    pie(c, [("a", "add"), ("d", "delete"), ("e", "edit"), ("t", "transfer"),
            ("q", "quit")], y=28)


def bagels_calendario(c: Lienzo) -> None:
    _cabecera_bagels(c)

    caja(c, 0, 2, 52, 26, "Period · Nov 2024")
    c.texto(2, 3, "<<< 17 Nov - 23 Nov >>>", "texto")
    c.texto(2, 5, " S   M   T   W   T   F   S", "titulo")
    dias = [["27", "28", "29", "30", "31", " 1", " 2"],
            [" 3", " 4", " 5", " 6", " 7", " 8", " 9"],
            ["10", "11", "12", "13", "14", "15", "16"],
            ["17", "18", "19", "20", "21", "22", "23"],
            ["24", "25", "26", "27", "28", "29", "30"]]
    for indice, semana in enumerate(dias):
        fila = 6 + indice
        for columna, dia in enumerate(semana):
            c.texto(2 + columna * 4, fila, dia, "texto")
    c.relleno(2 + 1 * 4, 9, 2, 1, "seleccion")
    c.texto(2 + 1 * 4, 9, "18", "seleccion")
    c.texto(2, 11, "Días con gasto marcados con ·", "tenue")
    for columna, dia in enumerate(("17", "20", "22", "23")):
        c.texto(2 + columna * 4, 12, "·", "naranja")

    # el gasto de la semana en barras verticales: lo que el calendario no dice
    c.texto(2, 14, "gasto por día", "titulo")
    c.texto(20, 14, "máximo 1240.0 el 17", "tenue")
    importe = [("17", 0.96), ("18", 0.05), ("19", 0.11), ("20", 0.03),
               ("21", 0.02), ("22", 0.06), ("23", 0.04)]
    for indice, (dia, parte) in enumerate(importe):
        x = 4 + indice * 6
        alto = max(1, round(parte * 8))
        for nivel in range(alto):
            c.texto(x, 23 - nivel, "████", "violeta")
        c.texto(x, 24, dia.center(4), "tenue")
    c.texto(2, 25, "18 Nov · 50.0 · Restaurants + 25.0 de Sarah", "texto")

    caja(c, 54, 2, 46, 10, "Expense of 17 Nov - 23 Nov")
    c.texto(56, 3, "Total", "tenue")
    c.texto(64, 3, "1262.5", "texto")
    c.texto(56, 4, "Por día", "tenue")
    c.texto(64, 4, "180.36", "texto")
    c.texto(56, 6, "//////" * 6, "naranja")
    c.texto(56, 7, "Un gasto grande y muchos pequeños.", "tenue")
    c.texto(56, 9, "7 días · 9 registros", "tenue")

    caja(c, 54, 13, 46, 15, "Insights")
    for indice, (nombre, porcentaje) in enumerate((("● Housing", 0.95),
                                                   ("● Food", 0.03),
                                                   ("● Transport", 0.02))):
        fila = 14 + indice * 2
        c.texto(56, fila, nombre, "violeta")
        barra(c, 68, fila, 20, porcentaje, "violeta")
        c.texto(90, fila, f"{int(porcentaje * 100):3d}%", "texto")
    c.texto(56, 21, "El 95 % del gasto es el alquiler:", "tenue")
    c.texto(56, 22, "un solo registro decide la semana.", "tenue")
    c.texto(56, 24, "▸ filtrar por categoría con ⏎", "tenue")
    pie(c, [("←→", "periodo"), ("↑↓", "día"), ("q", "quit")], y=28)


def bagels_resumen(c: Lienzo) -> None:
    _cabecera_bagels(c)

    caja(c, 0, 2, 100, 12, "Gasto por día · Nov")
    c.texto(2, 3, "máximo 1240.0 · el 17", "tenue")
    serie = [("10", 0.04), ("11", 0.10), ("12", 0.03), ("13", 0.09), ("14", 0.05),
             ("15", 0.00), ("16", 0.00), ("17", 0.96), ("18", 0.04), ("19", 0.06),
             ("20", 0.07), ("21", 0.03), ("22", 0.08), ("23", 0.02)]
    for indice, (dia, parte) in enumerate(serie):
        x = 3 + indice * 7
        alto = round(parte * 7)
        for nivel in range(alto):
            c.texto(x, 11 - nivel, "█████", "violeta")
        c.texto(x + 1, 12, dia, "tenue")

    caja(c, 0, 14, 46, 14, "Categorías")
    for indice, (nombre, parte, importe) in enumerate((("Housing", 0.95, "1200.0"),
                                                       ("Groceries", 0.05, "62.5"),
                                                       ("Transport", 0.02, "20.0"),
                                                       ("Snacks", 0.01, "2.5"))):
        fila = 15 + indice * 3
        c.texto(2, fila, nombre, "texto")
        barra(c, 14, fila, 22, parte, "violeta")
        c.texto(38, fila, importe, "texto")
        c.texto(14, fila + 1, f"{int(parte * 100)} % del total", "tenue")

    caja(c, 48, 14, 52, 14, "Resumen del periodo")
    c.texto(50, 15, "ingresos", "tenue")
    c.texto(66, 15, "+ 1200.0", "verde")
    c.texto(50, 16, "gastos", "tenue")
    c.texto(66, 16, "- 1262.5", "texto")
    c.texto(50, 17, "balance", "tenue")
    c.texto(66, 17, "- 62.5", "rojo")
    c.texto(50, 19, "Días con gasto", "tenue")
    c.texto(66, 19, "9 de 14", "texto")
    c.texto(50, 21, "El periodo gasta más de lo que", "texto")
    c.texto(50, 22, "ingresa: la diferencia son los", "texto")
    c.texto(50, 23, "1200.0 del alquiler.", "texto")
    c.texto(50, 25, "El color no explica el balance;", "tenue")
    c.texto(50, 26, "lo explica la resta.", "tenue")
    pie(c, [("q", "quit"), ("p", "periodo"), ("e", "exportar")], y=28)


BAGELS = App(
    clave="bagels",
    nombre="bagels",
    comando="bagels",
    descripcion="Gestor de gastos: cuentas, plantillas, tabla de registros, calendario y "
    "gráficas. Es el que más se parece a una app de escritorio de los siete —paneles con "
    "título, pestañas, filas— y el que usa el color **por categoría**, no por estado.",
    fuente="**Medida** de una captura: fondo `#1a1b26`, panel `#24283b`, selección "
    "`#414868` y el violeta `#bb9af7` que ocupa el 2 % de los píxeles. Que coincida con "
    "`tokyo-night.theme` de btop no es casualidad: Bagels usa ese tema. Los verdes y rojos "
    "del balance son **derivados** de esa familia y van marcados.",
    paleta={"fondo": "#1a1b26", "texto": "#c0caf5", "titulo": "#7aa2f7",
            "tenue": "#565f89", "pestana_activa": "#bb9af7", "seleccion": "#414868",
            "sel_fg": "#c0caf5", "violeta": "#bb9af7", "naranja": "#ff9e64",
            "verde": "#9ece6a", "rojo": "#f7768e"},
    origen={"fondo": "medido", "texto": "derivado", "titulo": "derivado", "tenue": "medido",
            "pestana_activa": "medido", "violeta": "medido", "naranja": "derivado",
            "verde": "derivado", "rojo": "derivado"},
    uso={"fondo": "fondo", "texto": "texto y filas", "titulo": "cabeceras de tabla",
         "tenue": "etiquetas", "pestana_activa": "pestaña Home",
         "violeta": "barras y categorías", "naranja": "gasto", "verde": "ingreso",
         "rojo": "balance negativo"},
    pantallas=[("01", "Registro", "Cuentas, plantillas y la tabla de registros con sus "
                "categorías, importes y cuentas.", bagels_registro),
               ("02", "Calendario", "El periodo con su calendario, los días con gasto y las "
                "gráficas de resumen.", bagels_calendario),
               ("03", "Resumen", "Gasto por día, reparto por categorías y balance. Aquí el "
                "color hace de leyenda: verde ingreso, naranja gasto, rojo balance.",
                bagels_resumen)],
)

APPS1 = [BTOP, NCDU, GITUI, BAGELS]
