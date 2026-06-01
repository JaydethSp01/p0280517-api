import os
from contextlib import contextmanager
from typing import Any, Iterator, Optional

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover
    psycopg = None  # type: ignore

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

_memory: dict[str, list[dict]] = {
    "servicios": [],
    "barberos": [],
    "clientes": [],
    "citas": [],
}
_seq: dict[str, int] = {"servicios": 0, "barberos": 0, "clientes": 0, "citas": 0}


def use_db() -> bool:
    return bool(DATABASE_URL) and psycopg is not None


@contextmanager
def conn_ctx() -> Iterator[Any]:
    if not use_db():
        yield None
        return
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as c:
        yield c


def init_db() -> None:
    if not use_db():
        return
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS servicios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT DEFAULT '',
                    duracion INT NOT NULL DEFAULT 30,
                    precio NUMERIC(10,2) NOT NULL DEFAULT 0,
                    activo BOOLEAN NOT NULL DEFAULT TRUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS barberos (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    especialidad TEXT DEFAULT '',
                    telefono TEXT DEFAULT '',
                    horario TEXT DEFAULT '',
                    foto TEXT DEFAULT '',
                    activo BOOLEAN NOT NULL DEFAULT TRUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT DEFAULT '',
                    telefono TEXT DEFAULT '',
                    notas TEXT DEFAULT ''
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS citas (
                    id SERIAL PRIMARY KEY,
                    cliente_id INT REFERENCES clientes(id) ON DELETE CASCADE,
                    barbero_id INT REFERENCES barberos(id) ON DELETE CASCADE,
                    servicio_id INT REFERENCES servicios(id) ON DELETE CASCADE,
                    fecha DATE NOT NULL,
                    hora TIME NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'pendiente',
                    precio NUMERIC(10,2) NOT NULL DEFAULT 0
                );
            """)
        c.commit()


SEED_SERVICIOS = [
    ("Corte clásico", "Corte tradicional con tijera y máquina", 30, 25, True),
    ("Corte + Barba", "Combo completo con perfilado de barba", 45, 40, True),
    ("Afeitado clásico", "Afeitado con navaja y toalla caliente", 30, 30, True),
    ("Diseño de barba", "Perfilado y diseño personalizado", 20, 20, True),
    ("Tinte de cabello", "Aplicación de tinte profesional", 60, 70, True),
    ("Corte infantil", "Corte especial para niños menores de 12", 25, 18, True),
    ("Tratamiento capilar", "Hidratación profunda y masaje", 40, 50, True),
    ("Paquete novio", "Corte, barba y tratamiento facial", 90, 120, True),
]

SEED_BARBEROS = [
    ("Carlos Mendoza", "Fade y diseños", "+51 999 123 001", "Lun-Sab 9:00-19:00", "https://images.unsplash.com/photo-1503443207922-dff7d543fd0e?w=400&q=80", True),
    ("Diego Ramírez", "Corte clásico y barba", "+51 999 123 002", "Mar-Dom 10:00-20:00", "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=400&q=80", True),
    ("Andrés Torres", "Afeitado a navaja", "+51 999 123 003", "Lun-Vie 8:00-18:00", "https://images.unsplash.com/photo-1554151228-14d9def656e4?w=400&q=80", True),
    ("Javier Soto", "Coloración", "+51 999 123 004", "Lun-Sab 11:00-20:00", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80", True),
    ("Luis Paredes", "Corte infantil", "+51 999 123 005", "Vie-Dom 10:00-19:00", "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=400&q=80", True),
    ("Mario Quispe", "Estilismo urbano", "+51 999 123 006", "Lun-Sab 9:00-18:00", "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&q=80", True),
]

SEED_CLIENTES = [
    ("Pedro Sánchez", "pedro.sanchez@mail.com", "+51 988 100 001", "Prefiere atención con Carlos"),
    ("Juan Castillo", "juan.castillo@mail.com", "+51 988 100 002", "Cliente VIP"),
    ("Miguel Rojas", "miguel.rojas@mail.com", "+51 988 100 003", "Alergia a ciertos tintes"),
    ("Ricardo Vela", "ricardo.vela@mail.com", "+51 988 100 004", "Reserva mensual"),
    ("Sofía Núñez", "sofia.nunez@mail.com", "+51 988 100 005", "Trae a su hijo"),
    ("Hugo Pérez", "hugo.perez@mail.com", "+51 988 100 006", ""),
    ("Alonso García", "alonso.garcia@mail.com", "+51 988 100 007", "Prefiere mañanas"),
    ("Renato León", "renato.leon@mail.com", "+51 988 100 008", "Promoción WhatsApp"),
    ("Marco Aguilar", "marco.aguilar@mail.com", "+51 988 100 009", ""),
    ("Bruno Salas", "bruno.salas@mail.com", "+51 988 100 010", "Cliente desde 2022"),
]

SEED_CITAS = [
    (1, 1, 1, "2026-06-01", "09:00", "confirmada", 25),
    (2, 2, 2, "2026-06-01", "10:00", "confirmada", 40),
    (3, 3, 3, "2026-06-01", "11:30", "pendiente", 30),
    (4, 1, 4, "2026-06-01", "15:00", "confirmada", 20),
    (5, 5, 6, "2026-06-01", "16:30", "confirmada", 18),
    (6, 4, 5, "2026-06-02", "12:00", "pendiente", 70),
    (7, 6, 1, "2026-06-02", "17:00", "confirmada", 25),
    (8, 2, 8, "2026-06-03", "10:30", "confirmada", 120),
    (9, 3, 7, "2026-06-03", "15:30", "cancelada", 50),
    (10, 1, 2, "2026-06-04", "11:00", "confirmada", 40),
]


def _seed_memory() -> None:
    if _memory["servicios"]:
        return
    for n, d, du, p, a in SEED_SERVICIOS:
        _seq["servicios"] += 1
        _memory["servicios"].append({"id": _seq["servicios"], "nombre": n, "descripcion": d, "duracion": du, "precio": float(p), "activo": a})
    for n, e, t, h, f, a in SEED_BARBEROS:
        _seq["barberos"] += 1
        _memory["barberos"].append({"id": _seq["barberos"], "nombre": n, "especialidad": e, "telefono": t, "horario": h, "foto": f, "activo": a})
    for n, e, t, no in SEED_CLIENTES:
        _seq["clientes"] += 1
        _memory["clientes"].append({"id": _seq["clientes"], "nombre": n, "email": e, "telefono": t, "notas": no})
    for cl, ba, se, fe, ho, es, pr in SEED_CITAS:
        _seq["citas"] += 1
        _memory["citas"].append({"id": _seq["citas"], "cliente_id": cl, "barbero_id": ba, "servicio_id": se, "fecha": fe, "hora": ho, "estado": es, "precio": float(pr)})


def seed_if_empty() -> None:
    if not use_db():
        _seed_memory()
        return
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM servicios")
            if (cur.fetchone() or {}).get("n", 0) == 0:
                cur.executemany("INSERT INTO servicios(nombre,descripcion,duracion,precio,activo) VALUES (%s,%s,%s,%s,%s)", SEED_SERVICIOS)
            cur.execute("SELECT COUNT(*) AS n FROM barberos")
            if (cur.fetchone() or {}).get("n", 0) == 0:
                cur.executemany("INSERT INTO barberos(nombre,especialidad,telefono,horario,foto,activo) VALUES (%s,%s,%s,%s,%s,%s)", SEED_BARBEROS)
            cur.execute("SELECT COUNT(*) AS n FROM clientes")
            if (cur.fetchone() or {}).get("n", 0) == 0:
                cur.executemany("INSERT INTO clientes(nombre,email,telefono,notas) VALUES (%s,%s,%s,%s)", SEED_CLIENTES)
            cur.execute("SELECT COUNT(*) AS n FROM citas")
            if (cur.fetchone() or {}).get("n", 0) == 0:
                cur.executemany("INSERT INTO citas(cliente_id,barbero_id,servicio_id,fecha,hora,estado,precio) VALUES (%s,%s,%s,%s,%s,%s,%s)", SEED_CITAS)
        c.commit()


def mem() -> dict[str, list[dict]]:
    if not _memory["servicios"]:
        _seed_memory()
    return _memory


def next_id(table: str) -> int:
    _seq[table] += 1
    return _seq[table]
