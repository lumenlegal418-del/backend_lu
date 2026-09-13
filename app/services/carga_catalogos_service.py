import pandas as pd
from app.repositories.anos_repo import AnoRepository
from app.repositories.archivo_origen_repo import NombreArchivoRepository
from app.repositories.clasificacion_nombre_cuenta_repo import ClasificacionNombreCuentaRepository
from app.repositories.clasificacion_repo import ClasificacionRepository
from app.repositories.codigo_repo import CodigoRepository
from app.repositories.detalles_repo import DetalleRepository
from app.repositories.documento_repo import DocumentoRepository
from app.repositories.meses_repo import MesRepository
from app.repositories.referencia_repo import ReferenciaRepository
from app.repositories.terceros_repo import TerceroRepository
from app.repositories.tipo_egresos_repo import TipoEgresoRepository
from app.repositories.tipo_ingresos_repo import TipoIngresoRepository
from app.repositories.vigencias_repo import VigenciaRepository
from app.repositories.movimientos_contable_repo import (
    MovimientoContableRepository
)

async def cargar_anos(df: pd.DataFrame,db):
    ano_repository = AnoRepository(db)

    # =========================
    # ANO
    # =========================

    if "ano" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'ano'."
        )
    anos = (df["ano"].dropna().astype(str).str.strip().unique())

    anos_creados = 0
    for ano in anos:
        if not await ano_repository.existe(ano):
            await ano_repository.crear(ano)
            anos_creados += 1
    return {
        "anos_procesados": len(anos),
        "anos_creados": anos_creados
    }

async def cargar_nombres_archivos(df: pd.DataFrame,db):

    nombre_archivo_repository = NombreArchivoRepository(db)

    # =========================
    # NOMBRE_ARCHIVO
    # =========================

    if "archivo_origen" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'archivo_origen'."
        )

    archivos = (df["archivo_origen"].dropna().astype(str).str.strip().unique())
    archivos_creados = 0
    for archivo in archivos:

        if not await nombre_archivo_repository.existe(archivo):
            await nombre_archivo_repository.crear(archivo)
            archivos_creados += 1

    return {
        "archivos_procesados": len(archivos),
        "archivos_creados": archivos_creados
    }

async def cargar_clasificaciones_nombre_cuenta(df: pd.DataFrame,db):
    clasificacion_repository = ClasificacionNombreCuentaRepository(db)
    # =========================
    # CLASIFICACION_NOMBRE_CUENTA
    # =========================
    if "clasificacion_nombre_cuenta" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna "
            "'clasificacion_nombre_cuenta'."
        )

    clasificaciones = (df["clasificacion_nombre_cuenta"].dropna().astype(str).str.strip().unique())
    clasificaciones_creadas = 0
    for clasificacion in clasificaciones:
        if not await clasificacion_repository.existe(clasificacion):
            await clasificacion_repository.crear(clasificacion)
            clasificaciones_creadas += 1
    return {
        "clasificaciones_procesadas": len(clasificaciones),
        "clasificaciones_creadas": clasificaciones_creadas
    }

async def cargar_clasificaciones(df: pd.DataFrame,db):
    clasificacion_repository = ClasificacionRepository(db)

    # =========================
    # CLASIFICACION
    # =========================

    if "Clasificacion" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'Clasificacion'."
        )

    clasificaciones = (df["Clasificacion"].dropna().astype(str).str.strip().unique())

    clasificaciones_creadas = 0

    for clasificacion in clasificaciones:

        if not await clasificacion_repository.existe(clasificacion):
            await clasificacion_repository.crear(clasificacion)
            clasificaciones_creadas += 1

    return {
        "clasificaciones_procesadas": len(clasificaciones),
        "clasificaciones_creadas": clasificaciones_creadas
    }

async def cargar_codigos(df: pd.DataFrame,db):
    codigo_repository = CodigoRepository(db)

    # =========================
    # CODIGO
    # =========================
    if "codigo" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'codigo'."
        )

    codigos = (df["codigo"].dropna().astype(str).str.strip().unique())

    codigos_creados = 0

    for codigo in codigos:

        if not await codigo_repository.existe(codigo):
            await codigo_repository.crear(codigo)
            codigos_creados += 1

    return {
        "codigos_procesados": len(codigos),
        "codigos_creados": codigos_creados
    }

