"""Dimensión Descuento: valores distintos de order_details.discount -> dim_descuento."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

TABLA = "dim_descuento"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Dimensión de bandas: agrupa los porcentajes de descuento en rangos.

    - Una fila por cada porcentaje distinto en order_details (11 valores).
    - descuento_texto: 0.15 -> '15 %'.
    - rango_descuento: Sin descuento / Bajo (1-5 %) / Medio (6-15 %) / Alto (16-25 %).
    - Conserva los descuentos atípicos del pedido 11077 (H7).
    """
    descuentos = (
        fuente["order_details"]
        .select(F.col("discount").cast("decimal(4,2)").alias("descuento_pct"))
        .distinct()
    )
    pct = F.col("descuento_pct")

    return (
        descuentos
        .select(
            pct,
            F.concat((pct * 100).cast("int").cast("string"), F.lit(" %"))
             .alias("descuento_texto"),
            F.when(pct == 0, F.lit("Sin descuento"))
             .when(pct <= 0.05, F.lit("Bajo (1-5 %)"))
             .when(pct <= 0.15, F.lit("Medio (6-15 %)"))
             .otherwise(F.lit("Alto (16-25 %)"))
             .alias("rango_descuento"),
            F.when(pct > 0, F.lit("Sí"))
             .otherwise(F.lit("No"))
             .alias("tiene_descuento"),
        )
        .orderBy("descuento_pct")
    )
