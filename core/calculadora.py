# --- pegar al inicio de core/calculadora.py ---
import json
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def cargar_configuracion(path: str | None = None) -> dict:
    """
    Carga la configuración normativa desde JSON compartido por la imagen base.
    Prioriza:
      1) env NORMATIVA_CONFIG_PATH
      2) /app/config/normativa_config.json
    """
    ruta = path or os.environ.get("NORMATIVA_CONFIG_PATH", "/app/config/normativa_config.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Configuración cargada exitosamente desde {ruta}")
        return data
    except FileNotFoundError:
        logger.error(f"No se encontró archivo de configuración: {ruta}")
        return {}
    except Exception as e:
        logger.error(f"Error cargando archivo de configuración: {e}")
        return {}

"""
📘 Módulo central de cálculo de componentes para Tarifa Eléctrica.
Versión optimizada: ahora todas las funciones usan una base común.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def calcular_componente(nombre: str, consumo_kwh: float, valor_unitario: float) -> Dict[str, Any]:
    """
    Calcula el valor total de un componente dado su nombre, consumo y valor unitario.
    Ejemplo: calcular_componente('G', 120, 320) → {'G': 38400}
    """
    try:
        total = round(consumo_kwh * valor_unitario, 3)
        logger.info(f"⚙️  Componente {nombre}: {valor_unitario} x {consumo_kwh} = {total}")
        return {nombre: total}
    except Exception as e:
        logger.error(f"❌ Error en componente {nombre}: {str(e)}")
        return {nombre: None, "error": str(e)}


def sumar_componentes(componentes: Dict[str, float]) -> float:
    """
    Suma los valores por kWh de cada componente (G, T, D, PR, R, C...).
    """
    try:
        total = round(sum(componentes.values()), 2)
        logger.info(f"💰 Tarifa total calculada: {total}")
        return total
    except Exception as e:
        logger.error(f"❌ Error sumando componentes: {str(e)}")
        return 0.0


# Funciones específicas (compatibles con lo que ya tienes)
def calcular_generacion(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("G", consumo_kwh, valor_unitario)

def calcular_transmision(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("T", consumo_kwh, valor_unitario)

def calcular_distribucion(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("D", consumo_kwh, valor_unitario)

def calcular_perdidas(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("PR", consumo_kwh, valor_unitario)

def calcular_restricciones(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("R", consumo_kwh, valor_unitario)

def calcular_comercializacion(consumo_kwh: float, valor_unitario: float):
    return calcular_componente("C", consumo_kwh, valor_unitario)
