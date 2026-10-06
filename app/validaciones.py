"""Módulo de validaciones de SIGEAH.

Cada función recibe un dato, lo valida y devuelve el valor limpio
(sin espacios sobrantes y, cuando aplica, en minúsculas).
Si el dato no es válido, lanza ValueError con un mensaje claro
que el menú de consola puede mostrar directamente al usuario.
"""

from datetime import datetime

# ---------------------------------------------------------------------------
# Catálogos permitidos (si el equipo decide otros valores, se cambian aquí)
# ---------------------------------------------------------------------------
TIPOS_EMERGENCIA = ("incendio", "accidente", "medica", "inundacion", "seguridad", "otro")
PRIORIDADES = ("baja", "media", "alta")
ESTADOS = ("pendiente", "en proceso", "finalizada")

# Qué cambios de estado están permitidos: estado actual -> estados siguientes
TRANSICIONES = {
    "pendiente": ("en proceso",),
    "en proceso": ("finalizada",),
    "finalizada": (),
}

FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M"  # Ejemplo: 2026-10-05 14:30


def validar_texto(valor, campo, minimo=3, maximo=200):
    """Valida que un texto no esté vacío y tenga una longitud razonable.

    Args:
        valor: texto ingresado por el usuario.
        campo: nombre del campo (se usa en el mensaje de error).
        minimo: cantidad mínima de caracteres.
        maximo: cantidad máxima de caracteres.

    Returns:
        El texto sin espacios al inicio ni al final.

    Raises:
        ValueError: si no es texto, está vacío o su longitud no es válida.
    """
    if not isinstance(valor, str):
        raise ValueError(f"El campo '{campo}' debe ser texto.")
    texto = valor.strip()
    if not texto:
        raise ValueError(f"El campo '{campo}' no puede estar vacío.")
    if len(texto) < minimo:
        raise ValueError(f"El campo '{campo}' debe tener al menos {minimo} caracteres.")
    if len(texto) > maximo:
        raise ValueError(f"El campo '{campo}' no puede superar {maximo} caracteres.")
    return texto


def _validar_opcion(valor, campo, opciones):
    """Función interna: comprueba que el valor esté dentro de una lista permitida."""
    texto = validar_texto(valor, campo, minimo=1, maximo=50).lower()
    if texto not in opciones:
        permitidas = ", ".join(opciones)
        raise ValueError(f"{campo.capitalize()} no válido. Opciones: {permitidas}.")
    return texto


def validar_tipo_emergencia(valor):
    """Valida que el tipo de emergencia esté en TIPOS_EMERGENCIA."""
    return _validar_opcion(valor, "tipo de emergencia", TIPOS_EMERGENCIA)


def validar_prioridad(valor):
    """Valida que la prioridad sea baja, media o alta."""
    return _validar_opcion(valor, "prioridad", PRIORIDADES)


def validar_estado(valor):
    """Valida que el estado esté en ESTADOS."""
    return _validar_opcion(valor, "estado", ESTADOS)


def validar_fecha_hora(valor):
    """Valida que la fecha y hora tengan el formato AAAA-MM-DD HH:MM y no sean futuras.

    Returns:
        El texto de la fecha ya validado.

    Raises:
        ValueError: si el formato es incorrecto o la fecha está en el futuro.
    """
    texto = validar_texto(valor, "fecha y hora", minimo=1, maximo=30)
    try:
        fecha = datetime.strptime(texto, FORMATO_FECHA_HORA)
    except ValueError:
        raise ValueError("Fecha y hora inválidas. Use el formato AAAA-MM-DD HH:MM.") from None
    if fecha > datetime.now():
        raise ValueError("La fecha y hora no pueden estar en el futuro.")
    return texto


def validar_id(valor):
    """Valida que el id sea un número entero positivo.

    Acepta int o texto numérico (por ejemplo "5", como llega del input()).

    Returns:
        El id como int.
    """
    if isinstance(valor, bool):
        raise ValueError("El id debe ser un número entero positivo.")
    try:
        numero = int(str(valor).strip())
    except ValueError:
        raise ValueError("El id debe ser un número entero positivo.") from None
    if numero <= 0:
        raise ValueError("El id debe ser un número entero positivo.")
    return numero


def validar_transicion_estado(estado_actual, estado_nuevo):
    """Valida que el cambio de estado esté permitido.

    Flujo permitido: pendiente -> en proceso -> finalizada.

    Returns:
        El nuevo estado ya validado.

    Raises:
        ValueError: si algún estado no existe o el cambio no está permitido.
    """
    actual = validar_estado(estado_actual)
    nuevo = validar_estado(estado_nuevo)
    if nuevo not in TRANSICIONES[actual]:
        raise ValueError(f"No se puede cambiar de '{actual}' a '{nuevo}'.")
    return nuevo