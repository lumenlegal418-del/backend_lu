from pydantic import BaseModel, ConfigDict


class CatalogoOut(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DocumentoOut(CatalogoOut):
    nombre_documento: str | None = None


class CodigoOut(CatalogoOut):
    codigo: str | None = None


class DetalleOut(CatalogoOut):
    informacion_detalle: str | None = None


class ReferenciaOut(CatalogoOut):
    referencia: str | None = None


class TercerosOut(CatalogoOut):
    nombre_tercero: str | None = None
    nit: str | None = None


class MesOut(CatalogoOut):
    mes: str | None = None


class AnoOut(CatalogoOut):
    ano: str | None = None


class ClasificacionOut(CatalogoOut):
    clasificacion: str | None = None


class TipoIngresoOut(CatalogoOut):
    tipo_ingreso: str | None = None


class VigenciaOut(CatalogoOut):
    vigencia: str | None = None


class ClasificacionNombreCuentaOut(CatalogoOut):
    clasificacion_nombre_cuenta: str | None = None


class TipoEgresoOut(CatalogoOut):
    tipo_egreso: str | None = None
