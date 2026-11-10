"""Ejemplo de aplicación usando TUI Kit.

Este es un gestor de biblioteca personal ficticio, completamente ajeno a
Muelle, Hannon o Vitruvio. Sirve únicamente como inspiración de cómo
construir una CLI con el kit.
"""

from __future__ import annotations

from tui import Lienzo, Tema, preguntar_texto, preguntar_clave, preguntar_si_no


class Biblioteca:
    """Modelo de datos ficticio: una lista de libros."""

    def __init__(self) -> None:
        self.libros: list[dict[str, str]] = []

    def agregar(self, titulo: str, autor: str) -> None:
        self.libros.append({"titulo": titulo, "autor": autor})

    def listar(self) -> list[dict[str, str]]:
        return self.libros


def cmd_listar(biblio: Biblioteca, lienzo: Lienzo) -> None:
    libros = biblio.listar()
    if not libros:
        lienzo.escribir(lienzo.frase("La biblioteca está vacía.", "aviso"))
        return

    filas = [[str(i + 1), l["titulo"], l["autor"]] for i, l in enumerate(libros)]
    lienzo.escribir()
    lienzo.escribir(lienzo.titulo("Libros registrados"))
    lienzo.escribir(
        lienzo.tabla(["#", "Título", "Autor"], filas)
    )
    lienzo.escribir()


def cmd_agregar(biblio: Biblioteca, lienzo: Lienzo) -> None:
    lienzo.escribir()
    lienzo.escribir(lienzo.titulo("Agregar libro"))
    titulo = preguntar_texto(lienzo, "Título del libro")
    if titulo is None:
        lienzo.escribir(lienzo.aviso("Operación cancelada."))
        return
    autor = preguntar_texto(lienzo, "Autor")
    if autor is None:
        lienzo.escribir(lienzo.aviso("Operación cancelada."))
        return

    biblio.agregar(titulo, autor)
    lienzo.escribir(lienzo.ok(f"Se agregó '{titulo}' de {autor}."))


def cmd_configurar(lienzo: Lienzo) -> None:
    """Muestra cómo usar el tema y el prompt de confirmación."""
    lienzo.escribir()
    lienzo.escribir(lienzo.titulo("Configuración"))
    tema_actual = lienzo.tema.nombre
    lienzo.escribir(f"Tema actual: {tema_actual}")

    cambiar = preguntar_si_no(lienzo, "¿Cambiar tema a 'claro'?", defecto_si=False)
    if cambiar is None:
        lienzo.escribir(lienzo.aviso("Operación cancelada."))
        return
    if cambiar:
        lienzo.tema = Tema("claro")
        lienzo.escribir(lienzo.ok("Tema cambiado a claro."))
    else:
        lienzo.escribir(lienzo.info("Se mantiene el tema actual."))


def menu_principal(lienzo: Lienzo, biblio: Biblioteca) -> None:
    """Bucle principal de la aplicación."""
    while True:
        lienzo.escribir()
        lienzo.escribir(lienzo.titulo("Gestor de Biblioteca Personal"))
        lienzo.escribir(lienzo.caja(
            ["1. Listar libros",
             "2. Agregar libro",
             "3. Configurar tema",
             "4. Salir"],
            titulo="Opciones",
        ))
        lienzo.escribir()

        opcion = preguntar_texto(lienzo, "Elige una opción")
        if opcion is None:
            lienzo.escribir(lienzo.info("Saliendo..."))
            break

        if opcion == "1":
            cmd_listar(biblio, lienzo)
        elif opcion == "2":
            cmd_agregar(biblio, lienzo)
        elif opcion == "3":
            cmd_configurar(lienzo)
        elif opcion == "4":
            lienzo.escribir(lienzo.ok("¡Hasta luego!"))
            break
        else:
            lienzo.escribir(lienzo.fallo("Opción no válida."))


def main() -> None:
    """Punto de entrada de la aplicación de ejemplo."""
    tema = Tema("fosforo")
    lienzo = Lienzo(tema=tema)

    biblio = Biblioteca()
    # Datos de ejemplo
    biblio.agregar("Cien años de soledad", "Gabriel García Márquez")
    biblio.agregar("1984", "George Orwell")

    try:
        menu_principal(lienzo, biblio)
    except KeyboardInterrupt:
        lienzo.escribir()
        lienzo.escribir(lienzo.info("Interrumpido por el usuario."))


if __name__ == "__main__":
    main()
