import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from logica import calcular_componente_R

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Microservicio Restricciones",
    description="Calcula el componente R (Restricciones) de la tarifa eléctrica",
    version="1.0.0"
)

# Modelo de entrada
class EventoRestriccion(BaseModel):
    energia_afectada_kWh: float
    costo_unitario_kWh: float


@app.get("/")
def root():
    return {"mensaje": "Microservicio de Restricciones activo"}


@app.post("/restricciones/calcular")
def calcular_restricciones(eventos: List[EventoRestriccion]):
    """
    Calcula el componente R (Restricciones) a partir de los eventos registrados.
    """
    try:
        data = [e.dict() for e in eventos]
        resultado = calcular_componente_R(data)
        return resultado
    except Exception as e:
        logger.error(f"Error en cálculo de restricciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))
