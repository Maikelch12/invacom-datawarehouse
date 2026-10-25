import os
import sys

from dotenv import load_dotenv
from pyspark.sql import SparkSession

load_dotenv()
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Windows: Spark necesita winutils.exe y hadoop.dll (ver README)
hadoop_home = os.getenv("HADOOP_HOME", r"C:\hadoop")
os.environ["HADOOP_HOME"] = hadoop_home
os.environ["PATH"] = os.path.join(hadoop_home, "bin") + os.pathsep + os.environ["PATH"]

print("=== Revisión del entorno ===")
print("HADOOP_HOME =", hadoop_home)
for archivo in ("winutils.exe", "hadoop.dll"):
    ruta = os.path.join(hadoop_home, "bin", archivo)
    if not os.path.exists(ruta):
        sys.exit(f"FALTA {ruta}: descárguenlo antes de continuar.")
    print("OK", ruta)

# Spark descarga los drivers JDBC automáticamente la primera vez
spark = (
    SparkSession.builder
    .appName("Invacom - prueba de conexion")
    .master("local[*]")
    .config(
        "spark.jars.packages",
        "org.postgresql:postgresql:42.7.4,"
        "com.microsoft.sqlserver:mssql-jdbc:12.8.1.jre11",
    )
    .config("spark.driver.extraJavaOptions", f"-Dhadoop.home.dir={hadoop_home.replace(chr(92), '/')}")
    .getOrCreate()
)

# Origen: PostgreSQL
PG_URL = (
    f"jdbc:postgresql://{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/"
    f"{os.getenv('PG_DB')}"
)
PG_PROPS = {
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "driver": "org.postgresql.Driver",
}

# Destino: SQL Server
SQL_URL = (
    f"jdbc:sqlserver://{os.getenv('MS_HOST')}:{os.getenv('MS_PORT')};"
    f"databaseName={os.getenv('MS_DB')};"
    "encrypt=true;trustServerCertificate=true"
)
SQL_PROPS = {
    "user": os.getenv("MS_USER"),
    "password": os.getenv("MS_PASSWORD"),
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
}

print("=== Leyendo shippers desde PostgreSQL ===")
df = spark.read.jdbc(PG_URL, "shippers", properties=PG_PROPS)
df.show()

print("=== Escribiendo en SQL Server ===")
df.write.jdbc(SQL_URL, "prueba_shippers", mode="overwrite", properties=SQL_PROPS)

print("=== Leyendo de vuelta desde SQL Server ===")
spark.read.jdbc(SQL_URL, "prueba_shippers", properties=SQL_PROPS).show()

spark.stop()