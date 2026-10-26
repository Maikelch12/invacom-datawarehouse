"""Dimensión Cliente: customers -> dim_cliente."""

from pyspark.sql import DataFrame, SparkSession

from config import estandarizar_pais, limpiar_texto

TABLA = "dim_cliente"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Limpia los textos (H4) y estandariza los países (H5).

    Se cargan los 91 clientes, incluidos los 2 que nunca compraron (H9).
    contact_name se descarta porque no responde ninguna pregunta de negocio.
    """
    customers = fuente["customers"]

    return customers.select(
        limpiar_texto("customer_id").alias("cliente_id"),
        limpiar_texto("company_name").alias("empresa"),
        limpiar_texto("contact_title").alias("cargo_contacto"),
        limpiar_texto("city").alias("ciudad"),
        estandarizar_pais("country").alias("pais"),
    )
