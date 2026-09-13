from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Terceros


class TerceroRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe_por_nit(self, nit: str) -> bool:
        resultado = await self.db.execute(
            select(Terceros).where(
                Terceros.nit == nit
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(
        self,
        nombre_tercero: str,
        nit: str
    ):
        nuevo_tercero = Terceros(
            nombre_tercero=nombre_tercero,
            nit=nit
        )

        self.db.add(nuevo_tercero)

        return nuevo_tercero