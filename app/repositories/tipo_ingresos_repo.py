from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import TipoIngreso

class TipoIngresoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, tipo_ingreso: str) -> bool:
        resultado = await self.db.execute(
            select(TipoIngreso).where(
                TipoIngreso.tipo_ingreso == tipo_ingreso
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, tipo_ingreso: str):
        nuevo_tipo_ingreso = TipoIngreso(
            tipo_ingreso=tipo_ingreso
        )

        self.db.add(nuevo_tipo_ingreso)

        return nuevo_tipo_ingreso