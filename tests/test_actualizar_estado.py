import pytest
from app.database import conectar, inicializar_db, actualizar_estado


@pytest.fixture
def db():
    """Fixture que crea una base de datos en memoria para cada prueba."""
    conexion = conectar(":memory:")
    inicializar_db(conexion)
    # Insertar emergencia de prueba en estado 'pendiente'
    conexion.execute(
        """
        INSERT INTO emergencias (titulo, tipo, descripcion, ubicacion, fecha, prioridad, estado)
        VALUES ('Fuga de gas', 'seguridad', 'Fuga en cocina', 'Central', '2026-10-05 10:00', 'alta', 'pendiente')
        """
    )
    conexion.commit()
    yield conexion
    conexion.close()


def test_transicion_valida_pendiente_a_en_proceso(db):
    res = actualizar_estado(db, 1, "en proceso")
    assert res["estado"] == "en proceso"


def test_transicion_valida_en_proceso_a_finalizada(db):
    actualizar_estado(db, 1, "en proceso")
    res = actualizar_estado(db, 1, "finalizada")
    assert res["estado"] == "finalizada"


def test_transicion_invalida_salto_de_estado(db):
    with pytest.raises(ValueError, match="No se puede cambiar"):
        actualizar_estado(db, 1, "finalizada")


def test_actualizar_emergencia_inexistente(db):
    with pytest.raises(ValueError, match="No se encontró ninguna emergencia"):
        actualizar_estado(db, 999, "en proceso")


def test_id_invalido(db):
    with pytest.raises(ValueError, match="El id debe ser un número entero positivo"):
        actualizar_estado(db, -5, "en proceso")