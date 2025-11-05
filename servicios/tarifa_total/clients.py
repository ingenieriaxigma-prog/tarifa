import httpx
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Dict, Any, List

# 👇 importa el loader centralizado del core (compartido por todos)
from core.calculadora import cargar_configuracion

logger = logging.getLogger(__name__)

# =====================================================
# 🔗 URLs base de los microservicios (sin cambios)
# =====================================================
URLS: Dict[str, str] = {
    "G": "http://generacion:8001/generacion/calcular",
    "T": "http://transmision:8002/transmision/calcular",
    "D": "http://distribucion:8003/distribucion/calcular",
    "PR": "http://perdidas_reconocidas:8004/perdidas/calcular",
    "R": "http://restricciones:8005/restricciones/calcular",
    "C": "http://comercializacion:8006/comercializacion/calcular",
}

# =====================================================
# 🧭 Campos esperados en las respuestas (sin cambios)
# =====================================================
CAMPOS: Dict[str, str] = {
    "G": "G_promedio",
    "T": "T_promedio",
    "D": "D_promedio",
    "PR": "PR_promedio",
    "R": "R_promedio",
    "C": "C_promedio",
}

# =====================================================
# 🧩 Helpers para construir payloads desde el JSON
#     con fallbacks a los ejemplos anteriores
# =====================================================

def _cfg() -> Dict[str, Any]:
    """
    Devuelve el dict de configuración normativa.
    Carga desde /app/config/normativa_config.json (imagen base)
    o la ruta indicada por NORMATIVA_CONFIG_PATH.
    """
    return cargar_configuracion() or {}

def _payload_generacion(consumo_kWh: float) -> List[Dict[str, float]]:
    """
    Espera: lista de compras con energia_kWh y precio_kWh
    JSON: componente_G.compras = [{ energia_kWh, precio_kWh }, ...]
    """
    cfg = _cfg().get("componente_G", {})
    compras = cfg.get("compras")
    if isinstance(compras, list) and compras:
        return compras
    # fallback: usa 'tarifas' si existiera, o ejemplo fijo
    tarifas = (_cfg().get("tarifas", {}).get("generacion") or {})
    v = tarifas.get("valor_kWh", 320.5)
    return [
        {"energia_kWh": 5000, "precio_kWh": v},
        {"energia_kWh": 3000, "precio_kWh": v},
        {"energia_kWh": 2000, "precio_kWh": v},
    ]

def _payload_transmision(consumo_kWh: float) -> List[Dict[str, float]]:
    """
    Espera: lista de líneas con energia_kWh y costo_unitario_kWh
    JSON: componente_T.lineas = [{ energia_kWh, costo_unitario_kWh }, ...]
    """
    cfg = _cfg().get("componente_T", {})
    lineas = cfg.get("lineas")
    if isinstance(lineas, list) and lineas:
        return lineas
    tarifas = (_cfg().get("tarifas", {}).get("transmision") or {})
    v = tarifas.get("valor_kWh", 35.0)
    return [
        {"energia_kWh": 4000, "costo_unitario_kWh": v},
        {"energia_kWh": 6000, "costo_unitario_kWh": v},
    ]

def _payload_distribucion(consumo_kWh: float) -> List[Dict[str, float]]:
    """
    Espera: lista de redes con energia_kWh y costo_unitario_kWh
    JSON: componente_D.redes = [{ energia_kWh, costo_unitario_kWh }, ...]
    """
    cfg = _cfg().get("componente_D", {})
    redes = cfg.get("redes")
    if isinstance(redes, list) and redes:
        return redes
    tarifas = (_cfg().get("tarifas", {}).get("distribucion") or {})
    v = tarifas.get("valor_kWh", 40.0)
    return [
        {"energia_kWh": 5000, "costo_unitario_kWh": v},
        {"energia_kWh": 3000, "costo_unitario_kWh": v},
        {"energia_kWh": 2000, "costo_unitario_kWh": v},
    ]

