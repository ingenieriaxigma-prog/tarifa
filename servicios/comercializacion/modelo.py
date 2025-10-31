from pydantic import BaseModel

class ComercializacionRequest(BaseModel):
    consumo_kWh: float
