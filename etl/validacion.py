"""Validación de la carga: concilia la fuente (PostgreSQL) contra el DW (SQL Server).

Se ejecuta al final de main.py (etapa 8) o por separado, sin recargar el DW:

    python etl/validacion.py

Cada control compara el valor de la fuente, el del DW y el esperado
(docs/04_diseno_etl.md §6) y muestra OK, ERROR o PENDIENTE.
"""

import importlib.util
from decimal import Decimal

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import leer_dw

TABLAS_DW = [
    "dim_tiempo", "dim_cliente", "dim_producto", "dim_empleado",
    "dim_transportista", "dim_descuento", "dim_estado_envio",
    "fact_ventas", "fact_pedidos",
]


def _suma(df: DataFrame, expresion) -> Decimal | None:
    """Suma redondeada a 2 decimales (None si la tabla está vacía)."""
    return df.select(F.round(F.sum(expresion), 2)).first()[0]


def _modulo_existe(nombre: str) -> bool:
    return importlib.util.find_spec(nombre) is not None


def _controles(fuente: dict[str, DataFrame], dw: dict[str, DataFrame]) -> list[tuple]:
    """Devuelve (control, tabla_dw, valor_fuente, valor_dw, esperado)."""
    detalle = fuente["order_details"]
    pedidos = fuente["orders"]
    ventas = dw["fact_ventas"]
    hechos_pedidos = dw["fact_pedidos"]

    # Medidas en DECIMAL (no en float) para que la suma sea exacta
    neto_fuente = (
        F.col("unit_price").cast("decimal(10,2)")
        * F.col("quantity").cast("int")
        * (F.lit(1) - F.col("discount").cast("decimal(4,2)"))
    )

    return [
        ("Clientes", "dim_cliente",
         fuente["customers"].count(), dw["dim_cliente"].count(), 91),
        ("Productos", "dim_producto",
         fuente["products"].count(), dw["dim_producto"].count(), 77),
        ("Empleados", "dim_empleado",
         fuente["employees"].count(), dw["dim_empleado"].count(), 9),
        ("Transportistas", "dim_transportista",
         fuente["shippers"].count(), dw["dim_transportista"].count(), 3),
        ("Días", "dim_tiempo",
         None, dw["dim_tiempo"].count(), 1095),
        ("Descuentos", "dim_descuento",
         detalle.select(F.col("discount").cast("decimal(4,2)")).distinct().count(),
         dw["dim_descuento"].count(), 11),
        ("Estados de envío", "dim_estado_envio",
         None, dw["dim_estado_envio"].count(), 9),
        ("Líneas de venta", "fact_ventas",
         detalle.count(), ventas.count(), 2155),
        ("Pedidos", "fact_pedidos",
         pedidos.count(), hechos_pedidos.count(), 830),
        ("Ventas netas", "fact_ventas",
         _suma(detalle, neto_fuente), _suma(ventas, F.col("monto_neto")),
         Decimal("1265793.04")),
        # Flete: el esperado es que fuente y DW sean iguales
        ("Flete total", "fact_pedidos",
         _suma(pedidos, F.col("freight").cast("decimal(10,2)")),
         _suma(hechos_pedidos, F.col("flete")), None),
        ("Pedidos pendientes", "fact_pedidos",
         pedidos.filter(F.col("shipped_date").isNull()).count(),
         hechos_pedidos
         .join(dw["dim_estado_envio"], "estado_envio_key")
         .filter(F.col("estado_envio") == "Pendiente")
         .count(),
         21),
        ("Pedidos tarde", "fact_pedidos",
         pedidos.filter(F.col("shipped_date") > F.col("required_date")).count(),
         hechos_pedidos.filter(F.col("entregado_a_tiempo") == 0).count(),
         37),
    ]


def _resultado(tabla: str, fuente, dw, esperado) -> str:
    # Hecho todavía sin ETL (falta etl/fact_*.py): no es un error de la carga
    if tabla.startswith("fact_") and not _modulo_existe(tabla) and not dw:
        return "PENDIENTE"
    valores = [v for v in (fuente, dw, esperado) if v is not None]
    if dw is None or len(set(valores)) != 1:
        return "ERROR"
    return "OK"


def _formato(valor) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, Decimal):
        return f"{valor:,.2f}"
    return f"{valor:,}"


def ejecutar(spark: SparkSession, fuente: dict[str, DataFrame]) -> bool:
    """Imprime la tabla de controles y devuelve True si no hay errores."""
    dw = {tabla: leer_dw(spark, tabla) for tabla in TABLAS_DW}

    print(f"  {'Control':<20}{'Fuente':>15}{'DW':>15}{'Esperado':>15}  Resultado")
    print("  " + "-" * 76)
    resumen = {"OK": 0, "ERROR": 0, "PENDIENTE": 0}
    for control, tabla, v_fuente, v_dw, esperado in _controles(fuente, dw):
        resultado = _resultado(tabla, v_fuente, v_dw, esperado)
        resumen[resultado] += 1
        texto_esperado = "= fuente" if esperado is None else _formato(esperado)
        print(f"  {control:<20}{_formato(v_fuente):>15}{_formato(v_dw):>15}"
              f"{texto_esperado:>15}  {resultado}")

    print("  " + "-" * 76)
    print(f"  {resumen['OK']} OK · {resumen['ERROR']} ERROR · "
          f"{resumen['PENDIENTE']} PENDIENTE")
    if resumen["ERROR"]:
        print("  Hay controles con ERROR: revisar la transformación antes de usar los reportes.")
    return resumen["ERROR"] == 0


if __name__ == "__main__":
    # Validación sola, sobre lo que ya está cargado en el DW
    import sys

    from config import crear_spark
    from main import extraer

    spark = crear_spark()
    try:
        fuente = extraer(spark)
        print("\n=== VALIDACIÓN (fuente vs. DW) ===")
        sys.exit(0 if ejecutar(spark, fuente) else 1)
    finally:
        spark.stop()
