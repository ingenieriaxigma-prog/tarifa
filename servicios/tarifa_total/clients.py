import httpx
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

# 🔗 URLs base de los microservicios
URLS = {
    "G": "http://generacion:8001/generacion/calcular",
    "T": "http://transmision:8002/transmision/calcular",
    "D": "http://distribucion:8003/distribucion/calcular",
    "PR": "http://perdidas_reconocidas:8004/perdidas/calcular",
    "R": "http://restricciones:8005/restricciones/calcular",
    "C": "http://comercializacion:8006/comercializacion/calcular"
}

# 📦 Datos base para pruebas o simulaciones
PAYLOADS = {
    "G": [
        {"energia_kWh": 5000, "precio_kWh": 320.5},
        {"energia_kWh": 3000, "precio_kWh": 315.2},
        {"energia_kWh": 2000, "precio_kWh": 325.0}
    ],
    "T": [
        {"energia_kWh": 4000, "costo_unitario_kWh": 35.0},
        {"energia_kWh": 6000, "costo_unitario_kWh": 36.2}
    ],
    "D": [
        {"energia_kWh": 5000, "costo_unitario_kWh": 40.0},
        {"energia_kWh": 3000, "costo_unitario_kWh": 41.5},
        {"energia_kWh": 2000, "costo_unitario_kWh": 39.0}
    ],
    "PR": {
        "energia_total_kWh": 10000,
        "costo_promedio_kWh": 130.0,
        "porcentaje_perdidas": 0.10
    },
    "R": [
        {"energia_afectada_kWh": 3000, "costo_unitario_kWh": 5.2},
        {"energia_afectada_kWh": 2000, "costo_unitario_kWh": 6.0},
        {"energia_afectada_kWh": 5000, "costo_unitario_kWh": 4.8}
    ],
    "C": {"consumo_kWh": 150}
}

# 🧭 Campos esperados en la respuesta
CAMPOS = {
    "G": "G_promedio",
    "T": "T_promedio",
    "D": "D_promedio",
    "PR": "PR_promedio",
    "R": "R_promedio",
    "C": "C_promedio"
}

# 🔁 Decorador de reintentos automáticos
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def consultar_servicio(nombre: str) -> float:
    """Consulta un microservicio con reintentos y logs visuales."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(URLS[nombre], json=PAYLOADS[nombre])
            response.raise_for_status()
            json_data = response.json()
            data = json_data.get("datos", json_data)
            campo = CAMPOS[nombre]
            valor = data.get(campo, 0.0)

            logger.info(f"✅ [{nombre}] OK → {campo} = {valor}")
            return valor

    except httpx.RequestError as e:
        logger.warning(f"⚠️ [{nombre}] Error de conexión: {e}")
        return 0.0
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ [{nombre}] Error HTTP {e.response.status_code}")
        return 0.0
    except Exception as e:
        logger.exception(f"💥 [{nombre}] Error inesperado: {e}")
        return 0.0


# 🧩 Llama todos los microservicios en paralelo
async def obtener_componentes_en_paralelo() -> dict:
    nombres = ["G", "T", "D", "PR", "R", "C"]
    resultados = await asyncio.gather(*(consultar_servicio(n) for n in nombres))
    componentes = dict(zip(nombres, resultados))

    for k, v in componentes.items():
        estado = "OK" if v > 0 else "FALLÓ"
        simbolo = "🟢" if v > 0 else "🔴"
        logger.info(f"{simbolo} {k}: {v} ({estado})")

    return componentes
