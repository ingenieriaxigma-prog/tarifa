import logging
import asyncio
from typing import Dict
from core.utils import redondear, respuesta_estandar
from clients import obtener_componentes_en_paralelo
import httpx

logger = logging.getLogger(__name__)

# ==========================================================
# 🔹 CÁLCULO AUTOMÁTICO (PRODUCCIÓN)
# ==========================================================
async def calcular_tarifa_total_automatica(consumo_kWh: float) -> Dict:
    """
    Calcula la tarifa total consultando microservicios en paralelo.
    Si 'G' proviene de XM, se indica explícitamente.
    Si falla, se usa el valor de respaldo del config.json.
    """
    try:
        logger.info("🚀 Iniciando cálculo automático (modo producción)...")

        componentes = await obtener_componentes_en_paralelo()
        valor_G_final = None
        fuente_G = None
        comentario_G = None
        mensaje = None

        # ==========================================================
        # 🌐 Intentar obtener G desde el microservicio de generación (API XM)
        # ==========================================================
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                logger.info("🌐 Consultando valor G desde http://generacion:8001/generacion/precio-xm ...")
                r = await client.get("http://generacion:8001/generacion/precio-xm")

                if r.status_code == 200:
                    data = r.json()
                    valor_G_api = float(data.get("valor_kWh", 0))
                    fuente_G_api = data.get("fuente", "XM")

                    # Validar si el valor obtenido es real (>0)
                    if valor_G_api > 0:
                        valor_G_final = valor_G_api
                        fuente_G = fuente_G_api
                        componentes["G"] = valor_G_final
                        logger.info(f"✅ Valor G obtenido correctamente desde {fuente_G}: {valor_G_final}")
                    else:
                        logger.warning("⚠️ API XM respondió 200 pero sin datos válidos.")
        except Exception as e:
            logger.warning(f"⚠️ Error al consultar G desde XM: {e}")

        # ==========================================================
        # 🔁 Si no se obtuvo valor válido desde XM → usar respaldo local
        # ==========================================================
        if valor_G_final is None:
            valor_G_final = componentes.get("G", 0)
            fuente_G = "Respaldo local (config.json)"
            logger.info(f"🔁 API XM no disponible, usando valor de respaldo: {valor_G_final}")

        # ==========================================================
        # 💬 Ajuste de mensajes según fuente de G
        # ==========================================================
        if str(fuente_G).lower().startswith("xm"):
            mensaje = "✅ Cálculo automático completado con G obtenido desde API XM"
            comentario_G = (
                f"✅ G obtenido correctamente desde la fuente '{fuente_G}' "
                f"con valor {valor_G_final} $/kWh"
            )
        else:
            mensaje = "⚠️ Cálculo automático completado con G desde respaldo local (config.json)"
            comentario_G = (
                f"⚠️ API XM no disponible o sin datos válidos. "
                f"Se utilizó el valor de respaldo {valor_G_final} $/kWh desde config.json"
            )

        # ==========================================================
        # 💰 Cálculo de tarifa total
        # ==========================================================
        total_tarifa = sum(componentes.values())
        total_costo = redondear(total_tarifa * consumo_kWh, 2)
        logger.info(f"💰 Tarifa total = {total_tarifa} | Costo = {total_costo}")

        # ==========================================================
        # 🧾 Estructurar respuesta final
        # ==========================================================
        componentes_detalle = dict(componentes)
        componentes_detalle["G_valor"] = valor_G_final
        componentes_detalle["G_fuente"] = fuente_G
        componentes_detalle["G_comentario"] = comentario_G

        # ==========================================================
        # ✅ Respuesta estándar
        # ==========================================================
        return respuesta_estandar(True, mensaje, {
            "componentes": componentes_detalle,
            "tarifa_total_$por_kWh": redondear(total_tarifa, 2),
            "consumo_kWh": consumo_kWh,
            "costo_total_$": total_costo,
            "fuente_G": fuente_G
        })

    except Exception as e:
        logger.exception("Error crítico en cálculo automático:")
        return respuesta_estandar(False, f"Error interno: {str(e)}", {})


# ==========================================================
# 🔹 CÁLCULO MANUAL (DEBUG Y PRUEBAS)
# ==========================================================
def calcular_tarifa_total(componentes: Dict[str, float], consumo_kWh: float) -> Dict:
    """
    Cálculo manual de tarifa total — versión estable con logs.
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
