from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Referencia


class ReferenciaRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, referencia: str) -> bool:
        resultado = await self.db.execute(
            select(Referencia).where(
                Referencia.referencia == referencia
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, referencia: str):
        nueva_referencia = Referencia(
            referencia=referencia
        )

        self.db.add(nueva_referencia)

        return nueva_referencia