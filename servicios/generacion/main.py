# servicios/generacion/main.py
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from logica import calcular_componente_G
from core.xm_api import listar_metricas_xm, obtener_precio_bolsa_xm

# ==========================================================
# 🔹 Configuración básica de logging
# ==========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================================
# 🔹 Inicialización de la aplicación FastAPI
# ==========================================================
app = FastAPI(
    title="Microservicio Generación",
    description="Calcula el componente G (Generación) de la tarifa eléctrica usando datos reales de XM",
    version="1.1.1"
)

# ==========================================================
# 🔹 Modelos de datos
# ==========================================================
class CompraEnergia(BaseModel):
    energia_kWh: float
    precio_kWh: float | None = None  # si viene 0/None, se usa PBND desde XM


# ==========================================================
# 🔹 Endpoints
# ==========================================================
@app.get("/")
def root():
    """Verificación rápida del estado del microservicio"""
    return {"mensaje": "Microservicio de Generación activo ✅"}


@app.get("/generacion/precio-xm")
async def obtener_precio_xm():
    """
    Devuelve el Precio Bolsa Nacional Diario (PBND) desde XM o el respaldo local si no hay conexión.
    """
    try:
        valor, fuente = await obtener_precio_bolsa_xm()
        logger.info(f"📊 Valor G obtenido: {valor} $/kWh | Fuente: {fuente}")
        return {"valor_kWh": valor, "fuente": fuente}
    except Exception as e:
        logger.exception("❌ Error al obtener el precio desde XM")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generacion/metricas-xm")
async def listar_metricas():
    """
    Consulta y lista las métricas disponibles en el servicio XM.
    """
    try:
        items = await listar_metricas_xm(force=True)
        return {
            "ok": True,
            "total_metricas": len(items),
            "metricas": items
        }
    except Exception as e:
        logger.exception("❌ Error al listar métricas XM")
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/generacion/calcular")
async def calcular_generacion(compras: List[CompraEnergia]):
    """
    Calcula el componente G (Generación) total.  
    Si `precio_kWh` es 0 o None en alguna compra, se reemplaza internamente por el PBND de XM.
    """
    try:
        data = [c.model_dump() for c in compras]
        resultado = await calcular_componente_G(data)
        logger.info("✅ Cálculo de componente G completado correctamente")
        return resultado
    except Exception as e:
        logger.exception("❌ Error al procesar solicitud de cálculo de generación")
        raise HTTPException(status_code=500, detail=str(e))
