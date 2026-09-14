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

    async def crear(self, datos):
        registro = Empleados(**datos)

        self.db.add(registro)

        await self.db.flush()
        await self.db.refresh(registro)

        return registro

    async def eliminar(self, datos):
        result = await self.db.execute(
            select(Empleados).where(
                Empleados.nombre_tercero == datos.nombre_tercero,
                Empleados.tipo_egreso == datos.tipo_egreso,
            )
        )

        registro = result.scalar_one_or_none()

        if registro is None:
            return False

        await self.db.delete(registro)

        return True