async def cargar_detalles(
    df: pd.DataFrame,
    db
):
    detalle_repository = DetalleRepository(db)

    # =========================
    # DETALLE
    # =========================

    if "detalle" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'detalle'."
        )

    detalles = (
        df["detalle"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    detalles_creados = 0

    for detalle in detalles:

        if not await detalle_repository.existe(detalle):
            await detalle_repository.crear(detalle)
            detalles_creados += 1

    return {
        "detalles_procesados": len(detalles),
        "detalles_creados": detalles_creados
    }

async def cargar_documentos(df: pd.DataFrame,db):
    documento_repository = DocumentoRepository(db)

    # =========================
    # DOCUMENTO
    # =========================

    if "documento" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'documento'."
        )
    documentos = (df["documento"].dropna().astype(str).str.strip().unique())
    documentos_creados = 0
    for documento in documentos:
        if not await documento_repository.existe(documento):
            await documento_repository.crear(documento)
            documentos_creados += 1
    return {
        "documentos_procesados": len(documentos),
        "documentos_creados": documentos_creados
    }

async def cargar_meses(df: pd.DataFrame,db):
    mes_repository = MesRepository(db)

    # =========================
    # MES
    # =========================

    if "mes" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'mes'."
        )

    meses = (df["mes"].dropna().astype(str).str.strip().unique())

    meses_creados = 0

    for mes in meses:

        if not await mes_repository.existe(mes):
            await mes_repository.crear(mes)
            meses_creados += 1

    return {
        "meses_procesados": len(meses),
        "meses_creados": meses_creados
    }

async def cargar_referencias(df: pd.DataFrame,db):
    referencia_repository = ReferenciaRepository(db)
    # =========================
    # REFERENCIA
    # =========================
    if "referencia" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'referencia'."
        )

    referencias = (df["referencia"].dropna().astype(str).str.strip().unique())
    referencias_creadas = 0
    for referencia in referencias:
        if not await referencia_repository.existe(referencia):
            await referencia_repository.crear(referencia)
            referencias_creadas += 1
    return {
        "referencias_procesadas": len(referencias),
        "referencias_creadas": referencias_creadas
    }

async def cargar_terceros(df: pd.DataFrame,db):
    tercero_repository = TerceroRepository(db)

    # =========================
    # TERCEROS
    # =========================

    columnas_requeridas = [
        "nombre_tercero",
        "nit"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan las siguientes columnas en el Excel: "
            + ", ".join(columnas_faltantes)
        )

    terceros = (df[["nombre_tercero", "nit"]].dropna(subset=["nombre_tercero", "nit"]).copy())

    terceros["nombre_tercero"] = (terceros["nombre_tercero"].astype(str).str.strip())

    terceros["nit"] = (terceros["nit"].astype(str).str.strip())

    # Eliminar registros duplicados por NIT
    terceros = terceros.drop_duplicates(
        subset=["nit"]
    )

    terceros_creados = 0

    for _, fila in terceros.iterrows():

        nit = fila["nit"]
        nombre_tercero = fila["nombre_tercero"]

        if not await tercero_repository.existe_por_nit(nit):
            await tercero_repository.crear(
                nombre_tercero=nombre_tercero,
                nit=nit
            )

            terceros_creados += 1

    return {
        "terceros_procesados": len(terceros),
        "terceros_creados": terceros_creados
    }

async def cargar_tipos_egreso(df: pd.DataFrame,db):
    tipo_egreso_repository = TipoEgresoRepository(db)

    # =========================
    # TIPO_EGRESO
    # =========================

    if "tipo_egreso" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'tipo_egreso'."
        )

    tipos_egreso = (df["tipo_egreso"].dropna().astype(str).str.strip().unique())
    tipos_egreso_creados = 0
    for tipo_egreso in tipos_egreso:

        if not await tipo_egreso_repository.existe(tipo_egreso):
            await tipo_egreso_repository.crear(tipo_egreso)
            tipos_egreso_creados += 1

    return {
        "tipos_egreso_procesados": len(tipos_egreso),
        "tipos_egreso_creados": tipos_egreso_creados
    }

async def cargar_tipos_ingreso(df: pd.DataFrame,db):
    tipo_ingreso_repository = TipoIngresoRepository(db)

    # =========================
    # TIPO_INGRESO
    # =========================

    if "tipo_ingresos" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'tipo_ingresos'."
        )

    tipos_ingreso = (df["tipo_ingresos"].dropna().astype(str).str.strip().unique())

    tipos_ingreso_creados = 0

    for tipo_ingreso in tipos_ingreso:

        if not await tipo_ingreso_repository.existe(tipo_ingreso):
            await tipo_ingreso_repository.crear(tipo_ingreso)
            tipos_ingreso_creados += 1

    return {
        "tipos_ingreso_procesados": len(tipos_ingreso),
        "tipos_ingreso_creados": tipos_ingreso_creados
    }

async def cargar_vigencias(df: pd.DataFrame,db):
    vigencia_repository = VigenciaRepository(db)

    # =========================
    # VIGENCIA
    # =========================

    if "vigencia" not in df.columns:
        raise ValueError(
            "El archivo Excel no contiene la columna 'vigencia'."
        )

    vigencias = (df["vigencia"].dropna().astype(str).str.strip().unique())
    vigencias_creadas = 0
    for vigencia in vigencias:

        if not await vigencia_repository.existe(vigencia):
            await vigencia_repository.crear(vigencia)
            vigencias_creadas += 1
    return {
        "vigencias_procesadas": len(vigencias),
        "vigencias_creadas": vigencias_creadas
    }

