"""Dimensión Empleado: employees (unida consigo misma) -> dim_empleado."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import estandarizar_pais, limpiar_texto

TABLA = "dim_empleado"

JEFE_DIRECCION = "Sin jefe (Dirección)"


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Resuelve el nombre del jefe directo con un self-join sobre employees.

    - jefe: nombre del empleado indicado en reports_to. El máximo jerarca
      (Andrew Fuller) no tiene jefe y queda como 'Sin jefe (Dirección)' (H3).
    - Textos sin espacios dobles (H4) y países estandarizados (H5).
    - Elimina posibles duplicados por llave natural.
    """
    empleados = fuente["employees"].alias("e")
    jefes = fuente["employees"].alias("j")

    return (
        # LEFT JOIN para no perder al empleado que no tiene jefe
        empleados
        .join(jefes, F.col("e.reports_to") == F.col("j.employee_id"), "left")
        .select(
            F.col("e.employee_id").cast("int").alias("empleado_id"),
            limpiar_texto("e.employee_name").alias("empleado"),
            limpiar_texto("e.title").alias("cargo"),
            limpiar_texto("e.city").alias("ciudad"),
            estandarizar_pais("e.country").alias("pais"),
            F.coalesce(limpiar_texto("j.employee_name"), F.lit(JEFE_DIRECCION))
             .alias("jefe"),
        )
        .dropDuplicates(["empleado_id"])
        .orderBy("empleado_id")
    )
