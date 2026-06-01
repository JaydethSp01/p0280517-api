import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db, seed_if_empty
from app.routers import cita, barbero, servicio, cliente, auth

app = FastAPI(title="BarberPro API", version="1.0.0")

origins_raw = os.environ.get("CORS_ORIGINS", "*")
origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(servicio.router, prefix="/servicios", tags=["servicios"])
app.include_router(barbero.router, prefix="/barberos", tags=["barberos"])
app.include_router(cliente.router, prefix="/clientes", tags=["clientes"])
app.include_router(cita.router, prefix="/citas", tags=["citas"])


@app.on_event("startup")
def on_startup() -> None:
    try:
        init_db()
        seed_if_empty()
    except Exception as exc:
        print(f"[startup] DB init skipped: {exc}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "barberpro-api"}


@app.get("/")
def root():
    return {"name": "BarberPro API", "docs": "/docs"}
