import base64
import json
from fastapi import APIRouter, HTTPException
from app.models import LoginIn, LoginOut

router = APIRouter()

DEMO_USERS = {
    "admin@barberpro.com": {"password": "admin123", "rol": "admin", "nombre": "Administrador"},
    "barbero@barberpro.com": {"password": "barbero123", "rol": "usuario", "nombre": "Barbero"},
}


def _tok(payload: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")


@router.post("/login", response_model=LoginOut)
def login(data: LoginIn):
    u = DEMO_USERS.get(data.email)
    if not u or u["password"] != data.password:
        raise HTTPException(401, "Credenciales inválidas")
    return LoginOut(token=_tok({"email": data.email, "rol": u["rol"]}), user={"email": data.email, "rol": u["rol"], "nombre": u["nombre"]})


@router.get("/me")
def me():
    return {"email": "admin@barberpro.com", "rol": "admin", "nombre": "Administrador"}
