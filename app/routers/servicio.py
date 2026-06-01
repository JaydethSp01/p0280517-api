from fastapi import APIRouter, HTTPException
from app.db import use_db, conn_ctx, mem, next_id
from app.models import Servicio, ServicioIn

router = APIRouter()


@router.get("")
def list_servicios():
    if not use_db():
        return mem()["servicios"]
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id,nombre,descripcion,duracion,precio,activo FROM servicios ORDER BY id")
            return [dict(r) for r in cur.fetchall()]


@router.get("/{sid}")
def get_servicio(sid: int):
    if not use_db():
        for s in mem()["servicios"]:
            if s["id"] == sid:
                return s
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT * FROM servicios WHERE id=%s", (sid,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
            return dict(r)


@router.post("")
def create_servicio(data: ServicioIn):
    if not use_db():
        nu = data.model_dump()
        nu["id"] = next_id("servicios")
        mem()["servicios"].append(nu)
        return nu
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO servicios(nombre,descripcion,duracion,precio,activo) VALUES (%s,%s,%s,%s,%s) RETURNING *",
                (data.nombre, data.descripcion, data.duracion, data.precio, data.activo),
            )
            r = cur.fetchone()
        c.commit()
        return dict(r)


@router.put("/{sid}")
def update_servicio(sid: int, data: ServicioIn):
    if not use_db():
        for s in mem()["servicios"]:
            if s["id"] == sid:
                s.update(data.model_dump())
                return s
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE servicios SET nombre=%s,descripcion=%s,duracion=%s,precio=%s,activo=%s WHERE id=%s RETURNING *",
                (data.nombre, data.descripcion, data.duracion, data.precio, data.activo, sid),
            )
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
        c.commit()
        return dict(r)


@router.delete("/{sid}")
def delete_servicio(sid: int):
    if not use_db():
        lst = mem()["servicios"]
        for i, s in enumerate(lst):
            if s["id"] == sid:
                lst.pop(i)
                return {"ok": True}
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM servicios WHERE id=%s", (sid,))
        c.commit()
    return {"ok": True}
