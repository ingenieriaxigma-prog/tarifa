import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from logica import calcular_componente_D

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Microservicio Distribución",
    description="Calcula el componente D (Distribución) de la tarifa eléctrica",
    version="1.0.0"
)

# Modelo de entrada
class TramoDistribucion(BaseModel):
    energia_kWh: float
    costo_unitario_kWh: float


@app.get("/")
def root():
    return {"mensaje": "Microservicio de Distribución activo"}


@app.post("/distribucion/calcular")
def calcular_distribucion(redes: List[TramoDistribucion]):
    """
    Calcula el componente D con base en los tramos de red.
    """
    try:
        data = [r.dict() for r in redes]
        resultado = calcular_componente_D(data)
        return resultado
    except Exception as e:
        logger.error(f"Error en cálculo de distribución: {e}")
        raise HTTPException(status_code=500, detail=str(e))
