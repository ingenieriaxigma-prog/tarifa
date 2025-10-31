import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from logica import calcular_componente_G

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Microservicio Generación",
    description="Calcula el componente G (Generación) de la tarifa eléctrica",
    version="1.0.0"
)

# Modelo de entrada (estructura JSON)
class CompraEnergia(BaseModel):
    energia_kWh: float
    precio_kWh: float


@app.get("/")
def root():
    """Ruta de prueba"""
    return {"mensaje": "Microservicio de Generación activo"}


@app.post("/generacion/calcular")
def calcular_generacion(compras: List[CompraEnergia]):
    """
    Calcula el componente G con base en las compras de energía.
    """
    try:
        data = [c.dict() for c in compras]
        resultado = calcular_componente_G(data)
        return resultado
    except Exception as e:
        logger.error(f"Error al procesar solicitud: {e}")
        raise HTTPException(status_code=500, detail=str(e))
