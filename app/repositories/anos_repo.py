from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Ano


class AnoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, ano: str) -> bool:
        resultado = await self.db.execute(
            select(Ano).where(Ano.ano == ano)
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, ano: str):
        nuevo_ano = Ano(ano=ano)

        self.db.add(nuevo_ano)

        return nuevo_ano