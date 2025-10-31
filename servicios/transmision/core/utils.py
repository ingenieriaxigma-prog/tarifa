import datetime
import math
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ===============================
# 🔹 FUNCIONES DE VALIDACIÓN
# ===============================

def validar_consumo(consumo_kwh: float) -> float:
    """Valida que el consumo sea un número positivo."""
    if consumo_kwh is None or not isinstance(consumo_kwh, (int, float)):
        raise ValueError("El consumo debe ser un número.")
    if consumo_kwh < 0:
        raise ValueError("El consumo no puede ser negativo.")
    return consumo_kwh


# ===============================
# 🔹 FUNCIONES DE CÁLCULO
# ===============================

def redondear(valor: float, decimales: int = 2) -> float:
    """Redondea un valor numérico a la cantidad de decimales especificada."""
    return round(valor, decimales)


def porcentaje(valor: float, porcentaje: float) -> float:
    """Calcula el porcentaje de un valor."""
    return (valor * porcentaje) / 100


def aplicar_incremento(valor: float, incremento_pct: float) -> float:
    """Aplica un incremento porcentual a un valor."""
    return valor + porcentaje(valor, incremento_pct)


def aplicar_descuento(valor: float, descuento_pct: float) -> float:
    """Aplica un descuento porcentual a un valor."""
    return valor - porcentaje(valor, descuento_pct)


# ===============================
# 🔹 UTILIDADES DE TIEMPO
# ===============================

def obtener_fecha_actual() -> str:
    """Devuelve la fecha actual en formato YYYY-MM-DD."""
    return datetime.date.today().isoformat()


def obtener_mes_actual() -> int:
    """Devuelve el número de mes actual (1-12)."""
    return datetime.date.today().month


# ===============================
# 🔹 FORMATO DE RESPUESTA ESTÁNDAR
# ===============================

def respuesta_estandar(
    exito: bool,
    mensaje: str,
    datos: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Genera una respuesta estandarizada para API o CLI.
    """
    return {
        "ok": exito,
        "mensaje": mensaje,
        "datos": datos or {},
        "timestamp": datetime.datetime.now().isoformat()
    }
