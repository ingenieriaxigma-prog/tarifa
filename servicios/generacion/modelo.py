from pydantic import BaseModel
from typing import List

class CompraEnergia(BaseModel):
    nombre: str
    energia_kWh: float
    precio_kWh: float

class ListaCompras(BaseModel):
    compras: List[CompraEnergia]
