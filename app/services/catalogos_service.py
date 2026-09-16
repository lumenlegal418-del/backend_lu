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

    @staticmethod
    async def listar_estado_clientes(
        db: AsyncSession,
        id: int | None = None,
        nombre_tercero: str | None = None,
        ano_inicio: str | None = None,
        mes_inicio: str | None = None,
        ano_fin: str | None = None,
        mes_fin: str | None = None,
        estado: str | None = None,
    ):
        repository = EstadoClienteRepository(db)

        return await repository.listar(
            id=id,
            nombre_tercero=nombre_tercero,
            ano_inicio=ano_inicio,
            mes_inicio=mes_inicio,
            ano_fin=ano_fin,
            mes_fin=mes_fin,
            estado=estado,
        )

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

    @staticmethod
    async def listar_registro_egreso(
        db: AsyncSession,
        id: int | None = None,
        nombre_cuenta: str |None=None,
        clasificacion_nombre_cuenta: str | None=None,
        tipo_egreso: str | None=None,

    ):
        repository = ClasificacionEgresosRepository(db)

        return await repository.listar(
            id=id,
            nombre_cuenta=nombre_cuenta,
            clasificacion_nombre_cuenta=clasificacion_nombre_cuenta,
            tipo_egreso=tipo_egreso,
        )

    
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

    @staticmethod
    async def listar_empleado(
        db: AsyncSession,
        id: int | None = None,
        nombre_tercero:str | None=None,
        tipo_egreso:str | None=None,
    ):
        repository = ClasificacionEmpleadosRepository(db)

        return await repository.listar(
            id=id,
            nombre_tercero=nombre_tercero,
            tipo_egreso=tipo_egreso,
        )