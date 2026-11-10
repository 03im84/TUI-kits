#!/usr/bin/env python3
"""Lanzador de la réplica de la TUI.

    python3 main.py                      # interactivo si hay terminal; si no, guion
    python3 main.py --guion              # fuerza el guion de marcos
    python3 main.py --guion --lang en --size 76x24 --ascii
    python3 main.py --guion --out marcos.txt
    python3 main.py --guion --solo resultado

Sin dependencias: solo la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tuikit.backend import DemoBackend
from tuikit.demo import GUION, run, storyboard, volcar
from tuikit.i18n import CATALOGOS
from tuikit import theme


def _tamano(texto: str) -> tuple[int, int]:
    try:
        ancho, alto = texto.lower().split("x")
        return max(20, int(ancho)), max(8, int(alto))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("usa ANCHOxALTO, por ejemplo 92x26") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="main.py", description="Réplica de la TUI de Incunable (demostración).")
    parser.add_argument("--lang", default="es", choices=sorted(CATALOGOS),
                        help="idioma de la interfaz (es, en)")
    parser.add_argument("--size", type=_tamano, default=(92, 26), metavar="ANCHOxALTO",
                        help="tamaño del marco en el guion (por omisión 92x26)")
    parser.add_argument("--ascii", action="store_true",
                        help="sin dibujo de caja ni flechas unicode")
    parser.add_argument("--guion", action="store_true",
                        help="recorre el guion y vuelca los marcos (no interactivo)")
    parser.add_argument("--solo", metavar="PANTALLA", default="",
                        help="con --guion, deja solo los marcos cuyo título lo mencione")
    parser.add_argument("--out", metavar="ARCHIVO", default="",
                        help="con --guion, escribe ahí en vez de por pantalla")
    parser.add_argument("--tema", default=theme.DEFAULT, choices=sorted(theme.PALETTES),
                        help="tema de color para el modo interactivo")
    args = parser.parse_args(argv)

    if args.guion:
        marcos = storyboard(args.size[0], args.size[1], lang=args.lang, ascii_only=args.ascii)
        if args.solo:
            aguja = args.solo.casefold()
            marcos = [par for par in marcos if aguja in par[0].casefold()] or marcos[:1]
        if args.out:
            destino = Path(args.out)
            destino.parent.mkdir(parents=True, exist_ok=True)
            with destino.open("w", encoding="utf-8") as fichero:
                volcar(marcos, fichero)
            print(f"{len(marcos)} marcos → {destino}", file=sys.stderr)
            return 0
        volcar(marcos)
        return 0

    return run(lang=args.lang, ascii_only=args.ascii, backend=DemoBackend())


if __name__ == "__main__":
    raise SystemExit(main())
