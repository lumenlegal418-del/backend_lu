from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.movimiento_repo import MovimientoRepository
from app.repositories.prediccion_repo import PrediccionRepository
from app.schemas.prediccion import ClasificacionPrediccion, PrediccionMes, RecalculoPrediccionOut
from app.services.prediccion_service import (
    ANO_FINAL_DEFECTO,
    ANO_INICIAL_DEFECTO,
    MES_FINAL_DEFECTO,
    MES_INICIAL_DEFECTO,
    PrediccionService,
)

router = APIRouter(prefix="/predicciones", tags=["predicciones"])


def _get_service(db: AsyncSession = Depends(get_db)) -> PrediccionService:
    return PrediccionService(MovimientoRepository(db), PrediccionRepository(db))


@router.post("/recalcular", response_model=RecalculoPrediccionOut)
async def recalcular_predicciones(
    clasificacion: ClasificacionPrediccion,
    ano_inicial: str = Query(default=ANO_INICIAL_DEFECTO),
    mes_inicial: str = Query(default=MES_INICIAL_DEFECTO),
    ano_final: str = Query(default=ANO_FINAL_DEFECTO),
    mes_final: str = Query(default=MES_FINAL_DEFECTO),
    service: PrediccionService = Depends(_get_service),
):
    """Reentrena el modelo Holt-Winters para GASTOS o COSTOS con todo el histórico disponible
    y guarda en la tabla PREDICCION el valor ajustado/pronosticado para cada mes del rango
    [ano_inicial/mes_inicial, ano_final/mes_final] (por defecto: Enero 2024 - Diciembre 2026).
    Los meses dentro del histórico usan el valor ajustado del modelo (backtesting); los meses
    posteriores al último dato real usan el pronóstico. Ejecutar cada vez que se cargue
    información nueva."""
    try:
        return await service.recalcular(
            clasificacion=clasificacion,
            ano_inicial=ano_inicial,
            mes_inicial=mes_inicial,
            ano_final=ano_final,
            mes_final=mes_final,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{clasificacion}", response_model=list[PrediccionMes])
async def obtener_predicciones(
    clasificacion: ClasificacionPrediccion,
    ano: str | None = Query(default=None),
    service: PrediccionService = Depends(_get_service),
):
    """Lee las predicciones ya precalculadas (respuesta instantánea, no reentrena el modelo).
    Filtro opcional por año. Si aún no se ha corrido /predicciones/recalcular para esa
    clasificación, devuelve vacío."""
    return await service.obtener(clasificacion=clasificacion, ano=ano)
