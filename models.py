from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class GenerarCita(BaseModel):
    nombreCliente: str
    fechaCita: datetime
    marcaDispositivo: str
    modeloDispositivo: str
    posibleFalla: Optional[str] = None  # Campo opcional con valor por defecto
    estatus: Optional[str] = "pendiente"  # Establecer el valor por defecto # Agregar fecha de entrega como un atributo opcional

