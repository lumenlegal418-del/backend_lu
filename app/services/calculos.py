from typing import Literal

from app.repositories.movimiento_repo import MovimientoRepository
from app.schemas.movimiento import (
    ComposicionCuentaEgreso,
    ComposicionEgresos,
    ComposicionEgresosFijos,
    ComposicionEgresosVarios,
    ComposicionTipoEgreso,
    PesoCliente,
    PesoClientes,
    ImportanciaClientesAnual,
    RegistroPeriodo,
    ResumenEgresos,
    ResumenGeneral,
    ResumenIngresos,
    SerieMensual,
    TotalPorCategoria,
)

# Valores exactos tal como están en la tabla CLASIFICACION
CLASIFICACIONES_INGRESO = ["INGRESO OPERACIONAL", "INGRESO NO OPERACIONAL"]
CLASIFICACIONES_EGRESO = ["COSTOS", "GASTOS"]
ClasificacionValida = Literal["COSTOS", "GASTOS", "INGRESO OPERACIONAL", "INGRESO NO OPERACIONAL"]

# Valores exactos tal como están en las tablas TIPO_INGRESO / TIPO_EGRESO
TipoIngresoValido = Literal["Ingreso fijo", "Ingreso vario"]
TipoEgresoValido = Literal["Egreso fijo", "Egreso variable"]
TIPOS_EGRESO = ["Egreso fijo", "Egreso variable"]

SIN_REGISTRO = "Sin registro"

MESES_ORDEN = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _mes_anterior(ano: str, mes: str) -> tuple[str, str]:
    idx = MESES_ORDEN.index(mes)
    if idx == 0:
        return str(int(ano) - 1), MESES_ORDEN[-1]
    return ano, MESES_ORDEN[idx - 1]


def _mes_siguiente(ano: str, mes: str) -> tuple[str, str]:
    idx = MESES_ORDEN.index(mes)
    if idx == len(MESES_ORDEN) - 1:
        return str(int(ano) + 1), MESES_ORDEN[0]
    return ano, MESES_ORDEN[idx + 1]


