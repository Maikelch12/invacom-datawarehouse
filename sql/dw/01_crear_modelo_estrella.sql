-- =====================================================================
-- Modelo dimensional del Data Warehouse de Invacom Inc S.A.
-- Motor: SQL Server  |  Base: InvacomDW
-- 7 dimensiones + 2 tablas de hechos (fact_ventas y fact_pedidos)
-- Ejecutar en SSMS (F5). Se puede volver a ejecutar: borra y recrea todo.
-- =====================================================================

USE InvacomDW;
GO

-- ---------------------------------------------------------------------
-- 0. Limpieza: primero los hechos (dependen de las dimensiones)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS dbo.fact_ventas;
DROP TABLE IF EXISTS dbo.fact_pedidos;
DROP TABLE IF EXISTS dbo.dim_tiempo;
DROP TABLE IF EXISTS dbo.dim_cliente;
DROP TABLE IF EXISTS dbo.dim_producto;
DROP TABLE IF EXISTS dbo.dim_empleado;
DROP TABLE IF EXISTS dbo.dim_transportista;
DROP TABLE IF EXISTS dbo.dim_descuento;
DROP TABLE IF EXISTS dbo.dim_estado_envio;
DROP TABLE IF EXISTS dbo.prueba_shippers;   -- tabla de la prueba de conexión
GO


-- =====================================================================
-- DIMENSIONES
-- =====================================================================

-- Dimensión Tiempo: un registro por día (2013-01-01 a 2015-12-31)
-- La llave no es IDENTITY: es la fecha en formato AAAAMMDD (ej. 20140315)
CREATE TABLE dbo.dim_tiempo (
    tiempo_key        INT           NOT NULL,
    fecha             DATE          NOT NULL,
    anio              SMALLINT      NOT NULL,
    trimestre         TINYINT       NOT NULL,
    nombre_trimestre  CHAR(2)       NOT NULL,   -- T1, T2, T3, T4
    mes               TINYINT       NOT NULL,
    nombre_mes        NVARCHAR(15)  NOT NULL,   -- Enero, Febrero...
    anio_mes          CHAR(7)       NOT NULL,   -- 2014-03 (ordena bien en Excel)
    dia               TINYINT       NOT NULL,
    dia_semana        TINYINT       NOT NULL,   -- 1 = lunes ... 7 = domingo
    nombre_dia        NVARCHAR(10)  NOT NULL,   -- Lunes, Martes...
    es_fin_de_semana  NVARCHAR(2)   NOT NULL,   -- Sí / No
    CONSTRAINT pk_dim_tiempo PRIMARY KEY (tiempo_key),
    CONSTRAINT uq_dim_tiempo_fecha UNIQUE (fecha)
);

-- Dimensión Cliente
CREATE TABLE dbo.dim_cliente (
    cliente_key     INT IDENTITY(1,1) NOT NULL,
    cliente_id      VARCHAR(5)     NOT NULL,   -- llave de negocio (customers.customer_id)
    empresa         NVARCHAR(100)  NOT NULL,
    cargo_contacto  NVARCHAR(100)  NULL,
    ciudad          NVARCHAR(50)   NULL,
    pais            NVARCHAR(50)   NULL,       -- estandarizado (UK -> United Kingdom)
    CONSTRAINT pk_dim_cliente PRIMARY KEY (cliente_key),
    CONSTRAINT uq_dim_cliente_id UNIQUE (cliente_id)
);

-- Dimensión Producto (incluye la categoría: esquema estrella, no copo de nieve)
CREATE TABLE dbo.dim_producto (
    producto_key         INT IDENTITY(1,1) NOT NULL,
    producto_id          INT            NOT NULL,   -- llave de negocio (products.product_id)
    producto             NVARCHAR(100)  NOT NULL,
    cantidad_por_unidad  NVARCHAR(50)   NULL,
    categoria            NVARCHAR(50)   NOT NULL,
    precio_lista         DECIMAL(10,2)  NULL,       -- precio actual de catálogo (atributo, no medida)
    descontinuado        NVARCHAR(2)    NOT NULL,   -- Sí / No
    CONSTRAINT pk_dim_producto PRIMARY KEY (producto_key),
    CONSTRAINT uq_dim_producto_id UNIQUE (producto_id)
);

