import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from logica import calcular_tarifa_total, calcular_tarifa_total_automatica

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Microservicio Tarifa Total (Async)",
    description="Calcula la tarifa eléctrica total consultando microservicios en paralelo",
    version="3.0.0"
)

class TarifaRequest(BaseModel):
    componentes: dict
    consumo_kWh: float

class TarifaAutoRequest(BaseModel):
    consumo_kWh: float


@app.get("/")
def root():
    return {"mensaje": "Microservicio Tarifa Total (Async) activo"}


@app.post("/tarifa/calcular")
def calcular_manual(req: TarifaRequest):
    return calcular_tarifa_total(req.componentes, req.consumo_kWh)


@app.post("/tarifa/calcular/auto")
async def calcular_automatico(req: TarifaAutoRequest):
    try:
        return await calcular_tarifa_total_automatica(req.consumo_kWh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
