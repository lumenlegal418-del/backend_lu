from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalogos import Clasificacion

class ClasificacionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, clasificacion: str) -> bool:
        resultado = await self.db.execute(
            select(Clasificacion).where(
                Clasificacion.clasificacion == clasificacion
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, clasificacion: str):
        nueva_clasificacion = Clasificacion(
            clasificacion=clasificacion
        )

        self.db.add(nueva_clasificacion)

        return nueva_clasificacion