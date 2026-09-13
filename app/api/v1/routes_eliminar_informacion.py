from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.eliminar_movimiento_repo import (
    EliminarMovimientoRepository,
)
from app.services.movimiento import MovimientoService


router = APIRouter(
    prefix="/eliminar",
    tags=["eliminar información"]
)


@router.delete("/movimientos")
async def eliminar_movimientos(
    nombre_archivo: str = Query(...),
    ano: str | None = Query(default=None),
    mes: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    repository = EliminarMovimientoRepository(db)
    service = MovimientoService(repository)

    resultado = await service.eliminar_por_archivo(
        nombre_archivo=nombre_archivo,
        ano=ano,
        mes=mes,
    )

    return resultado