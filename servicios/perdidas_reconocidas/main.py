from fastapi import FastAPI

app = FastAPI(title="Servicio de Pérdidas Reconocidas", version="1.0")

@app.get("/")
def root():
    return {"message": "Servicio de Pérdidas Reconocidas activo"}

@app.get("/valor")
def obtener_valor_perdidas():
    """
    Representa el costo de pérdidas reconocidas dentro del sistema eléctrico.
    """
    return {"valor": 8.4}
