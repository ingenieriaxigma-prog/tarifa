from pydantic import BaseModel

class DatosDistribucion(BaseModel):
    consumo_kWh: float
    estrato: int
    zona: str  # 'urbana' o 'rural'
