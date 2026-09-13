from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Vigencia


class VigenciaRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, vigencia: str) -> bool:
        resultado = await self.db.execute(
            select(Vigencia).where(
                Vigencia.vigencia == vigencia
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, vigencia: str):
        nueva_vigencia = Vigencia(
            vigencia=vigencia
        )

        self.db.add(nueva_vigencia)

        return nueva_vigencia