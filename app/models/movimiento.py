from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.catalogos import (
    Ano,
    Clasificacion,
    ClasificacionNombreCuenta,
    Codigo,
    Detalle,
    Documento,
    Mes,
    NombreArchivo,
    Referencia,
    Terceros,
    TipoEgreso,
    TipoIngreso,
    Vigencia,
)


class MovimientoContable(Base):
    __tablename__ = "movimiento_contable"

    id: Mapped[int] = mapped_column("id", primary_key=True)

    id_documento: Mapped[int | None] = mapped_column("id_documento", ForeignKey("documento.id"))
    id_codigo: Mapped[int | None] = mapped_column("id_codigo", ForeignKey("codigo.id"))
    id_detalle: Mapped[int | None] = mapped_column("id_detalle", ForeignKey("detalle.id"))
    id_referencia: Mapped[int | None] = mapped_column("id_referencia", ForeignKey("referencia.id"))
    id_terceros: Mapped[int | None] = mapped_column("id_terceros", ForeignKey("terceros.id"))
    id_mes: Mapped[int | None] = mapped_column("id_mes", ForeignKey("mes.id"))
    id_ano: Mapped[int | None] = mapped_column("id_ano", ForeignKey("ano.id"))
    id_nombre_archivo: Mapped[int | None] = mapped_column("id_nombre_archivo", ForeignKey("nombre_archivo.id"))
    id_clasificacion: Mapped[int | None] = mapped_column("id_clasificacion", ForeignKey("clasificacion.id"))
    id_tipo_ingreso: Mapped[int | None] = mapped_column("id_tipo_ingreso", ForeignKey("tipo_ingreso.id"))
    id_vigencia: Mapped[int | None] = mapped_column("id_vigencia", ForeignKey("vigencia.id"))
    id_clasificacion_nombre_cuenta: Mapped[int | None] = mapped_column(
        "id_clasificacion_nombre_cuenta", ForeignKey("clasificacion_nombre_cuenta.id")
    )
    id_tipo_egreso: Mapped[int | None] = mapped_column("id_tipo_egreso", ForeignKey("tipo_egreso.id"))

    debito: Mapped[float | None] = mapped_column("debito", Float)
    credito: Mapped[float | None] = mapped_column("credito", Float)
    total: Mapped[float | None] = mapped_column("total", Float)

    documento: Mapped[Documento | None] = relationship(lazy="joined")
    codigo: Mapped[Codigo | None] = relationship(lazy="joined")
    detalle: Mapped[Detalle | None] = relationship(lazy="joined")
    referencia: Mapped[Referencia | None] = relationship(lazy="joined")
    terceros: Mapped[Terceros | None] = relationship(lazy="joined")
    mes: Mapped[Mes | None] = relationship(lazy="joined")
    ano: Mapped[Ano | None] = relationship(lazy="joined")
    nombre_archivo: Mapped[NombreArchivo | None] = relationship(lazy="joined")
    clasificacion: Mapped[Clasificacion | None] = relationship(lazy="joined")
    tipo_ingreso: Mapped[TipoIngreso | None] = relationship(lazy="joined")
    vigencia: Mapped[Vigencia | None] = relationship(lazy="joined")
    clasificacion_nombre_cuenta: Mapped[ClasificacionNombreCuenta | None] = relationship(lazy="joined")
    tipo_egreso: Mapped[TipoEgreso | None] = relationship(lazy="joined")