def _rango_periodos(ano_inicial: str, mes_inicial: str, ano_final: str, mes_final: str) -> list[tuple[str, str]]:
    """Expande un rango [ano_inicial/mes_inicial, ano_final/mes_final] en la lista de pares
    (ano, mes) que contiene, mes a mes."""
    clave_inicio = int(ano_inicial) * 12 + MESES_ORDEN.index(mes_inicial)
    clave_fin = int(ano_final) * 12 + MESES_ORDEN.index(mes_final)
    if clave_fin < clave_inicio:
        raise ValueError("El periodo final no puede ser anterior al periodo inicial")
    return [(str(clave // 12), MESES_ORDEN[clave % 12]) for clave in range(clave_inicio, clave_fin + 1)]


def _variacion(actual: float, anterior: float | None) -> tuple[float | str, float | str]:
    """Calcula (diferencia, % diferencia) contra un periodo anterior, o SIN_REGISTRO si no hay dato."""
    if anterior is None:
        return SIN_REGISTRO, SIN_REGISTRO
    diferencia = round(actual - anterior, 2)
    if anterior == 0:
        return diferencia, SIN_REGISTRO
    porcentaje = round((diferencia / anterior) * 100, 2)
    return diferencia, porcentaje


class CalculosService:
    """Lógica de negocio/cálculos derivados sobre los movimientos contables.

    Las agregaciones simples (SUM/AVG/COUNT) se delegan a Postgres vía el repositorio;
    aquí solo se arma la respuesta y se hacen cálculos que combinan varios valores.
    """

    def __init__(self, repo: MovimientoRepository):
        self.repo = repo

    async def resumen_general(
        self, *, ano: str | None = None, mes: str | None = None, clasificacion: str | None = None
    ) -> ResumenGeneral:
        row = await self.repo.resumen_totales(ano=ano, mes=mes, clasificacion=clasificacion)
        return ResumenGeneral(
            total_debito=row["total_debito"],
            total_credito=row["total_credito"],
            total_neto=row["total_neto"],
            cantidad_movimientos=row["cantidad"],
            promedio_total=round(row["promedio_total"], 2),
        )

    async def serie_mensual(self, *, ano: str | None = None) -> list[SerieMensual]:
        filas = await self.repo.totales_por_mes(ano=ano)
        return [
            SerieMensual(
                mes=f["mes"],
                ano=f["ano"],
                total_debito=f["total_debito"],
                total_credito=f["total_credito"],
                total_neto=f["total_neto"],
            )
            for f in filas
        ]

    async def totales_por_clasificacion(self) -> list[TotalPorCategoria]:
        filas = await self.repo.totales_por_clasificacion()
        return [TotalPorCategoria(categoria=f["categoria"], total=f["total"]) for f in filas]

    async def total_por_clasificacion_anual(self, *, ano: str, clasificacion: ClasificacionValida) -> dict[str, float]:
        """Suma TOTAL por cada mes del año, para una única clasificación (COSTOS, GASTOS,
        INGRESO OPERACIONAL o INGRESO NO OPERACIONAL). Devuelve {mes: total} con los 12 meses."""
        return await self._registro_por_mes(clasificaciones=[clasificacion], ano=ano)

    async def resumen_ingresos(self, *, ano: str, mes: str) -> ResumenIngresos:
        valores = await self._calcular_resumen(clasificaciones=CLASIFICACIONES_INGRESO, ano=ano, mes=mes)
        return ResumenIngresos(
            ano=ano,
            mes=mes,
            ingresos_mes=valores["total_mes"],
            incremento_ingresos_mes_anterior=valores["incremento_mes_anterior"],
            porcentaje_incremento_mes_anterior=valores["pct_incremento_mes_anterior"],
            incremento_ingresos_ano_anterior=valores["incremento_ano_anterior"],
            porcentaje_incremento_ano_anterior=valores["pct_incremento_ano_anterior"],
            ingreso_mes_acumulado=valores["total_acumulado"],
            incremento_acumulado_ano_anterior=valores["incremento_acumulado_ano_anterior"],
            porcentaje_incremento_acumulado_ano_anterior=valores["pct_incremento_acumulado_ano_anterior"],
        )

    async def resumen_egresos(self, *, ano: str, mes: str) -> ResumenEgresos:
        valores = await self._calcular_resumen(clasificaciones=CLASIFICACIONES_EGRESO, ano=ano, mes=mes)
        return ResumenEgresos(
            ano=ano,
            mes=mes,
            egresos_mes=valores["total_mes"],
            incremento_egresos_mes_anterior=valores["incremento_mes_anterior"],
            porcentaje_incremento_mes_anterior=valores["pct_incremento_mes_anterior"],
            incremento_egresos_ano_anterior=valores["incremento_ano_anterior"],
            porcentaje_incremento_ano_anterior=valores["pct_incremento_ano_anterior"],
            egreso_mes_acumulado=valores["total_acumulado"],
            incremento_acumulado_ano_anterior=valores["incremento_acumulado_ano_anterior"],
            porcentaje_incremento_acumulado_ano_anterior=valores["pct_incremento_acumulado_ano_anterior"],
        )

    async def registro_ingresos(self, *, ano: str) -> dict[str, float]:
        return await self._registro_por_mes(clasificaciones=CLASIFICACIONES_INGRESO, ano=ano)

    async def registro_egresos(self, *, ano: str) -> dict[str, float]:
        return await self._registro_por_mes(clasificaciones=CLASIFICACIONES_EGRESO, ano=ano)

    async def registro_ingresos_acumulado(self, *, ano: str) -> dict[str, float]:
        return self._acumular_por_mes(await self.registro_ingresos(ano=ano))

    async def registro_egresos_acumulado(self, *, ano: str) -> dict[str, float]:
        return self._acumular_por_mes(await self.registro_egresos(ano=ano))

    async def registro_ingresos_por_tipo(self, *, ano: str, tipo_ingreso: TipoIngresoValido) -> dict[str, float]:
        filas = await self.repo.totales_por_mes_ingresos_por_tipo(
            clasificaciones=CLASIFICACIONES_INGRESO, ano=ano, tipo_ingreso=tipo_ingreso
        )
        totales_por_mes = {f["mes"]: round(f["total"], 2) for f in filas}
        return {mes: totales_por_mes.get(mes, 0.0) for mes in MESES_ORDEN}

    async def registro_egresos_por_tipo(self, *, ano: str, tipo_egreso: TipoEgresoValido) -> dict[str, float]:
        filas = await self.repo.totales_por_mes_egresos_por_tipo(
            clasificaciones=CLASIFICACIONES_EGRESO, ano=ano, tipo_egreso=tipo_egreso
        )
        totales_por_mes = {f["mes"]: round(f["total"], 2) for f in filas}
        return {mes: totales_por_mes.get(mes, 0.0) for mes in MESES_ORDEN}

    async def composicion_egresos(self, *, ano: str, mes: str) -> ComposicionEgresos:
        """Qué tanto pesan Egreso fijo / Egreso variable (en plata y %) dentro del total de egresos
        (COSTOS + GASTOS) de un año y mes dados."""
        filas = await self.repo.totales_por_tipo_egreso(clasificaciones=CLASIFICACIONES_EGRESO, ano=ano, mes=mes)
        montos = {f["tipo_egreso"]: round(f["total"], 2) for f in filas}

        total_egresos = round(sum(montos.get(tipo, 0.0) for tipo in TIPOS_EGRESO), 2)
        composicion = [
            ComposicionTipoEgreso(
                tipo_egreso=tipo,
                monto=montos.get(tipo, 0.0),
                porcentaje=round((montos.get(tipo, 0.0) / total_egresos) * 100, 2) if total_egresos else 0.0,
            )
            for tipo in TIPOS_EGRESO
        ]
        return ComposicionEgresos(ano=ano, mes=mes, total_egresos=total_egresos, composicion=composicion)

    async def composicion_egresos_fijos(self, *, ano: str, mes: str) -> ComposicionEgresosFijos:
        """Qué tanto pesa cada cuenta (CLASIFICACION_NOMBRE_CUENTA) dentro de los egresos fijos
        (COSTOS + GASTOS, TIPO_EGRESO = "Egreso fijo") de un año y mes dados."""
        filas = await self.repo.totales_por_cuenta_para_tipo_egreso(
            clasificaciones=CLASIFICACIONES_EGRESO, tipo_egreso="Egreso fijo", ano=ano, mes=mes
        )
        total_egresos_fijos = round(sum(f["total"] for f in filas), 2)
        composicion = [
            ComposicionCuentaEgreso(
                nombre_cuenta=f["nombre_cuenta"],
                monto=round(f["total"], 2),
                porcentaje=round((f["total"] / total_egresos_fijos) * 100, 2) if total_egresos_fijos else 0.0,
            )
            for f in filas
        ]
        return ComposicionEgresosFijos(
            ano=ano, mes=mes, total_egresos_fijos=total_egresos_fijos, composicion=composicion
        )

    async def composicion_egresos_varios(self, *, ano: str, mes: str) -> ComposicionEgresosVarios:
        """Qué tanto pesa cada cuenta (CLASIFICACION_NOMBRE_CUENTA) dentro de los egresos varios
        (COSTOS + GASTOS, TIPO_EGRESO = "Egreso variable") de un año y mes dados."""
        filas = await self.repo.totales_por_cuenta_para_tipo_egreso(
            clasificaciones=CLASIFICACIONES_EGRESO, tipo_egreso="Egreso variable", ano=ano, mes=mes
        )
        total_egresos_varios = round(sum(f["total"] for f in filas), 2)
        composicion = [
            ComposicionCuentaEgreso(
                nombre_cuenta=f["nombre_cuenta"],
                monto=round(f["total"], 2),
                porcentaje=round((f["total"] / total_egresos_varios) * 100, 2) if total_egresos_varios else 0.0,
            )
            for f in filas
        ]
        return ComposicionEgresosVarios(
            ano=ano, mes=mes, total_egresos_varios=total_egresos_varios, composicion=composicion
        )

    async def peso_clientes(self, *, ano: str, mes: str) -> PesoClientes:
        """Qué tanto pesa cada cliente (TERCEROS) dentro del total de ingresos
        (INGRESO OPERACIONAL + INGRESO NO OPERACIONAL) de un año y mes dados."""
        total_general, clientes = await self._peso_clientes(ano=ano, mes=mes)
        return PesoClientes(ano=ano, mes=mes, total_general=total_general, clientes=clientes)

    async def importancia_clientes_anual(self, *, ano: str) -> ImportanciaClientesAnual:
        """Igual que peso_clientes, pero acumulando todo el año (sin filtro de mes),
        para graficar la importancia de cada cliente en el año completo."""
        total_general, clientes = await self._peso_clientes(ano=ano)
        return ImportanciaClientesAnual(ano=ano, total_general=total_general, clientes=clientes)

    async def registros_por_periodo(
        self,
        *,
        ano_inicial: str,
        mes_inicial: str,
        ano_final: str,
        mes_final: str,
        cliente: str | None = None,
        nit: str | None = None,
        documento: str | None = None,
    ) -> list[RegistroPeriodo]:
        """Suma TOTAL agrupado por cliente/nit/documento/mes/año, dentro de un rango de fechas
        (año/mes inicial - año/mes final), con filtros opcionales de cliente, nit y documento."""
        periodos = _rango_periodos(ano_inicial, mes_inicial, ano_final, mes_final)
        filas = await self.repo.registros_por_periodo(
            periodos=periodos, cliente=cliente, nit=nit, documento=documento
        )
        return [
            RegistroPeriodo(
                cliente=f["cliente"],
                nit=f["nit"],
                documento=f["documento"],
                mes=f["mes"],
                ano=f["ano"],
                total=round(f["total"], 2),
            )
            for f in filas
        ]

    async def _peso_clientes(self, *, ano: str, mes: str | None = None) -> tuple[float, list[PesoCliente]]:
        filas = await self.repo.totales_por_cliente(clasificaciones=CLASIFICACIONES_INGRESO, ano=ano, mes=mes)
        total_general = round(sum(f["total"] for f in filas), 2)
        clientes = [
            PesoCliente(
                cliente=f["cliente"],
                total_cliente=round(f["total"], 2),
                peso_porcentual=round((f["total"] / total_general) * 100, 2) if total_general else 0.0,
            )
            for f in filas
        ]
        return total_general, clientes

    @staticmethod
    def _acumular_por_mes(totales_por_mes: dict[str, float]) -> dict[str, float]:
        """Convierte {mes: total} en {mes: acumulado desde Enero hasta ese mes}."""
        acumulado = 0.0
        resultado = {}
        for mes in MESES_ORDEN:
            acumulado = round(acumulado + totales_por_mes[mes], 2)
            resultado[mes] = acumulado
        return resultado

    async def _registro_por_mes(self, *, clasificaciones: list[str], ano: str) -> dict[str, float]:
        """Suma TOTAL por cada mes del año para las clasificaciones dadas, en formato {mes: total}.
        Incluye los 12 meses aunque no tengan movimientos (total 0)."""
        filas = await self.repo.totales_por_mes_para_clasificaciones(clasificaciones=clasificaciones, ano=ano)
        totales_por_mes = {f["mes"]: round(f["total"], 2) for f in filas}
        return {mes: totales_por_mes.get(mes, 0.0) for mes in MESES_ORDEN}

    async def _calcular_resumen(self, *, clasificaciones: list[str], ano: str, mes: str) -> dict:
        """Lógica compartida entre resumen_ingresos y resumen_egresos: total del mes, variación
        vs. mes anterior, variación vs. mismo mes del año anterior y acumulado del año."""
        total_mes, _ = await self.repo.total_por_clasificaciones(
            clasificaciones=clasificaciones, ano=ano, mes=mes
        )
        total_mes = round(total_mes, 2)

        ano_prev, mes_prev = _mes_anterior(ano, mes)
        total_mes_anterior, cantidad_mes_anterior = await self.repo.total_por_clasificaciones(
            clasificaciones=clasificaciones, ano=ano_prev, mes=mes_prev
        )
        incremento_mes_anterior, pct_incremento_mes_anterior = _variacion(
            total_mes, total_mes_anterior if cantidad_mes_anterior > 0 else None
        )

        ano_anterior = str(int(ano) - 1)
        total_ano_anterior, cantidad_ano_anterior = await self.repo.total_por_clasificaciones(
            clasificaciones=clasificaciones, ano=ano_anterior, mes=mes
        )
        incremento_ano_anterior, pct_incremento_ano_anterior = _variacion(
            total_mes, total_ano_anterior if cantidad_ano_anterior > 0 else None
        )

        meses_hasta_actual = MESES_ORDEN[: MESES_ORDEN.index(mes) + 1]
        total_acumulado, _ = await self.repo.total_por_clasificaciones(
            clasificaciones=clasificaciones, ano=ano, meses=meses_hasta_actual
        )
        total_acumulado = round(total_acumulado, 2)

        total_acumulado_ano_anterior, cantidad_acumulado_ano_anterior = await self.repo.total_por_clasificaciones(
            clasificaciones=clasificaciones, ano=ano_anterior, meses=meses_hasta_actual
        )
        incremento_acumulado_ano_anterior, pct_incremento_acumulado_ano_anterior = _variacion(
            total_acumulado, total_acumulado_ano_anterior if cantidad_acumulado_ano_anterior > 0 else None
        )

        return {
            "total_mes": total_mes,
            "incremento_mes_anterior": incremento_mes_anterior,
            "pct_incremento_mes_anterior": pct_incremento_mes_anterior,
            "incremento_ano_anterior": incremento_ano_anterior,
            "pct_incremento_ano_anterior": pct_incremento_ano_anterior,
            "total_acumulado": total_acumulado,
            "incremento_acumulado_ano_anterior": incremento_acumulado_ano_anterior,
            "pct_incremento_acumulado_ano_anterior": pct_incremento_acumulado_ano_anterior,
        }
