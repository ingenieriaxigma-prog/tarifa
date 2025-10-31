from fastapi import FastAPI

app = FastAPI(title="Servicio de Comercialización", version="1.0")

@app.get("/")
def root():
    return {"message": "Servicio de Comercialización activo"}

@app.get("/valor")
def obtener_valor_comercializacion():
    """
    Simula el componente de comercialización en la tarifa final.
    """
    return {"valor": 21.7}
