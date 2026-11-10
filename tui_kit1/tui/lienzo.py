"""Lienzo de dibujo para terminal.

Provee primitivas para construir interfaces de texto: títulos, frases con
semántica, tablas, pares clave-valor, cajas con borde y reglas separadoras.
"""

from __future__ import annotations

from typing import Iterable

from .tema import Tema, RESET, NEGRITA


class Lienzo:
    """Objeto que pinta en la salida de terminal.

    Recibe un tema y escribe directamente a `salida` (por defecto stdout).
    """

    def __init__(self, tema: Tema | None = None, salida=None) -> None:
        import sys

        self.tema = tema or Tema()
        self.salida = salida or sys.stdout

    # ------------------------------------------------------------------ #
    # Escritura directa
    # ------------------------------------------------------------------ #

    def escribir(self, texto: str = "") -> None:
        """Escribe una línea en la salida."""
        self.salida.write(texto + "\n")
        self.salida.flush()

    def volcar(self, texto: str) -> None:
        """Escribe texto sin salto de línea adicional (útil para bloques)."""
        self.salida.write(texto)
        self.salida.flush()

    # ------------------------------------------------------------------ #

    def pintar(self, texto: str, clave: str) -> str:
        """Aplica color semántico a `texto` según el tema activo."""
        return self.tema.pinta(texto, clave)

    def frase(self, texto: str, clave: str = "texto") -> str:
        """Devuelve `texto` con el color de `clave` listo para imprimir."""
        return self.pintar(texto, clave)

    def ok(self, texto: str = "") -> str:
        return self.pintar(texto or "✓", "exito")

    def fallo(self, texto: str = "") -> str:
        return self.pintar(texto or "✖", "error")

    def aviso(self, texto: str = "") -> str:
        return self.pintar(texto or "⚠", "aviso")

    def info(self, texto: str = "") -> str:
        return self.pintar(texto or "ℹ", "texto")

    # ------------------------------------------------------------------ #
    # Elementos de pantalla
    # ------------------------------------------------------------------ #

    def titulo(self, texto: str, subtitulo: str = "") -> str:
        """Devuelve una línea de título con borde inferior."""
        linea = f"{NEGRITA}{self.pintar(texto, 'resaltado')}{RESET}"
        if subtitulo:
            linea += f"  {self.pintar(subtitulo, 'tenue')}"
        return linea

    def regla(self, caracter: str = "─", largo: int | None = None) -> str:
        """Devuelve una regla horizontal."""
        if largo is None:
            largo = 60
        return self.pintar(caracter * largo, "borde")

    def pares(
        self,
        filas: list[tuple[str, str]],
        sangria: int = 2,
        separador: str = " = ",
    ) -> str:
        """Devuelve una lista de pares clave = valor alineados."""
        if not filas:
            return ""
        largo_clave = max(len(k) for k, _ in filas)
        lineas = []
        for clave, valor in filas:
            clave_pintada = self.pintar(clave, "etiqueta")
            valor_pintada = self.pintar(valor, "valor")
            lineas.append(
                " " * sangria
                + clave_pintada.ljust(largo_clave)
                + separador
                + valor_pintada
            )
        return "\n".join(lineas)

    def tabla(
        self,
        cabeceras: list[str],
        filas: list[list[str]],
        anchos_minimos: list[int] | None = None,
    ) -> str:
        """Devuelve una tabla alineada con bordes sencillos."""
        if not cabeceras and not filas:
            return ""

        columnas = len(cabeceras) if cabeceras else len(filas[0])
        anchos = [0] * columnas

        for i in range(columnas):
            valores = [str(filas[f][i]) for f in range(len(filas))]
            if cabeceras:
                valores.append(cabeceras[i])
            anchos[i] = max(len(v) for v in valores)
            if anchos_minimos and anchos_minimos[i] > anchos[i]:
                anchos[i] = anchos_minimos[i]

        partes = []

        def celda(texto: str, ancho: int, clave: str = "texto") -> str:
            return self.pintar(texto.ljust(ancho), clave)

        # Cabecera
        if cabeceras:
            fila_cab = "  ".join(
                celda(cabeceras[i], anchos[i], "etiqueta") for i in range(columnas)
            )
            partes.append(fila_cab)
            partes.append(
                "  ".join(self.pintar("─" * anchos[i], "borde") for i in range(columnas))
            )

        # Filas
        for fila in filas:
            partes.append(
                "  ".join(celda(str(fila[i]), anchos[i]) for i in range(columnas))
            )

        return "\n".join(partes)

    def caja(
        self,
        lineas: list[str],
        titulo: str | None = None,
        borde: str = "│",
    ) -> str:
        """Devuelve `lineas` envueltas en un cuadro sencillo."""
        if not lineas:
            return ""

        ancho = max(len(l) for l in lineas)
        if titulo:
            ancho = max(ancho, len(titulo) + 2)

        partes = []
        partes.append(self.pintar("┌" + "─" * (ancho + 2) + "┐", "borde"))
        if titulo:
            partes.append(
                self.pintar(borde, "borde")
                + " "
                + self.pintar(titulo, "resaltado").ljust(ancho)
                + " "
                + self.pintar(borde, "borde")
            )
            partes.append(
                self.pintar("├" + "─" * (ancho + 2) + "┤", "borde")
            )
        for linea in lineas:
            partes.append(
                self.pintar(borde, "borde")
                + " "
                + linea.ljust(ancho)
                + " "
                + self.pintar(borde, "borde")
            )
        partes.append(self.pintar("└" + "─" * (ancho + 2) + "┘", "borde"))
        return "\n".join(partes)

    def bloque_error(
        self,
        mensaje: str,
        contacto: str = "",
        carpeta_informes: str = "",
    ) -> str:
        """Devuelve un bloque de error legible para mostrar al usuario."""
        lineas = [self.pintar("✖ Error:", "error"), "", mensaje]
        if contacto:
            lineas += ["", f"Contacto: {contacto}"]
        if carpeta_informes:
            lineas += [f"Informes: {carpeta_informes}"]
        return self.caja(lineas, titulo="Error")
