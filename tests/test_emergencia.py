"""Pruebas unitarias para el módulo de emergencias (Issue #2 / RF-01)."""

import pytest

from app.database import conectar, inicializar_db
from app.emergencia import obtener_emergencia, registrar_emergencia


@pytest.fixture
def conexion():
    """Proporciona una conexión de base de datos SQLite en memoria."""
    conn = conectar(":memory:")
    inicializar_db(conn)
    return conn


def datos_validos():
    """Retorna un diccionario con datos de prueba válidos."""
    return {
        "titulo": "Inundación en Santiago",
        "tipo": "inundacion",
        "descripcion": "Desborde de río en el sector central",
        "ubicacion": "Santiago, Veraguas",
        "fecha": "2026-10-05 14:30",
        "prioridad": "alta",
        "estado": "pendiente",
    }


def test_registrar_emergencia_exito(conexion):
    """Verifica que una emergencia válida se guarde correctamente."""
    datos = datos_validos()
    emergencia = registrar_emergencia(conexion, datos)

    assert emergencia is not None
    assert emergencia.id == 1
    assert emergencia.titulo == "Inundación en Santiago"
    assert emergencia.prioridad == "alta"


def test_obtener_emergencia_existente(conexion):
    """Verifica la búsqueda de una emergencia registrada."""
    datos = datos_validos()
    creada = registrar_emergencia(conexion, datos)

    encontrada = obtener_emergencia(conexion, creada.id)
    assert encontrada is not None
    assert encontrada.id == creada.id


def test_obtener_emergencia_inexistente(conexion):
    """Verifica que obtener_emergencia retorne None si no existe el ID."""
    assert obtener_emergencia(conexion, 999) is None


def test_registrar_emergencia_datos_invalidos(conexion):
    """Verifica que falle si los datos no cumplen con las validaciones."""
    datos = datos_validos()
    datos["prioridad"] = "super-alta"

    with pytest.raises(ValueError):
        registrar_emergencia(conexion, datos)
