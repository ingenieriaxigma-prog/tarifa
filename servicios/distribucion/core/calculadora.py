import json
import os
import logging
from typing import Dict, Any

# Configurar logging global
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cargar_configuracion(ruta: str = "config/normativa_config.json") -> Dict[str, Any]:
    """
    Carga la configuración normativa desde un archivo JSON.
    Permite definir tarifas dinámicas por año, componente, etc.
    """
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_completa = os.path.join(base_path, ruta)
        with open(ruta_completa, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Configuración cargada exitosamente desde {ruta_completa}")
        return data
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo de configuración: {ruta}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error en el formato del archivo JSON: {e}")
        raise


def calcular_tarifa_total(config: Dict[str, Any], consumo_kwh: float) -> Dict[str, Any]:
    """
    Calcula el costo total de la tarifa eléctrica con base en la configuración cargada.
    (Por ahora usa los valores estáticos del JSON, pero luego se conectará a microservicios.)
    """
    logger.info(f"Iniciando cálculo de tarifa total para {consumo_kwh} kWh")

    # Extraer valores desde la configuración
    tarifas = config.get("tarifas", {})

    # Calcular cada componente (si existe)
    componentes = {}
    total = 0.0
    for nombre, datos in tarifas.items():
        valor_kwh = datos.get("valor_kWh", 0)
        subtotal = consumo_kwh * valor_kwh
        componentes[nombre] = round(subtotal, 2)
        total += subtotal

    resultado = {
        "consumo_kWh": consumo_kwh,
        "componentes": componentes,
        "total_tarifa": round(total, 2)
    }

    logger.info(f"Cálculo completado: {resultado}")
    return resultado


if __name__ == "__main__":
    """
    Permite ejecutar la calculadora desde consola para pruebas rápidas:
    $ python core/calculadora.py
    """
    config = cargar_configuracion()
    resultado = calcular_tarifa_total(config, consumo_kwh=150)
    print(json.dumps(resultado, indent=4))
