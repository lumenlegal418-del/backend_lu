import pandas as pd
import unicodedata

def quitar_espacios_col_df(df):
    df.columns = df.columns.str.strip()
    return df

def pasar_nombres_columnas_str_lower_sin_tildes(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8"))
        .str.replace(" ", "_")
    )
    return df

def agregar_columnas_ingresos(registros_estructurados, df_clientes):
    # Copias para no modificar los DataFrames originales
    df = registros_estructurados.copy()
    df_clientes = df_clientes.copy()

    # ---------------------------------------------------------
    # 1. Limpiar nombres de columnas de df_clientes
    # ---------------------------------------------------------
    df_clientes = quitar_espacios_col_df(df_clientes)
    df_clientes = pasar_nombres_columnas_str_lower_sin_tildes(df_clientes)

    # ---------------------------------------------------------
    # 2. Clasificaciones que corresponden a ingresos
    # ---------------------------------------------------------
    clasificaciones_ingreso = [
        "INGRESO OPERACIONAL",
        "INGRESO NO OPERACIONAL"
    ]

    # ---------------------------------------------------------
    # 3. Inicializar las columnas
    # ---------------------------------------------------------
    df["tipo_ingresos"] = "No aplica"
    df["vigencia"] = "No aplica"

    # ---------------------------------------------------------
    # 4. Crear período numérico para los registros
    # ---------------------------------------------------------
    df["_periodo_registro"] = (
        df["ano"].astype(int) * 12
        + df["mes_int"].astype(int)
    )

    df_clientes["_periodo_inicio"] = (
        df_clientes["ano_inicio"].astype(int) * 12
        + df_clientes["mes_inicio"].astype(int)
    )

    # ---------------------------------------------------------
    # 5. Procesar únicamente los registros de ingreso
    # ---------------------------------------------------------
    mask_ingreso = df["Clasificacion"].isin(clasificaciones_ingreso)

    for idx in df.index[mask_ingreso]:

        nombre_tercero = df.loc[idx, "nombre_tercero"]
        periodo_registro = df.loc[idx, "_periodo_registro"]

        # Buscar coincidencia por nombre_tercero
        clientes = df_clientes[
            df_clientes["nombre_tercero"] == nombre_tercero
        ]

        # Si no existe el tercero, se mantiene No aplica
        if clientes.empty:
            continue

        ingreso_fijo = False

        # -----------------------------------------------------
        # 6. Revisar clientes FINALIZADOS
        # -----------------------------------------------------
        clientes_finalizados = clientes[
            clientes["estado"]
            .astype(str)
            .str.upper()
            .eq("FINALIZADO")
        ]

        for _, cliente in clientes_finalizados.iterrows():

            # Verificar que tenga fecha de finalización
            if (
                pd.notna(cliente["ano_fin"])
                and pd.notna(cliente["mes_fin"])
            ):

                periodo_fin = (
                    int(cliente["ano_fin"]) * 12
                    + int(cliente["mes_fin"])
                )

                # Registro dentro del rango del contrato
                if (
                    cliente["_periodo_inicio"]
                    <= periodo_registro
                    <= periodo_fin
                ):

                    ingreso_fijo = True

                    df.loc[idx, "tipo_ingresos"] = "Ingreso fijo"
                    df.loc[idx, "vigencia"] = "Finalizado"

                    break

        if ingreso_fijo:
            continue

        # -----------------------------------------------------
        # 7. Revisar clientes VIGENTES
        # -----------------------------------------------------
        clientes_vigentes = clientes[
            clientes["estado"]
            .astype(str)
            .str.upper()
            .eq("VIGENTE")
        ]

        for _, cliente in clientes_vigentes.iterrows():

            # Para un cliente vigente solamente se verifica
            # que el registro sea posterior o igual al inicio
            if periodo_registro >= cliente["_periodo_inicio"]:

                ingreso_fijo = True

                df.loc[idx, "tipo_ingresos"] = "Ingreso fijo"
                df.loc[idx, "vigencia"] = "Vigente"

                break

        if ingreso_fijo:
            continue

        # -----------------------------------------------------
        # 8. Si es ingreso pero no pertenece a ningún período
        #    de ingreso fijo
        # -----------------------------------------------------
        df.loc[idx, "tipo_ingresos"] = "Ingreso vario"
        df.loc[idx, "vigencia"] = "Finalizado"

    # ---------------------------------------------------------
    # 9. Regla adicional
    #
    # Si la clasificación es de ingreso y tipo_ingresos
    # quedó como No aplica, convertirlo en Ingreso vario
    # y vigencia Finalizado.
    # ---------------------------------------------------------
    mask_ingreso_vario = (
        df["Clasificacion"].isin(clasificaciones_ingreso)
        & df["tipo_ingresos"].eq("No aplica")
    )

    df.loc[mask_ingreso_vario, "tipo_ingresos"] = "Ingreso vario"
    df.loc[mask_ingreso_vario, "vigencia"] = "Finalizado"

    # ---------------------------------------------------------
    # 10. Eliminar columna auxiliar
    # ---------------------------------------------------------
    df.drop(
        columns=["_periodo_registro"],
        inplace=True
    )

    return df

#registros_estructurados= pd.read_excel("Datos_estructurados_prueba.xlsx")
#df_clientes=pd.read_excel("Empresas_vigentes_lumen.xlsx")

#dato=agregar_columnas_ingresos(registros_estructurados,df_clientes)
#print(dato)