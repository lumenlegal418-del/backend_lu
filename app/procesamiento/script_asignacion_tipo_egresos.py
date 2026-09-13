import pandas as pd


def asignar_columna_clasificacion_nombre_cuenta(
    dataframe_transformaciones,
    df_registros
):
    # Crear diccionario para buscar la cuenta
    mapa_clasificacion = (
        dataframe_transformaciones
        .set_index("nombre_cuenta")["clasificacion_nombre_cuenta"]
        .to_dict()
    )

    mapa_tipo_egreso = (
        dataframe_transformaciones
        .set_index("nombre_cuenta")["tipo_egreso"]
        .to_dict()
    )

    # Por defecto, todos los registros tendrán "No aplica"
    df_registros["clasificacion_nombre_cuenta"] = "No aplica"
    df_registros["tipo_egreso"] = "No aplica"

    # Identificar registros que sean COSTOS o GASTOS
    filtro = df_registros["Clasificacion"].isin(["COSTOS", "GASTOS"])

    # Asignar clasificación según nombre_cuenta
    df_registros.loc[filtro, "clasificacion_nombre_cuenta"] = (
        df_registros.loc[filtro, "nombre_cuenta"]
        .map(mapa_clasificacion)
        .fillna("No aplica")
    )

    # Asignar tipo de egreso según nombre_cuenta
    df_registros.loc[filtro, "tipo_egreso"] = (
        df_registros.loc[filtro, "nombre_cuenta"]
        .map(mapa_tipo_egreso)
        .fillna("No aplica")
    )

    return df_registros


def actualizar_tipo_egreso(registros, empleados):

    registros = registros.copy()
    empleados = empleados.copy()

    # Limpiar nombres de terceros
    registros["nombre_tercero"] = (
        registros["nombre_tercero"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    empleados["nombre_tercero"] = (
        empleados["nombre_tercero"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Crear diccionario nombre_tercero -> tipo_egreso
    mapa_tipo_egreso = (
        empleados
        .set_index("nombre_tercero")["tipo_egreso"]
        .to_dict()
    )

    # Buscar coincidencias y reemplazar tipo_egreso
    registros["tipo_egreso"] = (
        registros["nombre_tercero"]
        .map(mapa_tipo_egreso)
        .fillna(registros["tipo_egreso"])
    )

    # Cambiar nombres
    registros["tipo_egreso"] = registros["tipo_egreso"].replace({
        "Variable": "Egreso variable",
        "Fijo": "Egreso fijo"
    })

    return registros


def asignar_egresos(
    registros_estructurados,
    clasificacion_egresos,
    empleados
):

    # 1. Clasificación según nombre_cuenta
    asignacion_columna_egresos = (
        asignar_columna_clasificacion_nombre_cuenta(
            clasificacion_egresos,
            registros_estructurados
        )
    )

    # 2. Actualizar tipo de egreso según empleado
    resultado = actualizar_tipo_egreso(
        asignacion_columna_egresos,
        empleados
    )

    return resultado




#resultado = asignar_egresos(
#    registros_estructurados=datos_estructurados,
#    clasificacion_egresos=registros_egresos,
#    empleados=empleados
#)

    