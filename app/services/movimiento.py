from app.repositories.eliminar_movimiento_repo import (
    EliminarMovimientoRepository,
)


class MovimientoService:

    def __init__(self, repository: EliminarMovimientoRepository):
        self.repository = repository

    async def eliminar_por_archivo(
        self,
        nombre_archivo: str,
        ano: str | None = None,
        mes: str | None = None,
    ):
        resultado = await self.repository.eliminar_por_archivo(
            nombre_archivo=nombre_archivo,
            ano=ano,
            mes=mes,
        )

        return {
            "mensaje": "Eliminación completada correctamente",
            **resultado,
        }