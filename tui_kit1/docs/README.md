# TUI Kit — Interfaz de terminal genérica

Kit de construcción para interfaces de línea de órdenes (CLI/TUI) basado en los
patrones de Muelle, pero **desvinculado de cualquier producto específico**.
No menciona a Muelle, Hannon, Vitruvio ni La Groma. Está listo para usarse como
inspiración o base en cualquier proyecto propio.

---

## Temas para terminal (no hay temas de interfaz gráfica)

Se eliminaron los 3 temas de web (osuro, claro, sepia) porque no tienen
utilidad en una terminal. En su lugar, el kit trae los **7 temas de emulación
de monitores antiguos**, que sí tienen sentido en una TUI:

| Tema | Descripción |
|------|-------------|
| `alto_contraste` | Blanco puro sobre negro, máximo contraste. |
| `ambar` | Texto ámbar sobre negro, como monitores IBM antiguos. |
| `blanco_calido` | Blanco con tono amarillento sobre negro. |
| `daltonico` | Colores seguros para daltónicos (evita confusión rojo/verde). |
| `fosforo` | Texto verde fosforescente sobre negro, monitores antiguos. |
| `fosforo_color` | Verde fosforescente con acento de color. |
| `verde_apagado` | Texto verde oscuro sobre negro, monitores de oficina. |

También incluye `mono` para tuberías o sesiones remotas sin color.

---

## ¿Qué incluye?

| Módulo | Qué hace |
|--------|----------|
| `tui/lienzo.py` | Dibujo en terminal: títulos, frases, tablas, pares clave-valor, cajas con borde, reglas y bloques de error. |
| `tui/tema.py` | Temas de terminal (los 7 de monitores antiguos + mono). |
| `tui/prompt.py` | Entrada segura de teclado: texto, contraseña oculta y confirmación sí/no. |
| `ejemplo/uso.py` | Aplicación ficticia de gestor de biblioteca para ver el kit en acción. |

---

## Instalación

Solo necesita Python 3. No hay dependencias externas:

```bash
python ejemplo/uso.py
```

O como módulo:

```bash
python -m ejemplo.uso
```

---

## Uso rápido en tu propio proyecto

```python
from tui import Lienzo, Tema, preguntar_texto, preguntar_si_no

tema = Tema("fosforo")  # tema de monitor antiguo
lienzo = Lienzo(tema=tema)

# Título y frase con semántica
lienzo.escribir(lienzo.titulo("Mi aplicación"))
lienzo.escribir(lienzo.frase("Bienvenido", "exito"))

# Tabla
lienzo.escribir(
    lienzo.tabla(
        ["Producto", "Precio"],
        [["Manzana", "$1.00"], ["Pan", "$2.50"]],
    )
)

# Caja con borde
lienzo.escribir(
    lienzo.caja(
        ["Opción 1", "Opción 2", "Opción 3"],
        titulo="Menú",
    )
)

# Entrada segura
nombre = preguntar_texto(lienzo, "¿Cómo te llamas?")
if nombre is not None:
    lienzo.escribir(lienzo.ok(f"Hola, {nombre}"))
```

---

## Principios

* Solo biblioteca estándar de Python.
* Sin colores de interfaz gráfica (no hay temas tipo fosforo web, sepia, etc.).
* Semántica de terminal: éxito, aviso, error, información, borde, etiqueta, valor.
* Entrada protegida contra Ctrl+C y fin de entrada (EOF).

---

## Origen

Los patrones de dibujo (lienzo, tabla, caja, pares) están inspirados en la
interfaz de terminal de Muelle, pero este kit es independiente y no contiene
ni una referencia a Muelle, Hannon, Vitruvio ni La Groma.
