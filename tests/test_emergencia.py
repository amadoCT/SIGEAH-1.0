"""Pruebas unitarias para el módulo de emergencias.

Cubre RF-01 (registrar, Issue #2) y RF-02 (consultar y filtrar, Issue #4).
"""

import pytest

from app.database import conectar, inicializar_db
from app.emergencia import (
    listar_emergencias,
    obtener_emergencia,
    registrar_emergencia,
)


@pytest.fixture
def conexion():
    """Proporciona una conexión de base de datos SQLite en memoria."""
    conn = conectar(":memory:")
    inicializar_db(conn)
    return conn


@pytest.fixture
def conexion_con_datos(conexion):
    """Proporciona una base en memoria con tres emergencias registradas."""
    registrar_emergencia(conexion, datos_validos())
    registrar_emergencia(
        conexion,
        datos_validos(
            titulo="Incendio forestal",
            tipo="incendio",
            ubicacion="David, Chiriquí",
            prioridad="media",
        ),
    )
    registrar_emergencia(
        conexion,
        datos_validos(
            titulo="Accidente en carretera",
            tipo="accidente",
            ubicacion="Boquete, Chiriquí",
            estado="en proceso",
        ),
    )
    return conexion


def datos_validos(**cambios):
    """Retorna un diccionario con datos de prueba válidos.

    Args:
        **cambios: Campos que reemplazan a los valores por defecto.

    Returns:
        Diccionario con los campos de una emergencia.
    """
    datos = {
        "titulo": "Inundación en Santiago",
        "tipo": "inundacion",
        "descripcion": "Desborde de río en el sector central",
        "ubicacion": "Santiago, Veraguas",
        "fecha": "2026-10-05 14:30",
        "prioridad": "alta",
        "estado": "pendiente",
    }
    datos.update(cambios)
    return datos


# ---------- RF-01: registrar emergencia ----------


def test_registrar_emergencia_exito(conexion):
    """Verifica que una emergencia válida se guarde correctamente."""
    emergencia = registrar_emergencia(conexion, datos_validos())

    assert emergencia is not None
    assert emergencia.id == 1
    assert emergencia.titulo == "Inundación en Santiago"
    assert emergencia.prioridad == "alta"


def test_obtener_emergencia_existente(conexion):
    """Verifica la búsqueda de una emergencia registrada."""
    creada = registrar_emergencia(conexion, datos_validos())

    encontrada = obtener_emergencia(conexion, creada.id)
    assert encontrada is not None
    assert encontrada.id == creada.id


def test_obtener_emergencia_inexistente(conexion):
    """Verifica que obtener_emergencia retorne None si no existe el ID."""
    assert obtener_emergencia(conexion, 999) is None


def test_registrar_emergencia_datos_invalidos(conexion):
    """Verifica que falle si los datos no cumplen con las validaciones."""
    with pytest.raises(ValueError):
        registrar_emergencia(conexion, datos_validos(prioridad="super-alta"))


# ---------- RF-02: consultar y filtrar emergencias ----------


def test_listar_sin_filtros_devuelve_todas(conexion_con_datos):
    """Sin criterios se devuelven todas, de la más reciente a la más antigua."""
    resultado = listar_emergencias(conexion_con_datos)

    assert len(resultado) == 3
    assert [e.id for e in resultado] == [3, 2, 1]


def test_listar_base_vacia(conexion):
    """Una base sin registros devuelve una lista vacía."""
    assert listar_emergencias(conexion) == []


def test_buscar_por_texto_en_titulo(conexion_con_datos):
    """La búsqueda por texto encuentra coincidencias en el título."""
    resultado = listar_emergencias(conexion_con_datos, texto="incendio")

    assert [e.titulo for e in resultado] == ["Incendio forestal"]


def test_buscar_por_texto_en_ubicacion(conexion_con_datos):
    """La búsqueda por texto encuentra coincidencias en la ubicación."""
    resultado = listar_emergencias(conexion_con_datos, texto="david")

    assert [e.titulo for e in resultado] == ["Incendio forestal"]


def test_buscar_texto_con_espacios_se_limpia(conexion_con_datos):
    """Los espacios alrededor del texto buscado se ignoran."""
    resultado = listar_emergencias(conexion_con_datos, texto="  boquete  ")

    assert len(resultado) == 1


def test_filtrar_por_tipo(conexion_con_datos):
    """El filtro por tipo devuelve solo ese tipo, sin distinguir mayúsculas."""
    resultado = listar_emergencias(conexion_con_datos, tipo="INCENDIO")

    assert len(resultado) == 1
    assert resultado[0].tipo == "incendio"


def test_filtrar_por_estado(conexion_con_datos):
    """El filtro por estado devuelve solo las emergencias con ese estado."""
    resultado = listar_emergencias(conexion_con_datos, estado="en proceso")

    assert [e.titulo for e in resultado] == ["Accidente en carretera"]


def test_filtrar_por_prioridad(conexion_con_datos):
    """El filtro por prioridad devuelve solo las de esa prioridad."""
    resultado = listar_emergencias(conexion_con_datos, prioridad="alta")

    assert len(resultado) == 2


def test_filtros_combinados(conexion_con_datos):
    """Varios criterios a la vez deben cumplirse todos."""
    resultado = listar_emergencias(
        conexion_con_datos, texto="chiriquí", prioridad="alta"
    )

    assert [e.titulo for e in resultado] == ["Accidente en carretera"]


def test_filtros_sin_coincidencias(conexion_con_datos):
    """Si nada coincide se devuelve una lista vacía, sin error."""
    resultado = listar_emergencias(
        conexion_con_datos, tipo="incendio", prioridad="alta"
    )

    assert resultado == []


def test_texto_con_caracteres_de_sql_no_rompe_la_consulta(conexion_con_datos):
    """Un intento de inyección SQL se trata como texto normal."""
    resultado = listar_emergencias(
        conexion_con_datos, texto="'; DROP TABLE emergencias;--"
    )

    assert resultado == []
    assert len(listar_emergencias(conexion_con_datos)) == 3
