"""Dimensión Estado de envío: generada (no viene de la fuente) -> dim_estado_envio.

Dimensión basura (junk dimension): agrupa tres indicadores de baja cardinalidad
del pedido (estado, cumplimiento y rango de días de despacho) en 9 combinaciones.
"""

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F

TABLA = "dim_estado_envio"

ENVIADO = "Enviado"
PENDIENTE = "Pendiente"
A_TIEMPO = "A tiempo"
TARDE = "Tarde"
SIN_ENVIAR = "Sin enviar"

# (días máximos del rango, etiqueta). El último rango no tiene tope.
RANGOS_DESPACHO = [
    (7, "0-7 días"),
    (14, "8-14 días"),
    (28, "15-28 días"),
    (None, "Más de 28 días"),
]


def transformar(spark: SparkSession, fuente: dict[str, DataFrame]) -> DataFrame:
    """Genera las 9 combinaciones posibles (no depende de la fuente).

    - Enviado x (A tiempo, Tarde) x 4 rangos de despacho = 8 filas.
    - Pendiente / Pendiente / Sin enviar = 1 fila (pedidos sin shipped_date, H2).
    - Se generan todas aunque hoy algunas no tengan pedidos (Tarde con 0-7 u
      8-14 días), para que el DW acepte datos futuros sin cambios.
    - coalesce(1): se inserta en un solo bloque y en este orden, así la llave
      IDENTITY queda siempre igual (1 = Enviado / A tiempo / 0-7 días ... 9 = Pendiente).
    """
    filas = [
        (ENVIADO, cumplimiento, rango)
        for cumplimiento in (A_TIEMPO, TARDE)
        for _, rango in RANGOS_DESPACHO
    ]
    filas.append((PENDIENTE, PENDIENTE, SIN_ENVIAR))

    return spark.createDataFrame(
        filas, "estado_envio string, cumplimiento string, rango_despacho string"
    ).coalesce(1)


def columnas_estado(
    fecha_pedido: str = "order_date",
    fecha_requerida: str = "required_date",
    fecha_envio: str = "shipped_date",
) -> list[Column]:
    """Clasifica cada pedido con las mismas reglas de la dimensión (§4.7).

    Para usar en fact_pedidos: se agregan estas 3 columnas a orders y luego se
    hace join con dim_estado_envio (leída del DW) para obtener estado_envio_key:

        pedidos.select("*", *columnas_estado())
               .join(dw["dim_estado_envio"],
                     ["estado_envio", "cumplimiento", "rango_despacho"])

    - Pendiente: shipped_date nulo (H2).
    - A tiempo: shipped_date <= required_date; Tarde: posterior.
    - rango_despacho: según datediff(shipped_date, order_date).
    """
    envio = F.col(fecha_envio)
    pendiente = envio.isNull()
    dias = F.datediff(envio, F.col(fecha_pedido))

    estado = F.when(pendiente, F.lit(PENDIENTE)).otherwise(F.lit(ENVIADO))

    cumplimiento = (
        F.when(pendiente, F.lit(PENDIENTE))
        .when(envio <= F.col(fecha_requerida), F.lit(A_TIEMPO))
        .otherwise(F.lit(TARDE))
    )

    rango = F.when(pendiente, F.lit(SIN_ENVIAR))
    for tope, etiqueta in RANGOS_DESPACHO:
        if tope is None:
            rango = rango.otherwise(F.lit(etiqueta))
        else:
            rango = rango.when(dias <= tope, F.lit(etiqueta))

    return [
        estado.alias("estado_envio"),
        cumplimiento.alias("cumplimiento"),
        rango.alias("rango_despacho"),
    ]
