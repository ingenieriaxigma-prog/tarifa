# servicios/pr/modelo.py
from pydantic import BaseModel, Field

class DatosEntrada(BaseModel):
    consumo: float = Field(..., gt=0, description="Consumo de energía en kWh")
    estrato: int = Field(..., ge=1, le=6)
    zona: str = Field(..., description="Zona geográfica (por ejemplo: 'costa' o 'interior')")
    nivel_tension: str = Field(..., description="Nivel de tensión: NT1, NT2, NT3, NT4 o NT5")

class ResultadoPR(BaseModel):
    componente: str = "PR"
    valor: float
    detalle: dict
