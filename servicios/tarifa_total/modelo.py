# servicios/tarifa_total/modelo.py
from pydantic import BaseModel, Field
from typing import Dict

class DatosEntrada(BaseModel):
    consumo: float = Field(..., gt=0, description="Consumo en kWh")
    estrato: int = Field(..., ge=1, le=6)
    zona: str = Field(..., description="Zona geográfica: costa/interior")
    nivel_tension: str = Field(..., description="Nivel de tensión: NT1, NT2, NT3, NT4 o NT5")

class ResultadoTarifa(BaseModel):
    componentes: Dict[str, float]
    tarifa_total: float
