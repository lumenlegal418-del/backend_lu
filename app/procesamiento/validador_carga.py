import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.movimientos_contable_repo import MovimientoContableRepository


COLUMNAS_REQUERIDAS = {
    "Comprob",
    "Nombre",
    "Documento",
    "Código",
    "Nombre cuenta",
    "Detalle",
    "Referencia",
    "Débitos",
    "Créditos",
    "Nombre tercero",
    "Nit",
    "Centro de costo",
    "Base",
    "Mes",
    "Dia",
    "Año",
    "NIIF",
    "Item",
}


def validar_archivo_excel(nombre_archivo: str):

    extensiones_validas = {".xlsx", ".xls"}

    extension = "." + nombre_archivo.split(".")[-1].lower()

    if extension not in extensiones_validas:
        raise ValueError(
            "El archivo debe ser un Excel con extensión "
            ".xlsx o .xls"
        )


def validar_columnas(df: pd.DataFrame):

    columnas_faltantes = COLUMNAS_REQUERIDAS - set(df.columns)

    if columnas_faltantes:
        raise ValueError(
            f"El archivo no tiene las columnas requeridas: "
            f"{sorted(columnas_faltantes)}"
        )


def validar_periodo_unico(df: pd.DataFrame):

    anos = df["Año"].dropna().unique()
    meses = df["Mes"].dropna().unique()

    if len(anos) != 1:
        raise ValueError(
            f"El archivo debe contener un solo año. "
            f"Se encontraron: {list(anos)}"
        )

    if len(meses) != 1:
        raise ValueError(
            f"El archivo debe contener un solo mes. "
            f"Se encontraron: {list(meses)}"
        )

    return anos[0], meses[0]


async def validar_periodo_bd(
    db: AsyncSession,
    ano,
    mes
):
    mes = str(mes).strip()
    ano = str(int(ano)).strip()

    repositorio = MovimientoContableRepository(db)

    existe = await repositorio.periodo_existe(
        mes=mes,
        ano=ano
    )
    if existe:
        raise ValueError(
            f"El período {mes} de {ano} ya existe en la base de datos."
        )


async def validar_carga(
    ruta_archivo: str,
    nombre_archivo: str,
    db: AsyncSession
):

    # 1. Validar extensión
    validar_archivo_excel(nombre_archivo)

    # 2. Leer Excel
    df = pd.read_excel(ruta_archivo,sheet_name=0,skiprows=1)

    # 3. Validar columnas
    validar_columnas(df)

    # 4. Validar período
    ano, mes = validar_periodo_unico(df)

    # 5. Validar período en BD
    await validar_periodo_bd(
        db=db,
        ano=ano,
        mes=mes
    )

    return {
        "df": df,
        "ano": ano,
        "mes": mes,
    }