from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import Documento


class DocumentoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, nombre_documento: str) -> bool:
        resultado = await self.db.execute(
            select(Documento).where(
                Documento.nombre_documento == nombre_documento
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, nombre_documento: str):
        nuevo_documento = Documento(
            nombre_documento=nombre_documento
        )

        self.db.add(nuevo_documento)

        return nuevo_documento