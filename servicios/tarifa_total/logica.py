import logging
import asyncio
import httpx
from typing import Dict
from core.utils import redondear, respuesta_estandar
from clients import obtener_componentes_en_paralelo

logger = logging.getLogger(__name__)

# 🌐 URL interna del microservicio de generación (Docker network)
URL_GENERACION = "http://generacion:8001/generacion/precio-xm"


# ============================================================
# 🔹 Función auxiliar: obtener G (generación) desde XM vía microservicio
# ============================================================
async def obtener_valor_generacion_xm() -> float:
    """
    Consulta el valor de generación (G) desde el microservicio de generación.
    Si XM falla o responde mal, devuelve None para permitir fallback.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"🌐 Consultando valor G desde {URL_GENERACION} ...")
            resp = await client.get(URL_GENERACION)
            resp.raise_for_status()
            data = resp.json()
            valor = data.get("valor_kWh")

            if valor is None:
                raise ValueError("El campo 'valor_kWh' no está presente en la respuesta")

            logger.info(f"✅ Valor G obtenido desde XM: {valor}")
            return float(valor)
    except Exception as e:
        logger.warning(f"⚠️ No se pudo obtener valor G desde XM: {e}")
        return None


# ============================================================
# 🔹 Cálculo automático (usa XM en vivo para G)
# ============================================================
async def calcular_tarifa_total_automatica(consumo_kWh: float) -> Dict:
    """
    Calcula la tarifa total consultando microservicios en paralelo,
    obteniendo G desde XM (si está disponible).
    """
    try:
        logger.info("🚀 Iniciando cálculo automático (modo producción)...")

        # 1️⃣ Consultar todos los componentes en paralelo
        componentes = await obtener_componentes_en_paralelo()

        # 2️⃣ Reemplazar G con el valor real de XM si existe
        valor_g_xm = await obtener_valor_generacion_xm()
        if valor_g_xm is not None:
            logger.info(f"🔄 Reemplazando 'generacion' ({componentes.get('generacion')}) por {valor_g_xm}")
            componentes["generacion"] = valor_g_xm
        else:
            logger.info("🟡 Se mantiene valor de respaldo en 'generacion' (XM no disponible).")

        # 3️⃣ Calcular totales
        total_tarifa = sum(componentes.values())
        total_costo = redondear(total_tarifa * consumo_kWh, 2)

        logger.info(f"💰 Tarifa total = {total_tarifa} | Costo total = {total_costo}")

        return respuesta_estandar(True, "Cálculo automático con G desde XM", {
            "componentes": componentes,
            "tarifa_total_$por_kWh": redondear(total_tarifa, 2),
            "consumo_kWh": consumo_kWh,
            "costo_total_$": total_costo,
            "fuente_G": "XM" if valor_g_xm is not None else "Respaldo local"
        })

    except Exception as e:
        logger.exception("💥 Error crítico en cálculo automático:")
        return respuesta_estandar(False, f"Error interno: {str(e)}", {})


# ============================================================
# 🔹 Cálculo manual (sincrónico)
# ============================================================
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
