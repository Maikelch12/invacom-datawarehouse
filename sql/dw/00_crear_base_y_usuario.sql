-- 1. Base de datos del Data Warehouse
CREATE DATABASE InvacomDW;
GO

-- 2. Usuario exclusivo para el proceso ETL (Spark)
CREATE LOGIN etl_spark WITH PASSWORD = 'CambienEstaClave123!';
GO

USE InvacomDW;
GO
CREATE USER etl_spark FOR LOGIN etl_spark;
ALTER ROLE db_owner ADD MEMBER etl_spark;
GO

