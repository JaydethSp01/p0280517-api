from fastapi import APIRouter, HTTPException
from app.db import use_db, conn_ctx, mem, next_id
from app.models import CitaIn

router = APIRouter()


def _enrich_mem(c: dict) -> dict:
    cli = next((x for x in mem()["clientes"] if x["id"] == c["cliente_id"]), None)
    bar = next((x for x in mem()["barberos"] if x["id"] == c["barbero_id"]), None)
    ser = next((x for x in mem()["servicios"] if x["id"] == c["servicio_id"]), None)
    return {
        **c,
        "cliente_nombre": cli["nombre"] if cli else None,
        "barbero_nombre": bar["nombre"] if bar else None,
        "servicio_nombre": ser["nombre"] if ser else None,
    }


JOIN_SQL = """
SELECT c.id, c.cliente_id, c.barbero_id, c.servicio_id,
       to_char(c.fecha,'YYYY-MM-DD') AS fecha,
       to_char(c.hora,'HH24:MI') AS hora,
       c.estado, c.precio,
       cl.nombre AS cliente_nombre,
       b.nombre AS barbero_nombre,
       s.nombre AS servicio_nombre
FROM citas c
LEFT JOIN clientes cl ON cl.id = c.cliente_id
LEFT JOIN barberos b  ON b.id  = c.barbero_id
LEFT JOIN servicios s ON s.id  = c.servicio_id
"""


@router.get("")
def list_citas():
    if not use_db():
        return [_enrich_mem(x) for x in mem()["citas"]]
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(JOIN_SQL + " ORDER BY c.fecha, c.hora")
            return [dict(r) for r in cur.fetchall()]


@router.get("/{cid}")
def get_cita(cid: int):
    if not use_db():
        for x in mem()["citas"]:
            if x["id"] == cid:
                return _enrich_mem(x)
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(JOIN_SQL + " WHERE c.id=%s", (cid,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
            return dict(r)


@router.post("")
def create_cita(data: CitaIn):
    if not use_db():
        nu = data.model_dump()
        nu["id"] = next_id("citas")
        mem()["citas"].append(nu)
        return _enrich_mem(nu)
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO citas(cliente_id,barbero_id,servicio_id,fecha,hora,estado,precio) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (data.cliente_id, data.barbero_id, data.servicio_id, data.fecha, data.hora, data.estado, data.precio),
            )
            new_id = cur.fetchone()["id"]
            cur.execute(JOIN_SQL + " WHERE c.id=%s", (new_id,))
            r = cur.fetchone()
        c.commit()
        return dict(r)


@router.put("/{cid}")
def update_cita(cid: int, data: CitaIn):
    if not use_db():
        for x in mem()["citas"]:
            if x["id"] == cid:
                x.update(data.model_dump())
                return _enrich_mem(x)
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE citas SET cliente_id=%s,barbero_id=%s,servicio_id=%s,fecha=%s,hora=%s,estado=%s,precio=%s WHERE id=%s RETURNING id",
                (data.cliente_id, data.barbero_id, data.servicio_id, data.fecha, data.hora, data.estado, data.precio, cid),
            )
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
            cur.execute(JOIN_SQL + " WHERE c.id=%s", (cid,))
            r = cur.fetchone()
        c.commit()
        return dict(r)


@router.delete("/{cid}")
def delete_cita(cid: int):
    if not use_db():
        lst = mem()["citas"]
        for i, x in enumerate(lst):
            if x["id"] == cid:
                lst.pop(i)
                return {"ok": True}
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM citas WHERE id=%s", (cid,))
        c.commit()
    return {"ok": True}
