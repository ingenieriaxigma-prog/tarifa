# modelo.py
from pydantic import BaseModel

class TransmisionRequest(BaseModel):
    dummy: str = "no_required"
