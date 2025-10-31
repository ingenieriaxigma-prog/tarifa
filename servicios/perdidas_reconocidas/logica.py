import logging
from typing import Dict, Union
from core.utils import redondear, respuesta_estandar
from core.calculadora import cargar_configuracion

logger = logging.getLogger(__name__)

def calcular_componente_PR(energia_total_kWh: float, costo_promedio_kWh: float, porcentaje_perdidas: float) -> Dict:
    """
    Calcula el componente PR (Pérdidas Reconocidas).

    Parámetros:
    -----------
    energia_total_kWh : float
        Energía entregada al usuario final.
    costo_promedio_kWh : float
        Costo unitario promedio ponderado (de generación, transmisión, distribución).
    porcentaje_perdidas : float
        Porcentaje reconocido por pérdidas (por ejemplo, 10% = 0.10)

    Retorna:
    --------
    dict : Resultado con energía perdida, costo adicional y tarifa PR promedio.
    """
    try:
        config = cargar_configuracion()
        componente_cfg = config.get("componente_PR", {})
        metodo = componente_cfg.get("metodo", "porcentaje_reconocido")

        if energia_total_kWh <= 0:
            return respuesta_estandar(True, "Energía total nula", {"PR_promedio": 0.0})

        energia_perdida_kWh = energia_total_kWh * porcentaje_perdidas
        costo_total_PR = energia_perdida_kWh * costo_promedio_kWh
        PR_promedio = redondear(costo_total_PR / energia_total_kWh, 2)

        logger.info(f"Componente PR calculado: {PR_promedio} $/kWh")

        return respuesta_estandar(True, "Cálculo exitoso", {
            "metodo": metodo,
            "energia_total_kWh": energia_total_kWh,
            "porcentaje_perdidas": porcentaje_perdidas,
            "energia_perdida_kWh": energia_perdida_kWh,
            "costo_promedio_base": costo_promedio_kWh,
            "costo_total_PR": costo_total_PR,
            "PR_promedio": PR_promedio
        })

    except Exception as e:
        logger.error(f"Error al calcular componente PR: {e}")
        return respuesta_estandar(False, f"Error: {str(e)}", {"PR_promedio": 0.0})


if __name__ == "__main__":
    # Prueba manual
    resultado = calcular_componente_PR(
        energia_total_kWh=10000,
        costo_promedio_kWh=130.0,
        porcentaje_perdidas=0.10
    )
    print(resultado)
