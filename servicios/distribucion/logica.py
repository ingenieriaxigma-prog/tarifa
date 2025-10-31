import logging
from typing import Dict, List, Union
from core.calculadora import cargar_configuracion
from core.utils import redondear, respuesta_estandar

logger = logging.getLogger(__name__)

def calcular_componente_D(redes: List[Union[Dict, object]]) -> Dict:
    """
    Calcula el componente D (Distribución) con base en los tramos de red o centros de transformación.

    Parámetros:
    -----------
    redes : List[Dict|object]
        Lista de redes con los campos:
        - energia_kWh
        - costo_unitario_kWh

    Retorna:
    --------
    dict : Resultado con el valor promedio del componente D.
    """
    try:
        config = cargar_configuracion()
        componente_cfg = config.get("componente_D", {})
        metodo = componente_cfg.get("metodo", "promedio_simple")

        if not redes:
            logger.warning("Lista de redes vacía, retornando 0.0")
            return respuesta_estandar(True, "Sin datos de distribución", {"D_promedio": 0.0})

        energia_total = sum(
            r["energia_kWh"] if isinstance(r, dict) else r.energia_kWh
            for r in redes
        )

        costo_total = sum(
            (r["energia_kWh"] * r["costo_unitario_kWh"]) if isinstance(r, dict)
            else (r.energia_kWh * r.costo_unitario_kWh)
            for r in redes
        )

        if energia_total == 0:
            return respuesta_estandar(True, "Energía total nula", {"D_promedio": 0.0})

        promedio = redondear(costo_total / energia_total, 2)
        logger.info(f"Componente D calculado: {promedio} $/kWh")

        return respuesta_estandar(True, "Cálculo exitoso", {
            "metodo": metodo,
            "energia_total_kWh": energia_total,
            "costo_total": costo_total,
            "D_promedio": promedio
        })

    except Exception as e:
        logger.error(f"Error al calcular componente D: {e}")
        return respuesta_estandar(False, f"Error: {str(e)}", {"D_promedio": 0.0})


if __name__ == "__main__":
    # Prueba manual
    redes_ejemplo = [
        {"energia_kWh": 5000, "costo_unitario_kWh": 40.0},
        {"energia_kWh": 3000, "costo_unitario_kWh": 41.5},
        {"energia_kWh": 2000, "costo_unitario_kWh": 39.0}
    ]

    resultado = calcular_componente_D(redes_ejemplo)
    print(resultado)
