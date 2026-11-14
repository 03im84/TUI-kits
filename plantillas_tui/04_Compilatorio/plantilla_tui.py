#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plantilla_tui.py — la plantilla mínima: tres pantallas, una paleta, un verificador.

No es un framework ni un motor nuevo. Es **una pantalla que se puede leer de
arriba abajo** y que se copia para empezar otra. Reutiliza el motor de celdas
del proyecto (`mockups/celdas.py`, 200 líneas) en vez de traer el suyo: eso es
lo que significa reutilización nuclear.

    python3 plantilla_tui.py            # escribe plantilla.txt y plantilla.html
    python3 plantilla_tui.py --ansi     # la pinta en tu terminal, con color
    python3 plantilla_tui.py --test     # se verifica a sí misma; 0 = bien

Cinco decisiones, y ninguna más:

  1. REJILLA      100 × 30 celdas, y todo se mide en columnas, no en caracteres.
  2. PALETA       nueve roles, cada uno con su procedencia escrita.
  3. COMPOSICIÓN  cabecera · cuerpo · pie de teclas. Nada más.
  4. ESTADOS      lista, detalle y diálogo: los tres que toda utilidad necesita.
  5. VERIFICACIÓN ancho exacto, marcos intactos, estilos declarados.

Lo que esta plantilla NO es: una aplicación. No lee teclado ni tiene bucle;
eso está explicado en el capítulo 11 del compilatorio y en la parte IV del pack.
"""

from __future__ import annotations

import html
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mockups.celdas import Lienzo  # noqa: E402

ANCHO, ALTO = 100, 30


# --------------------------------------------------------------------------- #
# 1 · REJILLA — la única función que mide. Todo pasa por aquí.
# --------------------------------------------------------------------------- #
def ancho(texto: str) -> int:
    """Columnas que ocupa un texto, no caracteres que tiene.

    `len("漢字")` son 2 y ocupa 4 columnas. `len("cafe\\u0301")` son 5 y ocupa 4.
    Los escapes ANSI no ocupan ninguna y aquí no se pasan: el color va por celda.
    """
    total = 0
    for ch in texto:
        if unicodedata.combining(ch):
            continue                      # marcas combinadas: 0 columnas
        total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return total


def ajustar(texto: str, columnas: int, relleno: str = " ") -> str:
    """Deja el texto en exactamente `columnas`, recortando por columnas."""
    salida, usado = [], 0
    for ch in texto:
        paso = 0 if unicodedata.combining(ch) else (
            2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1)
        if usado + paso > columnas:
            break
        salida.append(ch)
        usado += paso
    return "".join(salida) + relleno * (columnas - usado)


# --------------------------------------------------------------------------- #
# 2 · PALETA — nueve roles y la procedencia de cada uno
# --------------------------------------------------------------------------- #
#: `origen` no es decoración: es la frase que se puede defender en una revisión.
PALETA = {
    "fondo":      "#101418",
    "texto":      "#d8dee6",
    "tenue":      "#7c8894",
    "titulo":     "#8fd6ff",
    "borde":      "#2c3946",
    "acento":     "#4fb3e8",
    "ok":         "#5fd39a",
    "aviso":      "#e8b455",
    "error":      "#e06c75",
}

ORIGEN = {
    "fondo":  "derivado: gris azulado muy oscuro, para que el texto supere 12:1",
    "texto":  "derivado: gris claro neutro sobre el fondo anterior",
    "tenue":  "derivado: texto bajado de brillo; se usa solo en metadatos",
    "titulo": "derivado: acento aclarado; es el único color que grita",
    "borde":  "derivado: fondo aclarado; un marco no debe competir con el texto",
    "acento": "elegido: un solo azul para foco y selección",
    "ok":     "elegido: verde de estado correcto",
    "aviso":  "elegido: ámbar de estado dudoso",
    "error":  "elegido: rojo de estado fallido",
}


# --------------------------------------------------------------------------- #
# 3 · COMPOSICIÓN — cuatro piezas de mobiliario, todas reutilizables
# --------------------------------------------------------------------------- #
def caja(c: Lienzo, x: int, y: int, ancho_: int, alto_: int, titulo: str = "") -> None:
    """Marco de una línea con el título en el borde. **No se reimplementa:**

    `Lienzo.caja()` ya lo hace y, además, registra el panel para que el
    verificador sepa dónde debería estar cada borde. Escribir aquí un `caja()`
    propio es el error que deja medio proyecto sin verificar.
    """
    c.caja(x, y, ancho_, alto_, titulo, estilo="borde", titulo_estilo="titulo")


def pie(c: Lienzo, teclas: list[tuple[str, str]], y: int = ALTO - 2) -> None:
    """El contrato visible: qué se puede hacer ahora mismo."""
    x = 2
    for tecla, accion in teclas:
        c.texto(x, y, tecla, "acento")
        c.texto(x + ancho(tecla) + 1, y, accion, "tenue")
        x += ancho(tecla) + ancho(accion) + 5


def cabecera(c: Lienzo, titulo: str, derecha: str = "") -> None:
    c.texto(0, 0, ajustar(f" {titulo}", ANCHO - ancho(derecha) - 1), "titulo")
    if derecha:
        c.texto(ANCHO - ancho(derecha), 0, derecha, "tenue")
    c.texto(0, 1, "─" * ANCHO, "borde")


# --------------------------------------------------------------------------- #
# 4 · ESTADOS — tres pantallas: lista, detalle y diálogo
# --------------------------------------------------------------------------- #
FILAS = [
    ("backups/2026-11", "12 ficheros", "ok"),
    ("backups/2026-10", "9 ficheros", "ok"),
    ("backups/2026-09", "0 ficheros", "aviso"),
    ("backups/2026-08", "31 ficheros", "error"),
    ("backups/2026-07", "27 ficheros", "ok"),
]


def pantalla_lista(c: Lienzo) -> None:
    """El estado por defecto: qué hay y cuál está elegido."""
    cabecera(c, "copias", "5 carpetas · 79 ficheros")
    caja(c, 1, 3, 62, 22, "carpetas")
    for i, (ruta, cuenta, estado) in enumerate(FILAS):
        fila = 4 + i * 2
        elegido = i == 1
        if elegido:                                   # primero el relleno…
            c.relleno(2, fila, 60, 1, "acento")
        c.texto(3, fila, ajustar(ruta, 34), "fondo" if elegido else "texto")
        c.texto(38, fila, ajustar(cuenta, 13), "fondo" if elegido else "tenue")
        marca = {"ok": "●", "aviso": "◐", "error": "○"}[estado]
        c.texto(56, fila, marca, "fondo" if elegido else estado)

    caja(c, 65, 3, 34, 22, "resumen")   # 2 columnas de pasillo: lo exige el verificador
    c.texto(67, 5, "total", "tenue")
    c.texto(67, 6, "79 ficheros", "texto")
    c.texto(67, 8, "última copia", "tenue")
    c.texto(67, 9, "hace 2 h", "texto")
    c.texto(67, 11, "con incidencias", "tenue")
    c.texto(67, 12, "2 carpetas", "aviso")
    pie(c, [("↑↓", "mover"), ("⏎", "abrir"), ("q", "salir")])


def pantalla_detalle(c: Lienzo) -> None:
    """El segundo estado: el contenido de lo elegido."""
    cabecera(c, "backups/2026-10 · 9 ficheros", "hace 30 días")
    caja(c, 1, 3, ANCHO - 2, 22, "contenido")
    for i in range(9):
        fila = 4 + i
        c.texto(3, fila, ajustar(f"fichero_{i + 1:02d}.tar.zst", 34), "texto")
        c.texto(40, fila, ajustar(f"{1.2 + i * 0.4:.1f} MiB", 12), "tenue")
        c.texto(55, fila, "ok" if i % 4 else "verificar", "ok" if i % 4 else "aviso")
    pie(c, [("↑↓", "mover"), ("⏎", "restaurar"), ("Esc", "volver")])


def pantalla_dialogo(c: Lienzo) -> None:
    """El tercer estado: una confirmación, con el foco lejos del botón peligroso."""
    cabecera(c, "copias · restauración", "")
    caja(c, 18, 8, 64, 11, "CONFIRMAR")
    c.texto(20, 10, "Se van a restaurar 9 ficheros sobre", "texto")
    c.texto(20, 11, "el directorio actual.", "texto")
    c.texto(20, 13, "Escribe restaurar para confirmar:", "tenue")
    c.texto(20, 14, "restaurar▌", "texto")
    c.relleno(20, 16, 16, 1, "acento")                # el foco está en «cancelar»
    c.texto(21, 16, "▸ cancelar", "fondo")            # …y además lleva marca
    c.texto(44, 16, "  restaurar", "tenue")
    pie(c, [("Esc", "cerrar"), ("⏎", "confirmar")])


PANTALLAS = [
    ("01", "Lista", "El estado por defecto: el relleno va antes que el texto.", pantalla_lista),
    ("02", "Detalle", "Lo elegido, con su pie de teclas propio.", pantalla_detalle),
    ("03", "Diálogo", "Confirmación con el foco lejos de lo destructivo.", pantalla_dialogo),
]


# --------------------------------------------------------------------------- #
# 5 · VERIFICACIÓN — lo barato que evita la mitad de los fallos
# --------------------------------------------------------------------------- #
def verificar(numero: str, lienzo: Lienzo) -> list[str]:
    problemas = []
    validos = set(PALETA) | {"seleccion"}
    for y, fila in enumerate(lienzo.lineas()):
        if ancho(fila) != ANCHO:
            problemas.append(f"[{numero}] fila {y}: {ancho(fila)} columnas, no {ANCHO}")
    for y, fila in enumerate(lienzo.rejilla):
        for x, celda in enumerate(fila):
            if celda.estilo and celda.estilo not in validos:
                problemas.append(f"[{numero}] celda ({x},{y}): estilo {celda.estilo!r} sin declarar")
    problemas += [f"[{numero}] {p}" for p in lienzo.comprobar()]
    return problemas


def construir() -> list[tuple[str, str, str, Lienzo]]:
    salida = []
    for numero, nombre, nota, funcion in PANTALLAS:
        lienzo = Lienzo(ANCHO, ALTO)
        funcion(lienzo)
        salida.append((numero, nombre, nota, lienzo))
    return salida


# --------------------------------------------------------------------------- #
# salida: TXT sin un solo escape y ANSI con color de verdad
# --------------------------------------------------------------------------- #
def _rgb(hexa: str) -> str:
    return f"{int(hexa[1:3], 16)};{int(hexa[3:5], 16)};{int(hexa[5:7], 16)}"


ANSI = {clave: f"\x1b[38;2;{_rgb(valor)};48;2;{_rgb(PALETA['fondo'])}m"
        for clave, valor in PALETA.items()}
ANSI["acento"] += "\x1b[1m"


def pintar(lienzo: Lienzo) -> str:
    salida = []
    for fila in lienzo.rejilla:
        actual, trozo = None, []
        for celda in fila:
            if celda.estilo != actual:
                if trozo:
                    salida.append(ANSI.get(actual, "") + "".join(trozo) + "\x1b[0m")
                actual, trozo = celda.estilo, [celda.char]
            else:
                trozo.append(celda.char)
        salida.append(ANSI.get(actual, "") + "".join(trozo) + "\x1b[0m\n")
    return "".join(salida)


def main(argv: list[str]) -> int:
    pantallas = construir()

    if "--test" in argv:
        problemas = [p for numero, _, _, lienzo in pantallas
                     for p in verificar(numero, lienzo)]

        # Prueba negativa: un verificador que nunca falla no verifica nada.
        roto = Lienzo(ANCHO, ALTO)
        pantalla_lista(roto)
        roto.texto(99, 4, "X", "rojo")            # estilo que no está en la paleta
        roto.texto(30, 24, "#", "texto")          # celda de contenido sobre el borde
        detectados = verificar("00", roto)

        for p in problemas:
            print("FALLA:", p)
        if len(detectados) < 2:
            print("FALLA: la prueba negativa no detectó las dos averías plantadas")
            problemas.append("prueba negativa")
        print("plantilla:", "ok" if not problemas else f"{len(problemas)} problemas",
              f"· la prueba negativa detectó {len(detectados)} averías")
        return 1 if problemas else 0

    if "--ansi" in argv:
        for numero, nombre, _, lienzo in pantallas:
            print(f"\n── {numero} · {nombre}".ljust(ANCHO, "─"))
            sys.stdout.write(pintar(lienzo))
        return 0

    destino = Path(__file__).resolve().parent
    with open(destino / "plantilla.txt", "w", encoding="utf-8") as fh:
        for numero, nombre, _, lienzo in pantallas:
            fh.write(f"\n=== {numero} · {nombre} " + "=" * (ANCHO - len(nombre) - 8) + "\n")
            fh.write("\n".join(linea.rstrip() for linea in lienzo.lineas()) + "\n")
    (destino / "plantilla.html").write_text(construir_html(pantallas), encoding="utf-8")

    problemas = [p for numero, _, _, lienzo in pantallas for p in verificar(numero, lienzo)]
    anchos = {ancho(linea) for _, _, _, lienzo in pantallas for linea in lienzo.lineas()}
    print(f"{len(pantallas)} pantallas · {ANCHO}×{ALTO} · anchos {sorted(anchos)} · "
          f"{len(PALETA)} colores · {len(problemas)} problemas → plantilla.txt y plantilla.html")
    return 1 if problemas else 0


def construir_html(pantallas) -> str:
    """El HTML no es la plantilla: es una comodidad para revisarla en el navegador."""
    def fila_html(fila) -> str:
        trozos, actual, buffer = [], "", []
        for celda in fila:
            if celda.estilo != actual:
                if buffer:
                    trozos.append(f'<i class="c-{actual}">{"".join(buffer)}</i>')
                actual, buffer = celda.estilo, [celda.char]
            else:
                buffer.append(celda.char)
        trozos.append(f'<i class="c-{actual}">{"".join(buffer)}</i>')
        return "".join(trozos)

    estilos = "\n".join(f".c-{k}{{color:{v}}}" for k, v in PALETA.items())
    estilos += "\n.c-{color:" + PALETA["fondo"] + "}"
    secciones = "".join(
        f'<section><h2>{n} · {html.escape(nombre)}</h2>'
        f'<p>{html.escape(nota)}</p><pre>'
        + "\n".join(fila_html(fila) for fila in lienzo.rejilla)
        + "</pre></section>"
        for n, nombre, nota, lienzo in pantallas)
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>plantilla · TUI</title><style>
body{{background:#0b0f14;color:#d8dee6;font-family:system-ui,sans-serif;margin:0;padding:40px}}
.wrap{{max-width:1000px;margin:0 auto}}
h1{{font-size:26px;font-weight:500;margin:0 0 6px}}
.sub{{color:#7c8894;margin:0 0 34px}}
h2{{font-size:14px;font-weight:600;color:#8fd6ff;margin:34px 0 4px}}
p{{color:#7c8894;font-size:13px;margin:0 0 10px}}
pre{{background:{PALETA["fondo"]};border:1px solid #1d2733;border-radius:8px;
padding:18px 20px;overflow-x:auto;line-height:1.32;
font-family:"DejaVu Sans Mono",monospace;font-size:12px}}
section{{page-break-inside:avoid}}
{estilos}
</style></head><body><div class="wrap">
<h1>plantilla · TUI mínima</h1>
<p class="sub">Tres pantallas, nueve colores, un verificador. Copiar y cambiar los datos.</p>
{secciones}
</div></body></html>"""


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
