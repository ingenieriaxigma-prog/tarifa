import logging
from typing import Dict, List, Union
from core.calculadora import cargar_configuracion
from core.utils import redondear, respuesta_estandar

logger = logging.getLogger(__name__)

def calcular_componente_R(eventos: List[Union[Dict, object]]) -> Dict:
    """
    Calcula el componente R (Restricciones) con base en los eventos o ajustes del sistema.

    Parámetros:
    -----------
    eventos : List[Dict|object]
        Lista con los campos:
        - energia_afectada_kWh
        - costo_unitario_kWh

    Retorna:
    --------
    dict : Resultado con el valor promedio del componente R.
    """
    try:
        config = cargar_configuracion()
        componente_cfg = config.get("componente_R", {})
        metodo = componente_cfg.get("metodo", "promedio_simple")

        if not eventos:
            logger.warning("Lista de eventos vacía, retornando 0.0")
            return respuesta_estandar(True, "Sin eventos de restricciones", {"R_promedio": 0.0})

        energia_total = sum(
            e["energia_afectada_kWh"] if isinstance(e, dict) else e.energia_afectada_kWh
            for e in eventos
        )

        costo_total = sum(
            (e["energia_afectada_kWh"] * e["costo_unitario_kWh"]) if isinstance(e, dict)
            else (e.energia_afectada_kWh * e.costo_unitario_kWh)
            for e in eventos
        )

        if energia_total == 0:
            return respuesta_estandar(True, "Energía total nula", {"R_promedio": 0.0})

        promedio = redondear(costo_total / energia_total, 2)
        logger.info(f"Componente R calculado: {promedio} $/kWh")

        return respuesta_estandar(True, "Cálculo exitoso", {
            "metodo": metodo,
            "energia_total_afectada_kWh": energia_total,
            "costo_total": costo_total,
            "R_promedio": promedio
        })

    except Exception as e:
        logger.error(f"Error al calcular componente R: {e}")
        return respuesta_estandar(False, f"Error: {str(e)}", {"R_promedio": 0.0})


if __name__ == "__main__":
    # Prueba rápida manual
    eventos_ejemplo = [
        {"energia_afectada_kWh": 3000, "costo_unitario_kWh": 5.2},
        {"energia_afectada_kWh": 2000, "costo_unitario_kWh": 6.0},
        {"energia_afectada_kWh": 5000, "costo_unitario_kWh": 4.8}
    ]

    resultado = calcular_componente_R(eventos_ejemplo)
    print(resultado)
