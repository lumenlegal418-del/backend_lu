from typing import Literal

from pydantic import BaseModel

ClasificacionPrediccion = Literal["GASTOS", "COSTOS", "Ingreso fijo", "Ingreso vario"]


class PrediccionMes(BaseModel):
    ano: str
    mes: str
    valor_predicho: float


class RecalculoPrediccionOut(BaseModel):
    clasificacion: ClasificacionPrediccion
    meses_historicos_usados: int
    predicciones_generadas: int
    predicciones: list[PrediccionMes]
