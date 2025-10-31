from fastapi import FastAPI

app = FastAPI(title="Servicio de Restricciones", version="1.0")

@app.get("/")
def root():
    return {"message": "Servicio de Restricciones activo"}

@app.get("/valor")
def obtener_valor_restricciones():
    """
    Valor de los costos de restricciones operativas del sistema.
    """
    return {"valor": 12.9}
