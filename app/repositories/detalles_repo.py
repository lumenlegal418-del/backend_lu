from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Detalle


class DetalleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, informacion_detalle: str) -> bool:
        resultado = await self.db.execute(
            select(Detalle).where(
                Detalle.informacion_detalle == informacion_detalle
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, informacion_detalle: str):
        nuevo_detalle = Detalle(
            informacion_detalle=informacion_detalle
        )

        self.db.add(nuevo_detalle)

        return nuevo_detalle