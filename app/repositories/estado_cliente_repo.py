from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogos import EstadoCliente


class EstadoClienteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar( 
            self, 
            id: int | None = None, 
            nombre_tercero: str | None = None, 
            ano_inicio: str | None = None,
            mes_inicio: str | None = None, 
            ano_fin: str | None = None, 
            mes_fin: str | None = None, 
            estado: str | None = None, 
            ): 
        query = select(EstadoCliente) 

        if id is not None: 
            query = query.where( EstadoCliente.id == id ) 

        if nombre_tercero is not None: 
            query = query.where( EstadoCliente.nombre_tercero == nombre_tercero ) 

        if ano_inicio is not None: 
            query = query.where( EstadoCliente.ano_inicio == ano_inicio ) 

        if mes_inicio is not None: 
            query = query.where( EstadoCliente.mes_inicio == mes_inicio ) 

        if ano_fin is not None: 
            query = query.where( EstadoCliente.ano_fin == ano_fin ) 

        if mes_fin is not None: 
            query = query.where( EstadoCliente.mes_fin == mes_fin ) 

        if estado is not None: 
            query = query.where( EstadoCliente.estado == estado ) 

        query = query.order_by(EstadoCliente.id) 

        result = await self.db.execute(query) 

        registros = result.scalars().all() 

        return [ 
            { 
                "id": registro.id, 
                "nombre_tercero": registro.nombre_tercero, 
                "ano_inicio": registro.ano_inicio, "mes_inicio": 
                registro.mes_inicio, "ano_fin": registro.ano_fin, 
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