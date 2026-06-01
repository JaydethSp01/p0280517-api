# BarberPro · Backend

API FastAPI para BarberPro. CRUD de servicios, barberos, clientes y citas, con auth mock.

## Desarrollo

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Si `DATABASE_URL` está vacío o falla, el backend usa **modo memoria** (seed automático). Nunca devuelve 500 por DB.

## Endpoints

- `GET /health`
- `POST /auth/login`
- `GET|POST /servicios`, `GET|PUT|DELETE /servicios/{id}`
- `GET|POST /barberos`, `GET|PUT|DELETE /barberos/{id}`
- `GET|POST /clientes`, `GET|PUT|DELETE /clientes/{id}`
- `GET|POST /citas`, `GET|PUT|DELETE /citas/{id}`

## Deploy Render

1. Crea un Web Service apuntando a esta carpeta.
2. Build: `pip install -r requirements.txt`.
3. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Variables: `DATABASE_URL` (Neon), `CORS_ORIGINS` (URL Vercel).
