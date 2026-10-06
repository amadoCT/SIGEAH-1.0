"""Conexión y esquema de la base de datos SQLite de SIGEAH."""

import os
import sqlite3
from pathlib import Path

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
