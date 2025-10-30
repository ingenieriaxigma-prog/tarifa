from fastapi import FastAPI
from servicios.generacion.modelo import ListaCompras
from servicios.generacion.logica import calcular_componente_G

app = FastAPI(title="Microservicio: Componente G")

@app.post("/calcular/generacion")
def calcular_generacion(data: ListaCompras):
    G = calcular_componente_G(data.compras)
    return {"componente_G": G}
