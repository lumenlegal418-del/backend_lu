from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediccion import Prediccion


class PrediccionRepository:
    """Acceso a la tabla PREDICCION (resultados precalculados del modelo de forecasting)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def reemplazar_predicciones(self, *, clasificacion: str, predicciones: list[dict]) -> None:
        """Borra las predicciones previas de esa clasificación e inserta las nuevas."""
        await self.db.execute(delete(Prediccion).where(Prediccion.clasificacion == clasificacion))
        self.db.add_all(
            [
                Prediccion(
                    clasificacion=clasificacion,
                    ano=p["ano"],
                    mes=p["mes"],
                    valor_predicho=p["valor_predicho"],
                )
                for p in predicciones
            ]
        )
        await self.db.commit()

    async def listar_por_clasificacion(self, *, clasificacion: str, ano: str | None = None) -> list[Prediccion]:
        query = select(Prediccion).where(Prediccion.clasificacion == clasificacion)
        if ano:
            query = query.where(Prediccion.ano == ano)
        result = await self.db.execute(query)
        return list(result.scalars().all())
