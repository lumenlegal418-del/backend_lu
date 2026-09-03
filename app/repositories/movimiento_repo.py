from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import (
    Ano,
    Clasificacion,
    ClasificacionNombreCuenta,
    Documento,
    Mes,
    NombreArchivo,
    Terceros,
    TipoEgreso,
    TipoIngreso,
)
from app.models.movimiento import MovimientoContable


class MovimientoRepository:
    """Acceso a datos de MOVIMIENTO_CONTABLE. Los cálculos SQL (SUM/AVG) se hacen en la BD."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar(
        self,
        *,
        ano: str | None = None,
        mes: str | None = None,
        clasificacion: str | None = None,
        nombre_documento: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MovimientoContable]:
        query = select(MovimientoContable)
        query = self._aplicar_filtros(
            query, ano=ano, mes=mes, clasificacion=clasificacion, nombre_documento=nombre_documento
        )
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def resumen_totales(
        self,
        *,
        ano: str | None = None,
        mes: str | None = None,
        clasificacion: str | None = None,
    ) -> dict:
        query = select(
            func.coalesce(func.sum(MovimientoContable.debito), 0).label("total_debito"),
            func.coalesce(func.sum(MovimientoContable.credito), 0).label("total_credito"),
            func.coalesce(func.sum(MovimientoContable.total), 0).label("total_neto"),
            func.count(MovimientoContable.id).label("cantidad"),
            func.coalesce(func.avg(MovimientoContable.total), 0).label("promedio_total"),
        )
        query = self._aplicar_filtros(query, ano=ano, mes=mes, clasificacion=clasificacion)
        result = await self.db.execute(query)
        return result.mappings().one()

    async def totales_por_mes(self, *, ano: str | None = None) -> list:
        query = (
            select(
                Mes.mes.label("mes"),
                Ano.ano.label("ano"),
                func.coalesce(func.sum(MovimientoContable.debito), 0).label("total_debito"),
                func.coalesce(func.sum(MovimientoContable.credito), 0).label("total_credito"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total_neto"),
            )
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .group_by(Mes.mes, Ano.ano)
            .order_by(Ano.ano, Mes.mes)
        )
        if ano:
            query = query.where(Ano.ano == ano)
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def totales_por_mes_ingresos_por_tipo(
        self, *, clasificaciones: list[str], ano: str, tipo_ingreso: str
    ) -> list:
        """Suma TOTAL agrupado por mes, para un conjunto de clasificaciones y un TIPO_INGRESO puntual."""
        query = (
            select(
                Mes.mes.label("mes"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(TipoIngreso, MovimientoContable.id_tipo_ingreso == TipoIngreso.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(TipoIngreso.tipo_ingreso == tipo_ingreso)
            .where(Ano.ano == ano)
            .group_by(Mes.mes)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def totales_por_mes_egresos_por_tipo(
        self, *, clasificaciones: list[str], ano: str, tipo_egreso: str
    ) -> list:
        """Suma TOTAL agrupado por mes, para un conjunto de clasificaciones y un TIPO_EGRESO puntual."""
        query = (
            select(
                Mes.mes.label("mes"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(TipoEgreso, MovimientoContable.id_tipo_egreso == TipoEgreso.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(TipoEgreso.tipo_egreso == tipo_egreso)
            .where(Ano.ano == ano)
            .group_by(Mes.mes)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def totales_por_tipo_egreso(
        self, *, clasificaciones: list[str], ano: str, mes: str
    ) -> list:
        """Suma TOTAL agrupado por TIPO_EGRESO, para un conjunto de clasificaciones, en un año y mes dados."""
        query = (
            select(
                TipoEgreso.tipo_egreso.label("tipo_egreso"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(TipoEgreso, MovimientoContable.id_tipo_egreso == TipoEgreso.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Ano.ano == ano)
            .where(Mes.mes == mes)
            .group_by(TipoEgreso.tipo_egreso)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def totales_por_cuenta_para_tipo_egreso(
        self, *, clasificaciones: list[str], tipo_egreso: str, ano: str, mes: str
    ) -> list:
        """Suma TOTAL agrupado por CLASIFICACION_NOMBRE_CUENTA, para egresos de un tipo puntual
        (ej. "Egreso fijo"), en un año y mes dados."""
        query = (
            select(
                ClasificacionNombreCuenta.clasificacion_nombre_cuenta.label("nombre_cuenta"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(TipoEgreso, MovimientoContable.id_tipo_egreso == TipoEgreso.id)
            .join(
                ClasificacionNombreCuenta,
                MovimientoContable.id_clasificacion_nombre_cuenta == ClasificacionNombreCuenta.id,
            )
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(TipoEgreso.tipo_egreso == tipo_egreso)
            .where(Ano.ano == ano)
            .where(Mes.mes == mes)
            .group_by(ClasificacionNombreCuenta.clasificacion_nombre_cuenta)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def totales_por_cliente(
        self, *, clasificaciones: list[str], ano: str, mes: str | None = None
    ) -> list:
        """Suma TOTAL agrupado por TERCEROS (cliente), para un conjunto de clasificaciones
        (ej. ingresos), en un año dado. Si se pasa mes, filtra también por ese mes puntual."""
        query = (
            select(
                Terceros.nombre_tercero.label("cliente"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(Terceros, MovimientoContable.id_terceros == Terceros.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Ano.ano == ano)
            .group_by(Terceros.nombre_tercero)
        )
        if mes is not None:
            query = query.join(Mes, MovimientoContable.id_mes == Mes.id).where(Mes.mes == mes)
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def listar_clientes(self, *, clasificaciones: list[str]) -> list[str]:
        """Nombres de TERCEROS (clientes) distintos que tengan movimientos con alguna
        de las clasificaciones dadas (ej. ingresos)."""
        query = (
            select(Terceros.nombre_tercero)
            .join(MovimientoContable, MovimientoContable.id_terceros == Terceros.id)
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Terceros.nombre_tercero.isnot(None))
            .distinct()
            .order_by(Terceros.nombre_tercero)
        )
        result = await self.db.execute(query)
        return [nombre for (nombre,) in result.all()]

    async def listar_nits(self, *, clasificaciones: list[str]) -> list[str]:
        """NIT (TERCEROS.nit) distintos que tengan movimientos con alguna de las
        clasificaciones dadas (ej. ingresos)."""
        query = (
            select(Terceros.nit)
            .join(MovimientoContable, MovimientoContable.id_terceros == Terceros.id)
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Terceros.nit.isnot(None))
            .distinct()
            .order_by(Terceros.nit)
        )
        result = await self.db.execute(query)
        return [nit for (nit,) in result.all()]

    async def listar_documentos(self, *, clasificaciones: list[str]) -> list[str]:
        """Nombres de DOCUMENTO distintos que tengan movimientos con alguna de las
        clasificaciones dadas (ej. ingresos)."""
        query = (
            select(Documento.nombre_documento)
            .join(MovimientoContable, MovimientoContable.id_documento == Documento.id)
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Documento.nombre_documento.isnot(None))
            .distinct()
            .order_by(Documento.nombre_documento)
        )
        result = await self.db.execute(query)
        return [nombre for (nombre,) in result.all()]

    async def registros_por_periodo(
        self,
        *,
        periodos: list[tuple[str, str]],
        cliente: str | None = None,
        nit: str | None = None,
        documento: str | None = None,
    ) -> list:
        """Suma TOTAL agrupado por cliente/nit/documento/mes/año, restringido a un conjunto
        puntual de pares (año, mes) -es decir, un rango de fechas ya expandido-, con filtros
        opcionales de cliente, nit y documento."""
        query = (
            select(
                Terceros.nombre_tercero.label("cliente"),
                Terceros.nit.label("nit"),
                Documento.nombre_documento.label("documento"),
                Mes.mes.label("mes"),
                Ano.ano.label("ano"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Terceros, MovimientoContable.id_terceros == Terceros.id)
            .join(Documento, MovimientoContable.id_documento == Documento.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .where(tuple_(Ano.ano, Mes.mes).in_(periodos))
            .group_by(Terceros.nombre_tercero, Terceros.nit, Documento.nombre_documento, Mes.mes, Ano.ano)
            .order_by(Ano.ano, Mes.mes, Terceros.nombre_tercero)
        )
        if cliente:
            query = query.where(Terceros.nombre_tercero == cliente)
        if nit:
            query = query.where(Terceros.nit == nit)
        if documento:
            query = query.where(Documento.nombre_documento == documento)
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def listar_archivos_meses(self) -> list:
        """Ternas distintas (nombre_archivo, año, mes) presentes en MOVIMIENTO_CONTABLE."""
        query = (
            select(
                NombreArchivo.nombre_archivo.label("nombre_archivo"),
                Ano.ano.label("ano"),
                Mes.mes.label("mes"),
            )
            .join(MovimientoContable, MovimientoContable.id_nombre_archivo == NombreArchivo.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(NombreArchivo.nombre_archivo.isnot(None))
            .distinct()
            .order_by(NombreArchivo.nombre_archivo, Ano.ano, Mes.mes)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def historico_por_clasificacion(self, *, clasificacion: str) -> list:
        """Suma TOTAL agrupado por año y mes, para una clasificación puntual, en TODOS los
        años disponibles (histórico completo, insumo para el modelo de predicción)."""
        query = (
            select(
                Ano.ano.label("ano"),
                Mes.mes.label("mes"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion == clasificacion)
            .group_by(Ano.ano, Mes.mes)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def historico_por_tipo_ingreso(self, *, tipo_ingreso: str) -> list:
        """Suma TOTAL agrupado por año y mes, para un TIPO_INGRESO puntual (Ingreso fijo o
        Ingreso vario), en TODOS los años disponibles (insumo para el modelo de predicción)."""
        query = (
            select(
                Ano.ano.label("ano"),
                Mes.mes.label("mes"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(TipoIngreso, MovimientoContable.id_tipo_ingreso == TipoIngreso.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(TipoIngreso.tipo_ingreso == tipo_ingreso)
            .group_by(Ano.ano, Mes.mes)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def totales_por_mes_para_clasificaciones(self, *, clasificaciones: list[str], ano: str) -> list:
        """Suma TOTAL agrupado por mes, para un conjunto de clasificaciones, en un año dado."""
        query = (
            select(
                Mes.mes.label("mes"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Ano.ano == ano)
            .group_by(Mes.mes)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    async def total_por_clasificaciones(
        self,
        *,
        clasificaciones: list[str],
        ano: str,
        mes: str | None = None,
        meses: list[str] | None = None,
    ) -> tuple[float, int]:
        """Suma TOTAL y cuenta movimientos para un conjunto de clasificaciones (ej. ingresos),
        dado un año y un mes puntual (mes) o un conjunto de meses (meses, para acumulados).
        Retorna (total, cantidad) para poder distinguir "sin registros" de un total real en 0.
        """
        query = (
            select(
                func.coalesce(func.sum(MovimientoContable.total), 0),
                func.count(MovimientoContable.id),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .join(Ano, MovimientoContable.id_ano == Ano.id)
            .join(Mes, MovimientoContable.id_mes == Mes.id)
            .where(Clasificacion.clasificacion.in_(clasificaciones))
            .where(Ano.ano == ano)
        )
        if mes is not None:
            query = query.where(Mes.mes == mes)
        elif meses is not None:
            query = query.where(Mes.mes.in_(meses))
        result = await self.db.execute(query)
        total, cantidad = result.one()
        return total, cantidad

    async def totales_por_clasificacion(self) -> list:
        query = (
            select(
                Clasificacion.clasificacion.label("categoria"),
                func.coalesce(func.sum(MovimientoContable.total), 0).label("total"),
            )
            .join(Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id)
            .group_by(Clasificacion.clasificacion)
            .order_by(Clasificacion.clasificacion)
        )
        result = await self.db.execute(query)
        return list(result.mappings().all())

    @staticmethod
    def _aplicar_filtros(
        query,
        *,
        ano: str | None,
        mes: str | None,
        clasificacion: str | None,
        nombre_documento: str | None = None,
    ):
        if ano:
            query = query.join(Ano, MovimientoContable.id_ano == Ano.id).where(Ano.ano == ano)
        if mes:
            query = query.join(Mes, MovimientoContable.id_mes == Mes.id).where(Mes.mes == mes)
        if clasificacion:
            query = query.join(
                Clasificacion, MovimientoContable.id_clasificacion == Clasificacion.id
            ).where(Clasificacion.clasificacion == clasificacion)
        if nombre_documento:
            query = query.join(
                Documento, MovimientoContable.id_documento == Documento.id
            ).where(Documento.nombre_documento == nombre_documento)
        return query
