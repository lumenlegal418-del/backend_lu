from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Mes

class MesRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, mes: str) -> bool:
        resultado = await self.db.execute(
            select(Mes).where(
                Mes.mes == mes
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, mes: str):
        nuevo_mes = Mes(
            mes=mes
        )

        self.db.add(nuevo_mes)

        return nuevo_mes