from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import EstadoCliente


class EstadoClienteRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_todos(self):
        result = await self.db.execute(
            select(EstadoCliente).order_by(EstadoCliente.id)
        )

        registros = result.scalars().all()

        return [
            {
                "nombre_tercero": registro.nombre_tercero,
                "ano_inicio": registro.ano_inicio,
                "mes_inicio": registro.mes_inicio,
                "ano_fin": registro.ano_fin,
                "mes_fin": registro.mes_fin,
                "estado": registro.estado,
            }
            for registro in registros
        ]