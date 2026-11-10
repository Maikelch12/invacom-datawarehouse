# Dimensión Descuento: valores distintos de order_details.discount -> dim_descuento.

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

# Nombre de la tabla de destino
TABLA = "dim_descuento"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Dimensión de bandas: agrupa los porcentajes de descuento en rangos.

    - Una fila por cada porcentaje distinto en order_details (11 valores).
    - descuento_texto: 0.15 -> '15 %'.
    - rango_descuento: Sin descuento / Bajo (1-5 %) / Medio (6-15 %) / Alto (16-25 %).
    - Conserva los descuentos atípicos del pedido 11077 (H7).
    """

    # Obtiene los descuentos de los detalles de pedidos y elimina duplicados
    descuentos = (
        fuente["order_details"]
        .select(F.col("discount").cast("decimal(4,2)").alias("descuento_pct"))
        .distinct()
    )

    # Define la columna que contiene el porcentaje de descuento
    pct = F.col("descuento_pct")

    # Genera las columnas descriptivas y clasifica los descuentos
    return (
        descuentos
        .select(
            pct,
            # Convierte el porcentaje a texto
            F.concat((pct * 100).cast("int").cast("string"), F.lit(" %"))
             .alias("descuento_texto"),

            # Clasifica los descuentos según su porcentaje
            F.when(pct == 0, F.lit("Sin descuento"))
             .when(pct <= 0.05, F.lit("Bajo (1-5 %)"))
             .when(pct <= 0.15, F.lit("Medio (6-15 %)"))
             .otherwise(F.lit("Alto (16-25 %)"))
             .alias("rango_descuento"),

            # Indica si el descuento es mayor que cero
            F.when(pct > 0, F.lit("Sí"))
             .otherwise(F.lit("No"))
             .alias("tiene_descuento"),
        )
        # Ordena los registros por porcentaje de descuento
        .orderBy("descuento_pct")
    )