from fastapi import APIRouter, HTTPException
from app.db import use_db, conn_ctx, mem, next_id
from app.models import ClienteIn

router = APIRouter()


@router.get("")
def list_clientes():
    if not use_db():
        return mem()["clientes"]
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT * FROM clientes ORDER BY id")
            return [dict(r) for r in cur.fetchall()]


@router.get("/{cid}")
def get_cliente(cid: int):
    if not use_db():
        for c in mem()["clientes"]:
            if c["id"] == cid:
                return c
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("SELECT * FROM clientes WHERE id=%s", (cid,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
            return dict(r)


@router.post("")
def create_cliente(data: ClienteIn):
    if not use_db():
        nu = data.model_dump()
        nu["id"] = next_id("clientes")
        mem()["clientes"].append(nu)
        return nu
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO clientes(nombre,email,telefono,notas) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.nombre, data.email, data.telefono, data.notas),
            )
            r = cur.fetchone()
        c.commit()
        return dict(r)


@router.put("/{cid}")
def update_cliente(cid: int, data: ClienteIn):
    if not use_db():
        for c in mem()["clientes"]:
            if c["id"] == cid:
                c.update(data.model_dump())
                return c
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE clientes SET nombre=%s,email=%s,telefono=%s,notas=%s WHERE id=%s RETURNING *",
                (data.nombre, data.email, data.telefono, data.notas, cid),
            )
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "not found")
        c.commit()
        return dict(r)


@router.delete("/{cid}")
def delete_cliente(cid: int):
    if not use_db():
        lst = mem()["clientes"]
        for i, c in enumerate(lst):
            if c["id"] == cid:
                lst.pop(i)
                return {"ok": True}
        raise HTTPException(404, "not found")
    with conn_ctx() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id=%s", (cid,))
        c.commit()
    return {"ok": True}
