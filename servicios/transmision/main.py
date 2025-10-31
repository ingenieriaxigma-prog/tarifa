from fastapi import FastAPI

app = FastAPI(title="Servicio de Transmisión", version="1.0")

@app.get("/")
def root():
    return {"message": "Servicio de Transmisión activo"}

@app.get("/valor")
def obtener_valor_transmision():
    return {"valor": 45.7}
