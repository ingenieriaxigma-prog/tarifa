from fastapi import FastAPI
from servicios.distribucion.logica import calcular_distribucion
from servicios.distribucion.modelo import DatosDistribucion

app = FastAPI()

@app.post("/calcular/distribucion")
def calcular(datos: DatosDistribucion):
    return {"componente_D": calcular_distribucion(datos)}
