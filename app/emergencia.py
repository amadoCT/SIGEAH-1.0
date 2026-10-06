"""Modelo y operaciones de negocio para las emergencias de SIGEAH."""

import sqlite3
from dataclasses import dataclass

from app.validaciones import (
    validar_estado,
    validar_fecha_hora,
    validar_prioridad,
    validar_texto,
    validar_tipo_emergencia,
)


@dataclass
class Emergencia:
    """Representa una emergencia registrada en el sistema."""

    id: int
    titulo: str
    tipo: str
    descripcion: str
    ubicacion: str
    fecha: str
    prioridad: str
    estado: str


def validar_emergencia(datos: dict) -> dict:
    """Valida y limpia todos los campos de una emergencia.

    Args:
        datos: Diccionario con titulo, tipo, descripcion, ubicacion,
            fecha, prioridad y estado.

    Returns:
        Diccionario con los mismos campos ya validados y normalizados.

    Raises:
        TypeError: Si ``datos`` no es un diccionario.
        ValueError: Si algún campo no es válido."""

    if not isinstance(datos, dict):
        raise TypeError("Los datos de la emergencia deben ser un diccionario.")

    return {
        "titulo": validar_texto(datos.get("titulo"), "título", minimo=3, maximo=100),
        "tipo": validar_tipo_emergencia(datos.get("tipo")),
        "descripcion": validar_texto(
            datos.get("descripcion"), "descripción", minimo=5, maximo=500
        ),
        "ubicacion": validar_texto(
            datos.get("ubicacion"), "ubicación", minimo=3, maximo=200
        ),
        "fecha": validar_fecha_hora(datos.get("fecha")),
        "prioridad": validar_prioridad(datos.get("prioridad")),
        "estado": validar_estado(datos.get("estado")),
    }


def obtener_emergencia(
    conexion: sqlite3.Connection, id_emergencia: int
) -> Emergencia | None:
    """Busca una emergencia por su identificador.

    Args:
        conexion: Conexión SQLite abierta.
        id_emergencia: Identificador de la emergencia.

    Returns:
        La emergencia encontrada, o None si no existe."""

    fila = conexion.execute(
        "SELECT * FROM emergencias WHERE id = ?", (id_emergencia,)
    ).fetchone()
    return Emergencia(**dict(fila)) if fila else None


def registrar_emergencia(conexion: sqlite3.Connection, datos: dict) -> Emergencia:
    """Valida y guarda una nueva emergencia.

    Args:
        conexion: Conexión SQLite abierta.
        datos: Diccionario con los campos de la emergencia.

    Returns:
        La emergencia guardada, con su id asignado.

    Raises:
        TypeError: Si ``datos`` no es un diccionario.
        ValueError: Si algún campo no es válido.
        RuntimeError: Si falla el guardado en la base de datos."""

    limpios = validar_emergencia(datos)
    try:
        cursor = conexion.execute(
            """
            INSERT INTO emergencias
                (titulo, tipo, descripcion, ubicacion, fecha, prioridad, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                limpios["titulo"],
                limpios["tipo"],
                limpios["descripcion"],
                limpios["ubicacion"],
                limpios["fecha"],
                limpios["prioridad"],
                limpios["estado"],
            ),
        )
        conexion.commit()
    except sqlite3.Error as error:
        conexion.rollback()
        raise RuntimeError("No se pudo guardar la emergencia.") from error

    return obtener_emergencia(conexion, cursor.lastrowid)


def listar_emergencias(
    conexion: sqlite3.Connection,
    texto: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    prioridad: str | None = None,
) -> list[Emergencia]:
    """Lista emergencias, con búsqueda y filtros opcionales.

    Args:
        conexion: Conexión SQLite abierta.
        texto: Fragmento a buscar en el título o la ubicación.
        tipo: Tipo de emergencia exacto (sin distinguir mayúsculas).
        estado: Estado exacto (sin distinguir mayúsculas).
        prioridad: Prioridad exacta (sin distinguir mayúsculas).

    Returns:
        Lista de emergencias que cumplen todos los criterios dados,
        de la más reciente a la más antigua.

    Raises:
        RuntimeError: Si ocurre un error al consultar la base de datos.
    """
    condiciones = []
    parametros = []
    if texto and texto.strip():
        patron = f"%{texto.strip()}%"
        condiciones.append("(titulo LIKE ? OR ubicacion LIKE ?)")
        parametros.extend([patron, patron])
    for columna, valor in (
        ("tipo", tipo),
        ("estado", estado),
        ("prioridad", prioridad),
    ):
        if valor and valor.strip():
            condiciones.append(f"{columna} = ? COLLATE NOCASE")
            parametros.append(valor.strip())

    consulta = "SELECT * FROM emergencias"
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    consulta += " ORDER BY id DESC"

    try:
        filas = conexion.execute(consulta, parametros).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError("No se pudo consultar las emergencias.") from error
    return [Emergencia(**dict(fila)) for fila in filas]
