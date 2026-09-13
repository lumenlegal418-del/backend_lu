from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import NombreArchivo


class NombreArchivoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, nombre_archivo: str) -> bool:
        resultado = await self.db.execute(
            select(NombreArchivo).where(
                NombreArchivo.nombre_archivo == nombre_archivo
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, nombre_archivo: str):
        nuevo_archivo = NombreArchivo(
            nombre_archivo=nombre_archivo
        )

        self.db.add(nuevo_archivo)

        return nuevo_archivo