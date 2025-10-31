from fastapi import FastAPI
from logica import calcular_comercializacion

app = FastAPI(title="Microservicio Comercialización")

@app.get("/")
async def root():
    return {"mensaje": "Microservicio Comercialización activo"}

# 👇 Importante: la ruta completa debe coincidir con la usada en tarifa_total ("/comercializacion/calcular")
@app.post("/comercializacion/calcular")
async def calcular(payload: dict):
    consumo_kWh = payload.get("consumo_kWh", 0)
    resultado = await calcular_comercializacion(consumo_kWh)
    return resultado