def _payload_perdidas(consumo_kWh: float) -> Dict[str, float]:
    """
    Espera: { energia_total_kWh, costo_promedio_kWh, porcentaje_perdidas }
    JSON: componente_PR.{ costo_promedio_kWh, porcentaje_perdidas }
    - energia_total_kWh la hacemos depender del consumo de entrada.
    """
    cfg = _cfg().get("componente_PR", {})
    costo_promedio = cfg.get("costo_promedio_kWh")
    porcentaje = cfg.get("porcentaje_perdidas")
    if costo_promedio is not None and porcentaje is not None:
        return {
            "energia_total_kWh": float(consumo_kWh),
            "costo_promedio_kWh": float(costo_promedio),
            "porcentaje_perdidas": float(porcentaje),
        }
    # fallback: si no hay config, usa ejemplo estable
    tarifas = (_cfg().get("tarifas", {}).get("perdidas_reconocidas") or {})
    v = tarifas.get("valor_kWh", 130.0)
    return {
        "energia_total_kWh": float(consumo_kWh),
        "costo_promedio_kWh": float(v),
        "porcentaje_perdidas": 0.10,  # 10% por defecto
    }

def _payload_restricciones(consumo_kWh: float) -> List[Dict[str, float]]:
    """
    Espera: lista de eventos con energia_afectada_kWh y costo_unitario_kWh
    JSON: componente_R.eventos = [{ energia_afectada_kWh, costo_unitario_kWh }, ...]
    """
    cfg = _cfg().get("componente_R", {})
    eventos = cfg.get("eventos")
    if isinstance(eventos, list) and eventos:
        return eventos
    tarifas = (_cfg().get("tarifas", {}).get("restricciones") or {})
    v = tarifas.get("valor_kWh", 5.2)
    return [
        {"energia_afectada_kWh": 3000, "costo_unitario_kWh": v},
        {"energia_afectada_kWh": 2000, "costo_unitario_kWh": v},
        {"energia_afectada_kWh": 5000, "costo_unitario_kWh": v},
    ]

def _payload_comercializacion(consumo_kWh: float) -> Dict[str, float]:
    """
    Espera: { consumo_kWh, valor_unitario_kWh }
    JSON: componente_C.valor_unitario_kWh
    """
    cfg = _cfg().get("componente_C", {})
    v = cfg.get("valor_unitario_kWh")
    if v is not None:
        return {"consumo_kWh": float(consumo_kWh), "valor_unitario_kWh": float(v)}
    # fallback a 'tarifas' o 0.0 si no hay nada definido
    tarifas = (_cfg().get("tarifas", {}).get("comercializacion") or {})
    vt = tarifas.get("valor_kWh", 0.0)
    return {"consumo_kWh": float(consumo_kWh), "valor_unitario_kWh": float(vt)}

# Mapa de builders para cada componente
_BUILDERS = {
    "G": _payload_generacion,
    "T": _payload_transmision,
    "D": _payload_distribucion,
    "PR": _payload_perdidas,
    "R": _payload_restricciones,
    "C": _payload_comercializacion,
}

# =====================================================
# 🔁 Consulta con reintentos y logs
# =====================================================
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def consultar_servicio(nombre: str, consumo_kWh: float) -> float:
    """
    Consulta un microservicio con payload construido desde el JSON.
    Si falta info en JSON, cae a fallbacks estables.
    """
    try:
        payload = _BUILDERS[nombre](consumo_kWh)
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.post(URLS[nombre], json=payload)
            resp.raise_for_status()
            data = resp.json()
            campo = CAMPOS[nombre]
            valor = data.get("datos", {}).get(campo, 0)
            return float(valor)
    except Exception as e:
        logger.warning(f"⚠️  Error consultando {nombre}: {e}")
        return 0.0

# =====================================================
# ⚡ Obtener todos los componentes en paralelo
# =====================================================
async def obtener_componentes_en_paralelo(consumo_kWh: float = 1000.0) -> Dict[str, float]:
    """
    Consulta todos los servicios simultáneamente y devuelve un dict
    con los promedios G, T, D, PR, R, C.
    - consumo_kWh se usa para construir los payloads de PR y C (y
      puede impactar otros si así lo modelas en el JSON).
    """
    tareas = [consultar_servicio(nombre, consumo_kWh) for nombre in URLS.keys()]
    resultados = await asyncio.gather(*tareas)
    return dict(zip(URLS.keys(), resultados))
