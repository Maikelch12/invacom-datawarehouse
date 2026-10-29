"""Dimensión Tiempo: generada (no viene de la fuente) -> dim_tiempo.

Calendario diario del 2013-01-01 al 2015-12-31 (1095 filas), que cubre todo
el rango de fechas de los pedidos.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

TABLA = "dim_tiempo"

# Nombres en español fijos: así no dependemos del idioma (locale) de la
# máquina donde corra Spark.
NOMBRES_MES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
NOMBRES_DIA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

FECHA_INICIO = "2013-01-01"
FECHA_FIN = "2015-12-31"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Genera una fila por día con sus atributos de calendario.

    - tiempo_key = AAAAMMDD (entero). Es la única llave que calcula el ETL.
    - dia_semana: 1 = lunes ... 7 = domingo. Spark usa 1 = domingo, por eso
      se convierte con ((dayofweek + 5) % 7) + 1.
    - es_fin_de_semana: 'Sí' si es sábado o domingo, 'No' en otro caso.
    """
    fechas = spark.sql(
        f"SELECT explode(sequence(to_date('{FECHA_INICIO}'), "
        f"to_date('{FECHA_FIN}'), interval 1 day)) AS fecha"
    )

    meses = F.array(*[F.lit(m) for m in NOMBRES_MES])
    dias = F.array(*[F.lit(d) for d in NOMBRES_DIA])

    return (
        fechas
        .withColumn("dia_semana", ((F.dayofweek("fecha") + 5) % 7) + 1)
        .select(
            F.date_format("fecha", "yyyyMMdd").cast("int").alias("tiempo_key"),
            F.col("fecha"),
            F.year("fecha").alias("anio"),
            F.quarter("fecha").alias("trimestre"),
            F.concat(F.lit("T"), F.quarter("fecha")).alias("nombre_trimestre"),
            F.month("fecha").alias("mes"),
            F.element_at(meses, F.month("fecha")).alias("nombre_mes"),
            F.date_format("fecha", "yyyy-MM").alias("anio_mes"),
            F.dayofmonth("fecha").alias("dia"),
            F.col("dia_semana"),
            F.element_at(dias, F.col("dia_semana")).alias("nombre_dia"),
            F.when(F.col("dia_semana") >= 6, F.lit("Sí"))
             .otherwise(F.lit("No"))
             .alias("es_fin_de_semana"),
        )
        .orderBy("tiempo_key")
    )
