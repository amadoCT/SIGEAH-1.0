"""Módulo principal de SIGEAH-1.0: menú interactivo por consola."""

from rich.console import Console
from rich.panel import Panel

from app.consola import (
    actualizar_estado_interactivo,
    consultar_interactivo,
    registrar_interactivo,
)
from app.database import conectar, inicializar_db

consola = Console()

OPCIONES_MENU = (
    "1. Registrar emergencia",
    "2. Consultar y filtrar emergencias",
    "3. Actualizar estado de emergencia",
    "4. Salir",
)


def mostrar_menu() -> None:
    """Muestra el menú principal."""
    consola.print(
        Panel("\n".join(OPCIONES_MENU), title="SIGEAH-1.0 - MENÚ", expand=False)
    )


def main() -> None:
    """Abre la base de datos y ejecuta el menú hasta que el usuario salga."""
    conexion = conectar()
    try:
        inicializar_db(conexion)
        while True:
            mostrar_menu()
            opcion = input("Seleccione una opción (1-4): ").strip()
            if opcion == "1":
                registrar_interactivo(conexion)
            elif opcion == "2":
                consultar_interactivo(conexion)
            elif opcion == "3":
                actualizar_estado_interactivo(conexion)
            elif opcion == "4":
                consola.print("\n¡Gracias por usar SIGEAH-1.0! Saliendo...")
                break
            else:
                consola.print("[red]Opción no válida. Intente de nuevo.[/red]")
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
