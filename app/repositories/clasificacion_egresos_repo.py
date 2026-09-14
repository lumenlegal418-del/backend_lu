from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import RegistrosEgresos


class ClasificacionEgresosRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_todos(self):
        result = await self.db.execute(
            select(RegistrosEgresos).order_by(RegistrosEgresos.id)
        )

        registros = result.scalars().all()

        return [
            {
                "nombre_cuenta": registro.nombre_cuenta,
                "clasificacion_nombre_cuenta": registro.clasificacion_nombre_cuenta,
                "tipo_egreso": registro.tipo_egreso,
            }
            for registro in registros
        ]

    async def crear(self, datos):
        registro = RegistrosEgresos(**datos)

        self.db.add(registro)

        await self.db.flush()
        await self.db.refresh(registro)

        return registro

    async def eliminar(self, datos):
        result = await self.db.execute(
            select(RegistrosEgresos).where(
                RegistrosEgresos.nombre_cuenta == datos.nombre_cuenta,
                RegistrosEgresos.clasificacion_nombre_cuenta == datos.clasificacion_nombre_cuenta,
                RegistrosEgresos.tipo_egreso == datos.tipo_egreso,
            )
        )

        registro = result.scalar_one_or_none()

        if registro is None:
            return False

        await self.db.delete(registro)

        return True