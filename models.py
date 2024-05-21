from pydantic import BaseModel
from typing import List

class Dispositivo(BaseModel):
    idDispositivo: int
    marca: str
    modelo: str
    caracteristicasHardware: str
    fallas: str
    fotosDispositivo: str

class NuevaCita(BaseModel):
    id: int
    motivoCita: str
    horaCita: str
    estatusCita: str = "Pendiente"  
    idUsuarioC: int
    idUsuarioT: int
    dispositivos: List[Dispositivo]

class ConfirmacionCita(BaseModel):
    mensaje: str