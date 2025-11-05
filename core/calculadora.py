import json
import os
import logging
from functools import lru_cache


@lru_cache(maxsize=1)
def cargar_configuracion(path: str | None = None) -> dict:
    """
    Lee el archivo de configuración normativa (normativa_config.json).
    Prioriza la variable de entorno NORMATIVA_CONFIG_PATH,
    y si no existe, usa /app/config/normativa_config.json.
    """
    ruta = path or os.environ.get("NORMATIVA_CONFIG_PATH", "/app/config/normativa_config.json")

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"Archivo no encontrado: {ruta}")
        return {}
    except Exception as e:
        logging.getLogger(__name__).exception("Error leyendo configuración normativa")
        return {}


# ==========================================================
# 🔹 FACTOR COMÚN PARA COMPONENTES: G, T, D, PR, R, C
# ==========================================================

def calcular_componente(nombre: str, consumo_kwh: float, valor_unitario: float):
    return {
        "componente": nombre,
        "consumo_kwh": consumo_kwh,
        "valor_unitario": valor_unitario,
        "total": round(consumo_kwh * valor_unitario, 6)
    }


# ==========================================================
# 🔹 WRAPPERS INDIVIDUALES
# ==========================================================

def calcular_generacion(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("G", consumo_kwh, valor_unitario)


def calcular_transmision(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("T", consumo_kwh, valor_unitario)


def calcular_distribucion(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("D", consumo_kwh, valor_unitario)
