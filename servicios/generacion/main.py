from fastapi import FastAPI

app = FastAPI(title="Servicio de Generación", version="1.0")

@app.get("/")
def root():
    return {"message": "Servicio de Generación activo"}

@app.get("/valor")
def obtener_valor_generacion():
    # Aquí podrías tener una lógica real de cálculo
    return {"valor": 120.5}
