from fastapi import FastAPI
from servicios.transmision.modelo import TransmisionRequest
from servicios.transmision.logica import obtener_valor_transmision

app = FastAPI(title="Microservicio: Componente T")

@app.post("/calcular/transmision")
def calcular_transmision(data: TransmisionRequest):
    valor_T = obtener_valor_transmision()
    return {"componente_T": valor_T}
