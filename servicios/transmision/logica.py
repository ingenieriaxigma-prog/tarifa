import logging
from typing import Dict, List, Union
from core.calculadora import cargar_configuracion
from core.utils import redondear, respuesta_estandar

logger = logging.getLogger(__name__)

def calcular_componente_T(lineas: List[Union[Dict, object]]) -> Dict:
    """
    Calcula el componente T (Transmisión) con base en las líneas o tramos transportados.

    Parámetros:
    -----------
    lineas : List[Dict|object]
        Lista con los campos:
        - energia_kWh
        - costo_unitario_kWh

    Retorna:
    --------
    dict : Resultado con el valor promedio del componente T.
    """
    try:
        config = cargar_configuracion()
        componente_cfg = config.get("componente_T", {})
        metodo = componente_cfg.get("metodo", "promedio_simple")

        if not lineas:
            logger.warning("Lista de líneas vacía, retornando 0.0")
            return respuesta_estandar(True, "Sin datos de transmisión", {"T_promedio": 0.0})

        energia_total = sum(
            l["energia_kWh"] if isinstance(l, dict) else l.energia_kWh
            for l in lineas
        )

        costo_total = sum(
            (l["energia_kWh"] * l["costo_unitario_kWh"]) if isinstance(l, dict)
            else (l.energia_kWh * l.costo_unitario_kWh)
            for l in lineas
        )

        if energia_total == 0:
            return respuesta_estandar(True, "Energía total nula", {"T_promedio": 0.0})

        promedio = redondear(costo_total / energia_total, 2)
        logger.info(f"Componente T calculado: {promedio} $/kWh")

        return respuesta_estandar(True, "Cálculo exitoso", {
            "metodo": metodo,
            "energia_total_kWh": energia_total,
            "costo_total": costo_total,
            "T_promedio": promedio
        })

    except Exception as e:
        logger.error(f"Error al calcular componente T: {e}")
        return respuesta_estandar(False, f"Error: {str(e)}", {"T_promedio": 0.0})


if __name__ == "__main__":
    # Prueba rápida manual
    lineas_ejemplo = [
        {"energia_kWh": 4000, "costo_unitario_kWh": 35.0},
        {"energia_kWh": 6000, "costo_unitario_kWh": 36.2}
    ]

    resultado = calcular_componente_T(lineas_ejemplo)
    print(resultado)
