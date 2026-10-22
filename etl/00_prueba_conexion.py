import os
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession

#En Windows, Spark necesita saber qué Python usar para sus procesos
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

#Lee las credenciales del archivo .env (nunca se escriben en el código)
load_dotenv()

#Inicia Spark en modo local usando todos los núcleos del CPU.
#spark.jars.packages descarga los drivers JDBC la primera vez (requiere internet).
spark = (
    SparkSession.builder
    .appName("Invacom-PruebaConexion")
    .master("local[*]")
    .config("spark.jars.packages",
            "org.postgresql:postgresql:42.7.4,"
            "com.microsoft.sqlserver:mssql-jdbc:12.8.1.jre11")
    .getOrCreate()
)

#--- Conexión a PostgreSQL (fuente) ---
pg_url = f"jdbc:postgresql://{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
pg_props = {
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "driver": "org.postgresql.Driver",
}

#--- Conexión a SQL Server (Data Warehouse) ---
ms_url = (
    f"jdbc:sqlserver://{os.getenv('MS_HOST')}:{os.getenv('MS_PORT')};"
    f"databaseName={os.getenv('MS_DB')};encrypt=true;trustServerCertificate=true"
)
ms_props = {
    "user": os.getenv("MS_USER"),
    "password": os.getenv("MS_PASSWORD"),
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
}

#1. Extraer: leer pedidos desde PostgreSQL
pedidos = spark.read.jdbc(pg_url, "orders", properties=pg_props)
print("Pedidos leídos desde PostgreSQL:", pedidos.count())
pedidos.show(5)

#2. Cargar: escribir 10 filas de prueba en SQL Server
pedidos.limit(10).write.jdbc(ms_url, "dbo.prueba_conexion", mode="overwrite", properties=ms_props)

#3. Verificar: leer de vuelta desde SQL Server
prueba = spark.read.jdbc(ms_url, "dbo.prueba_conexion", properties=ms_props)
print("Filas escritas en SQL Server:", prueba.count())

spark.stop()