
import argparse
import importlib
import time

from config import (
    TABLAS_FUENTE, crear_spark, ejecutar_sql_dw, escribir_dw, leer_dw, leer_fuente,
)

# Orden de carga: dimensiones primero, luego hechos (dependen de las dimensiones)
DIMENSIONES = [
    "dim_tiempo",
    "dim_cliente",
    "dim_producto",
    "dim_empleado",
    "dim_transportista",
    "dim_descuento",
    "dim_estado_envio",
]
HECHOS = ["fact_ventas", "fact_pedidos"]

# Tablas del DW con llave IDENTITY (se reinicia el contador en cada carga completa)
TABLAS_IDENTITY = [
    "fact_ventas", "dim_cliente", "dim_producto", "dim_empleado",
    "dim_transportista", "dim_descuento", "dim_estado_envio",
]


def importar(nombre: str):
    """Importa el módulo de una tabla; devuelve None si aún no existe."""
    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError as error:
        if error.name == nombre:
            return None
        raise


def extraer(spark) -> dict:
    print("\n=== 1. EXTRACCIÓN (PostgreSQL) ===")
    fuente = {}
    for tabla in TABLAS_FUENTE:
        fuente[tabla] = leer_fuente(spark, tabla).cache()
        print(f"  {tabla:<15} {fuente[tabla].count():>6} filas")
    return fuente


def vaciar_dw(spark) -> None:
    print("\n=== 2. VACIADO DEL DW (SQL Server) ===")
    # Orden inverso a la carga: los hechos referencian a las dimensiones
    sentencias = [f"DELETE FROM dbo.{tabla};" for tabla in HECHOS + DIMENSIONES[::-1]]
    for tabla in TABLAS_IDENTITY:
        # Solo se reinicia si la tabla ya tuvo filas alguna vez (si no, el primer valor sería 0)
        sentencias.append(
            f"IF (SELECT last_value FROM sys.identity_columns "
            f"WHERE object_id = OBJECT_ID('dbo.{tabla}')) IS NOT NULL "
            f"DBCC CHECKIDENT ('dbo.{tabla}', RESEED, 0);"
        )
    ejecutar_sql_dw(spark, sentencias)
    print("  Hechos y dimensiones vaciados; contadores IDENTITY reiniciados")


def cargar_dimensiones(spark, fuente: dict) -> list[str]:
    print("\n=== 3. TRANSFORMACIÓN Y CARGA DE DIMENSIONES ===")
    pendientes = []
    for nombre in DIMENSIONES:
        modulo = importar(nombre)
        if modulo is None:
            print(f"  {nombre:<20} PENDIENTE (falta etl/{nombre}.py)")
            pendientes.append(nombre)
            continue
        inicio = time.time()
        df = modulo.transformar(spark, fuente)
        filas = escribir_dw(df, modulo.TABLA)
        print(f"  {modulo.TABLA:<20} {filas:>6} filas  ({time.time() - inicio:.1f} s)")
    return pendientes


def cargar_hechos(spark, fuente: dict) -> None:
    print("\n=== 4. TRANSFORMACIÓN Y CARGA DE HECHOS ===")
    # Las dimensiones se leen de vuelta del DW para obtener las llaves sustitutas
    dw = {nombre: leer_dw(spark, nombre).cache() for nombre in DIMENSIONES}
    for nombre in HECHOS:
        modulo = importar(nombre)
        if modulo is None:
            print(f"  {nombre:<20} PENDIENTE (falta etl/{nombre}.py)")
            continue
        inicio = time.time()
        df = modulo.transformar(spark, fuente, dw)
        filas = escribir_dw(df, modulo.TABLA)
        print(f"  {modulo.TABLA:<20} {filas:>6} filas  ({time.time() - inicio:.1f} s)")


def validar(spark, fuente: dict) -> None:
    print("\n=== 5. VALIDACIÓN (fuente vs. DW) ===")
    modulo = importar("validacion")
    if modulo is None:
        print("  PENDIENTE (falta etl/validacion.py)")
        return
    modulo.ejecutar(spark, fuente)


def probar(spark, nombre: str) -> None:
    """Transforma una sola tabla y muestra el resultado sin escribir en el DW."""
    modulo = importar(nombre)
    if modulo is None:
        raise SystemExit(f"No existe etl/{nombre}.py")
    fuente = extraer(spark)
    if nombre in HECHOS:
        dw = {dim: leer_dw(spark, dim) for dim in DIMENSIONES}
        df = modulo.transformar(spark, fuente, dw)
    else:
        df = modulo.transformar(spark, fuente)
    print(f"\n=== PRUEBA: {nombre} ({df.count()} filas) — no se escribió en el DW ===")
    df.printSchema()
    df.show(20, truncate=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="ETL del Data Warehouse de Invacom")
    parser.add_argument("--probar", metavar="TABLA",
                        help="transforma y muestra una tabla sin escribir en el DW")
    args = parser.parse_args()

    inicio = time.time()
    spark = crear_spark()
    try:
        if args.probar:
            probar(spark, args.probar)
            return

        fuente = extraer(spark)
        vaciar_dw(spark)
        pendientes = cargar_dimensiones(spark, fuente)
        if pendientes:
            print("\n  Hechos NO cargados: faltan dimensiones -> " + ", ".join(pendientes))
        else:
            cargar_hechos(spark, fuente)
            validar(spark, fuente)
        print(f"\nETL terminado en {time.time() - inicio:.1f} s")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
