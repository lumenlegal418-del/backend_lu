from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.catalogos import (
    Ano,
    Clasificacion,
    ClasificacionNombreCuenta,
    Mes,
    TipoEgreso,
    TipoIngreso,
    Vigencia,
    EstadoCliente,
    RegistrosEgresos,
    Empleados,
)
from app.repositories.movimiento_repo import MovimientoRepository
from app.schemas.catalogos import (
    AnoOut,
    ClasificacionNombreCuentaOut,
    ClasificacionOut,
    MesOut,
    TipoEgresoOut,
    TipoIngresoOut,
    VigenciaOut,
    EstadoClienteOut,
    RegistrosEgresosOut,
    EmpleadosOut,
)
from app.schemas.movimiento import ArchivoInfo
from app.services.calculos import CLASIFICACIONES_INGRESO, MESES_ORDEN


router = APIRouter(prefix="/catalogos", tags=["catalogos"])


@router.get("/meses", response_model=list[MesOut])
async def listar_meses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Mes).order_by(Mes.id))
    return result.scalars().all()


@router.get("/anos", response_model=list[AnoOut])
async def listar_anos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ano).order_by(Ano.ano))
    return result.scalars().all()


@router.get("/clasificaciones", response_model=list[ClasificacionOut])
async def listar_clasificaciones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Clasificacion).order_by(Clasificacion.clasificacion))
    return result.scalars().all()


@router.get("/tipos-ingreso", response_model=list[TipoIngresoOut])
async def listar_tipos_ingreso(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TipoIngreso).order_by(TipoIngreso.tipo_ingreso))
    return result.scalars().all()


@router.get("/tipos-egreso", response_model=list[TipoEgresoOut])
async def listar_tipos_egreso(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TipoEgreso).order_by(TipoEgreso.tipo_egreso))
    return result.scalars().all()


@router.get("/vigencias", response_model=list[VigenciaOut])
async def listar_vigencias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vigencia).order_by(Vigencia.vigencia))
    return result.scalars().all()


@router.get("/clasificacion-nombre-cuenta", response_model=list[ClasificacionNombreCuentaOut])
async def listar_clasificacion_nombre_cuenta(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ClasificacionNombreCuenta).order_by(ClasificacionNombreCuenta.clasificacion_nombre_cuenta)
    )
    return result.scalars().all()


@router.get("/clientes", response_model=list[str])
async def listar_clientes(db: AsyncSession = Depends(get_db)):
    """Nombres de clientes (TERCEROS.nombre_tercero) con movimientos de
    INGRESO OPERACIONAL o INGRESO NO OPERACIONAL."""
    repo = MovimientoRepository(db)
    return await repo.listar_clientes(clasificaciones=CLASIFICACIONES_INGRESO)


@router.get("/nits", response_model=list[str])
async def listar_nits(db: AsyncSession = Depends(get_db)):
    """NIT (TERCEROS.nit) con movimientos de INGRESO OPERACIONAL o INGRESO NO OPERACIONAL."""
    repo = MovimientoRepository(db)
    return await repo.listar_nits(clasificaciones=CLASIFICACIONES_INGRESO)


@router.get("/documentos", response_model=list[str])
async def listar_documentos(db: AsyncSession = Depends(get_db)):
    """Nombres de DOCUMENTO con movimientos de INGRESO OPERACIONAL o INGRESO NO OPERACIONAL."""
    repo = MovimientoRepository(db)
    return await repo.listar_documentos(clasificaciones=CLASIFICACIONES_INGRESO)


@router.get("/archivos", response_model=list[ArchivoInfo])
async def listar_archivos(db: AsyncSession = Depends(get_db)):
    """Por cada NOMBRE_ARCHIVO, el/los año(s) en que aparece y los meses que contiene
    en cada año (ej. {nombre_archivo, ano_archivo, meses: [...]})."""
    repo = MovimientoRepository(db)
    filas = await repo.listar_archivos_meses()

    agrupado: dict[tuple[str, str], list[str]] = {}
    for f in filas:
        clave = (f["nombre_archivo"], f["ano"])
        agrupado.setdefault(clave, [])
        if f["mes"] not in agrupado[clave]:
            agrupado[clave].append(f["mes"])

    return [
        ArchivoInfo(
            nombre_archivo=nombre_archivo,
            ano_archivo=ano,
            meses=sorted(meses, key=lambda m: MESES_ORDEN.index(m) if m in MESES_ORDEN else len(MESES_ORDEN)),
        )
        for (nombre_archivo, ano), meses in agrupado.items()
    ]

@router.get("/estado-clientes", response_model=list[EstadoClienteOut])
async def listar_estado_clientes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EstadoCliente).order_by(EstadoCliente.id)
    )
    return result.scalars().all()


@router.get("/registros-egresos", response_model=list[RegistrosEgresosOut])
async def listar_registros_egresos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RegistrosEgresos).order_by(RegistrosEgresos.id)
    )
    return result.scalars().all()


@router.get("/empleados", response_model=list[EmpleadosOut])
async def listar_empleados(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Empleados).order_by(Empleados.id)
    )
    return result.scalars().all()

