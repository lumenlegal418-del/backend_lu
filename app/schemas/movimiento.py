from pydantic import BaseModel, ConfigDict


class MovimientoOut(BaseModel):
    id: int
    debito: float | None = None
    credito: float | None = None
    total: float | None = None
    mes: str | None = None
    ano: str | None = None
    clasificacion: str | None = None
    tipo_ingreso: str | None = None
    tipo_egreso: str | None = None
    tercero: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DetalleMovimiento(BaseModel):
    ano: str | None = None
    mes: str | None = None
    nit: str | None = None
    nombre_tercero: str | None = None
    detalle: str | None = None
    nombre_cuenta: str | None = None
    codigo: str | None = None
    documento: str | None = None
    debitos: float | None = None
    creditos: float | None = None
    total: float | None = None


class ResumenGeneral(BaseModel):
    """Totales agregados de un conjunto de movimientos."""

    total_debito: float
    total_credito: float
    total_neto: float
    cantidad_movimientos: int
    promedio_total: float


class SerieMensual(BaseModel):
    mes: str
    ano: str
    total_debito: float
    total_credito: float
    total_neto: float


class TotalPorCategoria(BaseModel):
    categoria: str
    total: float


class RegistroPeriodo(BaseModel):
    cliente: str | None = None
    nit: str | None = None
    documento: str | None = None
    mes: str
    ano: str
    total: float


class ArchivoInfo(BaseModel):
    nombre_archivo: str
    ano_archivo: str
    meses: list[str]


class ComposicionTipoEgreso(BaseModel):
    tipo_egreso: str
    monto: float
    porcentaje: float


class ComposicionEgresos(BaseModel):
    ano: str
    mes: str
    total_egresos: float
    composicion: list[ComposicionTipoEgreso]


class ComposicionCuentaEgreso(BaseModel):
    nombre_cuenta: str
    monto: float
    porcentaje: float


class ComposicionEgresosFijos(BaseModel):
    ano: str
    mes: str
    total_egresos_fijos: float
    composicion: list[ComposicionCuentaEgreso]


class ComposicionEgresosVarios(BaseModel):
    ano: str
    mes: str
    total_egresos_varios: float
    composicion: list[ComposicionCuentaEgreso]


class PesoCliente(BaseModel):
    cliente: str
    total_cliente: float
    peso_porcentual: float


class PesoClientes(BaseModel):
    ano: str
    mes: str
    total_general: float
    clientes: list[PesoCliente]


class ImportanciaClientesAnual(BaseModel):
    ano: str
    total_general: float
    clientes: list[PesoCliente]


class ResumenIngresos(BaseModel):
    ano: str
    mes: str
    ingresos_mes: float
    incremento_ingresos_mes_anterior: float | str
    porcentaje_incremento_mes_anterior: float | str
    incremento_ingresos_ano_anterior: float | str
    porcentaje_incremento_ano_anterior: float | str
    ingreso_mes_acumulado: float
    incremento_acumulado_ano_anterior: float | str
    porcentaje_incremento_acumulado_ano_anterior: float | str


class ResumenEgresos(BaseModel):
    ano: str
    mes: str
    egresos_mes: float
    incremento_egresos_mes_anterior: float | str
    porcentaje_incremento_mes_anterior: float | str
    incremento_egresos_ano_anterior: float | str
    porcentaje_incremento_ano_anterior: float | str
    egreso_mes_acumulado: float
    incremento_acumulado_ano_anterior: float | str
    porcentaje_incremento_acumulado_ano_anterior: float | str
