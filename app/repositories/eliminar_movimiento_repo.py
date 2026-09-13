from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movimiento import MovimientoContable
from app.models.catalogos import (
    Codigo,
    ClasificacionNombreCuenta,
    Detalle,
    Documento,
    NombreArchivo,
    Referencia,
    Terceros,
)


class EliminarMovimientoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def eliminar_por_archivo(
        self,
        *,
        nombre_archivo: str,
        ano: str | None = None,
        mes: str | None = None,
    ) -> dict:

        # =========================================================
        # 1. Buscar el ID del archivo
        # =========================================================

        resultado_archivo = await self.db.scalar(
            select(NombreArchivo.id)
            .where(
                NombreArchivo.nombre_archivo == nombre_archivo
            )
        )

        if resultado_archivo is None:
            return {
                "movimientos_eliminados": 0,
                "registros_huerfanos_eliminados": {},
            }

        id_nombre_archivo = resultado_archivo

        # =========================================================
        # 2. Construir filtros dinámicamente
        # =========================================================

        filtros = [
            MovimientoContable.id_nombre_archivo == id_nombre_archivo
        ]

        if ano is not None:
            id_ano = await self.db.scalar(
                select(MovimientoContable.id_ano)
                .join(
                    MovimientoContable.ano
                )
                .where(
                    MovimientoContable.id_nombre_archivo
                    == id_nombre_archivo,
                    MovimientoContable.ano.has(ano=ano),
                )
                .limit(1)
            )

            if id_ano is None:
                return {
                    "movimientos_eliminados": 0,
                    "registros_huerfanos_eliminados": {},
                }

            filtros.append(
                MovimientoContable.id_ano == id_ano
            )

        if mes is not None:
            id_mes = await self.db.scalar(
                select(MovimientoContable.id_mes)
                .join(
                    MovimientoContable.mes
                )
                .where(
                    MovimientoContable.id_nombre_archivo
                    == id_nombre_archivo,
                    MovimientoContable.mes.has(mes=mes),
                )
                .limit(1)
            )

            if id_mes is None:
                return {
                    "movimientos_eliminados": 0,
                    "registros_huerfanos_eliminados": {},
                }

            filtros.append(
                MovimientoContable.id_mes == id_mes
            )

        # =========================================================
        # 3. Obtener los movimientos que serán eliminados
        # =========================================================

        resultado = await self.db.execute(
            select(MovimientoContable)
            .where(*filtros)
        )

        movimientos = resultado.scalars().all()

        if not movimientos:
            return {
                "movimientos_eliminados": 0,
                "registros_huerfanos_eliminados": {},
            }

        cantidad_movimientos = len(movimientos)

        # =========================================================
        # 4. Guardar IDs de las tablas que SÍ pueden quedar
        #    huérfanas
        # =========================================================

        ids_documento = {
            movimiento.id_documento
            for movimiento in movimientos
            if movimiento.id_documento is not None
        }

        ids_codigo = {
            movimiento.id_codigo
            for movimiento in movimientos
            if movimiento.id_codigo is not None
        }

        ids_detalle = {
            movimiento.id_detalle
            for movimiento in movimientos
            if movimiento.id_detalle is not None
        }

        ids_referencia = {
            movimiento.id_referencia
            for movimiento in movimientos
            if movimiento.id_referencia is not None
        }

        ids_terceros = {
            movimiento.id_terceros
            for movimiento in movimientos
            if movimiento.id_terceros is not None
        }

        ids_nombre_archivo = {
            movimiento.id_nombre_archivo
            for movimiento in movimientos
            if movimiento.id_nombre_archivo is not None
        }

        ids_clasificacion_nombre_cuenta = {
            movimiento.id_clasificacion_nombre_cuenta
            for movimiento in movimientos
            if movimiento.id_clasificacion_nombre_cuenta is not None
        }

        # =========================================================
        # 5. Eliminar los movimientos contables
        # =========================================================

        await self.db.execute(
            delete(MovimientoContable)
            .where(*filtros)
        )

        # =========================================================
        # 6. Función auxiliar para comprobar huérfanos
        # =========================================================

        async def eliminar_huerfanos(
            modelo,
            columna_movimiento,
            ids_candidatos: set[int],
            nombre: str,
        ) -> int:

            if not ids_candidatos:
                return 0

            resultado_usados = await self.db.scalars(
                select(columna_movimiento)
                .where(
                    columna_movimiento.in_(ids_candidatos)
                )
            )

            ids_usados = {
                id_registro
                for id_registro in resultado_usados.all()
                if id_registro is not None
            }

            ids_huerfanos = ids_candidatos - ids_usados

            if not ids_huerfanos:
                return 0

            await self.db.execute(
                delete(modelo)
                .where(
                    modelo.id.in_(ids_huerfanos)
                )
            )

            return len(ids_huerfanos)

        # =========================================================
        # 7. Eliminar Documento huérfano
        # =========================================================

        documentos_eliminados = await eliminar_huerfanos(
            modelo=Documento,
            columna_movimiento=MovimientoContable.id_documento,
            ids_candidatos=ids_documento,
            nombre="documentos",
        )

        # =========================================================
        # 8. Eliminar Código huérfano
        # =========================================================

        codigos_eliminados = await eliminar_huerfanos(
            modelo=Codigo,
            columna_movimiento=MovimientoContable.id_codigo,
            ids_candidatos=ids_codigo,
            nombre="codigos",
        )

        # =========================================================
        # 9. Eliminar Detalle huérfano
        # =========================================================

        detalles_eliminados = await eliminar_huerfanos(
            modelo=Detalle,
            columna_movimiento=MovimientoContable.id_detalle,
            ids_candidatos=ids_detalle,
            nombre="detalles",
        )

        # =========================================================
        # 10. Eliminar Referencia huérfana
        # =========================================================

        referencias_eliminadas = await eliminar_huerfanos(
            modelo=Referencia,
            columna_movimiento=MovimientoContable.id_referencia,
            ids_candidatos=ids_referencia,
            nombre="referencias",
        )

        # =========================================================
        # 11. Eliminar Terceros huérfanos
        # =========================================================

        terceros_eliminados = await eliminar_huerfanos(
            modelo=Terceros,
            columna_movimiento=MovimientoContable.id_terceros,
            ids_candidatos=ids_terceros,
            nombre="terceros",
        )

        # =========================================================
        # 12. Eliminar NombreArchivo huérfano
        # =========================================================

        archivos_eliminados = await eliminar_huerfanos(
            modelo=NombreArchivo,
            columna_movimiento=MovimientoContable.id_nombre_archivo,
            ids_candidatos=ids_nombre_archivo,
            nombre="nombres_archivo",
        )

        # =========================================================
        # 13. Eliminar ClasificacionNombreCuenta huérfana
        # =========================================================

        clasificaciones_cuenta_eliminadas = await eliminar_huerfanos(
            modelo=ClasificacionNombreCuenta,
            columna_movimiento=(
                MovimientoContable.id_clasificacion_nombre_cuenta
            ),
            ids_candidatos=ids_clasificacion_nombre_cuenta,
            nombre="clasificaciones_nombre_cuenta",
        )

        # =========================================================
        # 14. Confirmar transacción
        # =========================================================

        await self.db.commit()

        # =========================================================
        # 15. Devolver resumen
        # =========================================================

        return {
            "movimientos_eliminados": cantidad_movimientos,
            "registros_huerfanos_eliminados": {
                "documentos": documentos_eliminados,
                "codigos": codigos_eliminados,
                "detalles": detalles_eliminados,
                "referencias": referencias_eliminadas,
                "terceros": terceros_eliminados,
                "nombres_archivo": archivos_eliminados,
                "clasificaciones_nombre_cuenta": (
                    clasificaciones_cuenta_eliminadas
                ),
            },
        }