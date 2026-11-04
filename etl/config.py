"""Configuración compartida del ETL: sesión de Spark, conexiones y utilidades.

Todos los módulos del ETL importan desde aquí; ninguno abre conexiones por su cuenta.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F

load_dotenv()
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Windows: Spark necesita winutils.exe y hadoop.dll en %HADOOP_HOME%\bin (ver README)
HADOOP_HOME = os.getenv("HADOOP_HOME", r"C:\hadoop")
os.environ["HADOOP_HOME"] = HADOOP_HOME
os.environ["PATH"] = os.path.join(HADOOP_HOME, "bin") + os.pathsep + os.environ["PATH"]

DRIVERS_JDBC = (
    "org.postgresql:postgresql:42.7.4,"
    "com.microsoft.sqlserver:mssql-jdbc:12.8.1.jre11"
)

# Origen: PostgreSQL
PG_URL = (
    f"jdbc:postgresql://{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/"
    f"{os.getenv('PG_DB')}"
)
PG_PROPS = {
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "driver": "org.postgresql.Driver",
}

# Destino: SQL Server
MS_URL = (
    f"jdbc:sqlserver://{os.getenv('MS_HOST')}:{os.getenv('MS_PORT')};"
    f"databaseName={os.getenv('MS_DB')};"
    "encrypt=true;trustServerCertificate=true"
)
MS_PROPS = {
    "user": os.getenv("MS_USER"),
    "password": os.getenv("MS_PASSWORD"),
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
}

TABLAS_FUENTE = [
    "categories", "customers", "employees", "products",
    "shippers", "orders", "order_details",
]

# Países abreviados en la fuente (hallazgo H5)
PAISES_ESTANDAR = {
    "UK": "United Kingdom",
    "USA": "United States",
}


# ---------------------------------------------------------------------
# Sesión de Spark
# ---------------------------------------------------------------------
def crear_spark() -> SparkSession:
    # Java interpreta "\" como escape: las rutas se le pasan con "/"
    hadoop_java = HADOOP_HOME.replace("\\", "/")
    # Log4j necesita la ruta como URL (file:///C:/...), no como ruta de Windows
    log4j_java = (Path(__file__).resolve().parent / "log4j2.properties").as_uri()
    spark = (
        SparkSession.builder
        .appName("Invacom - ETL Data Warehouse")
        .master("local[*]")
        .config("spark.jars.packages", DRIVERS_JDBC)
        .config(
            "spark.driver.extraJavaOptions",
            f"-Dhadoop.home.dir={hadoop_java} -Dlog4j2.configurationFile={log4j_java}",
        )
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


# ---------------------------------------------------------------------
# Lectura y escritura
# ---------------------------------------------------------------------
def leer_fuente(spark: SparkSession, tabla: str) -> DataFrame:
    """Lee una tabla de PostgreSQL (invacom_fuente)."""
    return spark.read.jdbc(PG_URL, tabla, properties=PG_PROPS)


def leer_dw(spark: SparkSession, tabla: str) -> DataFrame:
    """Lee una tabla del Data Warehouse en SQL Server."""
    return spark.read.jdbc(MS_URL, f"dbo.{tabla}", properties=MS_PROPS)


def escribir_dw(df: DataFrame, tabla: str) -> int:
    """Inserta el DataFrame en una tabla ya existente del DW y devuelve las filas cargadas.

    Se usa mode="append" para conservar las llaves y tipos creados por
    sql/dw/01_crear_modelo_estrella.sql (overwrite recrearía la tabla).
    """
    df.write.jdbc(MS_URL, f"dbo.{tabla}", mode="append", properties=MS_PROPS)
    return df.count()


def ejecutar_sql_dw(spark: SparkSession, sentencias: list[str]) -> None:
    """Ejecuta sentencias SQL (DELETE, DBCC...) directamente en SQL Server.

    Spark no ejecuta DELETE por JDBC, así que se usa el driver de Java
    que Spark ya tiene cargado.
    """
    jvm = spark.sparkContext._jvm
    props = jvm.java.util.Properties()
    props.setProperty("user", MS_PROPS["user"])
    props.setProperty("password", MS_PROPS["password"])
    conexion = jvm.com.microsoft.sqlserver.jdbc.SQLServerDriver().connect(MS_URL, props)
    try:
        sentencia = conexion.createStatement()
        for sql in sentencias:
            sentencia.execute(sql)
    finally:
        conexion.close()


# ---------------------------------------------------------------------
# Utilidades de limpieza compartidas
# ---------------------------------------------------------------------
def limpiar_texto(columna: str) -> Column:
    """Quita espacios al inicio/fin y reemplaza espacios múltiples por uno (H4)."""
    return F.trim(F.regexp_replace(F.col(columna), r"\s+", " "))


def estandarizar_pais(columna: str) -> Column:
    """Convierte países abreviados a su nombre completo (H5)."""
    pais = limpiar_texto(columna)
    resultado = pais
    for abreviado, completo in PAISES_ESTANDAR.items():
        resultado = F.when(pais == abreviado, F.lit(completo)).otherwise(resultado)
    return resultado


# ---------------------------------------------------------------------
# Utilidades para las tablas de hechos
# ---------------------------------------------------------------------
def fecha_key(columna: str) -> Column:
    """Fecha -> llave de dim_tiempo en formato AAAAMMDD (NULL si la fecha es nula)."""
    return F.date_format(F.col(columna), "yyyyMMdd").cast("int")


def buscar_llave(
    hechos: DataFrame,
    dimension: DataFrame,
    llaves_negocio: str | list[str],
    llave_sustituta: str,
    tabla: str,
) -> DataFrame:
    """Lookup de llave sustituta: agrega `llave_sustituta` de la dimensión a los hechos.

    Se une por la(s) llave(s) de negocio, que deben llamarse igual en ambos
    DataFrames. Usa LEFT JOIN y, si alguna fila no encuentra su llave, detiene
    el ETL con un mensaje claro en vez de perder filas sin avisar (un INNER JOIN
    las descartaría y el error solo se vería en la validación).
    """
    llaves = [llaves_negocio] if isinstance(llaves_negocio, str) else llaves_negocio
    resultado = hechos.join(
        dimension.select(*llaves, llave_sustituta), on=llaves, how="left"
    )
    huerfanas = resultado.filter(F.col(llave_sustituta).isNull())
    faltantes = huerfanas.count()
    if faltantes:
        ejemplos = [tuple(fila) for fila in huerfanas.select(*llaves).distinct().limit(5).collect()]
        raise ValueError(
            f"{tabla}: {faltantes} filas sin {llave_sustituta} "
            f"(no existen en la dimensión: {ejemplos})"
        )
    return resultado
