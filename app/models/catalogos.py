from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Documento(Base):
    __tablename__ = "documento"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    nombre_documento: Mapped[str | None] = mapped_column("nombre_documento", String(255), unique=True)


class Codigo(Base):
    __tablename__ = "codigo"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    codigo: Mapped[str | None] = mapped_column("codigo", String(100), unique=True)


class Detalle(Base):
    __tablename__ = "detalle"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    informacion_detalle: Mapped[str | None] = mapped_column("informacion_detalle", String(500), unique=True)


class Referencia(Base):
    __tablename__ = "referencia"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    referencia: Mapped[str | None] = mapped_column("referencia", String(100), unique=True)


class Terceros(Base):
    __tablename__ = "terceros"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    nombre_tercero: Mapped[str | None] = mapped_column("nombre_tercero", String(255))
    nit: Mapped[str | None] = mapped_column("nit", String(20), unique=True)


class Mes(Base):
    __tablename__ = "mes"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    mes: Mapped[str | None] = mapped_column("mes", String(50), unique=True)


class Ano(Base):
    __tablename__ = "ano"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    ano: Mapped[str | None] = mapped_column("ano", String(4), unique=True)


class NombreArchivo(Base):
    __tablename__ = "nombre_archivo"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    nombre_archivo: Mapped[str | None] = mapped_column("nombre_archivo", String(255), unique=True)


class Clasificacion(Base):
    __tablename__ = "clasificacion"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    clasificacion: Mapped[str | None] = mapped_column("clasificacion", String(100), unique=True)


class TipoIngreso(Base):
    __tablename__ = "tipo_ingreso"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    tipo_ingreso: Mapped[str | None] = mapped_column("tipo_ingreso", String(100), unique=True)


class Vigencia(Base):
    __tablename__ = "vigencia"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    vigencia: Mapped[str | None] = mapped_column("vigencia", String(100), unique=True)


class ClasificacionNombreCuenta(Base):
    __tablename__ = "clasificacion_nombre_cuenta"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    clasificacion_nombre_cuenta: Mapped[str | None] = mapped_column(
        "clasificacion_nombre_cuenta", String(100), unique=True
    )


class TipoEgreso(Base):
    __tablename__ = "tipo_egreso"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    tipo_egreso: Mapped[str | None] = mapped_column("tipo_egreso", String(100), unique=True)

class EstadoCliente(Base):
    __tablename__ = "estado_cliente"

    id: Mapped[int] = mapped_column("id",primary_key=True,autoincrement=True)
    nombre_tercero: Mapped[str] = mapped_column("nombre_tercero",String(50),nullable=False)
    ano_inicio: Mapped[str] = mapped_column("ano_inicio",String(4),nullable=False)
    mes_inicio: Mapped[str] = mapped_column("mes_inicio",String(50),nullable=False)
    ano_fin: Mapped[str | None] = mapped_column("ano_fin",String(4),nullable=True)
    mes_fin: Mapped[str | None] = mapped_column("mes_fin",String(50),nullable=True)
    estado: Mapped[str] = mapped_column("estado",String(50),nullable=False)

class RegistrosEgresos(Base):
    __tablename__ = "registros_egresos"

    id: Mapped[int] = mapped_column("id",primary_key=True,autoincrement=True)
    nombre_cuenta: Mapped[str] = mapped_column("nombre_cuenta",String(50),nullable=False)
    clasificacion_nombre_cuenta: Mapped[str] = mapped_column("clasificacion_nombre_cuenta",String(50),nullable=False)
    tipo_egreso: Mapped[str | None] = mapped_column("tipo_egreso",String(50),nullable=True)

class Empleados(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column("id",primary_key=True,autoincrement=True)
    nombre_tercero: Mapped[str] = mapped_column("nombre_tercero",String(50),nullable=False)
    tipo_egreso: Mapped[str | None] = mapped_column("tipo_egreso",String(50),nullable=True)