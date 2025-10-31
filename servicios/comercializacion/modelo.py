from pydantic import BaseModel

class DatosComercializacion(BaseModel):
    nivel_tension: str
    consumo: float
    zona: str

class ResultadoComercializacion(BaseModel):
    valor: float
    detalle: dict

