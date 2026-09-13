from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Empleados


class ClasificacionEmpleadosRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_todos(self):
        result = await self.db.execute(
            select(Empleados).order_by(Empleados.id)
        )

        registros = result.scalars().all()

        return [
            {
                "nombre_tercero": registro.nombre_tercero,
                "tipo_egreso": registro.tipo_egreso,
            }
            for registro in registros
        ]