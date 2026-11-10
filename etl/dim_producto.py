"""Dimensión Producto: products + categories -> dim_producto."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import limpiar_texto

# Nombre de la tabla de destino
TABLA = "dim_producto"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Une cada producto con su categoría (desnormalización del esquema estrella).

    - Textos sin espacios dobles (H4).
    - discontinued (true/false) -> 'Sí' / 'No' (H10).
    - precio_lista es el precio actual de catálogo; las ventas usan el
      precio histórico de order_details (H6).
    """

    # Obtiene los productos y las categorías de sus respectivas tablas
    products = fuente["products"].alias("p")
    categories = fuente["categories"].alias("c")

    # Une los productos con sus categorías y selecciona las columnas necesarias
    return (
        products
        .join(categories, F.col("p.category_id") == F.col("c.category_id"), "left")
        .select(
            # Identificador y nombre del producto
            F.col("p.product_id").alias("producto_id"),
            limpiar_texto("p.product_name").alias("producto"),

            # Información de presentación y categoría
            limpiar_texto("p.quantity_per_unit").alias("cantidad_por_unidad"),
            limpiar_texto("c.category_name").alias("categoria"),

            # Precio actual del producto
            F.col("p.unit_price").cast("decimal(10,2)").alias("precio_lista"),

            # Convierte el estado del producto a Sí o No
            F.when(F.col("p.discontinued"), F.lit("Sí"))
             .otherwise(F.lit("No"))
             .alias("descontinuado"),
        )
    )