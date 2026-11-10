
"""Hechos de pedidos: orders + líneas calculadas + dimensiones -> fact_pedidos.

Granularidad: una fila por pedido -> 830 filas. Guarda las medidas que
pertenecen al pedido completo (flete, fechas, cumplimiento) para no repetirlas
en cada línea de fact_ventas.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import buscar_llave, fecha_key, limpiar_texto
from dim_estado_envio import columnas_estado
from fact_ventas import calcular_lineas

# Nombre de la tabla de destino
TABLA = "fact_pedidos"


def transformar(
    spark: SparkSession, fuente: dict[str, DataFrame], dw: dict[str, DataFrame]
) -> DataFrame:
    """Agrega las líneas por pedido y calcula las medidas de logística (§4.9).

    - lineas y monto_neto_pedido salen de las mismas líneas de fact_ventas.
    - Pedidos pendientes (H2): fecha_envio_key, dias_despacho y
      entregado_a_tiempo quedan en NULL y apuntan a Pendiente / Sin enviar.
    - entregado_a_tiempo: 1 si shipped_date <= required_date, 0 si es posterior.
    """

    # Agrupa las líneas y calcula los totales de cada pedido
    totales = (
        calcular_lineas(fuente)
        .groupBy("pedido_id")
        .agg(
            F.count("*").cast("int").alias("lineas"),
            F.sum("monto_neto").cast("decimal(14,4)").alias("monto_neto_pedido"),
        )
    )

    # Identifica los pedidos que ya fueron enviados
    enviado = F.col("shipped_date").isNotNull()

    # Obtiene los pedidos y calcula sus medidas de logística
    pedidos = (
        fuente["orders"]
        .select(
            F.col("order_id").cast("int").alias("pedido_id"),
            fecha_key("order_date").alias("fecha_pedido_key"),
            fecha_key("required_date").alias("fecha_requerida_key"),
            fecha_key("shipped_date").alias("fecha_envio_key"),
            limpiar_texto("customer_id").alias("cliente_id"),
            F.col("employee_id").cast("int").alias("empleado_id"),
            F.col("shipper_id").cast("int").alias("transportista_id"),
            F.col("freight").cast("decimal(10,2)").alias("flete"),
            F.datediff("shipped_date", "order_date").alias("dias_despacho"),

            # Determina si el pedido fue entregado a tiempo
            F.when(enviado & (F.col("shipped_date") <= F.col("required_date")), F.lit(1))
             .when(enviado, F.lit(0))
             .cast("int")
             .alias("entregado_a_tiempo"),

            # Agrega la información del estado de envío
            # estado_envio, cumplimiento, rango_despacho (mismas reglas que la dimensión)
            *columnas_estado(),
        )

        # Une los pedidos con sus totales
        # Todo pedido tiene al menos una línea (docs/02 §2.3)
        .join(totales, "pedido_id", "inner")
        .cache()
    )

    # Busca las llaves correspondientes en las dimensiones
    pedidos = buscar_llave(pedidos, dw["dim_cliente"], "cliente_id", "cliente_key", TABLA)
    pedidos = buscar_llave(pedidos, dw["dim_empleado"], "empleado_id", "empleado_key", TABLA)
    pedidos = buscar_llave(
        pedidos, dw["dim_transportista"], "transportista_id", "transportista_key", TABLA
    )
    pedidos = buscar_llave(
        pedidos,
        dw["dim_estado_envio"],
        ["estado_envio", "cumplimiento", "rango_despacho"],
        "estado_envio_key",
        TABLA,
    )

    # Selecciona las columnas finales de la tabla fact_pedidos
    return pedidos.select(
        "pedido_id",
        "fecha_pedido_key",
        "fecha_requerida_key",
        "fecha_envio_key",
        "cliente_key",
        "empleado_key",
        "transportista_key",
        "estado_envio_key",
        "flete",
        "lineas",
        "monto_neto_pedido",
        "dias_despacho",
        "entregado_a_tiempo",
    )
