import logging
import json
from typing import List, Dict, Union
from core.calculadora import cargar_configuracion
from core.utils import redondear, respuesta_estandar
import asyncio
from core.xm_api import obtener_precio_bolsa_xm  # ✅ Nombre correcto de la función # 🔹 Nueva función real XM
logger = logging.getLogger(__name__)


async def calcular_componente_G(compras: List[Union[Dict, object]]) -> Dict:
    """
    Calcula el componente G (Generación) con base en datos reales de XM o respaldo local.

    1️⃣ Intenta obtener el Precio Bolsa Nacional Diario (PBND) desde la API de XM.
    2️⃣ Si falla la conexión, usa el valor de respaldo en normativa_config.json.
    3️⃣ Realiza el cálculo promedio ponderado si existen compras específicas.
    """

    try:
        # ================================================================
        # 🔹 Paso 1: Intentar obtener valor real desde XM
        # ================================================================
        try:
            valor_xm = await obtener_precio_bolsa_xm()
            fuente = "XM"
            logger.info(f"✅ Precio Bolsa Nacional obtenido desde XM: {valor_xm} $/kWh")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo obtener valor real de XM ({e}). Usando respaldo local.")
            config = cargar_configuracion()
            componente_cfg = config.get("componente_G", {})
            valor_xm = componente_cfg.get("valor_referencia", 320.5)
            fuente = "normativa_config.json"

        # ================================================================
        # 🔹 Paso 2: Si no hay compras, usa directamente el valor de XM
        # ================================================================
        if not compras:
            logger.info("No se proporcionaron compras, usando valor base de XM o JSON")
            return respuesta_estandar(True, f"Valor obtenido de {fuente}", {
                "G_promedio": redondear(valor_xm, 2),
                "fuente": fuente
            })

        # ================================================================
        # 🔹 Paso 3: Calcular promedio ponderado si hay compras
        # ================================================================
        energia_total = sum(
            c["energia_kWh"] if isinstance(c, dict) else c.energia_kWh
            for c in compras
        )
        costo_total = sum(
            (c["energia_kWh"] * c.get("precio_kWh", valor_xm)) if isinstance(c, dict)
            else (c.energia_kWh * getattr(c, "precio_kWh", valor_xm))
            for c in compras
        )

        if energia_total == 0:
            return respuesta_estandar(True, "Energía total nula", {"G_promedio": 0.0})

        promedio = redondear(costo_total / energia_total, 2)
        logger.info(f"Componente G calculado: {promedio} $/kWh | Fuente: {fuente}")

        return respuesta_estandar(True, "Cálculo exitoso", {
            "metodo": "promedio_ponderado",
            "energia_total_kWh": energia_total,
            "costo_total": costo_total,
            "G_promedio": promedio,
            "fuente": fuente
        })

    except Exception as e:
        logger.error(f"❌ Error al calcular componente G: {e}")
        return respuesta_estandar(False, f"Error: {str(e)}", {"G_promedio": 0.0})


# ================================================================
# 🔹 Ejecución manual de prueba
# ================================================================
if __name__ == "__main__":
    compras_ejemplo = [
        {"energia_kWh": 5000, "precio_kWh": 320.5},
        {"energia_kWh": 3000, "precio_kWh": 315.2},
        {"energia_kWh": 2000, "precio_kWh": 325.0}
    ]

    async def test():
        resultado = await calcular_componente_G(compras_ejemplo)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    asyncio.run(test())