async def cargar_movimientos(df: pd.DataFrame, db):
    movimiento_repository = MovimientoContableRepository(db)

    columnas_requeridas = [
        "documento",
        "codigo",
        "detalle",
        "referencia",
        "nit",
        "mes",
        "ano",
        "archivo_origen",
        "Clasificacion",
        "tipo_ingresos",
        "vigencia",
        "clasificacion_nombre_cuenta",
        "tipo_egreso",
        "debitos",
        "creditos",
        "total",
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan las siguientes columnas en el Excel: "
            + ", ".join(columnas_faltantes)
        )

    documentos = await movimiento_repository.obtener_documentos()
    codigos = await movimiento_repository.obtener_codigos()
    detalles = await movimiento_repository.obtener_detalles()
    referencias = await movimiento_repository.obtener_referencias()
    terceros = await movimiento_repository.obtener_terceros()
    meses = await movimiento_repository.obtener_meses()
    anos = await movimiento_repository.obtener_anos()
    archivos = await movimiento_repository.obtener_archivos()
    clasificaciones = await movimiento_repository.obtener_clasificaciones()
    tipos_ingreso = await movimiento_repository.obtener_tipos_ingreso()
    vigencias = await movimiento_repository.obtener_vigencias()
    clasificaciones_cuenta = (
        await movimiento_repository.obtener_clasificaciones_cuenta()
    )
    tipos_egreso = await movimiento_repository.obtener_tipos_egreso()

    movimientos = []

    for _, fila in df.iterrows():

        documento = (
            str(fila["documento"]).strip()
            if pd.notna(fila["documento"])
            else None
        )

        codigo = (
            str(fila["codigo"]).strip()
            if pd.notna(fila["codigo"])
            else None
        )

        detalle = (
            str(fila["detalle"]).strip()
            if pd.notna(fila["detalle"])
            else None
        )

        referencia = (
            str(fila["referencia"]).strip()
            if pd.notna(fila["referencia"])
            else None
        )

        nit = (
            str(fila["nit"]).strip()
            if pd.notna(fila["nit"])
            else None
        )

        mes = (
            str(fila["mes"]).strip()
            if pd.notna(fila["mes"])
            else None
        )

        ano = (
            str(fila["ano"]).strip()
            if pd.notna(fila["ano"])
            else None
        )

        archivo = (
            str(fila["archivo_origen"]).strip()
            if pd.notna(fila["archivo_origen"])
            else None
        )

        clasificacion = (
            str(fila["Clasificacion"]).strip()
            if pd.notna(fila["Clasificacion"])
            else None
        )

        tipo_ingreso = (
            str(fila["tipo_ingresos"]).strip()
            if pd.notna(fila["tipo_ingresos"])
            else None
        )

        vigencia = (
            str(fila["vigencia"]).strip()
            if pd.notna(fila["vigencia"])
            else None
        )

        clasificacion_cuenta = (
            str(fila["clasificacion_nombre_cuenta"]).strip()
            if pd.notna(fila["clasificacion_nombre_cuenta"])
            else None
        )

        tipo_egreso = (
            str(fila["tipo_egreso"]).strip()
            if pd.notna(fila["tipo_egreso"])
            else None
        )

        debito = (
            float(fila["debitos"])
            if pd.notna(fila["debitos"])
            else 0
        )

        credito = (
            float(fila["creditos"])
            if pd.notna(fila["creditos"])
            else 0
        )

        total = (
            float(fila["total"])
            if pd.notna(fila["total"])
            else 0
        )

        movimientos.append({
            "id_documento": documentos.get(documento),
            "id_codigo": codigos.get(codigo),
            "id_detalle": detalles.get(detalle),
            "id_referencia": referencias.get(referencia),
            "id_terceros": terceros.get(nit),
            "id_mes": meses.get(mes),
            "id_ano": anos.get(ano),
            "id_nombre_archivo": archivos.get(archivo),
            "id_clasificacion": clasificaciones.get(clasificacion),
            "id_tipo_ingreso": tipos_ingreso.get(tipo_ingreso),
            "id_vigencia": vigencias.get(vigencia),
            "id_clasificacion_nombre_cuenta": (
                clasificaciones_cuenta.get(clasificacion_cuenta)
            ),
            "id_tipo_egreso": tipos_egreso.get(tipo_egreso),
            "debito": debito,
            "credito": credito,
            "total": total,
        })

    await movimiento_repository.crear_muchos(movimientos)

    return {
        "movimientos_procesados": len(movimientos)
    }

async def cargar_todo(df: pd.DataFrame, db):
    await cargar_anos(df, db)
    await cargar_nombres_archivos(df, db)
    await cargar_clasificaciones_nombre_cuenta(df, db)
    await cargar_clasificaciones(df, db)
    await cargar_codigos(df, db)
    await cargar_detalles(df, db)
    await cargar_documentos(df, db)
    await cargar_meses(df, db)
    await cargar_referencias(df, db)
    await cargar_terceros(df, db)
    await cargar_tipos_egreso(df, db)
    await cargar_tipos_ingreso(df, db)
    await cargar_vigencias(df, db)
    await cargar_movimientos(df, db)