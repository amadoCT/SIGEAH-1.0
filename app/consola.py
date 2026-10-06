"""Interfaz de consola de SIGEAH: entradas del usuario y presentación."""

import sqlite3
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from app.database import actualizar_estado
from app.emergencia import Emergencia, listar_emergencias, registrar_emergencia
from app.validaciones import ESTADOS, PRIORIDADES, TIPOS_EMERGENCIA

consola = Console()

COLORES_PRIORIDAD = {"baja": "green", "media": "yellow", "alta": "red"}
TODOS = "todos"


def mostrar_titulo(texto: str) -> None:
    """Muestra un encabezado destacado.

    Args:
        texto: Texto del encabezado.
    """
    consola.print(Panel(texto, style="bold cyan", expand=False))


def mostrar_tabla(emergencias: list) -> None:
    """Muestra una lista de emergencias en forma de tabla.

    Args:
        emergencias: Lista de objetos Emergencia.
    """
    if not emergencias:
        consola.print("[yellow]No hay emergencias que coincidan.[/yellow]")
        return
    tabla = Table(title=f"Emergencias ({len(emergencias)})")
    for columna in (
        "ID",
        "Título",
        "Tipo",
        "Ubicación",
        "Fecha",
        "Prioridad",
        "Estado",
    ):
        tabla.add_column(columna)
    for e in emergencias:
        color = COLORES_PRIORIDAD.get(e.prioridad, "white")
        tabla.add_row(
            str(e.id),
            e.titulo,
            e.tipo,
            e.ubicacion,
            e.fecha,
            f"[{color}]{e.prioridad}[/{color}]",
            e.estado,
        )
    consola.print(tabla)


def _pedir_texto(nombre: str, anterior: str | None = None) -> str:
    """Pide un texto; si hay un valor anterior, lo ofrece como predeterminado.

    Args:
        nombre: Nombre del campo que se muestra al usuario.
        anterior: Valor escrito en un intento previo, si existe.

    Returns:
        El texto escrito por el usuario.
    """
    if anterior:
        return Prompt.ask(nombre, default=anterior)
    return Prompt.ask(nombre)


def registrar_interactivo(conexion: sqlite3.Connection) -> None:
    """Pide los datos de una emergencia y la registra.

    Si los datos son inválidos muestra el error y permite reintentar
    conservando lo escrito.

    Args:
        conexion: Conexión SQLite abierta.
    """
    mostrar_titulo("Registrar emergencia")
    ahora = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    datos = {"fecha": ahora, "prioridad": "media", "estado": "pendiente"}
    while True:
        datos["titulo"] = _pedir_texto("Título", datos.get("titulo"))
        datos["tipo"] = Prompt.ask(
            "Tipo", choices=list(TIPOS_EMERGENCIA), default=datos.get("tipo", "otro")
        )
        datos["descripcion"] = _pedir_texto("Descripción", datos.get("descripcion"))

        datos["ubicacion"] = _pedir_texto("Ubicación", datos.get("ubicacion"))
        datos["fecha"] = Prompt.ask(
            "Fecha y hora (AAAA-MM-DD HH:MM)", default=datos["fecha"]
        )
        datos["prioridad"] = Prompt.ask(
            "Prioridad", choices=list(PRIORIDADES), default=datos["prioridad"]
        )
        datos["estado"] = Prompt.ask(
            "Estado", choices=list(ESTADOS), default=datos["estado"]
        )
        try:
            emergencia = registrar_emergencia(conexion, datos)
        except (ValueError, TypeError) as error:
            consola.print(f"[bold red]Datos inválidos:[/bold red] {error}")
            if not Confirm.ask("¿Corregir y reintentar?", default=True):
                return
            continue
        except RuntimeError as error:
            consola.print(f"[bold red]Error:[/bold red] {error}")
            return
        consola.print(
            f"[bold green]Emergencia registrada con ID {emergencia.id}.[/bold green]"
        )
        return


def _filtro(nombre: str, opciones: tuple) -> str | None:
    """Pregunta un filtro opcional.

    Args:
        nombre: Nombre del filtro que se muestra al usuario.
        opciones: Valores permitidos.

    Returns:
        El valor elegido, o None si el usuario eligió "todos".
    """
    valor = Prompt.ask(nombre, choices=[TODOS, *opciones], default=TODOS)
    return None if valor == TODOS else valor


def consultar_interactivo(conexion: sqlite3.Connection) -> None:
    """Pide criterios de búsqueda y muestra las emergencias que coinciden.

    Args:
        conexion: Conexión SQLite abierta.
    """
    mostrar_titulo("Consultar y filtrar emergencias")
    texto = Prompt.ask(
        "Buscar en título o ubicación (Enter = sin búsqueda)", default=""
    )
    tipo = _filtro("Tipo", TIPOS_EMERGENCIA)
    estado = _filtro("Estado", ESTADOS)
    prioridad = _filtro("Prioridad", PRIORIDADES)
    try:
        resultado = listar_emergencias(
            conexion, texto=texto, tipo=tipo, estado=estado, prioridad=prioridad
        )
    except RuntimeError as error:
        consola.print(f"[bold red]Error:[/bold red] {error}")
        return
    mostrar_tabla(resultado)


def actualizar_estado_interactivo(conexion: sqlite3.Connection) -> None:
    """Pide un id y un nuevo estado, y actualiza la emergencia.

    Args:
        conexion: Conexión SQLite abierta.
    """
    mostrar_titulo("Actualizar estado de emergencia")
    try:
        mostrar_tabla(listar_emergencias(conexion))
    except RuntimeError as error:
        consola.print(f"[bold red]Error:[/bold red] {error}")
        return
    id_texto = Prompt.ask(
        "ID de la emergencia (Enter para cancelar)", default="", show_default=False
    )
    if not id_texto.strip():
        return
    nuevo_estado = Prompt.ask("Nuevo estado", choices=list(ESTADOS))
    try:
        actualizada = actualizar_estado(conexion, id_texto, nuevo_estado)
    except (ValueError, TypeError) as error:
        consola.print(f"[bold red]No se pudo actualizar:[/bold red] {error}")
        return
    except sqlite3.Error:
        conexion.rollback()
        consola.print(
            "[bold red]Error al guardar el cambio en la base de datos.[/bold red]"
        )
        return
    mostrar_tabla([Emergencia(**actualizada)])
    consola.print("[bold green]Estado actualizado.[/bold green]")
