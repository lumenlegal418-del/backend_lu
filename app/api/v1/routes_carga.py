import os
import tempfile

import pandas as pd
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.repositories.estado_cliente_repo import EstadoClienteRepository
from app.repositories.clasificacion_egresos_repo import (
    ClasificacionEgresosRepository
)
from app.repositories.clasificacion_empleados_repo import (
    ClasificacionEmpleadosRepository
)

from app.procesamiento.script_transfomacion_datos import limpiar_datos
from app.procesamiento.script_asignacion_tipo_ingresos import (
    agregar_columnas_ingresos
)
from app.procesamiento.script_asignacion_tipo_egresos import (
    asignar_egresos
)

from app.services.carga_catalogos_service import cargar_todo

from app.procesamiento.validador_carga import validar_carga


router = APIRouter(
    prefix="/carga",
    tags=["carga"]
)


@router.post("/excel")
async def cargar_excel(
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    contenido = await archivo.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".xlsx"
    ) as archivo_temporal:

        archivo_temporal.write(contenido)
        ruta = archivo_temporal.name

    try:
        # 0. Validar archivo
        await validar_carga(
            ruta_archivo=ruta,
            nombre_archivo=archivo.filename,
            db=db
        )

        # 1. Limpiar y estructurar el Excel
        resultado = limpiar_datos(
            ruta,
            nombre_archivo=archivo.filename
        )

        # 2. Obtener los estados de los clientes desde PostgreSQL
        repository = EstadoClienteRepository(db)
        datos_clientes = await repository.listar()

        # 3. Convertir los datos de clientes a DataFrame
        df_clientes = pd.DataFrame(datos_clientes)

        # 4. Agregar las columnas de ingresos
        resultado = agregar_columnas_ingresos(
            resultado,
            df_clientes
        )

        # 5. Obtener clasificación de egresos
        clasificacion_egresos_repo = ClasificacionEgresosRepository(db)

        registros_egresos = (
            await clasificacion_egresos_repo.listar()
        )

        # Obtener clasificación de empleados
        clasificacion_empleados_repo = (
            ClasificacionEmpleadosRepository(db)
        )

        empleados = await clasificacion_empleados_repo.listar()

        # 6. Convertir registros de egresos y empleados a DataFrame
        df_egresos = pd.DataFrame(registros_egresos)
        df_empleados = pd.DataFrame(empleados)

        # 7. Agregar columnas de egresos
        resultado = asignar_egresos(
            resultado,
            df_egresos,
            df_empleados
        )

        # 8. Cargar todos los catálogos y movimientos
        await cargar_todo(resultado, db)

        # 9. Confirmar toda la transacción
        await db.commit()

        return {
            "nombre_archivo": archivo.filename,
            "filas_procesadas": len(resultado),
            "columnas": list(resultado.columns)
        }

    except ValueError as e:
        # Error producido por una validación
        await db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        # Error inesperado
        await db.rollback()
        raise

    finally:
        # Eliminar el archivo temporal
        if os.path.exists(ruta):
            os.remove(ruta)