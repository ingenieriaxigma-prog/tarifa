import datetime
import math
import logging
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)
# 🔹 FUNCIONES DE VALIDACIÓN


def validar_consumo(consumo_kwh: float) -> float:
    """Valida que el consumo sea un número positivo."""
    if consumo_kwh is None or not isinstance(consumo_kwh, (int, float)):
        raise ValueError("El consumo debe ser un número.")
    if consumo_kwh < 0:
        ...

# 🔹 REDONDEOS Y RESPUESTA ESTÁNDAR
def redondear(valor: float, decimales: int = 4) -> float:
    ...

def respuesta_estandar(exito: bool, mensaje: str, datos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "ok": exito,
        "mensaje": mensaje,
        "datos": datos or {},
        "timestamp": datetime.datetime.now().isoformat()
    }
def redondear(valor: Optional[float], decimales: int = 4) -> float:
    if valor is None:
        return 0.0
    try:
        return round(float(valor), decimales)
    except Exception:
        return 0.0