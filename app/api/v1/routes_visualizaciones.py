from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.movimiento_repo import MovimientoRepository
from app.schemas.movimiento import (
    ComposicionEgresos,
    ComposicionEgresosFijos,
    ComposicionEgresosVarios,
    ImportanciaClientesAnual,
    PesoClientes,
    RegistroPeriodo,
    ResumenEgresos,
    ResumenGeneral,
    ResumenIngresos,
    SerieMensual,
    TotalPorCategoria,
)
from app.services.calculos import CalculosService, ClasificacionValida, TipoEgresoValido, TipoIngresoValido

router = APIRouter(prefix="/visualizaciones", tags=["visualizaciones"])


def _get_service(db: AsyncSession = Depends(get_db)) -> CalculosService:
    return CalculosService(MovimientoRepository(db))


@router.get("/resumen", response_model=ResumenGeneral)
async def resumen_general(
    ano: str | None = Query(default=None),
    mes: str | None = Query(default=None),
    clasificacion: str | None = Query(default=None),
    service: CalculosService = Depends(_get_service),
):
    """Totales (débito, crédito, neto), cantidad y promedio, con filtros opcionales."""
    return await service.resumen_general(ano=ano, mes=mes, clasificacion=clasificacion)


@router.get("/serie-mensual", response_model=list[SerieMensual])
async def serie_mensual(
    ano: str | None = Query(default=None),
    service: CalculosService = Depends(_get_service),
):
    """Totales agrupados por mes/año, listos para graficar una serie de tiempo."""
    return await service.serie_mensual(ano=ano)


@router.get("/por-clasificacion", response_model=list[TotalPorCategoria])
async def totales_por_clasificacion(service: CalculosService = Depends(_get_service)):
    """Totales agrupados por clasificación, listos para un gráfico de torta/barras."""
    return await service.totales_por_clasificacion()


