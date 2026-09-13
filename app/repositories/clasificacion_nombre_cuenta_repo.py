from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import ClasificacionNombreCuenta


class ClasificacionNombreCuentaRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def existe(self, clasificacion_nombre_cuenta: str) -> bool:
        resultado = await self.db.execute(
            select(ClasificacionNombreCuenta).where(
                ClasificacionNombreCuenta.clasificacion_nombre_cuenta
                == clasificacion_nombre_cuenta
            )
        )

        return resultado.scalar_one_or_none() is not None

    async def crear(self, clasificacion_nombre_cuenta: str):
        nueva_clasificacion = ClasificacionNombreCuenta(
            clasificacion_nombre_cuenta=clasificacion_nombre_cuenta
        )

        self.db.add(nueva_clasificacion)

        return nueva_clasificacion