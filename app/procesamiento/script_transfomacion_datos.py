# importacion de librerias

import pandas as pd
import glob
import os
import unicodedata
import numpy as np

# Funciones de limpieza 

def leer_archivo(ruta,sheet_name=0,skiprows=1):
    df=pd.read_excel(ruta,sheet_name=sheet_name,skiprows=skiprows)
    return df

def agregar_mes_int(df,col):
    meses = {'enero': 1,'febrero': 2,'marzo': 3,'abril': 4,'mayo': 5,
            'junio': 6,'julio': 7,'agosto': 8,'septiembre': 9,'octubre': 10,
            'noviembre': 11,'diciembre': 12}

    df['mes_int'] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(meses)
    )
    return df

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

def eliminar_columnas(df, columnas):
    df = df.drop(columns=columnas, errors="ignore")
    return df

def convertir_columnas_string(df, columnas):
    for columna in columnas:
        df[columna] = df[columna].fillna(0)
        df[columna] = df[columna].apply(
            lambda x: str(int(x)) if isinstance(x, (int, float)) and float(x).is_integer() else str(x)
        )
    return df

def convertir_columnas_int(df, columnas):
    df[columnas] = df[columnas].fillna(0).astype(int)  # Rellena NaN con 0
    return df

def quitar_elementos_de_columnas(df,columna,elemento):
    df=df[df[columna] != elemento]
    return df

#Clasificar según los primeros dígitos (PUC Colombia)
def clasificar(fila):
    # Verificar primero si es AJUSTE AL PESO
    if fila['detalle'] == 'AJUSTE AL PESO':
        return 'INGRESO NO OPERACIONAL'
    
    codigo = fila['codigo']
    # Verificar los códigos de 2 dígitos (más específicos)
    if codigo.startswith('41'):
        return 'INGRESO OPERACIONAL'
    elif codigo.startswith('42'):
        return 'INGRESO NO OPERACIONAL'
    # Luego verificar el primer dígito (más general)
    elif codigo[0] == '4':
        return 'INGRESO'
    elif codigo[0] == '6':
        return 'COSTOS'
    elif codigo[0] == '5':
        return 'GASTOS'
    else:
        return 'OTRO'

def calcular_total(df_total: pd.DataFrame) :
    df_total = df_total.copy()

    df_total['total'] = np.where(
        df_total['Clasificacion'].isin([
            'INGRESO OPERACIONAL',
            'INGRESO NO OPERACIONAL'
        ]),
        df_total['creditos'] - df_total['debitos'],
        df_total['debitos'] - df_total['creditos']
    )
    return df_total
    
def asignar_columna_archivo_origen(df, nombre_archivo):
    df["archivo_origen"] = nombre_archivo
    return df


def limpiar_datos(ruta,
                nombre_archivo=None,
                columnas_a_eliminar=["comprob","nombre","centro_de_costo","base","dia","item"],
                columnas_a_str=["nit","niif","codigo"],
                columnas_a_int=["ano"]):
    Datos=leer_archivo(ruta)
    Datos= quitar_espacios_col_df(Datos)
    Datos=pasar_nombres_columnas_str_lower_sin_tildes(Datos)
    Datos=eliminar_columnas(Datos,columnas_a_eliminar)
    Datos=convertir_columnas_string(Datos,columnas_a_str)
    Datos=convertir_columnas_int(Datos,columnas_a_int)
    Datos["Clasificacion"]=Datos.apply(clasificar, axis=1)
    Datos=calcular_total(Datos)
    Datos=quitar_elementos_de_columnas(Datos,"nombre_cuenta","AJUSTE AL PESO")
    Datos=quitar_elementos_de_columnas(Datos,"Clasificacion","OTRO")
    Datos=agregar_mes_int(Datos,"mes")
    Datos=asignar_columna_archivo_origen(Datos, nombre_archivo)
    return Datos 

#ruta="insumo/movimiento_2026.xlsx"
#Resultado=limpiar_datos(ruta)
#print(Resultado)

