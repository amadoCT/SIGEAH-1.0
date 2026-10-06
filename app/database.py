"""Conexión y esquema de la base de datos SQLite de SIGEAH."""

import os
import sqlite3
from pathlib import Path
from app.validaciones import validar_id, validar_transicion_estado


RUTA_POR_DEFECTO = Path("data") / "sigeah.db"


def obtener_ruta_db() -> str:
    """Devuelve la ruta de la base de datos.

    Lee la variable de entorno SIGEAH_DB_PATH; si no existe,
    usa ``data/sigeah.db``.

    Returns:
        Ruta del archivo de base de datos como cadena.
    """
    return os.getenv("SIGEAH_DB_PATH", str(RUTA_POR_DEFECTO))


def conectar(ruta: str | None = None) -> sqlite3.Connection:
    """Abre una conexión a la base de datos.

    Args:
        ruta: Ruta del archivo, o ``":memory:"`` para una base temporal.
            Si es None se usa :func:`obtener_ruta_db`.

    Returns:
        Conexión SQLite cuyas filas se pueden leer por nombre de columna.

    Raises:
        sqlite3.Error: Si no se puede abrir la base de datos.
    """
    ruta = ruta or obtener_ruta_db()
    if ruta != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db(conexion: sqlite3.Connection) -> None:
    """Crea la tabla ``emergencias`` si todavía no existe.

    Args:
        conexion: Conexión SQLite abierta.

    Raises:
        sqlite3.Error: Si falla la creación de la tabla.
    """
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS emergencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            estado TEXT NOT NULL
        )
        """
    )
    conexion.commit()


def obtener_emergencia_por_id(conexion: sqlite3.Connection, id_emergencia) -> sqlite3.Row | None:
    """Busca y devuelve una emergencia por su ID."""
    id_validado = validar_id(id_emergencia)
    cursor = conexion.execute(
        "SELECT * FROM emergencias WHERE id = ?", (id_validado,)
    )
    return cursor.fetchone()


def actualizar_estado(conexion: sqlite3.Connection, id_emergencia, nuevo_estado: str) -> dict:
    """Valida y actualiza el estado de una emergencia existente en la base de datos."""
    # 1. Validar que la emergencia exista
    emergencia = obtener_emergencia_por_id(conexion, id_emergencia)
    if not emergencia:
        raise ValueError(f"No se encontró ninguna emergencia con el ID {id_emergencia}.")

    # 2. Validar la transición del estado actual al nuevo
    estado_actual = emergencia["estado"]
    estado_validado = validar_transicion_estado(estado_actual, nuevo_estado)

    # 3. Actualizar en la base de datos
    conexion.execute(
        "UPDATE emergencias SET estado = ? WHERE id = ?",
        (estado_validado, emergencia["id"]),
    )
    conexion.commit()

    # 4. Devolver la emergencia actualizada como diccionario
    emergencia_actualizada = obtener_emergencia_por_id(conexion, emergencia["id"])
    return dict(emergencia_actualizada)