@router.get("/total-por-clasificacion-anual", response_model=dict[str, float])
async def total_por_clasificacion_anual(
    ano: str = Query(...),
    clasificacion: ClasificacionValida = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Suma TOTAL por cada mes del año, para una clasificación puntual (COSTOS, GASTOS,
    INGRESO OPERACIONAL o INGRESO NO OPERACIONAL). Devuelve un diccionario {mes: total}
    con los 12 meses."""
    return await service.total_por_clasificacion_anual(ano=ano, clasificacion=clasificacion)


@router.get("/resumen-ingresos", response_model=ResumenIngresos)
async def resumen_ingresos(
    ano: str = Query(...),
    mes: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Resumen de ingresos (INGRESO OPERACIONAL + INGRESO NO OPERACIONAL) para un año y mes:
    total del mes, variación vs. mes anterior, variación vs. mismo mes del año anterior
    y acumulado del año hasta el mes seleccionado."""
    return await service.resumen_ingresos(ano=ano, mes=mes)


@router.get("/resumen-egresos", response_model=ResumenEgresos)
async def resumen_egresos(
    ano: str = Query(...),
    mes: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Resumen de egresos (COSTOS + GASTOS) para un año y mes: total del mes, variación vs.
    mes anterior, variación vs. mismo mes del año anterior y acumulado del año hasta el mes."""
    return await service.resumen_egresos(ano=ano, mes=mes)


@router.get("/registro-ingresos", response_model=dict[str, float])
async def registro_ingresos(
    ano: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Suma TOTAL de ingresos (INGRESO OPERACIONAL + INGRESO NO OPERACIONAL) por cada mes
    del año dado. Devuelve un diccionario {mes: total} con los 12 meses."""
    return await service.registro_ingresos(ano=ano)


@router.get("/registro-egresos", response_model=dict[str, float])
async def registro_egresos(
    ano: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Suma TOTAL de egresos (COSTOS + GASTOS) por cada mes del año dado.
    Devuelve un diccionario {mes: total} con los 12 meses."""
    return await service.registro_egresos(ano=ano)


@router.get("/registro-ingresos-acumulado", response_model=dict[str, float])
async def registro_ingresos_acumulado(
    ano: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Igual que registro-ingresos, pero cada mes trae el acumulado desde Enero hasta ese mes."""
    return await service.registro_ingresos_acumulado(ano=ano)


@router.get("/registro-egresos-acumulado", response_model=dict[str, float])
async def registro_egresos_acumulado(
    ano: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Igual que registro-egresos, pero cada mes trae el acumulado desde Enero hasta ese mes."""
    return await service.registro_egresos_acumulado(ano=ano)


@router.get("/registro-ingresos-por-tipo", response_model=dict[str, float])
async def registro_ingresos_por_tipo(
    ano: str = Query(...),
    tipo_ingreso: TipoIngresoValido = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Suma TOTAL de ingresos por mes, filtrando además por TIPO_INGRESO
    ("Ingreso fijo" o "Ingreso vario"). Devuelve un diccionario {mes: total} con los 12 meses."""
    return await service.registro_ingresos_por_tipo(ano=ano, tipo_ingreso=tipo_ingreso)


@router.get("/registro-egresos-por-tipo", response_model=dict[str, float])
async def registro_egresos_por_tipo(
    ano: str = Query(...),
    tipo_egreso: TipoEgresoValido = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Suma TOTAL de egresos por mes, filtrando además por TIPO_EGRESO
    ("Egreso fijo" o "Egreso variable"). Devuelve un diccionario {mes: total} con los 12 meses."""
    return await service.registro_egresos_por_tipo(ano=ano, tipo_egreso=tipo_egreso)


@router.get("/composicion-egresos", response_model=ComposicionEgresos)
async def composicion_egresos(
    ano: str = Query(...),
    mes: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Composición de egresos (COSTOS + GASTOS) de un año y mes: cuánto pesan
    Egreso fijo y Egreso variable, en plata y en porcentaje sobre el total de ese mes."""
    return await service.composicion_egresos(ano=ano, mes=mes)


@router.get("/composicion-egresos-fijos", response_model=ComposicionEgresosFijos)
async def composicion_egresos_fijos(
    ano: str = Query(...),
    mes: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Composición de los egresos fijos (COSTOS + GASTOS, TIPO_EGRESO = "Egreso fijo") de un
    año y mes: cuánto pesa cada cuenta (CLASIFICACION_NOMBRE_CUENTA), en plata y en porcentaje."""
    return await service.composicion_egresos_fijos(ano=ano, mes=mes)


@router.get("/composicion-egresos-varios", response_model=ComposicionEgresosVarios)
async def composicion_egresos_varios(
    ano: str = Query(...),
    mes: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Composición de los egresos varios (COSTOS + GASTOS, TIPO_EGRESO = "Egreso variable") de un
    año y mes: cuánto pesa cada cuenta (CLASIFICACION_NOMBRE_CUENTA), en plata y en porcentaje."""
    return await service.composicion_egresos_varios(ano=ano, mes=mes)


@router.get("/peso-clientes", response_model=PesoClientes)
async def peso_clientes(
    ano: str = Query(...),
    mes: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Peso de cada cliente (TERCEROS) dentro del total de ingresos
    (INGRESO OPERACIONAL + INGRESO NO OPERACIONAL) de un año y mes dados."""
    return await service.peso_clientes(ano=ano, mes=mes)


@router.get("/importancia-clientes-anual", response_model=ImportanciaClientesAnual)
async def importancia_clientes_anual(
    ano: str = Query(...),
    service: CalculosService = Depends(_get_service),
):
    """Igual que peso-clientes, pero acumulado en todo el año (sin filtro de mes),
    para graficar la importancia anual de cada cliente."""
    return await service.importancia_clientes_anual(ano=ano)


@router.get("/registros-por-periodo", response_model=list[RegistroPeriodo])
async def registros_por_periodo(
    ano_inicial: str = Query(...),
    mes_inicial: str = Query(...),
    ano_final: str = Query(...),
    mes_final: str = Query(...),
    cliente: str | None = Query(default=None),
    nit: str | None = Query(default=None),
    documento: str | None = Query(default=None),
    service: CalculosService = Depends(_get_service),
):
    """Registros (cliente, nit, documento, mes, año, total) dentro de un rango de fechas
    (año/mes inicial hasta año/mes final), con filtros opcionales de cliente, nit y documento."""
    try:
        return await service.registros_por_periodo(
            ano_inicial=ano_inicial,
            mes_inicial=mes_inicial,
            ano_final=ano_final,
            mes_final=mes_final,
            cliente=cliente,
            nit=nit,
            documento=documento,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