-- Dimensión Empleado (incluye el nombre del jefe directo)
CREATE TABLE dbo.dim_empleado (
    empleado_key  INT IDENTITY(1,1) NOT NULL,
    empleado_id   INT            NOT NULL,   -- llave de negocio (employees.employee_id)
    empleado      NVARCHAR(100)  NOT NULL,
    cargo         NVARCHAR(100)  NULL,
    ciudad        NVARCHAR(50)   NULL,
    pais          NVARCHAR(50)   NULL,
    jefe          NVARCHAR(100)  NOT NULL,   -- 'Sin jefe (Dirección)' para el máximo jerarca
    CONSTRAINT pk_dim_empleado PRIMARY KEY (empleado_key),
    CONSTRAINT uq_dim_empleado_id UNIQUE (empleado_id)
);

-- Dimensión Transportista
CREATE TABLE dbo.dim_transportista (
    transportista_key  INT IDENTITY(1,1) NOT NULL,
    transportista_id   INT            NOT NULL,   -- llave de negocio (shippers.shipper_id)
    transportista      NVARCHAR(100)  NOT NULL,
    CONSTRAINT pk_dim_transportista PRIMARY KEY (transportista_key),
    CONSTRAINT uq_dim_transportista_id UNIQUE (transportista_id)
);

-- Dimensión Descuento (dimensión de bandas: agrupa los porcentajes en rangos)
-- Un registro por cada porcentaje de descuento distinto en order_details
CREATE TABLE dbo.dim_descuento (
    descuento_key    INT IDENTITY(1,1) NOT NULL,
    descuento_pct    DECIMAL(4,2)   NOT NULL,   -- llave de negocio (0.15 = 15 %)
    descuento_texto  NVARCHAR(10)   NOT NULL,   -- '15 %'
    rango_descuento  NVARCHAR(30)   NOT NULL,   -- Sin descuento / Bajo / Medio / Alto
    tiene_descuento  NVARCHAR(2)    NOT NULL,   -- Sí / No
    CONSTRAINT pk_dim_descuento PRIMARY KEY (descuento_key),
    CONSTRAINT uq_dim_descuento_pct UNIQUE (descuento_pct)
);

-- Dimensión Estado de envío (junk dimension: combina indicadores de logística)
-- 9 combinaciones posibles de estado + cumplimiento + rango de días de despacho
CREATE TABLE dbo.dim_estado_envio (
    estado_envio_key  INT IDENTITY(1,1) NOT NULL,
    estado_envio      NVARCHAR(10)   NOT NULL,   -- Enviado / Pendiente
    cumplimiento      NVARCHAR(10)   NOT NULL,   -- A tiempo / Tarde / Pendiente
    rango_despacho    NVARCHAR(20)   NOT NULL,   -- 0-7 días / 8-14 días / 15-28 días / Más de 28 días / Sin enviar
    CONSTRAINT pk_dim_estado_envio PRIMARY KEY (estado_envio_key),
    CONSTRAINT uq_dim_estado_envio UNIQUE (estado_envio, cumplimiento, rango_despacho)
);
GO


-- =====================================================================
-- HECHOS
-- =====================================================================

