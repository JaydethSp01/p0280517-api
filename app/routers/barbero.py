from fastapi import APIRouter, HTTPException
from app.db import use_db, conn_ctx, mem, next_id
from app.models import BarberoIn

router = APIRouter()


@router.get("")
def list_barberos():
    if not use_db():
        return mem()["barberos"]
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT * FROM barberos ORDER BY id")
            return [dict(r) for r in cur.fetchall()]


@router.get("/{bid}")
def get_barbero(bid: int):
    if not use_db():
        for b in mem()["barberos"]:
            if b["id"] == bid:
                return b
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT * FROM barberos WHERE id=%s", (bid,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
            return dict(r)


@router.post("")
def create_barbero(data: BarberoIn):
    if not use_db():
        nu = data.model_dump()
        nu["id"] = next_id("barberos")
        mem()["barberos"].append(nu)
        return nu
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO barberos(nombre,especialidad,telefono,horario,foto,activo) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
                (data.nombre, data.especialidad, data.telefono, data.horario, data.foto, data.activo),
            )
            r = cur.fetchone()
        c.commit()
        return dict(r)


@router.put("/{bid}")
def update_barbero(bid: int, data: BarberoIn):
    if not use_db():
        for b in mem()["barberos"]:
            if b["id"] == bid:
                b.update(data.model_dump())
                return b
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE barberos SET nombre=%s,especialidad=%s,telefono=%s,horario=%s,foto=%s,activo=%s WHERE id=%s RETURNING *",
                (data.nombre, data.especialidad, data.telefono, data.horario, data.foto, data.activo, bid),
            )
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
        c.commit()
        return dict(r)


@router.delete("/{bid}")
def delete_barbero(bid: int):
    if not use_db():
        lst = mem()["barberos"]
        for i, b in enumerate(lst):
            if b["id"] == bid:
                lst.pop(i)
                return {"ok": True}
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM barberos WHERE id=%s", (bid,))
        c.commit()
    return {"ok": True}
