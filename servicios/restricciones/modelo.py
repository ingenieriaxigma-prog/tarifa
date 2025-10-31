from pydantic import BaseModel

class DatosRestricciones(BaseModel):
    nivel_tension: str
    consumo: float
    zona: str

class ResultadoRestricciones(BaseModel):
    valor: float
    detalle: dict
