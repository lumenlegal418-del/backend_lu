from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Codigo


class CodigoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, codigo: str) -> bool:
        resultado = await self.db.execute(
            select(Codigo).where(
                Codigo.codigo == codigo
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, codigo: str):
        nuevo_codigo = Codigo(
            codigo=codigo
        )

        self.db.add(nuevo_codigo)

        return nuevo_codigo