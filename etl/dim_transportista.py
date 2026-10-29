"""Dimensión Transportista: shippers -> dim_transportista."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import limpiar_texto

TABLA = "dim_transportista"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Toma los transportistas de la tabla shippers.

    - Conserva shipper_id como llave natural (transportista_id).
    - Limpia el nombre de la empresa: espacios al inicio/final y dobles (H4).
    - Elimina posibles duplicados por llave natural.
    """
    origen = fuente["shippers"]
    return (
        origen.select(
            F.col("shipper_id").cast("int").alias("transportista_id"),
            limpiar_texto("company_name").alias("transportista"),
        )
        .dropDuplicates(["transportista_id"])
        .orderBy("transportista_id")
    )
