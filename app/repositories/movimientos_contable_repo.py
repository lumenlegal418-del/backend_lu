from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movimiento import MovimientoContable
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


class MovimientoContableRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtener_documentos(self):
        resultado = await self.db.execute(
            select(Documento.id, Documento.nombre_documento)
        )
        return {
            str(nombre).strip(): id_
            for id_, nombre in resultado.all()
        }

    async def obtener_codigos(self):
        resultado = await self.db.execute(
            select(Codigo.id, Codigo.codigo)
        )
        return {
            str(codigo).strip(): id_
            for id_, codigo in resultado.all()
        }

    async def obtener_detalles(self):
        resultado = await self.db.execute(
            select(Detalle.id, Detalle.informacion_detalle)
        )
        return {
            str(detalle).strip(): id_
            for id_, detalle in resultado.all()
        }

    async def obtener_referencias(self):
        resultado = await self.db.execute(
            select(Referencia.id, Referencia.referencia)
        )
        return {
            str(referencia).strip(): id_
            for id_, referencia in resultado.all()
        }

    async def obtener_terceros(self):
        resultado = await self.db.execute(
            select(Terceros.id, Terceros.nit)
        )
        return {
            str(nit).strip(): id_
            for id_, nit in resultado.all()
        }

    async def obtener_meses(self):
        resultado = await self.db.execute(
            select(Mes.id, Mes.mes)
        )
        return {
            str(mes).strip(): id_
            for id_, mes in resultado.all()
        }

    async def obtener_anos(self):
        resultado = await self.db.execute(
            select(Ano.id, Ano.ano)
        )
        return {
            str(ano).strip(): id_
            for id_, ano in resultado.all()
        }

    async def obtener_archivos(self):
        resultado = await self.db.execute(
            select(NombreArchivo.id, NombreArchivo.nombre_archivo)
        )
        return {
            str(archivo).strip(): id_
            for id_, archivo in resultado.all()
        }

    async def obtener_clasificaciones(self):
        resultado = await self.db.execute(
            select(Clasificacion.id, Clasificacion.clasificacion)
        )
        return {
            str(clasificacion).strip(): id_
            for id_, clasificacion in resultado.all()
        }

    async def obtener_tipos_ingreso(self):
        resultado = await self.db.execute(
            select(TipoIngreso.id, TipoIngreso.tipo_ingreso)
        )
        return {
            str(tipo_ingreso).strip(): id_
            for id_, tipo_ingreso in resultado.all()
        }

    async def obtener_vigencias(self):
        resultado = await self.db.execute(
            select(Vigencia.id, Vigencia.vigencia)
        )
        return {
            str(vigencia).strip(): id_
            for id_, vigencia in resultado.all()
        }

    async def obtener_clasificaciones_cuenta(self):
        resultado = await self.db.execute(
            select(
                ClasificacionNombreCuenta.id,
                ClasificacionNombreCuenta.clasificacion_nombre_cuenta,
            )
        )
        return {
            str(clasificacion).strip(): id_
            for id_, clasificacion in resultado.all()
        }

    async def obtener_tipos_egreso(self):
        resultado = await self.db.execute(
            select(TipoEgreso.id, TipoEgreso.tipo_egreso)
        )
        return {
            str(tipo_egreso).strip(): id_
            for id_, tipo_egreso in resultado.all()
        }

    async def crear_muchos(self, movimientos):
        self.db.add_all(
            [
                MovimientoContable(**movimiento)
                for movimiento in movimientos
            ]
        )