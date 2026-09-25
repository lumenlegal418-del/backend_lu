import warnings

from app.repositories.movimiento_repo import MovimientoRepository
from app.repositories.prediccion_repo import PrediccionRepository
from app.schemas.prediccion import (
    ClasificacionPrediccion,
    PrediccionMes,
    RecalculoPrediccionOut,
)
from app.services.calculos import MESES_ORDEN, _mes_siguiente, _rango_periodos


# Rango por defecto solicitado: histórico/backtesting desde 2024
# hasta el pronóstico de cierre de 2026.
ANO_INICIAL_DEFECTO = "2024"
MES_INICIAL_DEFECTO = "Enero"
ANO_FINAL_DEFECTO = "2026"
MES_FINAL_DEFECTO = "Diciembre"


# Valores que viven en TIPO_INGRESO.
TIPOS_INGRESO_PREDICCION = {
    "Ingreso fijo",
    "Ingreso vario",
}

# Valores que viven en TIPO_EGRESO.
TIPOS_EGRESO_PREDICCION = {
    "Egreso fijo",
    "Egreso variable",
}


class PrediccionService:
    """Entrena Holt-Winters sobre el histórico mensual de:
    Ingreso fijo, Ingreso vario, Egreso fijo o Egreso vario.

    Guarda en la tabla PREDICCION tanto los valores ajustados
    en el rango histórico (backtesting) como el pronóstico real
    para los meses futuros.
    """

    def __init__(
        self,
        movimiento_repo: MovimientoRepository,
        prediccion_repo: PrediccionRepository,
    ):
        self.movimiento_repo = movimiento_repo
        self.prediccion_repo = prediccion_repo

    async def recalcular(
        self,
        *,
        clasificacion: ClasificacionPrediccion,
        ano_inicial: str = ANO_INICIAL_DEFECTO,
        mes_inicial: str = MES_INICIAL_DEFECTO,
        ano_final: str = ANO_FINAL_DEFECTO,
        mes_final: str = MES_FINAL_DEFECTO,
    ) -> RecalculoPrediccionOut:

        # Ingresos: se buscan mediante TIPO_INGRESO.
        if clasificacion in TIPOS_INGRESO_PREDICCION:
            filas = await self.movimiento_repo.historico_por_tipo_ingreso(
                tipo_ingreso=clasificacion
            )

        # Egresos: se buscan mediante TIPO_EGRESO.
        elif clasificacion in TIPOS_EGRESO_PREDICCION:
            filas = await self.movimiento_repo.historico_por_tipo_egreso(
                tipo_egreso=clasificacion
            )

        else:
            raise ValueError(
                f'Clasificación de predicción no soportada: "{clasificacion}"'
            )

        if not filas:
            raise ValueError(
                f'No hay movimientos históricos para "{clasificacion}"'
            )

        historico = sorted(
            (
                {
                    "ano": f["ano"],
                    "mes": f["mes"],
                    "total": f["total"],
                }
                for f in filas
            ),
            key=lambda f: int(f["ano"]) * 12 + MESES_ORDEN.index(f["mes"]),
        )

        valores = [h["total"] for h in historico]

        ultimo_ano = historico[-1]["ano"]
        ultimo_mes = historico[-1]["mes"]

        clave_ultimo = (
            int(ultimo_ano) * 12
            + MESES_ORDEN.index(ultimo_mes)
        )

        clave_final = (
            int(ano_final) * 12
            + MESES_ORDEN.index(mes_final)
        )

        horizonte = max(0, clave_final - clave_ultimo)

        ajustados, pronosticados = self._entrenar(
            valores,
            horizonte=horizonte,
        )

        # Mapa (ano, mes) -> valor:
        # ajustado para el histórico y pronosticado para el futuro.
        mapa_valores = {
            (h["ano"], h["mes"]): ajustados[i]
            for i, h in enumerate(historico)
        }

        ano_f, mes_f = ultimo_ano, ultimo_mes

        for valor in pronosticados:
            ano_f, mes_f = _mes_siguiente(ano_f, mes_f)
            mapa_valores[(ano_f, mes_f)] = valor

        periodos = _rango_periodos(
            ano_inicial,
            mes_inicial,
            ano_final,
            mes_final,
        )

        predicciones = [
            PrediccionMes(
                ano=ano,
                mes=mes,
                valor_predicho=round(
                    mapa_valores[(ano, mes)],
                    2,
                ),
            )
            for ano, mes in periodos
            if (ano, mes) in mapa_valores
        ]

        await self.prediccion_repo.reemplazar_predicciones(
            clasificacion=clasificacion,
            predicciones=[
                p.model_dump()
                for p in predicciones
            ],
        )

        return RecalculoPrediccionOut(
            clasificacion=clasificacion,
            meses_historicos_usados=len(historico),
            predicciones_generadas=len(predicciones),
            predicciones=predicciones,
        )

    async def obtener(
        self,
        *,
        clasificacion: ClasificacionPrediccion,
        ano: str | None = None,
    ) -> list[PrediccionMes]:

        registros = await self.prediccion_repo.listar_por_clasificacion(
            clasificacion=clasificacion,
            ano=ano,
        )

        ordenados = sorted(
            registros,
            key=lambda r: int(r.ano) * 12 + MESES_ORDEN.index(r.mes),
        )

        return [
            PrediccionMes(
                ano=r.ano,
                mes=r.mes,
                valor_predicho=r.valor_predicho,
            )
            for r in ordenados
        ]

    @staticmethod
    def _entrenar(
        valores: list[float],
        *,
        horizonte: int,
    ) -> tuple[list[float], list[float]]:
        """Ajusta Holt-Winters y devuelve:

        - valores ajustados in-sample
        - pronóstico out-of-sample

        Usa una proyección lineal simple como respaldo
        si el ajuste falla.
        """

        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            usar_estacionalidad = len(valores) >= 24

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                modelo = ExponentialSmoothing(
                    valores,
                    trend="add",
                    seasonal="add" if usar_estacionalidad else None,
                    seasonal_periods=12 if usar_estacionalidad else None,
                    initialization_method="estimated",
                )

                ajuste = modelo.fit()

            ajustados = [
                max(0.0, float(v))
                for v in ajuste.fittedvalues
            ]

            pronosticados = (
                [
                    max(0.0, float(v))
                    for v in ajuste.forecast(horizonte)
                ]
                if horizonte
                else []
            )

            return ajustados, pronosticados

        except Exception:
            return PrediccionService._proyeccion_lineal_simple(
                valores,
                horizonte=horizonte,
            )

    @staticmethod
    def _proyeccion_lineal_simple(
        valores: list[float],
        *,
        horizonte: int,
    ) -> tuple[list[float], list[float]]:
        """Respaldo cuando Holt-Winters no se puede ajustar."""

        n = len(valores)

        if n < 2:
            valor_constante = valores[-1] if valores else 0.0

            return (
                [valor_constante] * n,
                [valor_constante] * horizonte,
            )

        x = list(range(n))

        promedio_x = sum(x) / n
        promedio_y = sum(valores) / n

        numerador = sum(
            (xi - promedio_x) * (yi - promedio_y)
            for xi, yi in zip(x, valores)
        )

        denominador = (
            sum(
                (xi - promedio_x) ** 2
                for xi in x
            )
            or 1.0
        )

        pendiente = numerador / denominador
        intercepto = promedio_y - pendiente * promedio_x

        ajustados = [
            max(
                0.0,
                intercepto + pendiente * xi,
            )
            for xi in x
        ]

        pronosticados = [
            max(
                0.0,
                intercepto + pendiente * (n + i),
            )
            for i in range(horizonte)
        ]

        return ajustados, pronosticados
