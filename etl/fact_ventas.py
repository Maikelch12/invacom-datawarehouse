"""Hechos de ventas: order_details + orders + dimensiones -> fact_ventas.

Granularidad: una fila por línea de pedido (pedido + producto) -> 2155 filas.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import buscar_llave, fecha_key, limpiar_texto

TABLA = "fact_ventas"


def calcular_lineas(fuente: dict[str, DataFrame]) -> DataFrame:
    """Une cada línea con su pedido y calcula las medidas (§4.8, pasos 1 a 3).

    Todavía con llaves de negocio (sin llaves sustitutas). La usa también
    fact_pedidos para sumar el monto neto de cada pedido con la misma regla.

    - Precio histórico de order_details, nunca el de products (H6).
    - Descuentos atípicos del pedido 11077 se conservan (H7).
    - Medidas en DECIMAL: la suma de monto_neto da exacto 1 265 793.04.
    """
    detalle = fuente["order_details"]
    pedidos = fuente["orders"].select(
        "order_id", "customer_id", "employee_id", "shipper_id", "order_date"
    )

    precio = F.col("unit_price").cast("decimal(10,2)")
    cantidad = F.col("quantity").cast("int")
    descuento = F.col("discount").cast("decimal(4,2)")
    monto_bruto = (precio * cantidad).cast("decimal(14,4)")
    monto_descuento = (monto_bruto * descuento).cast("decimal(14,4)")

    return (
        detalle
        .join(pedidos, "order_id", "inner")
        .select(
            F.col("order_id").cast("int").alias("pedido_id"),
            fecha_key("order_date").alias("fecha_pedido_key"),
            # Mismos nombres y limpieza que las llaves de negocio de las dimensiones
            limpiar_texto("customer_id").alias("cliente_id"),
            F.col("product_id").cast("int").alias("producto_id"),
            F.col("employee_id").cast("int").alias("empleado_id"),
            F.col("shipper_id").cast("int").alias("transportista_id"),
            cantidad.alias("cantidad"),
            precio.alias("precio_unitario"),
            descuento.alias("descuento_pct"),
            monto_bruto.alias("monto_bruto"),
            monto_descuento.alias("monto_descuento"),
            (monto_bruto - monto_descuento).cast("decimal(14,4)").alias("monto_neto"),
        )
    )


def transformar(
    spark: SparkSession, fuente: dict[str, DataFrame], dw: dict[str, DataFrame]
) -> DataFrame:
    """Reemplaza las llaves de negocio por las llaves sustitutas del DW (§4.8, paso 4).

    Si alguna línea no encuentra su cliente, producto, empleado, transportista
    o descuento, buscar_llave detiene el ETL indicando cuáles faltan.
    """
    ventas = calcular_lineas(fuente).cache()

    ventas = buscar_llave(ventas, dw["dim_cliente"], "cliente_id", "cliente_key", TABLA)
    ventas = buscar_llave(ventas, dw["dim_producto"], "producto_id", "producto_key", TABLA)
    ventas = buscar_llave(ventas, dw["dim_empleado"], "empleado_id", "empleado_key", TABLA)
    ventas = buscar_llave(
        ventas, dw["dim_transportista"], "transportista_id", "transportista_key", TABLA
    )
    # El descuento se busca por su porcentaje (dimensión de bandas)
    ventas = buscar_llave(ventas, dw["dim_descuento"], "descuento_pct", "descuento_key", TABLA)

    return ventas.select(
        "pedido_id",
        "fecha_pedido_key",
        "cliente_key",
        "producto_key",
        "empleado_key",
        "transportista_key",
        "descuento_key",
        "cantidad",
        "precio_unitario",
        "descuento_pct",
        "monto_bruto",
        "monto_descuento",
        "monto_neto",
    )
