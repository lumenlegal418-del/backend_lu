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