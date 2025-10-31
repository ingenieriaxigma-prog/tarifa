import logging
from typing import List, Dict, Union
from core.calculadora import cargar_configuracion
from core.utils import redondear, respuesta_estandar

logger = logging.getLogger(__name__)


def calcular_componente_G(compras: List[Union[Dict, object]]) -> Dict:
    """
    Calcula el componente G (Generación) con base en las compras de energía.

    Parámetros:
    -----------
    compras : List[Dict|object]
        Lista de compras con los campos:
        - energia_kWh
        - precio_kWh

    Retorna:
    --------
    dict : Resultado con el valor promedio del componente G y detalles intermedios.
    """

    try:
        config = cargar_configuracion()
        componente_cfg = config.get("componente_G", {})
        metodo = componente_cfg.get("metodo", "promedio_ponderado")

        if not compras:
            logger.warning("Lista de compras vacía, retornando 0.0")
            return respuesta_estandar(True, "Sin datos de compras", {"G_promedio": 0.0})

        if metodo == "promedio_ponderado":
            energia_total = sum(
                c["energia_kWh"] if isinstance(c, dict) else c.energia_kWh
                for c in compras
            )
            costo_total = sum(
                (c["energia_kWh"] * c["precio_kWh"]) if isinstance(c, dict)
                else (c.energia_kWh * c.precio_kWh)
                for c in compras
            )

            if energia_total == 0:
                logger.warning("Energía total = 0, retornando 0.0")
                return respuesta_estandar(True, "Energía total nula", {"G_promedio": 0.0})

            promedio = redondear(costo_total / energia_total, 2)
            logger.info(f"Componente G calculado: {promedio} $/kWh")

            return respuesta_estandar(True, "Cálculo exitoso", {
                "metodo": metodo,
                "energia_total_kWh": energia_total,
                "costo_total": costo_total,
                "G_promedio": promedio
            })

        else:
            raise ValueError(f"Método de cálculo no soportado: {metodo}")

    except Exception as e:
        logger.error(f"Error al calcular componente G: {e}")
        return respuesta_estandar(False, f"Error: {str(e)}", {"G_promedio": 0.0})


if __name__ == "__main__":
    # Prueba rápida manual
    compras_ejemplo = [
        {"energia_kWh": 5000, "precio_kWh": 320.5},
        {"energia_kWh": 3000, "precio_kWh": 315.2},
        {"energia_kWh": 2000, "precio_kWh": 325.0}
    ]

    resultado = calcular_componente_G(compras_ejemplo)
    print(resultado)
