from pydantic import BaseModel
from typing import List
from datetime import date
from typing import Optional

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

class Usuario(BaseModel):
    idUsuario: int
    nombre: str
    apellidos: str
    email: str
    password: str
    telefono: str
    rolUsuario: str

class DatosActualizados(BaseModel):
    nombre: str
    apellidos: str
    telefono: str
    correoElectronico: str
    contraseña: str

class CredencialesUsuario(BaseModel):
    email: str
    contraseña: str

class NuevaRefaccion(BaseModel):
    idRefaccion: int
    nombre: str
    cantidad: int
    precioUnitario: float
    descripcion: str

class Refaccion(BaseModel):
    idRefaccion: int
    nombreRefaccion: str
    precio: float
    cantidad: int
    descripcion: str
    estatus: str

class Reparacion(BaseModel):
    tipoReparacion: str
    detalles: str
    estatus: str
    costoServicio: float
    total: float
    idCita: int
    idUsuarioC: int
    idUsuarioT: int
    idDispositivo: int
    refacciones: List[Refaccion]

class NuevaRefaccion(BaseModel):
    idReparacion: Optional[int]
    idRefaccion: int
    nombre: str
    cantidad: int
    precioUnitario: float
    descripcion: str

class ActualizarRefaccion(BaseModel):
    nombre: str
    cantidad: int
    precioUnitario: float