import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from logica import calcular_componente_T

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Microservicio Transmisión",
    description="Calcula el componente T (Transmisión) de la tarifa eléctrica",
    version="1.0.0"
)

# Modelo de entrada
class LineaTransmision(BaseModel):
    energia_kWh: float
    costo_unitario_kWh: float


@app.get("/")
def root():
    return {"mensaje": "Microservicio de Transmisión activo"}


@app.post("/transmision/calcular")
def calcular_transmision(lineas: List[LineaTransmision]):
    """
    Calcula el componente T con base en los datos de transmisión.
    """
    try:
        data = [l.dict() for l in lineas]
        resultado = calcular_componente_T(data)
        return resultado
    except Exception as e:
        logger.error(f"Error en cálculo de transmisión: {e}")
        raise HTTPException(status_code=500, detail=str(e))
