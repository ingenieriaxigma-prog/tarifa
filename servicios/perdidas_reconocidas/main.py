import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logica import calcular_componente_PR

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Microservicio Pérdidas Reconocidas",
    description="Calcula el componente PR (Pérdidas Reconocidas) de la tarifa eléctrica",
    version="1.0.0"
)

# Modelo de entrada
class PerdidasRequest(BaseModel):
    energia_total_kWh: float
    costo_promedio_kWh: float
    porcentaje_perdidas: float


@app.get("/")
def root():
    return {"mensaje": "Microservicio de Pérdidas Reconocidas activo"}


@app.post("/perdidas/calcular")
def calcular_perdidas(req: PerdidasRequest):
    """
    Calcula el componente PR basado en energía total, costo promedio y porcentaje de pérdidas.
    """
    try:
        resultado = calcular_componente_PR(
            energia_total_kWh=req.energia_total_kWh,
            costo_promedio_kWh=req.costo_promedio_kWh,
            porcentaje_perdidas=req.porcentaje_perdidas
        )
        return resultado
    except Exception as e:
        logger.error(f"Error en cálculo de PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
