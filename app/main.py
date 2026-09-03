from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import routes_catalogos, routes_movimientos, routes_predicciones, routes_visualizaciones
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import prediccion  # noqa: F401  # registra la tabla en Base.metadata

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_movimientos.router, prefix=settings.API_V1_STR)
app.include_router(routes_visualizaciones.router, prefix=settings.API_V1_STR)
app.include_router(routes_catalogos.router, prefix=settings.API_V1_STR)
app.include_router(routes_predicciones.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def crear_tablas_nuevas():
    """Crea únicamente tablas nuevas (ej. PREDICCION) que no existan aún; no toca las existentes."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
