from pydantic import BaseModel, Field
from typing import Optional


class ServicioIn(BaseModel):
    nombre: str
    descripcion: str = ""
    duracion: int = 30
    precio: float = 0
    activo: bool = True


class Servicio(ServicioIn):
    id: int


class BarberoIn(BaseModel):
    nombre: str
    especialidad: str = ""
    telefono: str = ""
    horario: str = ""
    foto: str = ""
    activo: bool = True


class Barbero(BarberoIn):
    id: int


class ClienteIn(BaseModel):
    nombre: str
    email: str = ""
    telefono: str = ""
    notas: str = ""


class Cliente(ClienteIn):
    id: int


class CitaIn(BaseModel):
    cliente_id: int
    barbero_id: int
    servicio_id: int
    fecha: str
    hora: str
    estado: str = "pendiente"
    precio: float = 0


class Cita(CitaIn):
    id: int
    cliente_nombre: Optional[str] = None
    barbero_nombre: Optional[str] = None
    servicio_nombre: Optional[str] = None


class LoginIn(BaseModel):
    email: str
    password: str


class LoginOut(BaseModel):
    token: str
    user: dict
