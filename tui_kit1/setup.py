"""Instalador opcional de TUI Kit."""

from setuptools import setup, find_packages

setup(
    name="tui_kit",
    version="0.1.0",
    description="Kit de interfaz de terminal genérico (TUI) para CLI en Python.",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ejemplo-tui=ejemplo.uso:main",
        ],
    },
)
