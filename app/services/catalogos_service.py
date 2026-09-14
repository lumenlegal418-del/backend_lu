from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.estado_cliente_repo import EstadoClienteRepository
from app.repositories.clasificacion_egresos_repo import ClasificacionEgresosRepository
from app.repositories.clasificacion_empleados_repo import ClasificacionEmpleadosRepository


class CatalogosService:

    # =========================
    # ESTADO CLIENTE
    # =========================

    @staticmethod
    async def crear_estado_cliente(
        db: AsyncSession,
        datos
    ):
        repository = EstadoClienteRepository(db)

        registro = await repository.crear(
            datos.model_dump()
        )

        await db.commit()
        await db.refresh(registro)

        return registro

    @staticmethod
    async def eliminar_estado_cliente(
        db: AsyncSession,
        datos
    ):
        repository = EstadoClienteRepository(db)

        eliminado = await repository.eliminar(datos)

        if not eliminado:
            return False

        await db.commit()

        return True


    # =========================
    # REGISTROS EGRESOS
    # =========================

    @staticmethod
    async def crear_registro_egreso(
        db: AsyncSession,
        datos
    ):
        repository = ClasificacionEgresosRepository(db)

        registro = await repository.crear(
            datos.model_dump()
        )

        await db.commit()
        await db.refresh(registro)

        return registro

    @staticmethod
    async def eliminar_registro_egreso(
        db: AsyncSession,
        datos
    ):
        repository = ClasificacionEgresosRepository(db)

        eliminado = await repository.eliminar(datos)

        if not eliminado:
            return False

        await db.commit()

        return True


    # =========================
    # EMPLEADOS
    # =========================

    @staticmethod
    async def crear_empleado(
        db: AsyncSession,
        datos
    ):
        repository = ClasificacionEmpleadosRepository(db)

        registro = await repository.crear(
            datos.model_dump()
        )

        await db.commit()
        await db.refresh(registro)

        return registro

    @staticmethod
    async def eliminar_empleado(
        db: AsyncSession,
        datos
    ):
        repository = ClasificacionEmpleadosRepository(db)

        eliminado = await repository.eliminar(datos)

        if not eliminado:
            return False

        await db.commit()

        return True