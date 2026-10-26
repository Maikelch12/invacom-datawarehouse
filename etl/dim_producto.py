"""Dimensión Producto: products + categories -> dim_producto."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import limpiar_texto

TABLA = "dim_producto"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Une cada producto con su categoría (desnormalización del esquema estrella).

    - Textos sin espacios dobles (H4).
    - discontinued (true/false) -> 'Sí' / 'No' (H10).
    - precio_lista es el precio actual de catálogo; las ventas usan el
      precio histórico de order_details (H6).
    """
    products = fuente["products"].alias("p")
    categories = fuente["categories"].alias("c")

    return (
        products
        .join(categories, F.col("p.category_id") == F.col("c.category_id"), "left")
        .select(
            F.col("p.product_id").alias("producto_id"),
            limpiar_texto("p.product_name").alias("producto"),
            limpiar_texto("p.quantity_per_unit").alias("cantidad_por_unidad"),
            limpiar_texto("c.category_name").alias("categoria"),
            F.col("p.unit_price").cast("decimal(10,2)").alias("precio_lista"),
            F.when(F.col("p.discontinued"), F.lit("Sí"))
             .otherwise(F.lit("No"))
             .alias("descontinuado"),
        )
    )
