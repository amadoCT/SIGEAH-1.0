"""Pruebas de app/validaciones.py. Se ejecutan con:  pytest -v"""

import pytest

from app import validaciones as v


# --------------------------- validar_texto ---------------------------
def test_texto_valido_se_limpia():
    assert v.validar_texto("  Calle 5, casa 3  ", "dirección") == "Calle 5, casa 3"


@pytest.mark.parametrize("entrada", ["", "   ", None, 123])
def test_texto_invalido(entrada):
    with pytest.raises(ValueError):
        v.validar_texto(entrada, "descripción")


def test_texto_muy_corto():
    with pytest.raises(ValueError):
        v.validar_texto("ab", "descripción", minimo=3)


def test_texto_muy_largo():
    with pytest.raises(ValueError):
        v.validar_texto("a" * 201, "descripción", maximo=200)


# ------------------------ tipo, prioridad, estado ---------------------
def test_tipo_valido_en_mayusculas():
    assert v.validar_tipo_emergencia("  INCENDIO ") == "incendio"


def test_tipo_invalido():
    with pytest.raises(ValueError):
        v.validar_tipo_emergencia("terremoto")


def test_prioridad_valida():
    assert v.validar_prioridad("Alta") == "alta"


def test_prioridad_invalida():
    with pytest.raises(ValueError):
        v.validar_prioridad("urgentisima")


def test_estado_valido():
    assert v.validar_estado("En Proceso") == "en proceso"


def test_estado_invalido():
    with pytest.raises(ValueError):
        v.validar_estado("cancelada")


# --------------------------- fecha y hora -----------------------------
def test_fecha_valida():
    assert v.validar_fecha_hora("2020-01-15 08:30") == "2020-01-15 08:30"


@pytest.mark.parametrize("entrada", ["15/01/2020 08:30", "2020-13-45 99:99", "hoy", ""])
def test_fecha_formato_incorrecto(entrada):
    with pytest.raises(ValueError):
        v.validar_fecha_hora(entrada)


def test_fecha_futura_no_permitida():
    with pytest.raises(ValueError):
        v.validar_fecha_hora("2999-01-01 10:00")


# ------------------------------- id -----------------------------------
@pytest.mark.parametrize("entrada, esperado", [(5, 5), ("7", 7), (" 12 ", 12)])
def test_id_valido(entrada, esperado):
    assert v.validar_id(entrada) == esperado


@pytest.mark.parametrize("entrada", [0, -3, "abc", "", None, "2.5", True])
def test_id_invalido(entrada):
    with pytest.raises(ValueError):
        v.validar_id(entrada)


# ------------------------ transiciones de estado ----------------------
@pytest.mark.parametrize(
    "actual, nuevo",
    [("pendiente", "en proceso"), ("en proceso", "finalizada")],
)
def test_transicion_permitida(actual, nuevo):
    assert v.validar_transicion_estado(actual, nuevo) == nuevo


@pytest.mark.parametrize(
    "actual, nuevo",
    [
        ("pendiente", "finalizada"),  # se salta un paso
        ("finalizada", "pendiente"),  # ya está cerrada
        ("en proceso", "pendiente"),  # no se retrocede
        ("pendiente", "pendiente"),  # mismo estado
    ],
)
def test_transicion_no_permitida(actual, nuevo):
    with pytest.raises(ValueError):
        v.validar_transicion_estado(actual, nuevo)