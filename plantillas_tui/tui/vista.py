#!/usr/bin/env python3
"""Vista previa PNG de una pantalla — solo para revisar con los ojos.

    python3 tui/vista.py btop 01 salida.png

No forma parte del entregable: el motor de celdas ya sabe pintar en HTML y en
ANSI. Esto existe porque una regla del proyecto es «míralo, no lo confíes».
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from tui.apps1 import APPS1  # noqa: E402
from tui.apps2 import APPS2  # noqa: E402
from tui.comun import construir, paleta  # noqa: E402

FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
TAM = 15  # a 15 px DejaVuSansMono avanza 9,03 px por glifo: cabe en una celda


def hexa(valor: str) -> tuple[int, int, int]:
    valor = valor.lstrip("#")
    return tuple(int(valor[i:i + 2], 16) for i in (0, 2, 4))


def render(app, lienzo, destino: Path) -> None:
    col = paleta(app)
    fuente = ImageFont.truetype(FUENTE, TAM)
    ancho_celda = fuente.getlength("M")
    alto_celda = int(TAM * 1.32)
    ancho_px = int(lienzo.ancho * ancho_celda + 24)
    alto_px = lienzo.alto * alto_celda + 24
    img = Image.new("RGB", (ancho_px, alto_px), hexa(col["fondo"]))
    dibujo = ImageDraw.Draw(img)

    for y, fila in enumerate(lienzo.rejilla):
        x = 0
        while x < len(fila):
            estilo = fila[x].estilo
            texto = ""
            while x < len(fila) and fila[x].estilo == estilo:
                texto += fila[x].char
                x += 1
            px, py = 12 + (x - len(texto)) * ancho_celda, 12 + y * alto_celda
            if estilo == "seleccion":
                dibujo.rectangle([px, py, px + len(texto) * ancho_celda, py + alto_celda],
                                 fill=hexa(col["seleccion"]))
                color = hexa(col.get("sel_fg", col["texto"]))
            elif estilo == "inverso" and "inverso" in col:
                dibujo.rectangle([px, py, px + len(texto) * ancho_celda, py + alto_celda],
                                 fill=hexa(col["inverso"]))
                color = hexa(col["fondo"])
            elif estilo.startswith("#"):
                color = hexa(estilo)
            elif estilo in col:
                color = hexa(col[estilo])
            else:
                color = hexa(col["texto"])
            dibujo.text((px, py), texto, font=fuente, fill=color)
    img.save(destino)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    clave, numero, destino = argv[0], argv[1], Path(argv[2])
    apps = {a.clave: a for a in [*APPS1, *APPS2]}
    if clave not in apps:
        print(f"no existe {clave!r}; hay: {', '.join(apps)}", file=sys.stderr)
        return 1
    for num, _, _, lienzo in construir(apps[clave]):
        if num == numero:
            render(apps[clave], lienzo, destino)
            print(f"{destino} · {apps[clave].clave} {numero}")
            return 0
    print(f"{clave} no tiene pantalla {numero}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
