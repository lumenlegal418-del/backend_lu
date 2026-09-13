from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import TipoEgreso


class TipoEgresoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, tipo_egreso: str) -> bool:
        resultado = await self.db.execute(
            select(TipoEgreso).where(
                TipoEgreso.tipo_egreso == tipo_egreso
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, tipo_egreso: str):
        nuevo_tipo_egreso = TipoEgreso(
            tipo_egreso=tipo_egreso
        )

        self.db.add(nuevo_tipo_egreso)

        return nuevo_tipo_egreso