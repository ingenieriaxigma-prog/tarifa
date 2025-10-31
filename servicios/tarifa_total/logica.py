import logging
import asyncio
from typing import Dict
from core.utils import redondear, respuesta_estandar
from clients import obtener_componentes_en_paralelo

logger = logging.getLogger(__name__)

async def calcular_tarifa_total_automatica(consumo_kWh: float) -> Dict:
    """
    Calcula la tarifa total consultando microservicios en paralelo,
    con reintentos automáticos y tolerancia a fallos.
    """
    try:
        logger.info("🚀 Iniciando cálculo automático (modo producción)...")

        componentes = await obtener_componentes_en_paralelo()
        total_tarifa = sum(componentes.values())
        total_costo = redondear(total_tarifa * consumo_kWh, 2)

        logger.info(f"💰 Tarifa total = {total_tarifa} | Costo = {total_costo}")

        return respuesta_estandar(True, "Cálculo exitoso (producción)", {
            "componentes": componentes,
            "tarifa_total_$por_kWh": redondear(total_tarifa, 2),
            "consumo_kWh": consumo_kWh,
            "costo_total_$": total_costo
        })
    except Exception as e:
        logger.exception("Error crítico en cálculo automático:")
        return respuesta_estandar(False, f"Error interno: {str(e)}", {})


def calcular_tarifa_total(componentes: Dict[str, float], consumo_kWh: float) -> Dict:
    """
    Modo manual — versión estable con logs.
    """
    try:
        total_tarifa = sum(componentes.values())
        total_costo = redondear(total_tarifa * consumo_kWh, 2)
        logger.info(f"🧮 Cálculo manual: {componentes} → total {total_tarifa}")

        return respuesta_estandar(True, "Cálculo manual exitoso", {
            "metodo": "suma_directa",
            "componentes": componentes,
            "tarifa_total_$por_kWh": redondear(total_tarifa, 2),
            "consumo_kWh": consumo_kWh,
            "costo_total_$": total_costo
        })
    except Exception as e:
        logger.exception("Error en cálculo manual:")
        return respuesta_estandar(False, f"Error: {str(e)}", {})
