from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.movimiento_repo import MovimientoRepository
from app.schemas.movimiento import DetalleMovimiento, MovimientoOut

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


@router.get("", response_model=list[MovimientoOut])
async def listar_movimientos(
    ano: str | None = Query(default=None),
    mes: str | None = Query(default=None),
    clasificacion: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = MovimientoRepository(db)
    movimientos = await repo.listar(ano=ano, mes=mes, clasificacion=clasificacion, skip=skip, limit=limit)
    return [
        MovimientoOut(
            id=m.id,
            debito=m.debito,
            credito=m.credito,
            total=m.total,
            mes=m.mes.mes if m.mes else None,
            ano=m.ano.ano if m.ano else None,
            clasificacion=m.clasificacion.clasificacion if m.clasificacion else None,
            tipo_ingreso=m.tipo_ingreso.tipo_ingreso if m.tipo_ingreso else None,
            tipo_egreso=m.tipo_egreso.tipo_egreso if m.tipo_egreso else None,
            tercero=m.terceros.nombre_tercero if m.terceros else None,
        )
        for m in movimientos
    ]


@router.get("/detalle", response_model=list[DetalleMovimiento])
async def listar_detalle(
    ano: str = Query(...),
    mes: str = Query(...),
    nombre_documento: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Detalle de movimientos (uno por fila) para un año y mes dados, con filtro opcional
    de nombre_documento."""
    repo = MovimientoRepository(db)
    movimientos = await repo.listar(
        ano=ano, mes=mes, nombre_documento=nombre_documento, skip=skip, limit=limit
    )
    return [
        DetalleMovimiento(
            ano=m.ano.ano if m.ano else None,
            mes=m.mes.mes if m.mes else None,
            nit=m.terceros.nit if m.terceros else None,
            nombre_tercero=m.terceros.nombre_tercero if m.terceros else None,
            detalle=m.detalle.informacion_detalle if m.detalle else None,
            nombre_cuenta=(
                m.clasificacion_nombre_cuenta.clasificacion_nombre_cuenta
                if m.clasificacion_nombre_cuenta
                else None
            ),
            codigo=m.codigo.codigo if m.codigo else None,
            documento=m.documento.nombre_documento if m.documento else None,
            debitos=m.debito,
            creditos=m.credito,
            total=m.total,
        )
        for m in movimientos
    ]
