from sqlalchemy import select, and_
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
                "id": registro.id,
                "nombre_tercero": registro.nombre_tercero,
                "ano_inicio": registro.ano_inicio,
                "mes_inicio": registro.mes_inicio,
                "ano_fin": registro.ano_fin,
                "mes_fin": registro.mes_fin,
                "estado": registro.estado,
            }
            for registro in registros
        ]

    async def crear(self, datos):
        registro = EstadoCliente(**datos)

        self.db.add(registro)

        await self.db.flush()
        await self.db.refresh(registro)

        return registro

    async def eliminar(self, datos):
        result = await self.db.execute(
            select(EstadoCliente).where(
                EstadoCliente.nombre_tercero == datos.nombre_tercero,
                EstadoCliente.ano_inicio == datos.ano_inicio,
                EstadoCliente.mes_inicio == datos.mes_inicio,
                EstadoCliente.ano_fin == datos.ano_fin,
                EstadoCliente.mes_fin == datos.mes_fin,
                EstadoCliente.estado == datos.estado,
            )
        )

        registro = result.scalar_one_or_none()

        if registro is None:
            return False

        await self.db.delete(registro)

        return True