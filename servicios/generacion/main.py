# servicios/generacion/main.py
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from logica import calcular_componente_G
from core.xm_api import listar_metricas_xm, obtener_precio_bolsa_xm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Microservicio Generación",
    description="Calcula el componente G (Generación) de la tarifa eléctrica usando datos reales de XM",
    version="1.1.0"
)

class CompraEnergia(BaseModel):
    energia_kWh: float
    precio_kWh: float | None = None  # si viene 0/None, usamos PB de XM

@app.get("/")
def root():
    return {"mensaje": "Microservicio de Generación activo"}

@app.get("/generacion/precio-xm")
async def obtener_precio_xm():
    valor = await obtener_precio_bolsa_xm()
    return {"fuente": "XM", "valor_kWh": valor}

@app.get("/generacion/metricas-xm")
async def listar_metricas():
    try:
        items = await listar_metricas_xm(force=True)
        return {"ok": True, "total_metricas": len(items), "metricas": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/generacion/calcular")
async def calcular_generacion(compras: List[CompraEnergia]):
    """
    Si precio_kWh es 0 o None en alguna compra, se reemplaza por el PB de XM internamente.
    """
    try:
        data = [c.model_dump() for c in compras]
        resultado = await calcular_componente_G(data)  # <<<<<< await
        return resultado
    except Exception as e:
        logger.exception("Error al procesar solicitud")
        raise HTTPException(status_code=500, detail=str(e))