-- Hechos de ventas
-- Granularidad: una fila por LÍNEA de pedido (pedido + producto) -> 2155 filas
CREATE TABLE dbo.fact_ventas (
    venta_key          INT IDENTITY(1,1) NOT NULL,
    pedido_id          INT            NOT NULL,   -- dimensión degenerada
    fecha_pedido_key   INT            NOT NULL,
    cliente_key        INT            NOT NULL,
    producto_key       INT            NOT NULL,
    empleado_key       INT            NOT NULL,
    transportista_key  INT            NOT NULL,
    descuento_key      INT            NOT NULL,
    -- Medidas
    cantidad           INT            NOT NULL,
    precio_unitario    DECIMAL(10,2)  NOT NULL,   -- precio histórico de la venta
    descuento_pct      DECIMAL(4,2)   NOT NULL,   -- 0.15 = 15 %
    monto_bruto        DECIMAL(14,4)  NOT NULL,   -- precio_unitario * cantidad
    monto_descuento    DECIMAL(14,4)  NOT NULL,   -- monto_bruto * descuento_pct
    monto_neto         DECIMAL(14,4)  NOT NULL,   -- monto_bruto - monto_descuento
    CONSTRAINT pk_fact_ventas PRIMARY KEY (venta_key),
    CONSTRAINT uq_fact_ventas_linea UNIQUE (pedido_id, producto_key),
    CONSTRAINT fk_ventas_fecha         FOREIGN KEY (fecha_pedido_key)  REFERENCES dbo.dim_tiempo (tiempo_key),
    CONSTRAINT fk_ventas_cliente       FOREIGN KEY (cliente_key)       REFERENCES dbo.dim_cliente (cliente_key),
    CONSTRAINT fk_ventas_producto      FOREIGN KEY (producto_key)      REFERENCES dbo.dim_producto (producto_key),
    CONSTRAINT fk_ventas_empleado      FOREIGN KEY (empleado_key)      REFERENCES dbo.dim_empleado (empleado_key),
    CONSTRAINT fk_ventas_transportista FOREIGN KEY (transportista_key) REFERENCES dbo.dim_transportista (transportista_key),
    CONSTRAINT fk_ventas_descuento     FOREIGN KEY (descuento_key)     REFERENCES dbo.dim_descuento (descuento_key)
);

-- Hechos de pedidos (logística y totales por pedido)
-- Granularidad: una fila por PEDIDO -> 830 filas
CREATE TABLE dbo.fact_pedidos (
    pedido_id            INT            NOT NULL,   -- dimensión degenerada y llave
    fecha_pedido_key     INT            NOT NULL,
    fecha_requerida_key  INT            NOT NULL,
    fecha_envio_key      INT            NULL,       -- NULL = pedido pendiente de envío
    cliente_key          INT            NOT NULL,
    empleado_key         INT            NOT NULL,
    transportista_key    INT            NOT NULL,
    estado_envio_key     INT            NOT NULL,
    -- Medidas
    flete                DECIMAL(10,2)  NOT NULL,
    lineas               INT            NOT NULL,   -- cantidad de productos distintos en el pedido
    monto_neto_pedido    DECIMAL(14,4)  NOT NULL,   -- suma de monto_neto de sus líneas
    dias_despacho        INT            NULL,       -- fecha_envio - fecha_pedido (NULL si pendiente)
    entregado_a_tiempo   TINYINT        NULL,       -- 1 = a tiempo, 0 = tarde, NULL = pendiente
    CONSTRAINT pk_fact_pedidos PRIMARY KEY (pedido_id),
    CONSTRAINT fk_pedidos_fecha_pedido    FOREIGN KEY (fecha_pedido_key)    REFERENCES dbo.dim_tiempo (tiempo_key),
    CONSTRAINT fk_pedidos_fecha_requerida FOREIGN KEY (fecha_requerida_key) REFERENCES dbo.dim_tiempo (tiempo_key),
    CONSTRAINT fk_pedidos_fecha_envio     FOREIGN KEY (fecha_envio_key)     REFERENCES dbo.dim_tiempo (tiempo_key),
    CONSTRAINT fk_pedidos_cliente         FOREIGN KEY (cliente_key)         REFERENCES dbo.dim_cliente (cliente_key),
    CONSTRAINT fk_pedidos_empleado        FOREIGN KEY (empleado_key)        REFERENCES dbo.dim_empleado (empleado_key),
    CONSTRAINT fk_pedidos_transportista   FOREIGN KEY (transportista_key)   REFERENCES dbo.dim_transportista (transportista_key),
    CONSTRAINT fk_pedidos_estado_envio    FOREIGN KEY (estado_envio_key)    REFERENCES dbo.dim_estado_envio (estado_envio_key)
);
GO


-- ---------------------------------------------------------------------
-- Verificación: deben aparecer 9 tablas
-- ---------------------------------------------------------------------
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
