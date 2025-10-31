from fastapi import FastAPI

app = FastAPI(title="Servicio de Distribución", version="1.0")

@app.get("/")
def root():
    return {"message": "Servicio de Distribución activo"}

@app.get("/valor")
def obtener_valor_distribucion():
    """
    Simula el valor asociado al componente de distribución.
    En el futuro aquí puedes conectar con la base de datos o lógica real.
    """
    return {"valor": 63.8}
